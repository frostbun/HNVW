from discord_component import Button, ButtonStyle, InteractionCallback, View


class TicTacToe:

    EMOJIS = ( "❌", "⭕", "🔳" )
    WIN_COMBINATIONS = ( (0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6) )
    TIMEOUT = 180

    def __init__(self, ctx, other):
        self.ctx = ctx
        self.bot = ctx.bot
        self.users = ( ctx.author, other )

    async def btn_check(self, interaction) -> bool:
        if interaction.user != self.users[self.turn]:
            await interaction.response.send_message(
                content = "It's not yours",
                ephemeral = True,
                delete_after = 10,
            )
            return False
        return True

    async def btn_callback(self, index):
        async def status_check():
            marks = [ i for i, status in enumerate(self.board) if status == self.turn ]
            for comb in self.WIN_COMBINATIONS:
                if all(mark in marks for mark in comb):
                    return comb
            return -1 in self.board
        
        self.board[index] = self.turn
        status = await status_check()
        if status is True:
            await self.send_board_embed()
        elif status is False:
            await self.send_draw_embed()
        else:
            await self.send_win_embed(status)

    async def start(self):
        self.board = [-1] * 9
        self.turn = 1
        self.title = f"{self.users[0].display_name} vs. {self.users[1].display_name}"
        await self.ctx.send(
            f"{self.users[0].display_name} challenges {self.users[1].mention} to a tic-tac-toe game!",
            view = View(
                Button(
                    label = "Reject",
                    style = ButtonStyle.red,
                ),
                Button(
                    label = "Accept",
                    style = ButtonStyle.green,
                    callbacks = (InteractionCallback(self.send_board_embed), ),
                ),
                checks = (InteractionCallback(self.btn_check), ),
            ),
            delete_after = self.TIMEOUT
        )

    async def send_board_embed(self):
        self.turn = (self.turn+1) % 2
        await self.ctx.send(
            f"{self.title}\n{self.users[self.turn].mention} turn!",
            view = View(
                *[ Button(
                    emoji = self.EMOJIS[mark],
                    style = ButtonStyle.blurple if mark != -1 else ButtonStyle.gray,
                    disabled = mark != -1,
                    row = i//3,
                    callbacks = (
                        InteractionCallback(
                            func = self.btn_callback,
                            index = i,
                        ),
                    ),
                ) for i, mark in enumerate(self.board) ],
                checks = (InteractionCallback(self.btn_check), ),
            ),
            delete_after = self.TIMEOUT
        )

    async def send_draw_embed(self):
        await self.ctx.send(
            f"{self.title}\nDraw!",
            view = View(
                *[ Button(
                    emoji = self.EMOJIS[mark],
                    style = ButtonStyle.blurple,
                    disabled = True,
                    row = i//3,
                ) for i, mark in enumerate(self.board) ],
            ),
        )

    async def send_win_embed(self, comb):
        await self.ctx.send(
            f"{self.title}\n{self.users[self.turn].mention} win!",
            view = View(
                *[ Button(
                    emoji = self.EMOJIS[mark],
                    style = ButtonStyle.green if i in comb else ButtonStyle.blurple if mark != -1 else ButtonStyle.gray,
                    disabled = True,
                    row = i//3,
                ) for i, mark in enumerate(self.board) ],
            ),
        )
