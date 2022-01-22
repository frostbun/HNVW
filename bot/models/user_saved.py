from sqlite3 import connect
from time import time

from ..models.song import Song
from ..components import View, Button, Select, ButtonStyle, SelectOption
from ..utils.formatter import format_duration
from ..utils.extractor import extract_all_or_search

from configs import DATABASE
TABLE = "user_saved_table"

# schema
with connect(DATABASE) as conn:
    conn.execute(
        f"""CREATE TABLE IF NOT EXISTS {TABLE} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL,
            duration INTEGER NOT NULL,
            thumbnail TEXT NOT NULL,
            url TEXT NOT NULL
        )"""
    )

class UserSaved:

    def __init__(self, bot, ctx, id:str):
        self.bot = bot
        self.ctx = ctx
        self.id = id
        self.last_active = time()

    # check =======================================================================================
    async def check_ctx(self, ctx):
        self.last_active = time()
        # user change channel
        if self.ctx.channel != ctx.channel:
            self.ctx = ctx

    async def check_author(self, i):
        if self.id != i.user.id:
            await i.response.send_message(
                content = "It's not yours",
                ephemeral = True,
                delete_after = 10,
            )
            return False
        return True

    # database ====================================================================================
    async def fetch_one(self, id):
        with connect(DATABASE) as conn:
            return Song(
                conn.cursor().execute(
                    f"""SELECT title, duration, thumbnail, url 
                        FROM {TABLE} 
                        WHERE user_id=? 
                        AND id=? 
                    """,
                    (self.id, id)
                ).fetchone()
            )

    async def fetch(self, page):
        with connect(DATABASE) as conn:
            return [
                (data[0], Song(*data[1:])) for data in conn.cursor().execute(
                    f"""SELECT id, title, duration, thumbnail, url 
                        FROM {TABLE} 
                        WHERE user_id=? 
                        LIMIT 10 
                        OFFSET {10*(page-1)}
                    """,
                    (self.id, )
                ).fetchall()
            ]

    async def insert(self):
        with connect(DATABASE) as conn:
            conn.execute(
                f"""INSERT INTO {TABLE} (user_id, title, duration, thumbnail, url) 
                    VALUES (?, ?, ?, ?, ?) 
                """,
                (
                    self.id,
                    self.last_search.title,
                    self.last_search.duration,
                    self.last_search.thumbnail,
                    self.last_search.initial_url,
                )
            )
            conn.commit()
        await self.ctx.send(embed=self.last_search.get_embed("Your song was saved"))

    async def remove(self, id):
        song = await self.fetch_one(id)
        with connect(DATABASE) as conn:
            conn.execute(f"DELETE FROM {TABLE} WHERE id=?", (id, ))
            conn.commit()
        await self.ctx.send(embed=song.get_embed("Your song was removed"))

    def search(self, url):
        self.last_search = extract_all_or_search(url)[1]
        self.bot.loop.create_task(self.send_prompt_embed())

    # embed =======================================================================================
    async def send_prompt_embed(self):
        # delete old promt
        try:
            await self.last_promt.delete()
        except:
            pass
        # send new one
        self.last_promt = await self.ctx.send(
            embed = self.last_search.get_embed("Add to your playlist?"),
            view = View(
                Button(
                    label = "Cancel",
                    style = ButtonStyle.red,
                    check = [ self.check_author ],
                ),
                Button(
                    label = "Save",
                    style = ButtonStyle.green,
                    callback = [ self.insert ],
                    check = [ self.check_author ],
                ),
            )
        )

    async def send_playlist_embed(self, page):
        try:
            await self.last_playlist_message.delete()
        except:
            pass
        self.last_playlist_message = await self.ctx.send(
            "**Choose a song to play:**",
            view = View(
                Select(
                    placeholder = "Song goes here",
                    options = [
                        SelectOption(
                            label = song.title,
                            description = format_duration(song.duration),
                            value = song.initial_url,
                        ) for id, song in self.fetch(page)
                    ],
                    callback = [ self.bot.get_command("play") ],
                    check = [ self.check_author ],
                    default_param_name = "url",
                    ctx = self.ctx
                ),
                Button(
                    label = "Cancel",
                    style = ButtonStyle.red,
                    check = [ self.check_author ],
                ),
                Button(
                    label = "Previous",
                    style = ButtonStyle.gray if page<=1 else ButtonStyle.green,
                    disabled = page<=1,
                    callback = [ self.send_playlist_embed ],
                    check = [ self.check_author ],
                    page = page-1,
                ),
                Button(
                    label = "Next",
                    style = ButtonStyle.gray if page>=(len(self.saved)+9)//10 else ButtonStyle.green,
                    disabled = page>=(len(self.saved)+9)//10,
                    callback = [ self.send_playlist_embed ],
                    check = [ self.check_author ],
                    page = page+1,
                ),
            )
        )

    async def send_remove_playlist_embed(self, page):
        try:
            await self.last_remove_playlist_message.delete()
        except:
            pass
        self.last_remove_playlist_message = await self.ctx.send(
            "**Choose a song to remove:**",
            view = View(
                Select(
                    placeholder = "Song goes here",
                    options = [
                        SelectOption(
                            label = song.title,
                            description = format_duration(song.duration),
                            value = id,
                        ) for id, song in self.fetch(page)
                    ],
                    callback = [ self.remove ],
                    check = [ self.check_author ],
                    default_param_name = "id",
                ),
                Button(
                    label = "Cancel",
                    style = ButtonStyle.red,
                    check = [ self.check_author ],
                ),
                Button(
                    label = "Previous",
                    style = ButtonStyle.gray if page<=1 else ButtonStyle.green,
                    disabled = page<=1,
                    callback = [ self.send_remove_playlist_embed ],
                    check = [ self.check_author ],
                    page = page-1,
                ),
                Button(
                    label = "Next",
                    style = ButtonStyle.gray if page>=(len(self.saved)+9)//10 else ButtonStyle.green,
                    disabled = page>=(len(self.saved)+9)//10,
                    callback = [ self.send_remove_playlist_embed ],
                    check = [ self.check_author ],
                    page = page+1,
                ),
            )
        )

    # stop ========================================================================================
    async def stop(self):
        await self.delete_all_message()

    async def delete_all_message(self):
        # delete last prompt
        try:
            await self.last_promt.delete()
        except:
            pass
        # delete last playlist message
        try:
            await self.last_playlist_message.delete()
        except:
            pass
        # delete last remove playlist message
        try:
            await self.last_remove_playlist_message.delete()
        except:
            pass
