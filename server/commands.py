"""
Commands.py holds all of the commands and command-based interactions
to use within the chat.
"""

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from objects import User
    from database import Database


async def get_user_from_mention(db: "Database", message: str) -> "User" | None:
    """
    Get a mention of a user.
    """
    for word in message.split(" "):
        if word.startswith("@"):
            user = await db.get_user(word[1:])
            if user is None:
                return None

            return user

    return None


async def process_command(db: "Database", message: str, user: "User") -> str | None:
    """
    Process a command that is sent by a user.
    """
    match message.split(" ")[0].strip(":"):
        case "bonk":
            to_bonk = await get_user_from_mention(db, message)

            if to_bonk is None:
                return None

            message = await bonk(to_bonk)

            return message

        case "suck":
            to_suck = await get_user_from_mention(db, message)

            if to_suck is None:
                return None

            message = await suck(to_suck)

            return message

        case "squiddy":
            to_squid = await get_user_from_mention(db, message)

            if to_squid is None:
                return None

            message = await suck(to_squid)

            return message

    return None


async def bonk(user: "User") -> str:
    """
    Message command that sends a message to "bonk" a user.
    """
    bonk_messages = [
        "bonks {} on the head",
        "breaks {}'s kneecaps",
        "bonks {}'s head into the ground",
        "bonks {}'s head into the wall",
        "bonks {}'s head into the ceiling",
        "bonks {}'s head into the floor",
        "bonks {}'s head into the table",
        "bonks {}'s head into the chair",
        "bonks {}'s head into the door",
        "bonks {}'s head into the window",
        "bonks {}'s head into the computer",
        "bonks {} into the sun",
    ]

    return random.choice(bonk_messages).format(user.displayname)


async def suck(user: "User") -> str:
    """
    Message command that sends a message to "suck" a user.
    """
    suck_messages = [
        "sucks off {}",
    ]

    return random.choice(suck_messages).format(user.displayname)


async def squiddy(user: "User") -> str:
    """
    Message command that sends a quote from Squidward to a user.
    """
    squid_mess = [
        "NOVEMBER 12th, 2036: THE HEAT DEATH OF THE UNIVERSE! {}, YOUR RECKONING WILL BEFALL YOU!",
    ]
