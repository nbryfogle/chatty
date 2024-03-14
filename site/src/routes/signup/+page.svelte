<script lang="ts">
    import { goto } from "$app/navigation";
    import Cookie from "js-cookie";
    import { onMount } from 'svelte';

    let cookie = Cookie.get('token');;

    onMount(async () => {
        let res = await fetch(`${import.meta.env.VITE_API}/api/validate`, {
            method: "POST",
            headers: {
                'Authorization': `Bearer ${cookie}`
            }
        });

        if (res.ok) {
            goto('/app');
        }
    });


    let email: string;
    let username: string;
    let displayname: string;
    let dob: string;
    let password: string;

    async function signUp() {
        console.log("Signing up...");

        let res = await fetch(`${import.meta.env.VITE_API}/api/signup`, {
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
        goto("/app");
    }

</script>

<h1>Sign up</h1>
<input type="email" placeholder="Email" bind:value={email}/>
<input type="text" placeholder="Username" bind:value={username}/>
<input type="text" placeholder="Display name" bind:value={displayname}/>
<input type="date" placeholder="Date of birth" bind:value={dob}/>
<input type="password" placeholder="Password" bind:value={password}/>
<input type="button" value="Sign up" on:click={signUp}/>
<p>Already have an account? <a href="/login">Login</a></p>



