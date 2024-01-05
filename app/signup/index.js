const BASE_URL = "127.0.0.1:5000/";

if (document.cookie.includes("token") && document.cookie.split("token=")[1].split(";")[0] !== "") {
    window.location.replace("/app");
}


function signUp() {
    // Send a POST request to /api/signup

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