import random
from io import BytesIO

from aiohttp import ClientSession
from discord import File, Member
from discord.commands import Option, slash_command
from discord.ext.commands import Cog
from PIL import Image


class Trash(Cog):

    def __init__(self, bot):
        self.bot = bot

    @slash_command(description="Slap someone")
    async def slap(self, ctx, member:Option(Member,"Member to slap")):
        async with ClientSession() as session:
            async with session.get("https://content.techgig.com/photo/87663756.cms") as response:
                slap_img = Image.open(BytesIO(await response.read()))
            async with session.get(ctx.author.avatar.url) as response:
                user1_avt = Image.open(BytesIO(await response.read())).resize((150,150), Image.NEAREST)
            async with session.get(member.avatar.url) as response:
                user2_avt = Image.open(BytesIO(await response.read())).resize((150,150), Image.NEAREST)
        slap_img.paste(user1_avt, (500,50))
        slap_img.paste(user2_avt, (225,200))
        with BytesIO() as slap_img_bin:
            slap_img.save(slap_img_bin, "PNG")
            slap_img_bin.seek(0)
            await ctx.respond(file=File(slap_img_bin, "img.png"))

    @slash_command(description="Steal someone avatar")
    async def steal(self, ctx, member:Option(Member,"Member to steal")):
        await ctx.respond(member.avatar.url)

    @slash_command(description="Pick among option1/option2/etc...")
    async def pick(
        self,
        ctx,
        options: Option(str, description="Options to pick, divide by /"),
        ping: Option(Member, description="Member to ping", required=False, default=None),
    ):
        await ctx.respond(f"Bố m chọn {random.choice(options.split('/'))} {ping.mention if ping else ''}")
