chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {  
    console.log(request)
    const username = request.username;  
    const amount = request.amount; 
  
    fetch('https://8000-shree970-skeptick-201scrltfd6.ws-us104.gitpod.io/invest', {  
        method: 'POST',  
        body: JSON.stringify({username: username, amount: amount}),  
        headers: {  
            'Content-type': 'application/json'  
        }  
    })  
    .then(response => response.json())  
    .then(data => console.log(data))  
    .catch(error => console.error('Error:', error));  
});

