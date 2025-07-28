from discord import Member
from discord.commands import Option, slash_command
from discord.ext.commands import Cog

from .tictactoe import TicTacToe


class Game(Cog):

    def __init__(self, bot):
        self.bot = bot

    @slash_command(description="Challenge a member to a tic-tac-toe game")
    async def tictactoe(self, ctx, member: Option(Member, "Recipient")):
        await TicTacToe(ctx, member).start()
