"""
Objects.py holds a variety of objects that are used in the app,
such as the Permission enum, the Message object, and the Context
object.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from database import DBUser
from config import COMMAND_PREFIX
from enums import MessageType, Permissions

if TYPE_CHECKING:
    from database import Database
    from socketio import AsyncServer


class Message:
    """
    Message object to store message data.
    """

    def __init__(self, data: dict):
        self.id: int = data.get("id", None)
        self.content: str = data.get("message", data.get("content", None))
        self.author: str | "DBUser" = data.get("author", None)
        self.channel: str = data.get("channel", None)
        self.timestamp: str = data.get(
            "timestamp", datetime.strftime(datetime.now(), "%H:%M:%S")
        )
        self.type: MessageType = data.get("type", MessageType.NORMAL)

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
            "author": self.author
            if isinstance(self.author, str)
            else self.author.as_sendable(),
            "timestamp": self.timestamp,
            "type": self.type.value,
        }

    def __repr__(self):
        return f"<Message {self.id}>"


class Command:
    """
    Define a command that the user can use.
    """

    def __init__(self, name: str, func, description: str):
        self.name = name
        self.func = func
        self.description = description

    async def execute(self, ctx: "Context") -> Message | None:
        """
        Execute the command based on the context.
        """
        if (
            not ctx.is_command
            or not ctx.message.author.permissions & Permissions.COMMANDS
        ):
            return None

        return await self.func(ctx)


class Application:
    """
    Represents the entire app. It's easier to control the application when everything has access
    to anything it may ever want. This travels with the Context object to give Commands access
    to common things, such as the database and the socketio server.
    """

    def __init__(self, db: "Database", sio: "AsyncServer", commands: list[Command]):
        self.db = db
        self.sio = sio
        self.commands = commands

    async def process_command(self, ctx: "Context") -> Message | None:
        """
        Execute the associated callback method of a command.
        """
        for command in self.commands:
            if command.name == ctx.command:
                return await command.execute(ctx)

        return None

    async def send_message(self, ctx: "Context", to: str | None = None) -> None:
        """
        Send a message to a channel and save the result in a database.
        """
        await self.sio.emit("message", ctx.message.as_sendable(), to=to)
        await self.db.capture_message(ctx.message)


class Context:
    """
    Interaction Context is an object that holds information about interactions between
    a user and the system. This is used to pass useful information between parts of the
    system, especially the command system.
    """

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
        """
        Create a Context object from a Message object.
        """
        ctx = cls(app, message)
        ctx.mentioned = await ctx.get_mentions()
        ctx.command = await ctx.get_command()
        ctx.is_command = ctx.command is not None

        return ctx

    @classmethod
    async def with_message(
        cls,
        message_data: dict,
        app: "Application",
    ) -> "Context":
        """
        Create a Context object from message data. Shorthand for creating a message
        and then creating a context along side of it, because that seems to happen
        a lot these days.
        """
        message = Message(message_data)
        return await cls.from_message(app, message)

    async def get_mentions(self) -> None:
        """
        Check if the message contains mentions.
        """
        for word in self.message.content.split():
            if word.startswith("@"):  # The mention character is @
                user = await DBUser.get(
                    username=word[1:]
                )  # [1:] removes the @ from the username

                if user is not None:
                    # If the user exists, add it to the mentions.
                    # Commands can have multiple mentions.
                    self.mentions.append(user)

    async def get_command(self) -> str:
        """
        Get the command from the message.
        """
        if self.message.content.startswith(COMMAND_PREFIX):
            # This list comprehension removes the first word from the message, and then
            # joins the rest of the words back together. The [1:] removes the : from the command.
            return self.message.content.split()[0][1:]

        return None

    @property
    def first_mention(self) -> "DBUser | None":
        """
        Get the first mention in the message.
        """
        if len(self.mentions) > 0:
            return self.mentions[0]

        return None
