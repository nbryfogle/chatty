"""
Commands.py holds all there ever was, is, and will be regarding commands.
Commands allow a user to interact with the system-side of the program, or just
have fun with some funny messages.
"""

import random
from typing import Callable

from enums import MessageType, Permissions
from objects import Command, Context, MessageResponse, Message


command_register: list["Command"] = []


def command(name: str, description: str) -> Callable:
    """
    Decorator for describing a function as command.
    """

    def decorator(func):
        command_register.append(Command(name, func, description))
        return func

    return decorator


@command("bonk", "Bonk a sucker on the head. Usage: ~bonk @username")
async def bonk(ctx: Context) -> MessageResponse | None:
    """
    'Bonk' a user.
    """
    bonk_messages = [
        "{} bonks {} on the head",
        "{} breaks {}'s kneecaps",
        "{} bonks {}'s head into the ground",
        "{} bonks {}'s head into the wall",
        "{} bonks {}'s head into the ceiling",
        "{} bonks {}'s head into the floor",
        "{} bonks {}'s head into the table",
        "{} bonks {}'s head into the chair",
        "{} bonks {}'s head into the door",
        "{} bonks {}'s head into the window",
        "{} bonks {}'s head into the computer",
        "{} bonks {} into the sun",
    ]

    if not ctx.first_mention:
        return None

    return MessageResponse(
        ctx.author,
        ctx,
        Message(
            content=random.choice(bonk_messages).format(
                ctx.message.author.display_name, ctx.first_mention.display_name
            ),
            author=None,
            type=MessageType.COMMAND,
        ),
    )


@command("help", "Get help. Usage: ~help")
async def help_command(ctx: Context) -> MessageResponse | None:
    """
    Displays all available commands and what they do.
    """
    content = "<br/>".join(
        f"{cmd.name} - {cmd.description}" for cmd in ctx.app.commands
    )

    return MessageResponse(
        ctx.message.author,
        ctx,
        Message(
            content=content,
            author=None,
            type=MessageType.COMMAND,
        ),
        is_ephemeral=True,
    )


@command("squiddy", "Send a squidward quote. Usage: ~squiddy @username")
async def squiddy(ctx: Context) -> MessageResponse | None:
    """
    Send a random squidward quote, I guess?
    """
    squid_mess = [
        "{from_user}: AUGUST 12th, 2036: THE HEAT DEATH OF THE UNIVERSE! "
        "{to}, YOUR RECKONING WILL BEFALL UPON YOU!",
        "What if I pop my bumhole out and let it dry in the sun, {to}?",
    ]
    if not ctx.first_mention:
        return None

    return MessageResponse(
        ctx.author,
        ctx,
        Message(
            content=random.choice(squid_mess).format(
                from_user=ctx.message.author.display_name,
                to=ctx.first_mention.display_name,
            ),
            author=None,
            type=MessageType.COMMAND,
        ),
    )


@command("kwispy", "Light a sucker on fire. Usage: ~kwispy @username")
async def kwispy(ctx: Context) -> MessageResponse | None:
    """
    Send a fire-based meme message.
    """
    kwispy_mess = [
        "{} sets {} on fire.",
        "{} sets {} alight with his magic butane blaster.",
        "{} introduces {} to the complex process of combustion.",
        "{} proceeds to melt {}'s face off.",
        "{} lights {} on fire with some good ol' fasioned matches.",
    ]
    if not ctx.first_mention:
        return None

    return MessageResponse(
        ctx.author,
        ctx,
        Message(
            content=random.choice(kwispy_mess).format(
                ctx.message.author.display_name, ctx.first_mention.display_name
            ),
            author=None,
            type=MessageType.COMMAND,
        ),
    )


@command("chirp", "Insult someone, I guess. Usage: ~chirp @username")
async def chirp(ctx: Context) -> MessageResponse | None:
    """
    I don't know what this command's name is a reference to. Insult someone, I guess?
    """
    chirpmess = [
        "Hey {}, why don't ya skate, ya pheasant!?",
        "Hey {}, I've seen better hands on a digital clock!",
    ]
    if not ctx.first_mention:
        return None

    return MessageResponse(
        ctx.author,
        ctx,
        Message(
            content=random.choice(chirpmess).format(ctx.first_mention.display_name),
            author=None,
            type=MessageType.COMMAND,
        ),
    )


@command("ban", "Ban a sucker. Usage: ~ban @username")
async def ban(ctx: Context) -> MessageResponse | None:
    """
    Ban a user from the chat.
    """
    # Can't ban a sucker if there's no sucker to ban
    if not ctx.first_mention:
        return None

    # Can't ban a sucker if you don't have permissions to do so
    if not ctx.message.author.permissions & Permissions.BAN:
        return MessageResponse(
            ctx.author,
            ctx,
            Message(
                content="You don't have permission to ban users.",
                author=None,
                type=MessageType.ERROR,
            ),
            is_ephemeral=True,
        )

    # Setting the permissions to 0 will prevent the user from doing anything
    ctx.first_mention.permissions = Permissions(0)
    await ctx.first_mention.update()

    return MessageResponse(
        ctx.author,
        ctx,
        Message(
            content=f"{ctx.first_mention.username} ({ctx.first_mention.display_name}) has been banned.",
            author=None,
            type=MessageType.COMMAND,
        ),
    )
