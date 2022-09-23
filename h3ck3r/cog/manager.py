from discord import Member
from discord.commands import Option, slash_command
from discord.ext.commands import Cog, bot_has_permissions, has_permissions


class Manager(Cog):

    def __init__(self, bot):
        self.bot = bot

    @slash_command(description="Kick a member")
    async def kick(self, ctx, member:Option(Member,description="Member to kick")):
        pass

    @slash_command(description="Ban a member")
    async def ban(self, ctx, member:Option(Member,description="Member to ban")):
        pass

    @slash_command(description="Unban a user")
    async def un_ban(self, ctx, user_id:Option(str,description="User ID to unban")):
        pass

    @slash_command(description="Delete message(s) in this channel")
    @has_permissions(manage_messages=True, read_message_history=True)
    @bot_has_permissions(manage_messages=True, read_message_history=True)
    async def clear(self, ctx, limit:Option(int,description="Limit")):
        await ctx.respond(
            f"Deleted {len(await ctx.channel.purge(limit=limit))} message(s)!",
            delete_after = 30,
        )
