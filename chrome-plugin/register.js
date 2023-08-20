document.getElementById("register-form").onsubmit = function (e) {
  e.preventDefault();

  const username = document.getElementById("username").value;
  const amount = document.getElementById("amount").value;
  const age = document.getElementById("age").value;

  console.log({ username, amount, age });

  fetch("http://127.0.0.1:8000/register", {
    method: "POST",
    body: JSON.stringify({ username, amount, age }),
    headers: {
      "Content-type": "application/json",
    },
  })
    .then((response) => {
      if (response.status === 200) {
        return response.json();
      } else {
        throw new Error("Request failed with status " + response.status);
      }
    })
    .then((data) => {
      chrome.storage.local.set(
        { registered: true, username: username },
        function () {
          console.log("Registration is complete!");
          chrome.tabs.getCurrent(function (tab) {
            chrome.tabs.remove(tab.id);
          });
        }
      );
    })
    .catch((error) => console.error("Error:", error));
};
