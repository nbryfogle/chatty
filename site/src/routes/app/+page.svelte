<script lang="ts">
    import { io } from "socket.io-client";
    import type { message } from "$lib";
    import Cookie from "js-cookie";
    import TestB from "../../components/TestB.svelte";
    import { goto } from "$app/navigation";

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

    socket.on("disconnect", () => {
        console.log("Disconnected from server");
        goto('/login');
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

    function onKeyDown(e: { keyCode: any; }){
        switch(e.keyCode){
            case 13:
                sendMessage();
                break;
        }
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

<input type="text" bind:value={messageContent} on:keydown={onKeyDown} id="messageBox" placeholder="Enter a message..."/> 
<TestB on:click={sendMessage} />

<style>
    h1{
        font-family: Verdana, Geneva, Tahoma, sans-serif;
        text-align:center;
    }

    h6{
        font-family: Verdana, Geneva, Tahoma, sans-serif;
        text-align: left;
        margin-left: 1rem;
    }

    .message{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: left;
        margin-top: 32rem;
        margin-bottom: 2rem;
        font-family: Verdana, Geneva, Tahoma, sans-serif;
    }

    /* p{
        font-size: 1.5rem;
        margin: 0.5rem;
    } */

    #messageBox{
        font-size: 1.5rem;
        margin-top: 2rem;
        margin-left: 1rem;
        width: 50%;
        height: 4rem;
        border-radius: 15px;
    }
</style>
