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
});
