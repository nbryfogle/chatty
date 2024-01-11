// Development code to change the codespace URL from port 3000 to 5000
// The website is hosted on 3000, but the socket.io server is hosted on 5000
const BASE_URL = window.location.origin.replace("3000", "5000") + "/"; 

document.addEventListener("keypress", onEvent); // Submit a message when the enter key is pressed
  
function getCookie(cname) {
    // Return the value of a cookie based on its name. Thanks, w3schools!
    let name = cname + "=";
    let ca = document.cookie.split(';');

    for(let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }

    return "";
}

function logout() {
    // Remove the token from the cookies and redirect to the login page
    document.cookie = "token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    window.location.replace("/app/login");
}

// No token? No connection.
if (!getCookie("token")) {
    logout();
    console.log("No token found");
}

// Connect to the SocketIO server
const socket = io(BASE_URL, {
    reconnectionDelayMax: 10000,
    auth: getCookie("token"),
});

// Once we are connected, just print that status to the terminal for now.
socket.on("connect", () => {
    console.log("connect");
});

// Load the previous messages from the server so the chat doesn't seem so empty.
socket.on("previous_messages", (data) => {
    console.log("Received previous messages from server");
    console.log(data);
    data = data["messages"];
    // Define a counter starting at zero and incrementing every iteration. Keep going until i is 
    // equal to the length of the data array.
    for (let i = 0; i < data.length; i++) {
        $("#messages").append(`<li>${data[i].author} at ${data[i].timestamp.split(" ")[1]}: ${data[i].message}</li>`);
    } 
    $("html, body").animate({ scrollTop: document.body.scrollHeight }, "slow");
});

// Handle what happens when a new message is received from the server.
socket.on("message", (data) => {
    console.log("Received message from server");
    console.log(data);

    // If the type of message is a command, don't print the timestamp.
    // Otherwise, print the timestamp.
    if (data.type === "command") {
        $("#messages").append(`<li>${data.message}</li>`);
    } else {
        $("#messages").append(`<li>${data.author.displayname || data.author} at ${data.timestamp}: ${data.message}</li>`);
    }
    $("html, body").animate({ scrollTop: document.body.scrollHeight }, "slow");
});

function sendMessage() {
    socket.emit("message", $("#message").val());
    document.getElementById("message").value = "";
}

function onEvent(event) {
    if(event.keyCode=== 13) {
        sendMessage();
    }
}

