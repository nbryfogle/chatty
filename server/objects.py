"""
Objects.py holds a variety of objects that are used in the app,
such as the User object and the Message object.
"""

from enum import Flag, Enum
from typing import TYPE_CHECKING
from errors import InsufficientPermissions
from datetime import datetime

if TYPE_CHECKING:
    from database import Database
    from socketio import AsyncServer

class Message:
    """
    Message object to store message data.
    """
    def __init__(self, data: dict):
        self.id: int = data.get('id', None)
        self.content: str = data.get('message', data.get('content', None))
        self.author: str | User = data.get('author', None)
        self.channel: str = data.get('channel', None)
        self.timestamp: str = data.get('timestamp', datetime.strftime(datetime.now(), "%H:%M:%S"))
        self.type: MessageType = data.get('type', MessageType.NORMAL)

    def to_dict(self) -> dict:
        """
        Serialize the message object into JSON format,
        to be sent to the client.
        """
        return {
            "id": self.id,
            "message": self.content,
            "author": self.author,
            "channel": self.channel,
            "timestamp": self.timestamp,
            "type": self.type.value,
        }
    
    def as_sendable(self) -> dict:
        """
        Serialize the message object into JSON format,
        to be sent to the client.
        """
        return {
            "message": self.content,
            "author": self.author if isinstance(self.author, str) else self.author.as_sendable(),
            "timestamp": self.timestamp,
            "type": self.type.value,
        }

    def __repr__(self):
        return f"<Message {self.id}>"


class Command:
    def __init__(self, name: str, func, description: str):
        self.name = name
        self.func = func
        self.description = description

    async def execute(self, ctx: "Context") -> str:
        return await self.func(ctx)


class Application:
    def __init__(self, db: "Database", sio: "AsyncServer", commands: list[Command]):
        self.db = db
        self.sio = sio
        self.commands = commands

    async def process_command(self, ctx: "Context") -> Message | None:
        """
        Process the command from a context object.
        """
        for command in self.commands:
            if command.name == ctx.command:
                return await command.execute(ctx)

        return None

    async def send_message(self, ctx: "Context", to: str | None = None) -> None:
        """
        Send a message to a channel.
        """
        await self.sio.emit("message", ctx.message.as_sendable(), to=to)
        await self.db.capture_message(ctx.message)


class Context:
    def __init__(self, app: "Application", message: "Message"):
        self.app: "Application" = app
        self.message = message
        self.mentions = []
        self.mentioned = False
        self.is_command = False
        self.command = None
        self.args = []

    @classmethod
    async def from_message(cls, app: "Application", message: "Message") -> "Context":
        ctx = cls(app, message)
        ctx.mentioned = await ctx.get_mentions()
        ctx.command = await ctx.get_command()
        ctx.is_command = ctx.command is not None

        return ctx

    @classmethod
    async def with_message(cls, message_data: dict, app: "Application", ) -> "Context":
        message = Message(message_data)
        return await cls.from_message(app, message)

    async def get_mentions(self) -> None:
        """
        Check if the message contains mentions.
        """
        for word in self.message.content.split():
            if word.startswith("@"):
                user = await self.app.db.get_user(word[1:])

                if user is not None:
                    self.mentions.append(user)

    async def get_command(self) -> str:
        """
        Get the command from the message.
        """
        if self.message.content.startswith(":"):
            return self.message.content.split()[0][1:]

        return None

    @property
    def first_mention(self) -> "User | None":
        """
        Get the first mention in the message.
        """
        if len(self.mentions) > 0:
            return self.mentions[0]

        return None


class Permissions(Flag):
    """
    Flag enum to control what permissions a user
    may have.
    """
    READ = 1
    SEND = 2
    EDIT = 4
    DELETE = 8
    BAN  = 16
    KICK = 32
    COMMANDS = 64
    DELETE_OTHERS = 128


class MessageType(Enum):
    """
    Enum to control what type of message is being sent.
    """
    NORMAL = "message"
    COMMAND = "command"
    ERROR = "error"
    USER_CONNECT = "user_connect"
    USER_DISCONNECT = "user_disconnect"


class User:
    """
    User object to store user data. One day, this will become
    a powerful object that can be used to interact with the 
    database directly. Oh, the possibilities.
    """
    def __init__(self, data: dict):
        self.email: str = data.get('email', None)
        self.username: str = data.get('username', None)
        self.password: str = data.get('password', None)
        self.password_salt: str = data.get('password_salt', None)
        self.displayname: str = data.get('displayname', None)
        self.dob: str = data.get('dob', None)
        self.session: str = data.get('session', None)
        self.creation_date: str = data.get('creation_date', None)
        self.permissions: Permissions = Permissions(data.get('permissions', None))

    def to_dict(self) -> dict:
        """
        Serialize the user object into JSON format, 
        to be sent to the client.
        """
        return {
            "email": self.email,
            "username": self.username,
            "displayname": self.displayname,
            "dob": self.dob,
            "session": self.session,
            "creation_date": self.creation_date,
            "permissions": self.permissions.value,
        }

    def as_sendable(self) -> dict:
        """
        Serialize the user object into JSON format, 
        to be sent to the client.
        """
        return {
            "username": self.username,
            "displayname": self.displayname,
            "creation_date": self.creation_date,
        }

    def __repr__(self):
        return f"<User {self.username}>"

