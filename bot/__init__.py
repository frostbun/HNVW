from discord import Activity, ActivityType, Intents, DiscordException
from discord.ext.commands import Bot, when_mentioned_or
from discord.ext.commands.errors import MissingPermissions

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
bot.add_cog(Game(bot))
bot.add_cog(Music(bot))

@bot.check
async def no_dm(ctx):
    return ctx.guild or await bot.is_owner(ctx.author)

@bot.check
async def no_self_response(ctx):
    return ctx.author != bot.user

@bot.event
async def on_application_command_error(ctx, e: DiscordException):
    if isinstance(e, MissingPermissions):
        await ctx.response.send_message(
            content = e,
            ephemeral = True,
            delete_after = 10,
        )

@bot.command(brief="Pong")
async def ping(ctx):
    await ctx.send(
        embed = Embed(
            title = "Pong 🏓",
            desc = f"I'm alive\n`{bot.latency*1000:.2f}ms`",
            footer_text = bot.user,
            thumbnail = bot.user.avatar.url
        )
    )
