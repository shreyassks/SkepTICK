document.getElementById('investForm').onsubmit = function(e) {  
    e.preventDefault();  
  
    const username = document.getElementById('username').value;  
    const amount = document.getElementById('amount').value;  
  
    // Send a message to the background script  
    chrome.runtime.sendMessage({username: username, amount: amount});  
};