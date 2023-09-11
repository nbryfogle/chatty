const socket = io("http://127.0.0.1:8080/", {
    reconnectionDelayMax: 10000,
    query: {
        "session": "44492fa2-4826-433c-9900-3ef88b714ac7"
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

function onKeyDown(event) {
    console.log("event.keyCode", event.keyCode);
    if (event.keyCode == 13) {
        sendMessage();
    }
}