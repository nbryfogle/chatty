"""
Commands.py holds all there ever was, is, and will be regarding commands.
Commands allow a user to interact with the system-side of the program, or just
have fun with some funny messages.
"""

import random
from objects import Permissions, Context, Command, Message, MessageType, User
from typing import Callable


HELP_MSG = """
Current commands: (* = required argument)
:help - this command, the very one you just used
:bonk @username* - sends a wonderful message of cartoonish violence
:kwispy @username* - Pyromaniacal version of :bonk
:squiddy @username* - Meh, better if you figure this one out on your own...
:chirp @username* - Deliver a good old-fasioned ice hockey chirp to one of your buddies
:suck @username* - REDACTED
"""


command_register: list["Command"] = []

def command(name: str, description: str) -> Callable:
    """
    Decorator for describing a function as command.
    """
    def decorator(func):
        command_register.append(Command(name, func, description))
        return func

    return decorator

def command_msg(content: str, author: User | str = "Server") -> Message:
    """
    Create a message from a command.
    """
    return Message({
        "content": content,
        "author": author,
        "channel": "general",
        "type": MessageType.COMMAND,
    })

@command("bonk", "Bonk a sucker on the head. Usage: :bonk @username")
async def bonk(ctx: Context) -> Message | None:
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

    if not ctx.first_mention:
        return None

    return command_msg(
        random.choice(bonk_messages).format(ctx.first_mention.displayname),
        ctx.message.author
        )
        

@command("squiddy", "Send a squidward quote. Usage: :squiddy @username")
async def squiddy(ctx: Context) -> Message | None:
    squid_mess = [
        ": AUGUST 12th, 2036: THE HEAT DEATH OF THE UNIVERSE! {}, YOUR RECKONING WILL BEFALL UPON YOU!",
        "what if I pop my bumhole out and let it dry in the sun? {}",
    ]
    if not ctx.first_mention:
        return None

    return command_msg(
        random.choice(squid_mess).format(ctx.first_mention.displayname),
        ctx.message.author
        )
        
@command("kwispy", "Light a sucker on fire. Usage: :kwispy @username")
async def kwispy(ctx: Context) -> Message | None:
    kwispy_mess = [
        "sets {} on fire.",
        "sets {} alight with his magic butane blaster.",
        "introduces {} to the complex process of combustion.",
        "proceeds to melt {}'s face off.",
        "lights {} on fire with some good ol' fasioned matches.",
    ]
    if not ctx.first_mention:
        return None

    return command_msg(
        random.choice(kwispy_mess).format(ctx.first_mention.displayname),
        ctx.message.author
        )

@command("chirp", "Insult someone, I guess. Usage: :chirp @username")
async def chirp(ctx: Context) -> Message | None:
    chirpmess = [
        "Hey {}, why don't ya skate, ya pheasant!?",
        "Hey {}, I've seen better hands on a digital clock!",
    ]
    if not ctx.first_mention:
        return None

    return command_msg(
        random.choice(chirpmess).format(ctx.first_mention.displayname),
        ctx.message.author
        )

@command("ban", "Ban a sucker. Usage: :ban @username")
async def ban(ctx: Context) -> Message | None:
    if not ctx.first_mention:
        return None

    ctx.first_mention.permissions = Permissions(0)
    await ctx.app.db.update_user(ctx.first_mention)

    return command_msg(f"Banned {ctx.first_mention.username} ({ctx.first_mention.displayname}).")
