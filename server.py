import os
import asyncio
import threading
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from deepgram import DeepgramClient
from deepgram.core.events import EventType
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Initialize Deepgram Client
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

        # Connect to Deepgram using the correct SDK v5 pattern
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

            # Start the listening thread (non-blocking for the main loop)
            listen_thread = threading.Thread(target=dg_socket.start_listening)
            listen_thread.daemon = True
            listen_thread.start()

            try:
                while True:
                    data = await websocket.receive_bytes()
                    # Send raw audio to Deepgram
                    dg_socket.send_media(data)
            except WebSocketDisconnect:
                print("Client disconnected")
            except Exception as e:
                print(f"Error processing audio: {e}")
            
            # Context manager exit will close the socket automatically

    except Exception as e:
        print(f"Connection error: {e}")
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
