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
from database import Database
from objects import Permissions, Application, Context, MessageType
from commands import command_register
from quart import Quart, request
from quart_cors import cors

# Define the socketIO server and the Quart app
# SocketIO controls the chat functionality, while Quart
# handles HTTP requests for using the API.
sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")
app = Quart(__name__, instance_relative_config=True)
app = cors(app, allow_origin="*")

# Connect to the database and connect an ASGI app to the socketIO server
# in this case, Hypercorn is used as the ASGI server.
db = asyncio.run(Database.connect("server/database/database.db"))
sio_app = socketio.ASGIApp(sio, app)
hypercorn_config = hconfig.Config.from_mapping(bind=["localhost:5000"], debug=True)
server = Application(db, sio, command_register)

@app.route("/api/signup", methods=["POST"])
async def signup() -> tuple[dict[str, str], int]:
    """
    This request allows a user to create an account. The user will be
    required to provide a username, password, email address, and date
    of birth. The password will be hashed using bcrypt, and the hashed
    password will be stored in the database.

    Data example:
    {
        "username": "test",
        "password": "test",
        "email": "test@test.test",
        "display_name": "test"
    }
    """
    # Get the data from the request
    data: dict[str, str] = await request.get_json()
    required_keys = ["username", "password", "email", "dob"] # Keys that are required to sign a user up

    # Make sure all of the necessary information is supplied by the client
    if not data or not all(key in data and data[key] for key in required_keys):
        return {"status": "error", "message": "Invalid data"}, 400

    # Check if the email is valid, poorly. Maybe regex would be helpful here?
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
    # Get the data from the request
    data = await request.get_json()

    # If the data does not contain a username or password, we cannot log the user in.
    # This rejects the request.
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

    # If the user is None, that means it does not exist. 
    if user is None:
        return {"status": "error", "message": "User does not exist"}, 401

    # The bcrypt checkpw function will return True if the password matches, and False if it does not.
    # The fact that this does not require the password salt makes me wonder if we are supposed
    # to store the salt in the database.
    if bcrypt.checkpw(bytes(data["password"], encoding="utf-8"), user["password"]):
        if user["session"] is None: # Create a new session token if the user does not have one
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
            # Return the existing session token if the user already has one
            return {"status": "success", "session": user["session"]}, 200

    # If that does not work, it means the password is incorrect.
    return {"status": "error", "message": "Incorrect password"}, 401


@app.route("/api/user/<username>", methods=["GET"])
async def get_user(username) -> tuple[dict[str, str | dict], int]:
    """
    Returns information about a user from the database.
    """
    user = await db.get_user(username) # Get the user from the database

    # If the user does not exist, return an error
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

    # If the auth variable is not a string, disconnect the user.
    # This means the user did not provide a session token.
    if not isinstance(auth, str):
        await sio.disconnect(sid)
        return

    username = await db.authenticate_user(auth) # Check if the session token is valid

    # If the username is None, that means the session token is invalid.
    if username is None:
        await sio.disconnect(sid)
        return

    user = await db.get_user(username)

    # If the user does not exist, or the user does not have permission to connect,
    # disconnect them.
    if user is None or user.permissions.value == 0:
        await sio.disconnect(sid)
        return

    messages = await db.get_messages() # Get recent messages from the database

    # Save the session token to the socketIO session
    await sio.save_session(sid, {"username": user.username})
    await sio.emit("previous_messages", {"messages": messages}, to=sid) # Send the messages to the user
    await sio.emit( # Send a welcome message!
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

    # if, for some reason, the session is None or the username is not set,
    # do nothing.
    if session is None or not session.get("username"):
        return

    # Send a message to all users that the user has disconnected.
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

    # if there is no message data, do nothing.
    if not data:
        return

    # Get the current time in hours, minutes, and seconds.
    # Perhaps the database should store the day the message was
    # send too, and it should be the client's decision what
    # to show.
    current_time = datetime.datetime.now().strftime("%H:%M:%S")

    # Enforce the character limit of 1000 characters.
    if len(data) > 1000:
        await server.send_message(
            await Context.with_message({
                "message": "Message exceeds limit of 1000 characters.",
                "author": "server",
                "channel": "general",
                "timestamp": current_time,
                "type": MessageType.ERROR,
            }, server), sid)
        return

    user = await db.get_user(session["username"])

    # If the user does not exist, do nothing.
    if user is None:
        return

    context = await Context.with_message({
        "message": data,
        "author": user,
        "channel": "general",
        "timestamp": current_time,
        "type": MessageType.NORMAL,
    }, server)

    # If the message starts with a colon, it is a command.
    if context.message.content.startswith(":"):
        if not user.permissions & Permissions.COMMANDS:
            # Reject the command if the user does not have permission to send commands.
            await server.send_message(await Context.with_message({
                "message": "You do not have permission to send commands.",
                "author": "server",
                "channel": "general",
                "timestamp": current_time,
                "type": MessageType.ERROR,
            }, server), sid)
            return
        
        command_message = await server.process_command(context) # Process the command

        # If the command message returned None, it means the command failed for
        # some reason. Inform the user.
        if command_message is None:
            await server.send_message(await Context.with_message({
                "message": "Command failed (invalid command or mention?).",
                "author": "Server",
                "channel": "general",
                "timestamp": current_time,
                "type": MessageType.ERROR,
            }, server), sid)

        else:
            # Finally, send the command message to the user.
            await server.send_message(await Context.from_message(server, command_message))
        return

    # If the user does not have permission to send messages, reject the message.
    if not user.permissions & Permissions.SEND:
        await server.send_message(await Context.with_message({
                "message": "You do not have permission to send messages.",
                "username": "Server",
                "time": current_time,
                "type": MessageType.ERROR,
            }, server), sid)
        return

    # Finally, save the message to the database and send it to everyone.
    await server.send_message(context)


if __name__ == "__main__":
    try:
        asyncio.run(hasync.serve(sio_app, hypercorn_config))
    except Exception as error:
        raise error
    finally:
        asyncio.run(db.conn.close())
