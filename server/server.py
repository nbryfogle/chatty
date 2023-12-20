from quart import Quart, request
import socketio
import bcrypt
from database import Database, User
import asyncio
from uuid import uuid4
import hypercorn.asyncio as hasync
import hypercorn.config as hconfig

sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='asgi')
app = Quart(__name__, instance_relative_config=True)

# wrap with an ASGI application
db = asyncio.run(Database.connect('server/database/database.db'))
sio_app = socketio.ASGIApp(sio, app)
hypercorn_config = hconfig.Config.from_mapping(bind=["localhost:5000"], debug=True)

@app.route("/api/signup", methods=["POST"])
async def signup():
    """
    Data example:
    {
        "username": "test",
        "password": "test",
        "email": "test@test.test",
        "display_name": "test"
    }
    """
    data = await request.get_json()
    required_keys = ['username', 'password', 'email', 'dob']

    # Make sure all of the necessary information is supplied by the client
    if not data or not all(key in data for key in required_keys):
        return {"status": "error", "message": "Invalid data"}, 401
    
    # If there is no display name, set it to the username
    if not data.get('displayname'):
        data['displayname'] = data['username']

    # Use bcrypt to hash the password, so it is not stored in plaintext
    salt = bcrypt.gensalt()
    password = bcrypt.hashpw(bytes(data['password'], encoding='utf-8'), salt)

    # Insert the user into the database
    status = await db.create_user(
        {
            "username": data['username'],
            "password": password,
            "password_salt": salt,
            "email": data['email'],
            "displayname": data['displayname'],
            "dob": data['dob']
        }
    )

    return status

@app.route("/api/login", methods=["POST"])
async def login():
    """
    This request allows a user to get a session token using their username and 
    password combination. This session token will allow the user to connect to 
    the socketIO server.
    """
    data = await request.get_json()

    if not data or not data['username'] or not data['password']:
        return {"status": "error", "message": "Invalid data"}, 401

    # Check if the data is valid, if the user exists and whether the password matches after hashing
    # If the user exists and the password matches, return a token 
    await db.c.execute('''
        SELECT * FROM users WHERE username = ?
    ''', (data['username'],))
    user = await db.c.fetchone()

    print(user)

    if user is None:
        return {"status": "error", "message": "User does not exist"}, 401
    
    if bcrypt.checkpw(bytes(data['password'], encoding='utf-8'), user[2]):
        if user[6] is None:
            session = str(uuid4())
            await db.c.execute('''
                UPDATE users SET session = ? WHERE username = ?
            ''', (session, data['username']))
            await db.conn.commit()
            return {"status": "success", "session": session}, 200
        
    return {"status": "error", "message": "Incorrect password"}, 401

@app.route("/api/user/<username>", methods=["GET"])
async def get_user(username):
    user = await db.get_user(username)

    if user is None:
        return {"status": "error", "message": "User does not exist"}, 401
    
    return {"status": "success", "user": user.to_dict()}, 200

@sio.event
async def connect(sid: str, data: dict, auth: dict):
    """
    When a user connects, their session token will be checked. If the 
    token is valid, it will allow them to connect.
    """
    print("attempting to connect...")
    print(auth)
    username = await db.authenticate_user(auth['session'])
    
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

    if not data:
        return

    await sio.emit('message', data)

if __name__ == "__main__": 
    try:
        asyncio.run(hasync.serve(sio_app, hypercorn_config))
    except Exception as error:
        raise error
    finally:
        asyncio.run(db.conn.close())