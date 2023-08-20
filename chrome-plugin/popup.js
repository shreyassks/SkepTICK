// document.getElementById('investForm').onsubmit = function(e) {
//     e.preventDefault();

//     const username = document.getElementById('username').value;
//     const amount = document.getElementById('amount').value;

//     // Send a message to the background script
//     chrome.runtime.sendMessage({username: username, amount: amount});
// };

document.addEventListener("DOMContentLoaded", function () {
  chrome.storage.local.get(["registered", "username"], function (result) {
    if (result.registered) {
      document.getElementById("not-registered").style.display = "none";
      console.log("Todo - fetch the transcript if its there");
    } else {
      document.getElementById("registered").style.display = "none";
      const registerButton = document.getElementById("register-button");
      registerButton.addEventListener("click", function () {
        chrome.tabs.create({ url: "register.html" });
      });
    }
  });
});
