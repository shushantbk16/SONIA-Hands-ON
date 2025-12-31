let creating; // A global promise to avoid concurrency issues

async function setupOffscreenDocument(path) {
    // Check all windows controlled by the service worker to see if one 
    // of them is the offscreen document with the given path
    const offscreenUrl = chrome.runtime.getURL(path);
    const existingContexts = await chrome.runtime.getContexts({
        contextTypes: ['OFFSCREEN_DOCUMENT'],
        documentUrls: [offscreenUrl]
    });

    if (existingContexts.length > 0) {
        return;
    }

    // create offscreen document
    if (creating) {
        await creating;
    } else {
        creating = chrome.offscreen.createDocument({
            url: path,
            reasons: ['USER_MEDIA'],
            justification: 'Recording from tab'
        });
        await creating;
        creating = null;
    }
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'START_RECORDING') {
        startRecording(sendResponse);
        return true; // Keep the message channel open for async response
    } else if (message.type === 'STOP_RECORDING') {
        stopRecording(sendResponse);
        return true;
    }
});

async function startRecording(sendResponse) {
    try {
        await setupOffscreenDocument('offscreen.html');

        // Get the stream ID from the active tab
        const streamId = await chrome.tabCapture.getMediaStreamId({
            targetTabId: null // current active tab
        });

        // Send stream ID to offscreen document
        chrome.runtime.sendMessage({
            type: 'START_FROM_BACKGROUND',
            streamId: streamId
        });

        sendResponse({ success: true });
    } catch (err) {
        console.error('Error starting recording:', err);
        sendResponse({ success: false, error: err.message });
    }
}

async function stopRecording(sendResponse) {
    chrome.runtime.sendMessage({ type: 'STOP_FROM_BACKGROUND' });
    // Close offscreen document
    await chrome.offscreen.closeDocument();
    sendResponse({ success: true });
}
