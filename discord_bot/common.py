from discord import Activity, ActivityType, DiscordException, Intents
from discord.ext.commands import Bot, when_mentioned_or
from discord.ext.commands.errors import MissingPermissions
from discord_component import Embed


def create_bot(command_prefix):
    bot = Bot(
        command_prefix = when_mentioned_or(command_prefix),
        activity = Activity(
            type = ActivityType.listening,
            name = f"{command_prefix}help",
        ),
        intents = Intents.all(),
        strip_after_prefix = True,
    )

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

    return bot
