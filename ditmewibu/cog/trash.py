import asyncio
import random
from io import BytesIO

from aiohttp import ClientSession
from discord import ApplicationContext, File, Member
from discord.commands import Option, slash_command
from discord.ext.commands import Cog
from PIL import Image


class Trash(Cog):

    def __init__(self, bot):
        self.bot = bot

    @slash_command(description="Slap someone")
    async def slap(self, ctx, member: Option(Member, "Member to slap")):  # type: ignore
        await self.send_image(
            ctx,
            "https://content.techgig.com/photo/87663756.cms",
            ctx.author,
            member,
            (150, 150),
            (500, 50),
            (225, 200),
        )

    @slash_command(description="Kiss someone")
    async def kiss(self, ctx, member: Option(Member, "Member to kiss")):  # type: ignore
        await self.send_image(
            ctx,
            "https://content.imageresizer.com/images/memes/2-gay-black-mens-kissing-meme-1hnv2v.jpg",
            ctx.author,
            member,
            (100, 100),
            (100, 100),
            (350, 150),
        )

    async def send_image(
        self,
        ctx: ApplicationContext,
        url: str,
        member0: Member,
        member1: Member,
        avatar_size: tuple[int, int],
        position0: tuple[int, int],
        position1: tuple[int, int],
    ) -> None:
        async with ClientSession() as session:

            async def get_image(url: str):
                async with session.get(url) as response:
                    return Image.open(BytesIO(await response.read()))

            img, avatar0, avatar1 = await asyncio.gather(
                get_image(url),
                get_image(member0.avatar.url),
                get_image(member1.avatar.url),
            )

        img.paste(avatar0.resize(avatar_size, Image.NEAREST), position0)
        img.paste(avatar1.resize(avatar_size, Image.NEAREST), position1)

        with BytesIO() as bin:
            img.save(bin, "PNG")
            bin.seek(0)
            await ctx.respond(file=File(bin, "img.png"))

    @slash_command(description="Steal someone avatar")
    async def steal(self, ctx, member: Option(Member, "Member to steal")):  # type: ignore
        await ctx.respond(member.avatar.url)

    @slash_command(description="Pick among option1/option2/etc...")
    async def pick(
        self,
        ctx,
        options: Option(str, description="Options to pick, divide by /"),  # type: ignore
        ping: Option(
            Member, description="Member to ping", required=False, default=None
        ),  # type: ignore
    ):
        await ctx.respond(
            f"Bố m chọn {random.choice(options.split('/'))} {ping.mention if ping else ''}"
        )
