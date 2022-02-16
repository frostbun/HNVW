from ..components import View, Button, ButtonStyle

class TicTacToe:

    EMOJI = ( "❌", "⭕", "🔳" )
    WIN = ( (0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6) )
    TIMEOUT = 180

    def __init__(self, ctx, other):
        self.ctx = ctx
        self.bot = ctx.bot
        self.users = ( ctx.author, other )

    async def status_check(self):
        marks = [ i for i, status in enumerate(self.status) if status == self.turn ]
        for win in TicTacToe.WIN:
            if all(w in marks for w in win):
                return win
        return -1 in self.status

    async def btn_check(self, i):
        if i.user != self.users[self.turn]:
            await i.response.send_message(
                content = "It's not yours",
                ephemeral = True,
                delete_after = 10,
            )
            return False
        return True

    async def btn_callback(self, index):
        self.status[index] = self.turn
        status = await self.status_check()
        if status is True:
            await self.send_board_embed()
        elif status is False:
            await self.send_draw_embed()
        else:
            await self.send_win_embed(status)

    async def start(self):
        self.status = [-1] * 9
        self.turn = 1
        self.title = f"{self.users[0].display_name} vs. {self.users[1].mention}"
        await self.ctx.respond(
            f"{self.users[0].display_name} challenges {self.users[1].mention} to a tic-tac-toe game!",
            view = View(
                Button(
                    label = "Reject",
                    style = ButtonStyle.red,
                ),
                Button(
                    label = "Accept",
                    style = ButtonStyle.green,
                    callback = [ self.send_board_embed ],
                ),
                check = [ self.btn_check ],
            ),
            delete_after = TicTacToe.TIMEOUT
        )

    async def send_board_embed(self):
        self.turn = (self.turn+1) % 2
        await self.ctx.send(
            f"{self.title}\n{self.users[self.turn].mention} turn!",
            view = View(
                *[ Button(
                    emoji = TicTacToe.EMOJI[self.status[i]],
                    style = ButtonStyle.blurple if self.status[i] != -1 else ButtonStyle.gray,
                    disabled = self.status[i] != -1,
                    row = i//3,
                    callback = [ self.btn_callback ],
                    params = {"index": i},
                ) for i in range(9) ],
                check = [ self.btn_check ],
            ),
            delete_after = TicTacToe.TIMEOUT
        )

    async def send_draw_embed(self):
        await self.ctx.send(
            f"{self.title}\nDraw!",
            view = View(
                *[ Button(
                    emoji = TicTacToe.EMOJI[self.status[i]],
                    style = ButtonStyle.blurple,
                    disabled = True,
                    row = i//3,
                ) for i in range(9) ],
            ),
            # delete_after = TicTacToe.TIMEOUT
        )

    async def send_win_embed(self, marks):
        await self.ctx.send(
            f"{self.title}\n{self.users[self.turn].mention} win!",
            view = View(
                *[ Button(
                    emoji = TicTacToe.EMOJI[self.status[i]],
                    style = ButtonStyle.green if i in marks else ButtonStyle.blurple if self.status[i] != -1 else ButtonStyle.gray,
                    disabled = True,
                    row = i//3,
                ) for i in range(9) ],
            ),
            # delete_after = TicTacToe.TIMEOUT
        )
