"""
The main server file. This file controls all of the socketIO events and
the HTTP requests.
"""

import asyncio

import hypercorn.asyncio as hasync
import hypercorn.config as hconfig
import socketio
from commands import command_register
from database import User, db, Message, MessageResponse
from enums import MessageType, Permissions
from objects import Application, Context
from config import COMMAND_PREFIX, REQUIRED_USER_FIELDS
from quart import Quart, request, jsonify
from quart_cors import cors
from quart_jwt_extended import (
    JWTManager,
    create_access_token,
    decode_token,
    jwt_required,
)
from dotenv import load_dotenv
import os

load_dotenv()

# Define the socketIO server and the Quart app
# SocketIO controls the chat functionality, while Quart
# handles HTTP requests for using the API.
sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")
app = Quart(__name__, instance_relative_config=True)
app = cors(app, allow_origin="*")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET")

# Connect to the database and connect an ASGI app to the socketIO server
# in this case, Hypercorn is used as the ASGI server.
sio_app = socketio.ASGIApp(sio, app)
hypercorn_config = hconfig.Config.from_mapping(bind=["localhost:5000"], debug=True)
server = Application(db, sio, command_register)
jwt = JWTManager(app)


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

    # Make sure all of the necessary information is supplied by the client
    if not data or not all(key in data and data[key] for key in REQUIRED_USER_FIELDS):
        return {"status": "error", "message": "Invalid data"}, 400

    # Check if the email is valid, poorly. Maybe regex would be helpful here?
    if data["email"].find("@") == -1 or data["email"].find(".") == -1:
        return {"status": "error", "message": "Invalid email"}, 400

    # If there is no display name, set it to the username
    if not data.get("displayname"):
        data["displayname"] = data["username"]

    # Create a user object and insert it into the database
    user = await User(
        username=data["username"],
        email=data["email"],
        displayname=data["displayname"],
        dob=data["dob"],
    ).create(data["password"])

    return {"status": "success", "user": user.as_sendable()}, 200


@app.route("/api/login", methods=["POST"])
async def login() -> tuple[dict[str, str], int]:
    """
    This request allows a user to get a session token using their username and
    password combination. This session token will allow the user to connect to
    the socketIO server.
    """
    # Get the data from the request
    if not request.is_json:
        return {"status": "error", "message": "Invalid data"}, 401

    data = await request.get_json()

    # If the data does not contain a username or password, we cannot log the user in.
    # This rejects the request.
    if not data or not data["username"] or not data["password"]:
        return {"status": "error", "message": "Invalid data"}, 401

    # Check if the data is valid, if the user exists and whether the password matches after hashing
    # If the user exists and the password matches, return a token
    user = await User.get(data["username"])

    # If the user is None, that means it does not exist.
    if user is None:
        return {"status": "error", "message": "User does not exist"}, 401

    # The check_password function will return True if the password matches,
    # and False if it does not.
    if await user.check_password(data["password"]):
        access_token = create_access_token(identity=user.username, expires_delta=False)

        return jsonify(body={"status": "success"}, access_token=access_token), 200

    # If that does not work, it means the password is incorrect.
    return {"status": "error", "message": "Incorrect password"}, 401


@app.route("/api/user/<username>", methods=["GET"])
async def get_user(username) -> tuple[dict[str, str | dict], int]:
    """
    Returns information about a user from the database.
    """
    user = await User.get(username)  # Get the user from the database

    # If the user does not exist, return an error
    if user is None:
        return {"status": "error", "message": "User does not exist"}, 401

    return {"status": "success", "user": user.as_sendable()}, 200


@app.route("/api/validate", methods=["POST"])
async def validate_token():
    """
    Validate a JWT token from the Auth header
    """
    token = request.headers.get("Authorization").removeprefix("Bearer ").strip()

    if not token:
        return {"status": "error", "message": "No token provided"}, 401

    try:
        decode_token(token)
    except Exception:
        return {"status": "error", "message": "Invalid token"}, 401

    return {"status": "success", "message": "Token is valid"}, 200


@app.route("/api/messages", methods=["GET"])
@jwt_required
async def get_messages():
    """
    Get all messages from the database
    """
    raw_messages = await db.get_messages()
    messages = []

    for message in raw_messages:
        messages.append(
            Message(
                message["message"],
                message["author"],
                message["id"],
                message["channel"],
                message["timestamp"],
                MessageType.NORMAL,
            ).as_sendable()
        )

    return {"status": "success", "messages": messages}, 200


@sio.event
async def connect(sid: str, data: dict, auth: str):
    """
    When a user connects, their session token will be checked. If the
    token is valid, it will allow them to connect.
    """
    print("attempting to connect...")
    print(auth)

    # Do something useless with the data variable to get the linter
    # to stop complaining.
    print(data)

    # If the auth variable is not a string, disconnect the user.
    # This means the user did not provide a session token.
    if not isinstance(auth, dict):
        await sio.disconnect(sid)
        return

    async with app.app_context():
        decoded_token = decode_token(auth["token"])

    if not decoded_token:
        await sio.disconnect(sid)
        return

    username = decoded_token.get("identity")
    # Check if the session token is valid

    # If the username is None, that means the session token is invalid.
    if username is None:
        await sio.disconnect(sid)
        return

    user = await User.get(username, sid)

    # If the user does not exist, or the user does not have permission to connect,
    # disconnect them.
    if user is None or user.permissions.value == 0:
        await sio.disconnect(sid)
        return

    # raw_messages: list[dict] = await db.get_messages()  # Get recent messages from the database

    # messages = []

    # for message in raw_messages:
    #     messages.append(
    #         Message(
    #             message["message"],
    #             message["author"],
    #             message["id"],
    #             message["channel"],
    #             message["timestamp"],
    #             MessageType.NORMAL,
    #         ).as_sendable()
    #     )

    # Save the session token to the socketIO session
    await sio.save_session(sid, {"username": user.username})
    # Send the messages to the user
    # await sio.emit("previous_messages", messages, to=sid)
    # Send the message through the chat
    await server.send_message(
        MessageResponse(
            "Server",
            context_from=Context(server, Message("User connected", author="Server")),
            message=Message(
                f"Welcome to the chat, {user.display_name}!",
                author="Server",
                type=MessageType.USER_CONNECT,
            ),
        )
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
    await server.send_message(
        MessageResponse(
            "Server",
            context_from=Context(server, Message("User disconnected", author="Server")),
            message=Message(
                f"{session['username']} has disconnected",
                author="Server",
                type=MessageType.USER_DISCONNECT,
            ),
        )
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
    context = await Context.from_message(
        server,
        Message(
            content=data,
            author=await User.get(session["username"], sid),
        ),
    )

    # If the user does not exist, do nothing.
    if context.author is None:
        return

    # If the user does not have permission to send messages, reject the message.
    if not context.author.permissions & Permissions.SEND:
        await server.send_message(
            MessageResponse(
                context.author,
                context,
                message=Message(
                    "You do not have permission to send messages.",
                    author="Server",
                    type=MessageType.ERROR,
                ),
                is_ephemeral=True,
            )
        )
        return

    # Enforce the character limit of 1000 characters.
    if len(context.message.content) > 1000:
        await server.send_message(
            MessageResponse(
                context.author,
                context,
                Message(
                    "Your message was too long. Please keep your messages under 1000 characters.",
                    author="Server",
                    type=MessageType.ERROR,
                ),
                is_ephemeral=True,
            )
        )
        return

    # If the message starts with a colon, it is a command.
    if context.message.content.startswith(COMMAND_PREFIX):
        if not context.author.permissions & Permissions.COMMANDS:
            # Reject the command if the user does not have permission to send commands.
            await server.send_message(
                MessageResponse(
                    context.author,
                    context,
                    message=Message(
                        "You do not have permission to psend commands.",
                        author="Server",
                        type=MessageType.ERROR,
                    ),
                    is_ephemeral=True,
                )
            )
            return

        command_message = await server.process_command(context)  # Process the command

        # If the command message returned None, it means the command failed for
        # some reason. Inform the user.
        if command_message is None:
            await server.send_message(
                MessageResponse(
                    context.author,
                    context,
                    message=Message(
                        "Command failed.",
                        author="Server",
                        type=MessageType.ERROR,
                    ),
                    is_ephemeral=True,
                )
            )

        else:
            # Finally, send the command message to the user.
            await server.send_message(command_message)

        return

    # Finally, save the message to the database and send it to everyone.
    await server.user_message(context)


if __name__ == "__main__":
    try:
        asyncio.run(hasync.serve(sio_app, hypercorn_config))
    except Exception as error:
        raise error
    finally:
        asyncio.run(db.conn.close())
