const BASE_URL = window.location.origin.replace("3000", "5000") + "/";

document.addEventListener("keypress", onEvent);

function login() {
    fetch(BASE_URL + "api/login", {
        method: "POST",
        body: JSON.stringify({
            username: document.getElementById("username").value,
            password: document.getElementById("password").value,
        }),
        headers: {
            "Content-Type": "application/json",
        },
    }).then(async (response) =>{
        let data = await response.json();

        console.log(data);
<<<<<<< HEAD
        if (response.status === 200) {
            window.location.replace("/app");
        } else {
            alert("Error logging in: " + data.message);
        }
=======
        window.location.replace("/app");
>>>>>>> refs/remotes/origin/auth
    }).catch((error) => {
        console.error("Error:", error);
        alert("Error logging in: " + error);
    });
}

function onEvent(event) {
    if(event.keyCode=== 13) {
        login();
    }
}