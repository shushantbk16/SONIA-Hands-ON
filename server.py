import os
import asyncio
import threading
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
from deepgram import DeepgramClient
from deepgram.core.events import EventType
from dotenv import load_dotenv
from resume_parser import generate_interview_questions,parse_resume

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


api_key = os.getenv("DEEPGRAM_API_KEY")
if not api_key:
    raise ValueError("DEEPGRAM_API_KEY not found in .env")

deepgram = DeepgramClient(api_key=api_key)

@app.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected")

    try:
        options = {
            "model": "nova-2",
            "language": "en-US",
            "smart_format": "true",
            "interim_results": "true",
            "encoding": "linear16",
            "channels": "1",
            "sample_rate": "16000",
        }


        with deepgram.listen.v1.connect(**options) as dg_socket:
            print("Connected to Deepgram")

            def on_open(open, **kwargs):
                print("Deepgram Connection Open")

            def on_message(result, **kwargs):
                try:
                    if hasattr(result, 'channel'):
                        alternatives = result.channel.alternatives
                        if alternatives:
                            sentence = alternatives[0].transcript
                            if len(sentence) > 0:
                                if result.is_final:
                                    print(f"\r{sentence}")
                                else:
                                    print(f"\r{sentence}", end="", flush=True)
                except Exception as e:
                    pass

            def on_error(error, **kwargs):
                print(f"Deepgram Error: {error}")

            dg_socket.on(EventType.OPEN, on_open)
            dg_socket.on(EventType.MESSAGE, on_message)
            dg_socket.on(EventType.ERROR, on_error)


            listen_thread = threading.Thread(target=dg_socket.start_listening)
            listen_thread.daemon = True
            listen_thread.start()

            try:
                while True:
                    data = await websocket.receive_bytes()

                    dg_socket.send_media(data)
            except WebSocketDisconnect:
                print("Client disconnected")
            except Exception as e:
                print(f"Error processing audio: {e}")
            


    except Exception as e:
        print(f"Connection error: {e}")
    except Exception as e:
        print(f"Connection error: {e}")
        await websocket.close()

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    try:
        upload_dir = "uploads"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        print(f"Resume uploaded: {file.filename}")
        resume_text = parse_resume(file_path)
        questions = "Could not parse resume."
        if resume_text:
            questions = generate_interview_questions(resume_text)
        

        return {
            "filename": file.filename, 
            "message": "Resume uploaded successfully",
            "questions": questions 
        }
        
    except Exception as e:
        print(f"Error uploading resume: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
