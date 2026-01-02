# SONIA-Hands-ON


Real-time microphone transcription using Deepgram and Python.

## Features

- Real-time audio transcription
- Low latency streaming
- Easy-to-use command line interface


## Prerequisites

- Python 3.9+
- Deepgram API Key

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/shushantbk16/SONIA-Hands-ON.git
   cd SONIA-Hands-ON
   ``` 

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the root directory and add your Deepgram API key:
   ```
   DEEPGRAM_API_KEY=your_api_key_here
   ```

## Usage

Run the main script to start transcription:

```bash
python3 main.py
```

Speak into your microphone, and the transcript will appear in real-time in the terminal. Press `Enter` to stop.
