from discord import Activity, ActivityType
from discord.ext.commands import Bot, when_mentioned_or

from .cogs import *

from configs import COMMAND_PREFIX

bot = Bot(when_mentioned_or(COMMAND_PREFIX))
bot.add_cog(MusicCog(bot))

@bot.event
async def on_ready():
    await bot.change_presence(activity=Activity(type=ActivityType.listening, name=f"{COMMAND_PREFIX}help"))
    print(bot.user)
