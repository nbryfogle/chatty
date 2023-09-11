from aiohttp import web
import socketio
import bcrypt
from database import Database
import asyncio
from uuid import uuid4

sio = socketio.AsyncServer(cors_allowed_origins='*')
app = web.Application()
# wrap with a WSGI application
sio.attach(app)
db = asyncio.run(Database.connect('server/database/database.db'))

routes = web.RouteTableDef()

@routes.post('/api/signup')
async def signup(request):
    data = await request.json()
    """
    Data example:
    {
        "username": "test",
        "password": "test",
        "email": "test@test.test",
        "display_name": "test"
    }
    """
    salt=bcrypt.gensalt()
    password = bcrypt.hashpw(bytes(data['password'], encoding='utf-8'), salt)
    print(data["dob"])
    await db.c.execute('''
        INSERT INTO users (email, username, password, password_salt, displayname, dob)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (data['email'], data['username'], password, salt, data['displayname'], data['dob']))
    await db.conn.commit()
    return web.Response(status=200)

@routes.post('/api/login')
async def login(request):
    data = await request.json()
    # Check if the data is valid, if the user exists and whether the password matches after hashing
    # If the user exists and the password matches, return a token 
    await db.c.execute('''
        SELECT * FROM users WHERE username = ?
    ''', (data['username'],))
    user = await db.c.fetchone()
    print(user)

    if user is None:
        return web.Response(status=404)
    
    if bcrypt.checkpw(bytes(data['password'], encoding='utf-8'), user[2]):
        if user[6] is None:
            session = str(uuid4())
            await db.c.execute('''
                UPDATE users SET session = ? WHERE username = ?
            ''', (session, data['username']))
            await db.conn.commit()
            return web.Response(status=200, body=session)
        
    return web.Response(status=401)

async def authenticate_user(token):
    await db.c.execute('''
        SELECT * FROM users WHERE session = ?
    ''', (token,))
    user = await db.c.fetchone()
    if user is None:
        return False
    return user[0]

@sio.event
async def connect(sid: str, data: dict):
    username = await authenticate_user(data['token'])
    
    if username is False:
        await sio.disconnect(sid)
        return
    
    await sio.save_session(sid, {'username': username})

    print('connect ', sid)

@sio.event
async def message(sid, data):
    session = await sio.get_session(sid)
    print('message from ', session['username'])
    print(data)
    await sio.emit('message', data)

app.add_routes([web.post('/api/signup', signup), web.post('/api/login', login)])

if __name__ == "__main__": 
    try:
        web.run_app(app, host="127.0.0.1")
    except Exception as error:
        raise error
    finally:
        asyncio.run(db.conn.close())