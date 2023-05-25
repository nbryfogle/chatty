from aiohttp import web
import socketio
import bcrypt
from database import Database
import asyncio

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
    return web.Response(body="OK")

@routes.get('/api/login')
async def login(request):
    data = await request.json()
    # Check if the data is valid, if the user exists and whether the password matches after hashing
    # If the user exists and the password matches, return a token
    return web.Response(body="OK")

@sio.event
async def connect(sid: str, data: dict):
    print('connect ', sid)

@sio.event
async def message(sid, data):
    print('message ', sid)
    print(data)
    await sio.emit('message', data)

app.add_routes([web.post('/api/signup', signup), web.get('/api/login', login)])

if __name__ == "__main__": 
    try:
        web.run_app(app, host="127.0.0.1")
    except Exception as error:
        raise error
    finally:
        asyncio.run(db.conn.close())