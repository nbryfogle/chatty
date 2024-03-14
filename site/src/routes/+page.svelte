<script>
    import { goto } from '$app/navigation';
    import Cookie from 'js-cookie';
    import { onMount } from 'svelte';

    onMount(() => {
        let cookie = Cookie.get('token');

        console.log('cookie', cookie); 

        if (cookie) {
            goto('/app');
        } else {
            goto('/login');
        }
    });
</script>
