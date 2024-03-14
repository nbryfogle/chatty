import Cookie from 'js-cookie';
import { redirect } from '@sveltejs/kit';

export async function load() {
    let cookie = Cookie.get('token');
    
    console.log('cookie', cookie); 

    if (cookie) {
        return {
            status: 200,
            body: { token: cookie }
        }
    } else {
        return redirect(302, '/login');
    }
}