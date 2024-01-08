import aiosqlite

class User:
    def __init__(self, data: dict):
        self.email = data.get('email', None)
        self.username = data.get('username', None)
        self.password = data.get('password', None)
        self.password_salt = data.get('password_salt', None)
        self.displayname = data.get('displayname', None)
        self.dob = data.get('dob', None)
        self.session = data.get('session', None)
        self.creation_date = data.get('creation_date', None)

    def to_dict(self) -> dict:
        return {
            "email": self.email,
            "username": self.username,
            "displayname": self.displayname,
            "dob": self.dob,
            "session": self.session,
            "creation_date": self.creation_date
        }

    def __repr__(self):
        return f"<User {self.username}>"

class Message:
    def __init__(self, data: dict):
        self.id = data.get('id', None)
        self.message = data.get('message', None)
        self.author = data.get('author', None)
        self.channel = data.get('channel', None)
        self.timestamp = data.get('timestamp', None)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "message": self.message,
            "author": self.author,
            "channel": self.channel,
            "timestamp": self.timestamp
        }

    def __repr__(self):
        return f"<Message {self.id}>"

class Database:
    def __init__(self):
        self.conn: aiosqlite.Connection
        self.c: aiosqlite.Cursor 

    @classmethod
    async def connect(cls, path: str) -> 'Database':
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
                permissions INTEGER DEFAULT 71
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

    async def authenticate_user(self, token: str) -> bool | str:
        """
        Make sure the session token that the client is trying to connect with exists
        and is valid.
        """
        await self.c.execute('''
            SELECT * FROM users WHERE session = ?
        ''', (token,))
        user = await self.c.fetchone()

        if user is None:
            return False
        
        return user["username"]

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
    