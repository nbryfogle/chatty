"""
Objects.py holds a variety of objects that are used in the app,
such as the Permission enum, the Message object, and the Context
object.
"""

from typing import TYPE_CHECKING

from database import User, Message, MessageResponse
from config import COMMAND_PREFIX
from enums import Permissions

if TYPE_CHECKING:
    from socketio import AsyncServer
    from database import Database


class Command:
    """
    Define a command that the user can use.
    """

    def __init__(self, name: str, func, description: str):
        self.name = name
        self.callback = func
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

        return await self.callback(ctx)


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

    async def send_message(self, message: MessageResponse) -> None:
        """
        Send a message to a channel and save the result in a database.
        """
        if message.is_ephemeral:
            await self.sio.emit("message", message.serialize(), to=message.user.sid)
        else:
            await self.sio.emit("message", message.serialize())
            await message.save()

    async def user_message(self, context: "Context") -> None:
        await context.message.save()
        await self.sio.emit("message", context.message.as_sendable())


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
        self.channel = "general"

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

    async def get_mentions(self) -> None:
        """
        Check if the message contains mentions.
        """
        for word in self.message.content.split():
            if word.startswith("@"):  # The mention character is @
                user = await User.get(
                    username=word[1:],
                    sid=self.message.author.sid,
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
    def first_mention(self) -> User | None:
        """
        Get the first mention in the message.
        """
        if len(self.mentions) > 0:
            return self.mentions[0]

        return None

    @property
    def author(self) -> User:
        """
        Get the author of the message.
        """
        return self.message.author
