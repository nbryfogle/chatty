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
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.conn.commit()
        return db

    async def authenticate_user(self, token: str) -> bool | aiosqlite.Row:
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
        
        return user[0]

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
