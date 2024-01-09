const BASE_URL = window.location.origin.replace("3000", "5000") + "/";

document.addEventListener("keypress", onEvent);
  
function getCookie(cname) {
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
    document.cookie = "token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    window.location.replace("/app/login");
}

if (!getCookie("token")) {
    logout();
    console.log("No token found");
}

const socket = io(BASE_URL, {
    reconnectionDelayMax: 10000,
    auth: getCookie("token"),
});

socket.on("connect", () => {
    console.log("connect");
});

socket.on("previous_messages", (data) => {
    console.log("Received previous messages from server");
    console.log(data);
    data = data["messages"];
    for (let i = 0; i < data.length; i++) {
        $("#messages").append(`<li>${data[i].author} at ${data[i].timestamp.split(" ")[1]}: ${data[i].message}</li>`);
    } // end
});

socket.on("message", (data) => {
    console.log("Received message from server");
    console.log(data);

    if (data.type === "command") {
        $("#messages").append(`<li>${data.author} ${data.message}</li>`);
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

