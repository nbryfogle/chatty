
<button on:click>Enter</button>

<style>
    @font-face{
        font-family: 'WhiteRabbit-47pD';
        src: url('/static/WhiteRabbit-47pD.tff') format('tff');

    }

    button {
        height: 4rem;
        width: 8rem;
        background-color: blueviolet;
        border-color: cornflowerblue;
        font-size: 2.25rem;
        background-position: 100%;
        border-radius: 10px;
        font-family: 'WhiteRabbit27pD' ;
        background-image: linear-gradient(45deg, cornflowerblue, transparent 50%);
        transition: 300ms ease-in-out ;
        color: azure;
        font-weight: bold;
    }

    button:hover {
        background-position: 0%;
        color: black;
        background-color: azure;
    }
</style>