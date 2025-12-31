let socket;
let mediaRecorder;
let audioContext;
let processor;
let input;
let globalStream;

chrome.runtime.onMessage.addListener((message) => {
    if (message.type === 'START_FROM_BACKGROUND') {
        startCapture(message.streamId);
    } else if (message.type === 'STOP_FROM_BACKGROUND') {
        stopCapture();
    }
});

async function startCapture(streamId) {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            audio: {
                mandatory: {
                    chromeMediaSource: 'tab',
                    chromeMediaSourceId: streamId
                }
            },
            video: false
        });

        globalStream = stream;

        // Connect to WebSocket
        socket = new WebSocket('ws://localhost:8000/ws/audio');

        socket.onopen = () => {
            console.log('WebSocket connected');
            processAudio(stream);
        };

        socket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

    } catch (err) {
        console.error('Error starting capture:', err);
    }
}

function processAudio(stream) {
    audioContext = new AudioContext({ sampleRate: 16000 });
    input = audioContext.createMediaStreamSource(stream);
    processor = audioContext.createScriptProcessor(4096, 1, 1);

    input.connect(processor);
    processor.connect(audioContext.destination);
    // Connect input directly to destination to hear the audio
    input.connect(audioContext.destination);

    processor.onaudioprocess = (e) => {
        if (socket && socket.readyState === WebSocket.OPEN) {
            const inputData = e.inputBuffer.getChannelData(0);
            // Convert float32 to int16
            const pcmData = floatTo16BitPCM(inputData);
            socket.send(pcmData);
        }
    };
}

function stopCapture() {
    if (processor) {
        processor.disconnect();
        input.disconnect();
    }
    if (audioContext) {
        audioContext.close();
    }
    if (globalStream) {
        globalStream.getTracks().forEach(track => track.stop());
    }
    if (socket) {
        socket.close();
    }
}

function floatTo16BitPCM(output) {
    const buffer = new ArrayBuffer(output.length * 2);
    const view = new DataView(buffer);
    for (let i = 0; i < output.length; i++) {
        const s = Math.max(-1, Math.min(1, output[i]));
        view.setInt16(i * 2, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
    }
    return buffer;
}
