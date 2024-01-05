from enum import Flag

class Permissions(Flag):
    READ = 1
    SEND = 2
    EDIT = 4
    DELETE = 8
    BAN  = 16
    KICK = 32
    COMMANDS = 64
    DELETE_OTHERS = 128


class User:
    def __init__(self, data: dict):
        self.email: str = data.get('email', None)
        self.username: str = data.get('username', None)
        self.password: str = data.get('password', None)
        self.password_salt: str = data.get('password_salt', None)
        self.displayname: str = data.get('displayname', None)
        self.dob: str = data.get('dob', None)
        self.session: str = data.get('session', None)
        self.creation_date: str = data.get('creation_date', None)
        self.permissions: Permissions = Permissions(data.get('permissions', None))

    def to_dict(self) -> dict:
        return {
            "email": self.email,
            "username": self.username,
            "displayname": self.displayname,
            "dob": self.dob,
            "session": self.session,
            "creation_date": self.creation_date,
            "permissions": self.permissions.value,
        }

    def __repr__(self):
        return f"<User {self.username}>"


class Message:
    def __init__(self, data: dict):
        self.id: int = data.get('id', None)
        self.message: str = data.get('message', None)
        self.author: str = data.get('author', None)
        self.channel: str = data.get('channel', None)
        self.timestamp: str = data.get('timestamp', None)

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
