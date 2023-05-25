
function signUp() {
    // Send a POST request to /api/signup
    fetch("http://127.0.0.1:8080/api/signup", {
        method: "POST",
        mode: "no-cors",
        // Get the values from the form
        body: JSON.stringify({
            email: document.getElementById("email").value,
            password: document.getElementById("password").value,
            username: document.getElementById("username").value,
            displayname: document.getElementById("displayname").value,
            dob: document.getElementById("dob").value,
        }),
        headers: {
            "Content-Type": "application/json",
        }

    }).then(function (data) {
        // If successful, redirect the browser to the profile page
        window.location.replace("/login");
        // If there's an error, log the error
    }
    ).catch(function (err) {
        console.log(err);
        alert("Something went wrong :(")
    }
    );
}