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

    let username: string;
    let password: string;

    async function login() {
        console.log("Logging in...");

        let res = await fetch(`${import.meta.env.VITE_API}/api/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                username,
                password,
            }),
        });

        if (!res.ok) {
            console.log("Failed to log in!");
            return;
        } 
        let data = await res.json();
        Cookie.set("token", data.access_token, { path: "/" });
        goto("/app");
    }
</script>

<h1>Login</h1>
<input type="text" placeholder="Username" bind:value={username} />
<input type="password" placeholder="Password" bind:value={password}>
<button on:click={login}>Login</button>
<p>Don't have an account? <a href="/signup">Sign up</a></p>
