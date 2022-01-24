from discord import Activity, ActivityType
from discord.ext.commands import Bot, when_mentioned_or

from .cogs import *

COMMAND_PREFIX = "$"

bot = Bot(
    command_prefix = when_mentioned_or(COMMAND_PREFIX),
    activity = Activity(
        type = ActivityType.listening,
        name = f"{COMMAND_PREFIX}help",
    ),
    strip_after_prefix = True,
)
bot.add_cog(Music(bot))
bot.add_cog(Game(bot))
