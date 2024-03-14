<script lang="ts">
    import { io } from "socket.io-client";
    import type { message } from "$lib";
    import Cookie from "js-cookie";
    import TestB from "../components/TestB.svelte";

    const socket = io("http://127.0.0.1:5000", {
        auth: {
            token: Cookie.get("token"),
        },
    });

    let messages: message[] = [];

    function handleClick(){
        alert('clicked')
    }
    
    socket.on("connect", () => {
        console.log("Connected to server");
    });

    socket.on("message", (data: message) => {
        console.log("Message from server", data);
        messages = [...messages, data];
        console.log(messages);
    });

    let messageContent: string;

    function sendMessage() {
        console.log("Sending message...");
        socket.emit("message", messageContent);
        messageContent = "";
    }
</script>


<h1>Retro Rendezvous!</h1>
<h6><span>&copy;</span> Copyright, Norwegian Ball Waffles</h6>
    
<div class="message">
    {#each messages as message (message.id)}
        {#if typeof message.author === "string"}
            <p>{message.author}: {message.message}</p>
        {:else}
            <p>{message.author.displayname || message.author.username}: {message.message}</p>
        {/if}
    {/each}
</div>

<input type="text" placeholder="Message" bind:value={messageContent} />
<button on:click={sendMessage}>Send</button>


<TestB on:click={handleClick} />
