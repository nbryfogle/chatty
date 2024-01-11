"""
These enums are a useful way to represent common data in a human-readable format.
"""

from enum import Enum, Flag


class Permissions(Flag):
    """
    Flag enum to represent what permissions a user
    may have.
    """

    READ = 1
    SEND = 2
    EDIT = 4
    DELETE = 8
    BAN = 16
    KICK = 32
    COMMANDS = 64
    DELETE_OTHERS = 128


class MessageType(Enum):
    """
    Enum to represent what type of message is being sent.
    """

    NORMAL = "message"
    COMMAND = "command"
    ERROR = "error"
    USER_CONNECT = "user_connect"
    USER_DISCONNECT = "user_disconnect"
