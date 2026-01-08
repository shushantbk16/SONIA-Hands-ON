let creating;

async function setupOffscreenDocument(path) {

    const offscreenUrl = chrome.runtime.getURL(path);
    const existingContexts = await chrome.runtime.getContexts({
        contextTypes: ['OFFSCREEN_DOCUMENT'],
        documentUrls: [offscreenUrl]
    });

    if (existingContexts.length > 0) {
        return;
    }


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
        return true;
    } else if (message.type === 'STOP_RECORDING') {
        stopRecording(sendResponse);
        return true;
    }
});

async function startRecording(sendResponse) {
    try {
        await setupOffscreenDocument('offscreen.html');


        const streamId = await chrome.tabCapture.getMediaStreamId({
            targetTabId: null
        });


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

    await chrome.offscreen.closeDocument();
    sendResponse({ success: true });
}


chrome.action.onClicked.addListener((tab) => {
    chrome.sidePanel.open({ windowId: tab.windowId });
});
