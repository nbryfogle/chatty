"""
I can't wait to write code comments on this abomination.
"""

import asyncio
from typing import TYPE_CHECKING
from uuid import uuid4

import aiosqlite
import bcrypt
from enums import Permissions
from errors import MalformedDataError

if TYPE_CHECKING:
    from objects import Message


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
                if isinstance(message.author, DBUser)
                else message.author,
                "general",
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


class DBUser:
    """
    Represents a user in the database. This holds methods that may
    be useful for working with the user, such as changing information
    and, well, getting information. Obviously.
    """

    def __init__(self, data: dict):
        self.data = data

    @classmethod
    async def get(cls, username: str) -> "DBUser | None":
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

        return cls(dict(user))

    @classmethod
    async def create(cls, data: dict) -> "DBUser":
        """
        The user wants to exist. What a shame.
        Data should look something like this:
        {
            "username": "test",
            "password": "test",
            "email": "themail@mail.net",
            "displayname": "test",
            "dob": "01/01/2000"
        }
        """
        if not all(
            key in data and data[key]
            for key in ("username", "password", "email", "dob")
        ):
            raise MalformedDataError("Unable to create user: Missing key in data.")

        data["displayname"] = data.get("displayname", data["username"])

        salt = bcrypt.gensalt()
        data["password"] = bcrypt.hashpw(
            bytes(data["password"], encoding="utf-8"), salt
        )

        await db.c.execute(
            """
            INSERT INTO users (email, username, password, password_salt, displayname, dob)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                data["email"],
                data["username"],
                data["password"],
                salt,
                data["displayname"],
                data["dob"],
            ),
        )

        await db.conn.commit()
        user = await cls.get(data["username"])

        return user

    async def update(self) -> None:
        """
        Update the user's data in the database.
        """
        await db.c.execute(
            """            
            UPDATE users SET email = ?, username = ?, displayname = ?, 
            dob = ?, session = ?, permissions = ? WHERE username = ?
        """,
            (
                self.email,
                self.username,
                self.data.get("displayname", None),
                self.dob,
                self.session,
                self.permissions.value,
                self.username,
            ),
        )

        # This bullshit does NOT CARE if you exist or not. It will update you anyway.
        # I guess that's a job for whoever is calling this function.
        await db.conn.commit()

    def check_password(self, password: str) -> bool:
        """
        Check if the user's password is correct.
        """
        return bcrypt.checkpw(bytes(password, encoding="utf-8"), self.data["password"])

    async def refresh_session(self) -> str:
        """
        Refresh the user's session token.
        """
        self.data["session"] = str(uuid4())
        await self.update()

        return self.session

    def as_sendable(self) -> dict:
        """
        Get the user's data in a sendable format, so we are not leaking
        sensitive information to any joe schmoe who asks for it.
        """
        return {
            "username": self.username,
            "displayname": self.display_name,
            "permissions": self.permissions.value,
        }

    @property
    def email(self) -> str | None:
        """
        Get the user's email address.
        """
        return self.data.get("email", None)

    @email.setter
    def email(self, value: str) -> None:
        self.data["email"] = value

    @property
    def username(self) -> str:
        """
        Get the user's username.
        """
        return self.data["username"]

    @username.setter
    def username(self, value: str) -> None:
        self.data["username"] = value

    @property
    def display_name(self) -> str:
        """
        Get the user's display name.
        """
        return self.data.get("displayname", self.username)

    @display_name.setter
    def display_name(self, value: str) -> None:
        self.data["displayname"] = value

    @property
    def dob(self) -> str:
        """
        Get the user's date of birth.
        """
        return self.data["dob"]

    @dob.setter
    def dob(self, value: str) -> None:
        self.data["dob"] = value

    @property
    def permissions(self) -> Permissions:
        """
        Get the user's permissions.
        """
        return Permissions(self.data.get("permissions", 71))

    @property
    def session(self) -> str | None:
        """
        Get the user's session token. This should absolutely
        be public information.
        """
        return self.data.get("session", None)


db = asyncio.run(Database.connect("server/database/database.db"))
