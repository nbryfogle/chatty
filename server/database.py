"""
I can't wait to write code comments on this abomination.
"""

import aiosqlite
from objects import User, Message

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
    async def connect(cls, path: str) -> 'Database':
        """
        Connect to the database. Also construct the database if 
        it doesn't exist.
        """
        db = cls()
        db.conn = await aiosqlite.connect(path)
        db.conn.row_factory = aiosqlite.Row # I think this represents data in a dict-like format
        db.c = await db.conn.cursor() # There's our cursor to execute SQL statements with

        # Such as these ones
        await db.c.execute('''
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
        ''')
        await db.c.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                author TEXT NOT NULL,
                channel TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime'))
            )
        ''')
        await db.conn.commit()
        return db

    async def authenticate_user(self, token: str) -> None | str:
        """
        Make sure the session token that the client is trying to connect with exists
        and is valid.
        """
        await self.c.execute('''
            SELECT * FROM users WHERE session = ?
        ''', (token,))
        user = await self.c.fetchone()

        # If no user was found with that token, screw them
        if user is None:
            return None

        return user["username"]

    async def check_user_exists(self, username: str) -> bool:
        """
        Check if a user exists in the database.
        """
        await self.c.execute('''
            SELECT * FROM users WHERE username = ?
        ''', (username,))
        user = await self.c.fetchone()

        # If the user does not exist, their ass is grass
        if user is None:
            return False

        return True

    async def check_email_exists(self, email: str) -> bool:
        """
        Check if a user exists in the database.
        """
        await self.c.execute('''
            SELECT * FROM users WHERE email = ?
        ''', (email,))
        user = await self.c.fetchone()

        # If the email does not exist with a user, tell them so.
        if user is None:
            return False

        return True

    async def create_user(self, data: dict) -> tuple[dict, int]:
        """
        Create a user in the database.
        Data example:
        {
            "username": "test",
            "password": "test",
            "email": "ex@example.com"
            "display_name": "test"
        }
        """

        # If the user exists, fuck 'em
        if await self.check_user_exists(data['username']):
            return {"status": "error", "message": "Username is already in use."}, 401

        # Same with the email address
        if await self.check_email_exists(data['email']):
            return {"status": "error", "message": "Email is already in use."}, 401

        # This says, "create a new user with this information in the users table."
        await self.c.execute('''
            INSERT INTO users (email, username, password, password_salt, displayname, dob)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data['email'], data['username'], data['password'], data['password_salt'], data['displayname'], data['dob']))

        await self.conn.commit()

        return {"status": "success"}, 200

    async def get_user(self, username: str) -> User | None:
        """
        Get a user from the database.
        """
        await self.c.execute('''
            SELECT * FROM users WHERE username = ?
        ''', (username,))
        user = await self.c.fetchone()

        # Imagine not existing. Couldn't be me.
        if user is None:
            return None
        
        return User(dict(user))

    async def update_user(self, user: User) -> None:
        """
        Update a user's data in the database.
        """
        await self.c.execute('''
                             
            UPDATE users SET email = ?, username = ?, password = ?, password_salt = ?, displayname = ?, dob = ?, session = ?, permissions = ? WHERE username = ?
        ''', (user.email, user.username, user.password, user.password_salt, user.displayname, user.dob, user.session, user.permissions.value, user.username))
        
        # This bullshit does NOT CARE if you exist or not. It will update you anyway.
        # I guess that's a job for whoever is calling this function.

        await self.conn.commit()

    async def capture_message(self, message: "Message") -> None:
        """
        Capture a message from a user and store it in the database.
        """
        await self.c.execute('''
            INSERT INTO messages (message, author, channel)
            VALUES (?, ?, ?)
        ''', (message.content, message.author.displayname if isinstance(message.author, User) else message.author, "general"))

        await self.conn.commit()     

    async def get_messages(self, amount: int = 20) -> list[dict]:
        """
        Get the last 10 messages from the database.
        """
        await self.c.execute('''
            SELECT * FROM messages ORDER BY id DESC LIMIT ?
        ''', (amount,))
        
        messages = await self.c.fetchall()

        return [dict(message) for message in messages][::-1]
    