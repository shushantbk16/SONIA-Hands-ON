document.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const statusDiv = document.getElementById('status');

    startBtn.addEventListener('click', () => {
        chrome.runtime.sendMessage({ type: 'START_RECORDING' }, (response) => {
            if (response && response.success) {
                statusDiv.textContent = 'Recording...';
                startBtn.disabled = true;
                stopBtn.disabled = false;
            } else {
                statusDiv.textContent = 'Error starting';
            }
        });
    });

    stopBtn.addEventListener('click', () => {
        chrome.runtime.sendMessage({ type: 'STOP_RECORDING' }, (response) => {
            statusDiv.textContent = 'Stopped';
            startBtn.disabled = false;
            stopBtn.disabled = true;
        });
    });

    const uploadBtn = document.getElementById('uploadBtn');
    const resumeInput = document.getElementById('resumeInput');

    uploadBtn.addEventListener('click', async () => {
        const file = resumeInput.files[0];
        if (!file) {
            statusDiv.textContent = 'Please select a file first.';
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        statusDiv.textContent = 'Uploading...';
        uploadBtn.disabled = true;

        try {
            const response = await fetch('http://localhost:8000/upload-resume', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const result = await response.json();
                statusDiv.textContent = 'Upload successful!';
                console.log('Upload result:', result);
                if (result.questions) {

                    let questionsDiv = document.getElementById('questions-container');
                    if (!questionsDiv) {
                        questionsDiv = document.createElement('div');
                        questionsDiv.id = 'questions-container';
                        document.body.appendChild(questionsDiv);
                    }


                    questionsDiv.innerText = result.questions;
                }
            } else {
                statusDiv.textContent = 'Upload failed.';
                console.error('Upload failed:', response.statusText);
            }
        } catch (error) {
            statusDiv.textContent = 'Error uploading.';
            console.error('Error:', error);
        } finally {
            uploadBtn.disabled = false;
        }
    });
});
