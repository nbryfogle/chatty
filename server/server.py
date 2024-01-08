"""
The main server file. This file controls all of the socketIO events and
the HTTP requests.
"""

import asyncio
import datetime
from uuid import uuid4

import bcrypt
import hypercorn.asyncio as hasync
import hypercorn.config as hconfig
import socketio
from commands import process_command
from database import Database
from objects import Permissions
from quart import Quart, request
from quart_cors import cors

sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")
app = Quart(__name__, instance_relative_config=True)
app = cors(app, allow_origin="*")

# wrap with an ASGI application
db = asyncio.run(Database.connect("server/database/database.db"))
sio_app = socketio.ASGIApp(sio, app)
hypercorn_config = hconfig.Config.from_mapping(bind=["localhost:5000"], debug=True)


@app.route("/api/signup", methods=["POST"])
async def signup() -> tuple[dict[str, str], int]:
    """
    Data example:
    {
        "username": "test",
        "password": "test",
        "email": "test@test.test",
        "display_name": "test"
    }
    """
    data: dict[str, str] = await request.get_json()
    required_keys = ["username", "password", "email", "dob"]

    # Make sure all of the necessary information is supplied by the client
    if not data or not all(key in data and data[key] for key in required_keys):
        return {"status": "error", "message": "Invalid data"}, 400

    if data["email"].find("@") == -1 or data["email"].find(".") == -1:
        return {"status": "error", "message": "Invalid email"}, 400

    # If there is no display name, set it to the username
    if not data.get("displayname"):
        data["displayname"] = data["username"]

    # Use bcrypt to hash the password, so it is not stored in plaintext
    salt = bcrypt.gensalt()
    password = bcrypt.hashpw(bytes(data["password"], encoding="utf-8"), salt)

    # Insert the user into the database
    status = await db.create_user(
        {
            "username": data["username"],
            "password": password,
            "password_salt": salt,
            "email": data["email"],
            "displayname": data["displayname"],
            "dob": data["dob"],
        }
    )

    return status


@app.route("/api/login", methods=["POST"])
async def login() -> tuple[dict[str, str], int]:
    """
    This request allows a user to get a session token using their username and
    password combination. This session token will allow the user to connect to
    the socketIO server.
    """
    data = await request.get_json()

    if not data or not data["username"] or not data["password"]:
        return {"status": "error", "message": "Invalid data"}, 401

    # Check if the data is valid, if the user exists and whether the password matches after hashing
    # If the user exists and the password matches, return a token
    await db.c.execute(
        """
        SELECT * FROM users WHERE username = ?
    """,
        (data["username"],),
    )
    user = await db.c.fetchone()

    print(user)

    if user is None:
        return {"status": "error", "message": "User does not exist"}, 401

    if bcrypt.checkpw(bytes(data["password"], encoding="utf-8"), user["password"]):
        if user["session"] is None:
            session = str(uuid4())
            await db.c.execute(
                """
                UPDATE users SET session = ? WHERE username = ?
            """,
                (session, data["username"]),
            )
            await db.conn.commit()
            return {"status": "success", "session": session}, 200
        else:
            return {"status": "success", "session": user["session"]}, 200

    return {"status": "error", "message": "Incorrect password"}, 401


@app.route("/api/user/<username>", methods=["GET"])
async def get_user(username) -> tuple[dict[str, str | dict], int]:
    """
    Returns information about a user from the database.
    """
    user = await db.get_user(username)

    if user is None:
        return {"status": "error", "message": "User does not exist"}, 401

    return {"status": "success", "user": user.to_dict()}, 200


@sio.event
async def connect(sid: str, data: dict, auth: str):
    """
    When a user connects, their session token will be checked. If the
    token is valid, it will allow them to connect.
    """
    print("attempting to connect...")
    print(auth)
    print(data)

    if not isinstance(auth, str):
        await sio.disconnect(sid)
        return

    username = await db.authenticate_user(auth)

    if username is None:
        await sio.disconnect(sid)
        return

    user = await db.get_user(username)

    if user is None or user.permissions.value == 0:
        await sio.disconnect(sid)
        return

    messages = await db.get_messages()

    await sio.save_session(sid, {"username": user.username})
    await sio.emit("previous_messages", {"messages": messages}, to=sid)
    await sio.emit(
        "message",
        {
            "message": f"{user.username} has connected as {user.displayname}",
            "username": "Server",
            "time": datetime.datetime.now().strftime("%H:%M:%S"),
            "type": "user_connect",
        },
    )

    print("connect ", sid)


@sio.event
async def disconnect(sid):
    """
    What happens when a user disconnects from the server.
    """
    session = await sio.get_session(sid)

    if session is None or not session.get("username"):
        return

    await sio.emit(
        "message",
        {
            "message": f'{session["username"]} has disconnected',
            "username": "Server",
            "time": datetime.datetime.now().strftime("%H:%M:%S"),
        },
    )


@sio.event
async def message(sid, data):
    """
    Control when a user sends a message.
    """
    session = await sio.get_session(sid)

    print("message from ", session)
    print(data)

    if not data:
        return

    if len(data) > 1000:
        await sio.emit(
            "message",
            {
                "message": "Message exceeds limit of 1000 characters.",
                "username": "Server",
                "time": datetime.datetime.now().strftime("%H:%M:%S"),
            },
            to=sid,
        )
        return

    user = await db.get_user(session["username"])

    if user is None:
        return

    current_time = datetime.datetime.now().strftime("%H:%M:%S")

    if data.startswith(":"):
        if not user.permissions & Permissions.COMMANDS:
            await sio.emit(
                "message",
                {
                    "message": "You do not have permission to send commands.",
                    "username": "Server",
                    "time": datetime.datetime.now().strftime("%H:%M:%S"),
                    "type": "error",
                },
                to=sid,
            )
            return
        command_message = await process_command(db, data, user)

        if command_message is None:
            await sio.emit(
                "message",
                {
                    "message": "Invalid command or mention.",
                    "username": "Server",
                    "time": current_time,
                    "type": "error",
                },
                to=sid,
            )

        else:
            await sio.emit(
                "message",
                {
                    "message": command_message,
                    "username": user.displayname,
                    "time": current_time,
                    "type": "command",
                },
            )
        return

    if not user.permissions & Permissions.SEND:
        await sio.emit(
            "message",
            {
                "message": "You do not have permission to send messages.",
                "username": "Server",
                "time": datetime.datetime.now().strftime("%H:%M:%S"),
                "type": "error",
            },
            to=sid,
        )
        return

    await db.capture_message(user.displayname, data)
    await sio.emit(
        "message",
        {
            "message": data,
            "username": user.displayname,
            "time": current_time,
            "type": "message",
        },
    )


if __name__ == "__main__":
    try:
        asyncio.run(hasync.serve(sio_app, hypercorn_config))
    except Exception as error:
        raise error
    finally:
        asyncio.run(db.conn.close())
