<script lang="ts">
    import { io } from "socket.io-client";
    import type { message } from "$lib";
    import Cookie from "js-cookie";
    import SendButton from "../../components/SendButton.svelte";
    import Message from "../../components/Message.svelte";
    import { goto } from "$app/navigation";
    import { onMount } from "svelte";

    const socket = io(import.meta.env.VITE_API, {
        auth: {
            token: Cookie.get("token"),
        },
    });

    let messages: message[] = [];
    
    onMount(async () => {
        const response = await fetch(`${import.meta.env.VITE_API}/api/messages`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${Cookie.get("token")}`,
            },
        });

        const data = await response.json();
        messages = data.messages;
    })

    /** @type {import('svelte/action').Action<HTMLElement, string>}  */
    function messageBoxHook(node: HTMLElement, messages: message[]) {
        return {
            update: (messages: message[]) => {
                node.scroll({
                    top: node.scrollHeight,
                    behavior: "smooth",
                });
            },
        }
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
        if (messageContent === "") {
            return;
        }

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
        <div class="message-box" use:messageBoxHook={messages}>
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
