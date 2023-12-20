document.addEventListener("keypress", onEvent);

const socket = io("http://127.0.0.1:5000/", {
    reconnectionDelayMax: 10000,
    auth: {
        "session": "66512422-8050-46a9-a36d-13325f2b4226"
    }
});

socket.on("connect", () => {
    console.log("connect");
});

socket.on("message", (data) => {
    console.log("Received message from server");
    console.log(data);
    document.getElementById("messages").innerHTML += `<li>${data}</li>`;
});

function sendMessage() {
    socket.emit("message", document.getElementById("message").value);
    document.getElementById("message").value = "";
}

function onEvent(event) {
    if(event.keyCode=== 13) {
        sendMessage();
    }
}

