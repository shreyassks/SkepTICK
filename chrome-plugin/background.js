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
      // data.claims.GTBL = []
      // data.thesis.thesis_
    })
    .catch((error) => console.error("Error:", error));
});
