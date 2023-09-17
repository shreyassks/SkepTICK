chrome.runtime.onMessage.addListener(function (message, sender, sendResponse) {
  if (message.action === "setTimestamp") {
    const timestamp = message.timestamp;
    // Find the active tab
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
      const activeTab = tabs[0];
      // Send a script to the tab to set the YouTube video's timestamp
      chrome.scripting.executeScript(activeTab.id, {
        code: `document.querySelector('video').currentTime = ${timestamp};`,
      });
    });
  }
});
