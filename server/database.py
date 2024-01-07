"""
Database.py holds all of the database interactions.
"""

import aiosqlite
from objects import Permissions, User


class Database:
    """
    The main database class. 
    This class controls all database interactions.
    """
    def __init__(self) -> None:
        self.conn: aiosqlite.Connection
        self.c: aiosqlite.Cursor

    @classmethod
    async def connect(cls, path: str) -> 'Database':
        """
        Connect to the database.
        """
        db = cls()
        db.conn = await aiosqlite.connect(path)
        db.conn.row_factory = aiosqlite.Row
        db.c = await db.conn.cursor()
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
                permissions INTEGER DEFAULT 67
            )
        ''')
        # Make the timestamp the current time in EST
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

        return user if user is None else user["username"]

    async def check_user_exists(self, username: str) -> bool:
        """
        Check if a user exists in the database.
        """
        await self.c.execute('''
            SELECT * FROM users WHERE username = ?
        ''', (username,))
        user = await self.c.fetchone()
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
        if user is None:
            return False
        return True

    async def create_user(self, data: dict) -> tuple[dict, int]:
        """
        Data example:
        {
            "username": "test",
            "password": "test",
            "email": "ex@example.com"
            "display_name": "test"
        }
        """

        if await self.check_user_exists(data['username']):
            return {"status": "error", "message": "Username is already in use."}, 401
        
        if await self.check_email_exists(data['email']):
            return {"status": "error", "message": "Email is already in use."}, 401
        
        await self.c.execute('''
            INSERT INTO users (email, username, password, password_salt, displayname, dob, permissions)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['email'], 
            data['username'], 
            data['password'], 
            data['password_salt'], 
            data['displayname'], 
            data['dob'],
            (Permissions.READ | Permissions.SEND | Permissions.COMMANDS).value 
            ))

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

        if user is None:
            return None
        
        return User(dict(user))

    async def capture_message(self, username: str, message_content: str) -> None:
        """
        Capture a message from a user and store it in the database.
        """
        await self.c.execute('''
            INSERT INTO messages (message, author, channel)
            VALUES (?, ?, ?)
        ''', (message_content, username, "general"))
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
    