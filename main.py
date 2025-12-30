import os
import sys
import threading
import sounddevice as sd
from dotenv import load_dotenv
from deepgram import DeepgramClient
from deepgram.core.events import EventType

load_dotenv()

def main():
    try:
        # 1. Initialize Deepgram Client
        api_key = os.getenv("DEEPGRAM_API_KEY")
        if not api_key:
            print("Error: DEEPGRAM_API_KEY not found in .env")
            return

        print("Initializing Deepgram Client...")
        deepgram = DeepgramClient(api_key=api_key)

        # 2. Configure Options
        options = {
            "model": "nova-2",
            "language": "en-US",
            "smart_format": "true",
            "interim_results": "true",
            "encoding": "linear16",
            "channels": "1",
            "sample_rate": "16000",
        }

        # 3. Connect to Deepgram
        # deepgram.listen.v1.connect returns a context manager that yields the socket
        print("Connecting to Deepgram...")
        with deepgram.listen.v1.connect(**options) as socket:
            print("Connected!")

            # 4. Define Event Handlers
            def on_open(data):
                print(f"\n\n{'-'*50}")
                print("Connection Open! Speak into your microphone...")
                print(f"{'-'*50}\n")

            def on_message(result):
                try:
                    if hasattr(result, 'channel'):
                        alternatives = result.channel.alternatives
                        if alternatives:
                            sentence = alternatives[0].transcript
                            if len(sentence) > 0:
                                if result.is_final:
                                    # Final result: print on a new line
                                    print(f"\r{sentence}")
                                else:
                                    # Interim result: overwrite current line
                                    print(f"\r{sentence}", end="", flush=True)
                except Exception as e:
                    pass

            def on_error(error):
                print(f"\n\nError: {error}\n\n")

            def on_close(close):
                print(f"\n\nConnection Closed\n\n")

            # 5. Register Handlers
            socket.on(EventType.OPEN, on_open)
            socket.on(EventType.MESSAGE, on_message)
            socket.on(EventType.ERROR, on_error)
            socket.on(EventType.CLOSE, on_close)

            # 6. Start Listening Loop in a separate thread
            # This is necessary because socket.start_listening() blocks
            listen_thread = threading.Thread(target=socket.start_listening)
            listen_thread.daemon = True
            listen_thread.start()

            # 7. Start Microphone Stream
            def callback(indata, frames, time, status):
                if status:
                    print(status, file=sys.stderr)
                # Send raw audio bytes to Deepgram
                socket.send_media(indata.tobytes())

            print("Starting microphone stream...")
            
            # Open the stream
            with sd.InputStream(
                channels=1, 
                samplerate=16000, 
                dtype='int16', 
                callback=callback
            ):
                print("Press Enter to stop recording...")
                input()

            print("Stopping...")
            # Context manager exit will close the socket

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
