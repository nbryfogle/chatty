<script lang="ts">
    import { io } from "socket.io-client";
    import type { message } from "$lib";
    import Cookie from "js-cookie";
    import SendButton from "../../components/SendButton.svelte";
    import Message from "../../components/Message.svelte";
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

<div class="body">
    <h1>Retro Rendezvous!</h1>
    <h6><span>&copy;</span> Copyright, Norwegian Ball Waffles</h6>
    
    <div class="content">
        <div class="message-box">
            {#each messages as message (message.id)}
                {#if typeof message.author === "string"}
                    <Message isUser={true} username={message.author} message={message.message} />
                {:else}
                    <Message isUser={false} username={message.author.username} message={message.message} />
                {/if}
            {/each}
        </div>
        
        <div class="input-area">
            <input type="text" bind:value={messageContent} on:keydown={onKeyDown} id="messageBox" placeholder="Enter a message..."/> 
            <SendButton on:click={sendMessage} />
        </div>
    </div>
</div>


<style>

    h1{
        font-family: Verdana, Geneva, Tahoma, sans-serif;
        text-align: center;
    }

    h6{
        font-family: Verdana, Geneva, Tahoma, sans-serif;
        text-align: left;
    }

    .message-box {
        justify-content: left;
        overflow-y: auto;
        border: 2px solid black;
        font-family: Verdana, Geneva, Tahoma, sans-serif;
        padding: 10px;
        flex-grow: 1;
    }

    .content {
        display: flex;
        flex-direction: column;
        justify-content: center;
        height: 80vh;
        margin: 20px;
    }

    #messageBox{
        font-size: 1.5rem;
        border-radius: 15px;
        flex: 2;
        margin-right: 10px;
    }

    .input-area {
        display: flex;
        margin-top: 10px;
        width: 100%;
    }
</style>
