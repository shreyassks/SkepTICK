document.addEventListener("DOMContentLoaded", function () {
  chrome.storage.local.get(["registered", "username"], function (result) {
    if (result.registered) {
      document.getElementById("not-registered").style.display = "none";
      chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
        if (tabs.length > 0) {
          // The first tab in the array is the currently active tab
          const currentTab = tabs[0];

          // Get the URL of the current tab
          const currentTabUrl = currentTab.url;

          // Now, you can use currentTabUrl as needed in your extension
          console.log("Current tab URL:", currentTabUrl);

          if (currentTabUrl.indexOf("youtube.com/watch?v=") !== -1) {
            document.getElementById("not-youtube-watch").style.display = "none";
            const analyzeButton = document.getElementById("analyze-button");
            analyzeButton.addEventListener("click", () =>
              analyze(currentTabUrl)
            );
          } else {
            document.getElementById("youtube-watch").style.display = "none";
          }
        }
      });
    } else {
      document.getElementById("registered").style.display = "none";
      const registerButton = document.getElementById("register-button");
      registerButton.addEventListener("click", function () {
        chrome.tabs.create({ url: "register.html" });
      });
    }
  });
});

const data = {
  claims: {
    GTBL: [
      "The stock has given close to 2200% returns in the last five years.",
      "The company's revenues have been growing at an extremely high rate, with margins and earnings per share also growing significantly.",
      "The stock has gone from 55 Rupees to roughly 700 rupees level.",
      "The stock PE is right now at 19, compared to Nifty Pharma PE which is roughly at 31.",
      "The PEG ratio of this stock is right now 0.27, anything less than one is considered to be undervalued.",
    ],
    username: "Rahul Jain",
  },
  thesis: {
    thesis_theoretical: [
      {
        Thesis0:
          "The influencer suggests that the company's strong fundamentals and high growth rate are the key reasons for its impressive returns.",
      },
      {
        Thesis1:
          "The influencer also suggests that despite the significant increase in the stock's price, it still has potential for further growth due to its relatively low PE ratio and PEG ratio.",
      },
      {
        Thesis2:
          "The influencer also suggests that the company could potentially transition from a small cap to a mid or large cap stock.",
      },
    ],
    thesis_quantitative: [
      {
        Thesis0:
          "In the last five years, the stock has given close to 2200% returns.",
      },
      {
        Thesis1:
          "In the last few years, the company's revenues have been growing at a rate of 26-30%, with margins and earnings per share also growing significantly.",
      },
      {
        Thesis2:
          "The stock's price has increased from 55 Rupees to roughly 700 rupees.",
      },
      {
        Thesis3:
          "The stock's PE ratio is currently 19, compared to Nifty Pharma PE which is roughly at 31.",
      },
      {
        Thesis4: "The PEG ratio of the stock is currently 0.27.",
      },
    ],
    username: "Rahul Jain",
  },
};

let isTranscribedDataLoaded = false;

const analyze = (currentTabUrl) => {
  const analyzeButton = document.getElementById("analyze-button");
  analyzeButton.innerHTML =
    '<p>Skeptick agent at work ...</p><p class="analyze-subtitle">Fetching video transcript ...</p>';

  const step1Time = 1000 + Math.random() * 1000;
  // After 1 second
  setTimeout(function () {
    analyzeButton.innerHTML =
      '<p>Skeptick agent at work ...</p><p  class="analyze-subtitle">Extracting claims made</p>';
  }, step1Time);

  const step2Time = step1Time + 1000 + Math.random() * 1000;
  setTimeout(function () {
    analyzeButton.innerHTML =
      '<p>Skeptick agent at work ...</p><p  class="analyze-subtitle">Extracting thesis made</p>';
  }, step2Time);

  const step3Time = step2Time + 1000 + Math.random() * 1000;
  setTimeout(function () {
    analyzeButton.innerHTML =
      '<p>Skeptick agent at work ...</p><p  class="analyze-subtitle">Preparing ..</p>';
  }, step3Time);

  // const step4Time = step3Time + 1000 + Math.random() * 1000;
  // setTimeout(function () {
  //   updateTranscribeDOM(data);
  //   getWholeTruth(); // this also updates the transcribe dom
  //   getStockTip(); // this also updates the transcribe dom
  // }, 0);

  fetch("http://127.0.0.1:8000/v1/transcribe/breakdown", {
    method: "POST",
    body: JSON.stringify({ video_url: currentTabUrl }),
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
      console.log("Transcribe found !");
      isTranscribedDataLoaded = true;
      updateTranscribeDOM(data);
      getWholeTruth(); // this also updates the transcribe dom
      getStockTip(); // this also updates the transcribe dom
    })
    .catch((error) => console.error("Error:", error));
};

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
      wholeTruth_thesis = Object.values(data);

      updateWholeTruthList(wholeTruth_thesis, "thesis", 0);
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
      document.getElementById("stock-tips").innerHTML = `
			<img src="${data[0]}"/>
			<p>${data[1]}</p>
			`;
    });
}

const updateTranscribeDOM = (data) => {
  document.getElementById("not-transcribed").style.display = "none";
  document.getElementById("transcribed").style.display = "block";

  theoretical_thesis = data.thesis.thesis_theoretical.map(
    (item) => Object.values(item)[0]
  );

  claims_made = data.claims;

  createAndInsertList(theoretical_thesis, "thesis");

  populateClaims(claims_made, "claims");
};

// Attach event listeners to buttons
document.addEventListener("DOMContentLoaded", function () {
  const claimsButton = document.getElementById("claims-button");
  const thesisButton = document.getElementById("thesis-button");
  const stockTipsButton = document.getElementById("stock-tips-button");

  claimsButton.addEventListener("click", function (evt) {
    console.log("event", evt);
    openCity(evt, "claims");
    document.getElementById("claims-button").classList.remove("nav-selected");
    document.getElementById("thesis-button").classList.remove("nav-selected");
    document
      .getElementById("stock-tips-button")
      .classList.remove("nav-selected");
    document.getElementById("claims-button").classList.add("nav-selected");
  });

  thesisButton.addEventListener("click", function (evt) {
    openCity(evt, "thesis");
    document.getElementById("claims-button").classList.remove("nav-selected");
    document.getElementById("thesis-button").classList.remove("nav-selected");
    document
      .getElementById("stock-tips-button")
      .classList.remove("nav-selected");
    document.getElementById("thesis-button").classList.add("nav-selected");
  });

  stockTipsButton.addEventListener("click", function (evt) {
    openCity(evt, "stock-tips");
    document.getElementById("claims-button").classList.remove("nav-selected");
    document.getElementById("thesis-button").classList.remove("nav-selected");
    document
      .getElementById("stock-tips-button")
      .classList.remove("nav-selected");
    document.getElementById("stock-tips-button").classList.add("nav-selected");
  });
});

function openCity(evt, cityName) {
  console.log("event is", evt);
  console.log("city name is", cityName);
  var i;
  var x = document.getElementsByClassName("tab");
  for (i = 0; i < x.length; i++) {
    x[i].style.display = "none";
  }
  // tablinks = document.getElementsByClassName("tablink");
  // for (i = 0; i < x.length; i++) {
  //   tablinks[i].target.className = tablinks[i].target.className.replace(
  //     "nav-selected",
  //     ""
  //   );
  // }

  document.getElementById(cityName).style.display = "block";

  // console.log("eventis", evt);
  // evt.target.className += " nav-selected";
}

// Function to create a list and insert it into the 'thesis' div
function createAndInsertList(textList, containerId) {
  const listDiv = document.getElementById(containerId);
  // Create an unordered list element
  const ul = document.createElement("ul");

  // Loop through the textList and create list items (li) for each text
  textList.forEach((text) => {
    const li = document.createElement("li");
    // li.textContent = text;
    li.innerHTML = `<p>${text}</p><p  class="wholetruth"><i>Fetching 'wholetruth' behind claim ...</></p>`;
    ul.appendChild(li); // Append the list item to the unordered list
  });

  // Append the unordered list to the 'thesis' div
  listDiv.appendChild(ul);
}

function updateWholeTruthList(textList, containerId, current) {
  const listDiv = document.getElementById(containerId);
  listDiv.innerHTML = "";
  // Create an unordered list element
  const ul = document.createElement("ul");

  // Loop through the textList and create list items (li) for each text
  textList.forEach((text, index) => {
    const li = document.createElement("li");
    // li.textContent = text;
    li.innerHTML = `<p>${text[0]}</p><p class="wholetruth">${
      index <= current
        ? text[1]
        : "<i>Fetching 'wholetruth' behind claim ...</i>"
    }</p>`;
    ul.appendChild(li); // Append the list item to the unordered list
  });

  // Append the unordered list to the 'thesis' div
  listDiv.appendChild(ul);

  if (current < textList.length - 1) {
    setTimeout(() => {
      updateWholeTruthList(textList, containerId, current + 1);
    }, 1000 + Math.random() * 1000);
  }
}

// Function to convert JSON to HTML and insert it into an element with a specified ID
function populateClaims(jsonData, containerId) {
  const container = document.getElementById(containerId);

  for (const key in jsonData) {
    if (jsonData.hasOwnProperty(key) && key != "username") {
      const values = jsonData[key];
      const heading = document.createElement("h3");
      // heading.textContent = key;
      heading.innerText = `On ${key} stock`;
      container.appendChild(heading);

      const ul = document.createElement("ul");
      values.forEach((value) => {
        const li = document.createElement("li");
        li.textContent = value;
        ul.appendChild(li);
      });
      container.appendChild(ul);
    }
  }
}
