import discord

from configs import EMBED_COLOR

class Embed(discord.Embed):
    def __init__(self, title, desc, footer=None, thumbnail=None, color=EMBED_COLOR):
        super().__init__(
            title = title,
            description = desc,
            color = color,
        )
        if footer:
            self.set_footer(text=footer)
        if thumbnail:
            self.set_thumbnail(url=thumbnail)
