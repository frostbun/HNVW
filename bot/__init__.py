import os

from discord import Activity, ActivityType, Intents
from discord.ext.commands import Bot, when_mentioned_or

from .cogs import *
from .components import Embed

COMMAND_PREFIX = "$"

bot = Bot(
    command_prefix = when_mentioned_or(COMMAND_PREFIX),
    activity = Activity(
        type = ActivityType.listening,
        name = f"{COMMAND_PREFIX}help",
    ),
    intents = Intents.all(),
    strip_after_prefix = True,
)
bot.add_cog(Music(bot))
bot.add_cog(Game(bot))

@bot.check
async def no_dm(ctx):
    return ctx.guild or str(ctx.author.id) == os.environ["OWNER"]

@bot.command(brief="Check bot presence")
async def ping(ctx):
    await ctx.send(
        embed = Embed(
            title = "Pong 🏓",
            desc = f"I'm alive\n`{bot.latency*1000:.2f}ms`",
            footer_text = bot.user,
            thumbnail = bot.user.avatar.url
        )
    )
