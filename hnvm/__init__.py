from os import getenv

from discord_bot.common import create_bot
from dotenv import load_dotenv

from .cog import *


def run():
    load_dotenv()
    COMMAND_PREFIX = getenv("COMMAND_PREFIX")
    TOKEN = getenv("TOKEN")

    if COMMAND_PREFIX is None or TOKEN is None:
        raise ValueError("Missing environment variables")

    bot = create_bot(COMMAND_PREFIX)
    bot.add_cog(Game(bot))
    bot.add_cog(Music(bot))
    bot.run(TOKEN)
