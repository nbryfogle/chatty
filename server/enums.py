from enum import Flag, Enum

class Permissions(Flag):
    """
    Flag enum to control what permissions a user
    may have.
    """
    READ = 1
    SEND = 2
    EDIT = 4
    DELETE = 8
    BAN  = 16
    KICK = 32
    COMMANDS = 64
    DELETE_OTHERS = 128


class MessageType(Enum):
    """
    Enum to control what type of message is being sent.
    """
    NORMAL = "message"
    COMMAND = "command"
    ERROR = "error"
    USER_CONNECT = "user_connect"
    USER_DISCONNECT = "user_disconnect"
