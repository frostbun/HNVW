from discord import AllowedMentions, Member, Role
from discord.commands import Option, slash_command
from discord.ext.commands import Cog

from ..util.van_mau import get_van_mau


class VanMau(Cog):

    def __init__(self, bot):
        self.bot = bot

    @slash_command(description="Văn mẫu")
    async def ditmemay(self, ctx, member: Option(Member, "Thằng mày muốn chửi")):
        await ctx.respond(f"Địt mẹ {member.mention}")
        await self.send(ctx, member)

    @slash_command(description="Văn mẫu")
    async def ditcahonhamay(self, ctx, role: Option(Role, "Role mày muốn chửi")):
        await ctx.respond(f"Địt mẹ {role.mention}")
        for member in role.members:
            await self.send(ctx, member)

    @slash_command(description="Văn mẫu")
    async def ditkongungnghi(self, ctx):
        await ctx.respond(
            f"Địt mẹ @everyone", allowed_mentions=AllowedMentions(everyone=True)
        )
        for member in ctx.guild.members:
            await self.send(ctx, member)

    async def send(self, ctx, member):
        van_mau = f"Địt mẹ {member.mention}. {get_van_mau()}"
        for i in range((len(van_mau) + 1999) // 2000):
            await ctx.send(van_mau[i * 2000 : (i + 1) * 2000])
