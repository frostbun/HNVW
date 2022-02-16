from sqlite3 import connect

from ..models.song import Song
from ..components import View, Button, Select, ButtonStyle, SelectOption
from ..utils.formatter import format_duration
from ..utils.extractor import extract_all_or_search

from . import DATABASE
TABLE = "user_playlist_table"

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

class UserPlaylist:

    TIMEOUT = 60

    def __init__(self, ctx):
        self.ctx = ctx
        self.bot = ctx.bot
        self.user = ctx.author

    # database ====================================================================================
    async def fetch_one(self, id):
        with connect(DATABASE) as conn:
            return Song(
                *conn.cursor().execute(
                    f"""SELECT title, duration, thumbnail, url 
                        FROM {TABLE} 
                        WHERE user_id=? 
                        AND id=? 
                    """,
                    (self.user.id, id)
                ).fetchone()
            )

    async def fetch_size(self):
        with connect(DATABASE) as conn:
            return conn.cursor().execute(
                f"""SELECT COUNT(id) 
                    FROM {TABLE} 
                    WHERE user_id=? 
                """,
                (self.user.id, )
            ).fetchone()[0]

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
                    (self.user.id, )
                ).fetchall()
            ]

    async def insert(self):
        with connect(DATABASE) as conn:
            conn.execute(
                f"""INSERT INTO {TABLE} (user_id, title, duration, thumbnail, url) 
                    VALUES (?, ?, ?, ?, ?) 
                """,
                (
                    self.user.id,
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

    # embed =======================================================================================
    async def author_check(self, i):
        if self.user != i.user:
            await i.response.send_message(
                content = "It's not yours",
                ephemeral = True,
                delete_after = 10,
            )
            return False
        return True

    def search(self, url):
        self.last_search = extract_all_or_search(url)[1]
        self.bot.loop.create_task(self.send_prompt_embed())

    async def send_prompt_embed(self):
        await self.ctx.send(
            embed = self.last_search.get_embed("Add to your playlist?"),
            view = View(
                Button(
                    label = "Cancel",
                    style = ButtonStyle.red,
                ),
                Button(
                    label = "Save",
                    style = ButtonStyle.green,
                    callback = [ self.insert ],
                ),
                check = [ self.author_check ],
            ),
            delete_after = UserPlaylist.TIMEOUT,
        )

    async def send_playlist_embed(self, page):
        size = await self.fetch_size()
        await self.ctx.send(
            "**Choose a song to play:**",
            view = View(
                Select(
                    placeholder = "Song goes here",
                    options = [
                        SelectOption(
                            label = song.title,
                            description = format_duration(song.duration),
                            value = song.initial_url,
                        ) for id, song in await self.fetch(page)
                    ],
                    callback = [ self.bot.get_command("play") ],
                    default_param_name = "url",
                    default_param_type = str,
                    params = {"context": self.ctx},
                ),
                Button(
                    label = "Cancel",
                    style = ButtonStyle.red,
                ),
                Button(
                    label = "Previous",
                    style = ButtonStyle.gray if page<=1 else ButtonStyle.green,
                    disabled = page<=1,
                    callback = [ self.send_playlist_embed ],
                    params = {"page": page-1},
                ),
                Button(
                    label = "Next",
                    style = ButtonStyle.gray if page>=(size+9)//10 else ButtonStyle.green,
                    disabled = page>=(size+9)//10,
                    callback = [ self.send_playlist_embed ],
                    params = {"page": page+1},
                ),
                check = [ self.author_check ],
            ),
            delete_after = UserPlaylist.TIMEOUT,
        )

    async def send_remove_playlist_embed(self, page):
        size = await self.fetch_size()
        await self.ctx.send(
            "**Choose a song to remove:**",
            view = View(
                Select(
                    placeholder = "Song goes here",
                    options = [
                        SelectOption(
                            label = song.title,
                            description = format_duration(song.duration),
                            value = id,
                        ) for id, song in await self.fetch(page)
                    ],
                    callback = [ self.remove ],
                    default_param_name = "id",
                ),
                Button(
                    label = "Cancel",
                    style = ButtonStyle.red,
                ),
                Button(
                    label = "Previous",
                    style = ButtonStyle.gray if page<=1 else ButtonStyle.green,
                    disabled = page<=1,
                    callback = [ self.send_remove_playlist_embed ],
                    params = {"page": page-1},
                ),
                Button(
                    label = "Next",
                    style = ButtonStyle.gray if page>=(size+9)//10 else ButtonStyle.green,
                    disabled = page>=(size+9)//10,
                    callback = [ self.send_remove_playlist_embed ],
                    params = {"page": page+1},
                ),
                check = [ self.author_check ],
            ),
            delete_after = UserPlaylist.TIMEOUT,
        )
