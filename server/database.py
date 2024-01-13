"""
I can't wait to write code comments on this abomination.
"""

import asyncio
from typing import TYPE_CHECKING
from uuid import uuid4
from dataclasses import dataclass

import aiosqlite
import bcrypt
from enums import Permissions
from errors import MalformedDataError
from config import REQUIRED_USER_FIELDS

if TYPE_CHECKING:
    from objects import Message, MessageResponse


class Database:
    """
    The database. This represents the database that the server
    will use to store data. It will be used to interface with
    the database directly.
    """

    def __init__(self) -> None:
        self.conn: aiosqlite.Connection
        self.c: aiosqlite.Cursor

    @classmethod
    async def connect(cls, path: str) -> "Database":
        """
        Connect to the database. Also construct the database if
        it doesn't exist.
        """
        database = cls()
        database.conn = await aiosqlite.connect(path)
        database.conn.row_factory = (
            aiosqlite.Row
        )  # I think this represents data in a dict-like format
        database.c = (
            await database.conn.cursor()
        )  # There's our cursor to execute SQL statements with

        # Such as these ones
        await database.c.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                email TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                displayname TEXT NOT NULL,
                dob TEXT NOT NULL,
                session TEXT NULL,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                permissions INTEGER DEFAULT 71
            )
        """
        )
        await database.c.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                author TEXT NOT NULL,
                channel TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime'))
            )
        """
        )
        await database.conn.commit()
        return database

    async def authenticate_user(self, token: str) -> None | str:
        """
        Make sure the session token that the client is trying to connect with exists
        and is valid.
        """
        await self.c.execute(
            """
            SELECT * FROM users WHERE session = ?
        """,
            (token,),
        )
        user = await self.c.fetchone()

        # If no user was found with that token, screw them
        if user is None:
            return None

        return user["username"]

    async def capture_message(self, message: "Message") -> None:
        """
        Capture a message from a user and store it in the database.
        """
        await self.c.execute(
            """
            INSERT INTO messages (message, author, channel)
            VALUES (?, ?, ?)
        """,
            (
                message.content,
                message.author.display_name
                if isinstance(message.author, User)
                else message.author,
                "general",
            ),
        )

        await self.conn.commit()

    async def capture_message_response(self, message: "MessageResponse"):
        """
        Capture a MessageResponse object to the database.
        """
        await self.c.execute(
            "INSERT INTO messages (message, author, channel) VALUES (?, ?, ?)",
            (
                message.message.content,
                message.user.display_name,
                message.context_from.channel,
            ),
        )

        await self.conn.commit()

    async def get_messages(self, amount: int = 20) -> list[dict]:
        """
        Get the last 10 messages from the database.
        """
        await self.c.execute(
            """
            SELECT * FROM messages ORDER BY id DESC LIMIT ?
        """,
            (amount,),
        )

        messages = await self.c.fetchall()

        return [dict(message) for message in messages][::-1]


@dataclass
class User:
    username: str
    email: str
    creation_date: str
    permissions: Permissions = Permissions(71)
    displayname: str | None = None
    session: str | None = None
    dob: str | None = None
    sid: str | None = None

    @classmethod
    async def get(cls, username: str, sid: str | None = None) -> "User | None":
        """
        Get a user from the database.
        """
        await db.c.execute(
            """
            SELECT * FROM users WHERE username = ?
        """,
            (username,),
        )
        user = await db.c.fetchone()

        # The user doesn't exist. What a shame.
        if user is None:
            return None

        user = dict(user)

        del user["password"]
        del user["password_salt"]

        user["permissions"] = Permissions(user["permissions"])

        return cls(
            sid=sid,
            **user,
        )

    async def save(self) -> None:
        """
        Save the current data to the database.
        """
        serialized = self.serialize()
        req_fields = REQUIRED_USER_FIELDS.copy()
        req_fields.remove("password")

        if not all(key in serialized.keys() and serialized[key] for key in req_fields):
            raise MalformedDataError("Unable to save user: Missing key in data.")

        await db.c.execute(
            "UPDATE users SET (username, email, permissions, displayname, dob) = (?, ?, ?, ?, ?) WHERE username = ?",
            (*serialized.values(), self.username),
        )

        await db.conn.commit()

    async def create(self, password: str) -> "User":
        """
        Takes an already-created dataclass and creates a new entry
        for it in the database. Used for things such as hashing a password
        and storing it.
        """
        serialized = self.serialize()
        if not all(key in serialized for key in REQUIRED_USER_FIELDS):
            raise MalformedDataError("Unable to create user: Missing key in data.")

        salt = bcrypt.gensalt()
        serialized["password"] = bcrypt.hashpw(bytes(password, encoding="utf-8"), salt)
        serialized["password_salt"] = salt

        await db.c.execute(
            """
            INSERT INTO users (username, email, password, password_salt, permissions, displayname, dob)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (*serialized.values(),),
        )

        await db.conn.commit()

        return self

    def serialize(self) -> dict:
        """
        Get the user's data in a dictionary format with all data.
        """
        return {
            "username": self.username,
            "email": self.email,
            "permissions": self.permissions.value,
            "displayname": self.display_name,
            "dob": self.dob,
        }

    def as_sendable(self) -> dict:
        """
        Get the user's data in a sendable format, so we are not leaking
        sensitive information to any joe schmoe who asks for it.
        """
        return {
            "username": self.username,
            "displayname": self.display_name,
            "permissions": self.permissions.value,
            "creation_date": self.creation_date,
        }

    async def check_password(self, password: str) -> bool:
        """
        Check if the user's password is correct.
        """
        # Get the password from the database
        await db.c.execute(
            """
            SELECT password FROM users WHERE username = ?
        """,
            (self.username,),
        )
        correct_password = (await db.c.fetchone())["password"]

        return bcrypt.checkpw(bytes(password, encoding="utf-8"), correct_password)

    async def refresh_session(self) -> str:
        """
        Refresh the user's session token.
        """
        self.session = str(uuid4())
        await self.save()

        return self.session

    @property
    def display_name(self) -> str:
        return self.displayname or self.username

    @display_name.setter
    def display_name(self, value: str) -> None:
        self.displayname = value


db = asyncio.run(Database.connect("server/database/database.db"))
