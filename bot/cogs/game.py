from discord import Member
from discord.ext.commands import Cog, command

from ..models import TicTacToe

class Game(Cog):

    def __init__(self, bot):
        self.bot = bot

    @command(brief="Challenge a member to a tic-tac-toe game")
    async def tictactoe(self, ctx, member: Member):
        await TicTacToe(ctx, member).start()
