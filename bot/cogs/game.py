from discord import User
from discord.ext.commands import Cog, command

from ..models import TicTacToe

class Game(Cog):

    def __init__(self, bot):
        self.bot = bot

    @command()
    async def tictactoe(self, ctx, user:User):
        await TicTacToe(self.bot, ctx, ctx.author, user).start()
