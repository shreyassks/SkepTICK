chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log(request);

  fetch("http://127.0.0.1:8000/v1/transcribe/breakdown", {
    method: "POST",
    body: JSON.stringify({ video_url: request.url }),
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
      console.log(data);
      chrome.storage.local.set(
        { transcibed: data, url: request.url },
        function () {
          console.log("Transcribe found!");
          console.log("calling whole truth");
          getWholeTruth();
          getStockTip();
        }
      );
    })
    .catch((error) => console.error("Error:", error));
});

function getWholeTruth() {
  fetch("http://127.0.0.1:8000/v1/wholetruth")
    .then((response) => {
      if (response.status === 200) {
        return response.json();
      } else {
        throw new Error("Request failed with status " + response.status);
      }
    })
    .then((data) => {
      console.log(data);
    });
}

function getStockTip() {
  fetch("http://127.0.0.1:8000/v1/stock_tips")
    .then((response) => {
      if (response.status === 200) {
        return response.json();
      } else {
        throw new Error("Request failed with status " + response.status);
      }
    })
    .then((data) => {
      console.log(data);
    });
}
