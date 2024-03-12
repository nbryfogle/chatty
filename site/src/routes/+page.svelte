<script lang="ts">
    import { io } from "socket.io-client";
    import type { message } from "$lib";

    const socket = io("https://x36dw3tq-5000.use.devtunnels.ms/");

    let messages: message[] = [
        {
            message: "Welcome to Retro Rendezvous!",
            author: "Retro Rendezvous",
            timestamp: "now",
            type: 12,
            ephemeral: false,
        }
    ];

    socket.on("connect", () => {
        console.log("Connected to server");
    });

    socket.on("message", (data: message) => {
        console.log("Message from server", data);
        messages = [...messages, data];
    });
</script>


<h1>Retro Rendezvous!</h1>

<head>
    <title>Chat | App</title>
</head>


<body>
    <h6><span>&copy;</span> Copyright, Norwegian Ball Waffles</h6>
</body>

<div class="message">
    {#each messages as message (message.message)}
        <p>{message.message}</p>
    {/each}
</div>

<h1>Welcome to SvelteKit</h1>
<p>Visit <a href="https://kit.svelte.dev">kit.svelte.dev</a> to read the documentation</p>
