const BASE_URL = "https://potential-space-broccoli-v4jq9v97wg7hpq4v-5000.app.github.dev/";

document.addEventListener("keypress", onEvent);

if (document.cookie.includes("token") && document.cookie.split("token=")[1].split(";")[0] !== "") {
    window.location.replace("/app");
}

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
        if (response.status === 200) {
            document.cookie = `token=${data.session}; path=/;`;
        } else {
            alert("Error logging in: " + data.message);
            return;
        }

        window.location.replace("/app");
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