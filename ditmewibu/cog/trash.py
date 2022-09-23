from io import BytesIO
from random import choice

from discord import File, Member
from discord.commands import Option, slash_command
from discord.ext.commands import Cog
from PIL import Image
from requests import get


class Trash(Cog):

    def __init__(self, bot):
        self.bot = bot

    @slash_command(description="Slap someone")
    async def slap(self, ctx, member:Option(Member,"Member to slap")):
        slap_img = Image.open(BytesIO(get("https://content.techgig.com/photo/87663756.cms").content))
        user1_avt = Image.open(BytesIO(get(ctx.author.avatar.url).content)).resize((150,150), Image.NEAREST)
        user2_avt = Image.open(BytesIO(get(member.avatar.url).content)).resize((150,150), Image.NEAREST)
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
        await ctx.respond(f"Bố m chọn {choice(options.split('/'))} {ping.mention if ping else ''}")
