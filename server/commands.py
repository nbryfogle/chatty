import random
from database import Database
from objects import User, Permissions

help_mes = """
Current commands: (* = required argument)
:help - this command, the very one you just used
:bonk @username* - sends a wonderful message of cartoonish violence
:kwispy @username* - Pyromaniacal version of :bonk
:squiddy @username* - Meh, better if you figure this one out on your own...
:chirp @username* - Deliver a good old-fasioned ice hockey chirp to one of your buddies
:suck @username* - REDACTED

"""


async def get_user_from_mention(db: Database, message: str) -> User | None:
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

        case "squiddy":
            to_squid = await get_user_from_mention(db, message)

            if to_squid is None:
                return None

            message = await squiddy(to_squid)

            return message

        case "kwispy":
            to_kwispy = await get_user_from_mention(db, message)

            if to_kwispy is None:
                return None

            message = await kwispy(to_kwispy)

            return message

        case "chirp":
            chirping = await get_user_from_mention(db, message)

            if chirping is None:
                return None
            message = await chirp(chirping)
            return message
        case "help":
            message = help_mes
            return message

        case "ban":
            if not user.permissions & Permissions.BAN:
                return None

            to_ban = await get_user_from_mention(db, message)

            if to_ban is None:
                return None

            return await ban(db, to_ban)

        case "ban":
            if not user.permissions & Permissions.BAN:
                return None

            to_ban = await get_user_from_mention(db, message)

            if to_ban is None:
                return None

            return await ban(db, to_ban)

        case "ban":
            if not user.permissions & Permissions.BAN:
                return None

            to_ban = await get_user_from_mention(db, message)

            if to_ban is None:
                return None

            return await ban(db, to_ban)

    return None


async def bonk(user: User) -> str:
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


async def squiddy(user: User) -> str:
    squid_mess = [
        ": AUGUST 12th, 2036: THE HEAT DEATH OF THE UNIVERSE! {}, YOUR RECKONING WILL BEFALL UPON YOU!",
    ]

    return random.choice(squid_mess).format(user.displayname)


async def kwispy(user: User) -> str:
    kwispy_mess = [
        "sets {} on fire.",
        "sets {} alight with his magic butane blaster.",
        "introduces {} to the complex process of combustion.",
        "proceeds to melt {}'s face off.",
        "lights {} on fire with some good ol' fasioned matches.",
    ]

    return random.choice(kwispy_mess).format(user.displayname)


async def chirp(user: User) -> str:
    chirpmess = [
        "Hey {}, why don't ya skate, ya pheasant!?",
        "Hey {}, I've seen better hands on a digital clock!",
    ]

    return random.choice(chirpmess).format(user.displayname)


async def ban(db: "Database", user: User) -> str:
    user.permissions = Permissions(0)
    await db.update_user(user)

    return f"Banned {user.displayname}."
