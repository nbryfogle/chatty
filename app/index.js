// Development code to change the codespace URL from port 3000 to 5000
// The website is hosted on 3000, but the socket.io server is hosted on 5000
const BASE_URL = window.location.origin.replace("3000", "5000") + "/"; 

document.addEventListener("keypress", onEvent); // Submit a message when the enter key is pressed

// Connect to the SocketIO server
const socket = io(BASE_URL, {
    reconnectionDelayMax: 10000,
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
    if (["command", "user_connect", "user_disconnect"].includes(data.type)) {
        $("#messages").append(`<li>${data.message}</li>`);
    } else {
        $("#messages").append(`<li>${data.author.displayname || data.username} at ${data.timestamp}: ${data.message}</li>`);
    }
    $("html, body").animate({ scrollTop: document.body.scrollHeight }, "slow");
});

function sendMessage() {
    let message = $("#message").val();
    if (message.startsWith("/")) {
        message = message.replace("/", "");
        if (message==="logout") {
            logout();
        }
        else if (message==="clear") {
            $("#messages").empty();
            $("html, body").animate({ scrollTop: 0 }, "slow");
        }
        else if (message.startsWith("color")) {
            let color = message.split(" ")[1];
            $("#messages").append(`<li style="color: ${color}">Changed color to ${color}</li>`);
            $("html, body").animate({ scrollTop: document.body.scrollHeight }, "slow");
        }
        else if (message==="help") {
            $("#messages").append(`<li>Commands:</br> 
            logout - /logout - logs the user out (alternative to button)</br>
            clear - /clear - empties the on-screen messages</br> 
            color - /color #color_hex - changes the color of the user's name with hex</br>
            help - /help - shows the user a list of commands</li>`);
            $("html, body").animate({ scrollTop: document.body.scrollHeight }, "slow");
        }
        else {
            $("#messages").append(`<li>Invalid command. Type /help for a list of client-side commands or ~help for a list of server-wide commands.</li>`);
        }
        
    }
    else {
        socket.emit("message", message);
    }
    document.getElementById("message").value = "";
}

function onEvent(event) {
    if(event.keyCode=== 13) {
        sendMessage();
    }
}

