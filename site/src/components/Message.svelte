<script lang="ts">
    export let isUser: Boolean;
    export let username: string;
    export let message: string;
</script>

<div class="message">
    <p>
        {#if isUser}
            <span class="user">{username}: </span>
        {:else}
            <span class="other">{username}: </span>
        {/if}
        {@html message}
    </p>
</div>

<style>
    .user {
        color: blue;
    }

    .other {
        color: red;
    }
</style>