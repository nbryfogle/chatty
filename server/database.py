import aiosqlite

class Database:
    def __init__(self):
        self.conn: aiosqlite.Connection
        self.c: aiosqlite.Cursor 

    @classmethod
    async def connect(cls, path):
        db = cls()
        db.conn = await aiosqlite.connect(path)
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

