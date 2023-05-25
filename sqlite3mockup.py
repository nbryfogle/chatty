import sqlite3
conn = sqlite3.connect('acc.db')

c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        email TEXT NOT NULL,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        password_salt TEXT NOT NULL,
        firstname TEXT NOT NULL,
        lastname TEXT NOT NULL,
        displayname TEXT NOT NULL,
        dob TEXT NOT NULL,
        session TEXT NULL,
        creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    )
''')
conn.commit()