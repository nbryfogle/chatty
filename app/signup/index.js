const BASE_URL = window.location.origin.replace("3000", "5000") + "/";

document.addEventListener("keypress", onEvent);

if (document.cookie.includes("token") && document.cookie.split("token=")[1].split(";")[0] !== "") {
    window.location.replace("/app");
}


function signUp() {
    // Send a POST request to /api/signup

    // Validate the email address to make sure it could possibly be a valid one.
    if ($("#email").val().includes("@") === false || $("#email").val().includes(".") === false) {
        alert("Invalid email");
        return;
    }

    let body = {
        email: $("#email").val(),
        password: $("#password").val(),
        username: $("#username").val(),
        displayname: $("#displayname").val(),
        dob: $("#dob").val(),
    };

    console.log(body);
    fetch(BASE_URL + "/api/signup", {
        method: "POST",
        // Get the values from the form
        body: JSON.stringify(body),
        headers: {
            "Content-Type": "application/json",
        }

    }).then(async function (response) {
        // If successful, redirect the browser to the profile page
        console.log(response);
        let data = await response.json();
        console.log(data);

        if (response.status === 200) {
            // document.cookie = `token=${data.session}; path=/;`;
        } else {
            alert("Error logging in: " + data.message);
            return;
        }

        window.location.replace("../login");
        // If there's an error, log the error
    }
    ).catch(function (err) {
        console.log(err);
        alert("Something went wrong.")
    }
    );
}

function onEvent(event) {
    if(event.keyCode=== 13) {
        signUp();
    }
}