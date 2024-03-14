<script lang="ts">
    import { redirect } from "@sveltejs/kit";

    let email: string;
    let username: string;
    let displayname: string;
    let dob: string;
    let password: string;

    async function signUp() {
        console.log("Signing up...");

        let res = await fetch("http://127.0.0.1:5000/api/signup", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                email,
                username,
                displayname,
                dob,
                password,
            }),
        });

        if (!res.ok) {
            console.log("Failed to sign up!");
            alert("Failed to sign up!");
            return;
        }

        let data = await res.json();
        console.log(data);
        redirect(302, "/login");
    }

</script>

<h1>Sign up</h1>
<input type="email" placeholder="Email" bind:value={email}/>
<input type="text" placeholder="Username" bind:value={username}/>
<input type="text" placeholder="Display name" bind:value={displayname}/>
<input type="date" placeholder="Date of birth" bind:value={dob}/>
<input type="password" placeholder="Password" bind:value={password}/>
<input type="button" value="Sign up" on:click={signUp}/>


