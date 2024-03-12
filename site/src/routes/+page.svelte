<h1>Retro Rendezvous!</h1>

<head>
    <title>Chat | App</title>
</head>


<body>
    <h6><span>&copy;</span> Copyright, Norwegian Ball Waffles</h6>
</body>

<div class="message">
    {#each messages as message (message.id)}
        <p>{message.text}</p>
    {/each}
</div>

<h1>Welcome to SvelteKit</h1>
<p>Visit <a href="https://kit.svelte.dev">kit.svelte.dev</a> to read the documentation</p>

<script>
    import { io } from "socket.io-client";

    const socket = io("https://x36dw3tq-5000.use.devtunnels.ms/");

    let messages = [];

    socket.on("connect", () => {
        console.log("Connected to server");
    });

    socket.on("message", (data) => {
        console.log("Message from server", data);
        messages = [...messages, data];
    });
</script>
