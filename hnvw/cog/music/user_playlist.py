from discord_component import (Button, ButtonStyle, Embed, InteractionCallback,
                               Select, SelectOption, View)

from ...model import Song, connect_db
from ...util.extractor import extract_all_or_search
from ...util.formatter import format_duration

TABLE = "user_playlist_table"

# schema
with connect_db() as conn:
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
    PAGE_SIZE = 10

    def __init__(self, ctx):
        self.ctx = ctx
        self.bot = ctx.bot
        self.user = ctx.author

    # database ====================================================================================
    async def fetch_one(self, id: int) -> Song:
        with connect_db() as conn:
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

    async def fetch_size(self) -> int:
        with connect_db() as conn:
            return conn.cursor().execute(
                f"""SELECT COUNT(id) 
                    FROM {TABLE} 
                    WHERE user_id=? 
                """,
                (self.user.id, )
            ).fetchone()[0]

    async def fetch(self, page: int = 1) -> list[tuple[int, Song]]:
        with connect_db() as conn:
            return [
                (data[0], Song(*data[1:])) for data in conn.cursor().execute(
                    f"""SELECT id, title, duration, thumbnail, url 
                        FROM {TABLE} 
                        WHERE user_id=? 
                        LIMIT {self.PAGE_SIZE} 
                        OFFSET {self.PAGE_SIZE*(page-1)}
                    """,
                    (self.user.id, )
                ).fetchall()
            ]

    async def insert(self):
        with connect_db() as conn:
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
        await self.ctx.send(embed = self.last_search.get_embed("Your song was saved"))

    async def remove(self, id: int):
        song = await self.fetch_one(id)
        with connect_db() as conn:
            conn.execute(f"DELETE FROM {TABLE} WHERE id=?", (id, ))
        await self.ctx.send(embed = song.get_embed("Your song was removed"))

    # embed =======================================================================================
    async def author_check(self, interaction) -> bool:
        if self.user != interaction.user:
            await interaction.response.send_message(
                content = "It's not yours",
                ephemeral = True,
                delete_after = 10,
            )
            return False
        return True

    async def search(self, url: str):
        self.last_search = await extract_all_or_search(url)[0]
        await self.send_prompt_embed()

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
                    callbacks = (InteractionCallback(self.insert), ),
                ),
                checks = (InteractionCallback(self.author_check), ),
            ),
            delete_after = self.TIMEOUT,
        )

    async def send_empty_playlist_embed(self):
        await self.ctx.send(
            embed = Embed(
                title = "Opsss...",
                desc = "Your playlist is empty",
                footer_text = self.user,
                thumbnail = self.user.avatar.url
            ),
            delete_after = 10,
        )

    async def send_playlist_embed(self, page: int):
        last_page = (await self.fetch_size()+self.PAGE_SIZE-1)//self.PAGE_SIZE
        if page < 1 or page > last_page:
            await self.send_empty_playlist_embed()
            return
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
                    callbacks = (
                        InteractionCallback(
                            func = self.bot.get_command("play"),
                            default_arg_name = "url",
                            default_arg_type = str,
                            context = self.ctx,
                        ),
                    ),
                ),
                Button(
                    label = "Cancel",
                    style = ButtonStyle.red,
                ),
                Button(
                    label = "Previous",
                    style = ButtonStyle.gray if page<=1 else ButtonStyle.green,
                    disabled = page<=1,
                    callbacks = (
                        InteractionCallback(
                            func = self.send_playlist_embed,
                            page = page-1,
                        ),
                    ),
                ),
                Button(
                    label = "Next",
                    style = ButtonStyle.gray if page>=last_page else ButtonStyle.green,
                    disabled = page>=last_page,
                    callbacks = (
                        InteractionCallback(
                            func = self.send_playlist_embed,
                            page = page+1,
                        ),
                    ),
                ),
                checks = (InteractionCallback(self.author_check), ),
            ),
            delete_after = self.TIMEOUT,
        )

    async def send_remove_playlist_embed(self, page: int):
        last_page = (await self.fetch_size()+self.PAGE_SIZE-1)//self.PAGE_SIZE
        if page < 1 or page > last_page:
            await self.send_empty_playlist_embed()
            return
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
                    callbacks = (
                        InteractionCallback(
                            func = self.remove,
                            default_arg_name = "id",
                            default_arg_type = int,
                        ),
                    ),
                ),
                Button(
                    label = "Cancel",
                    style = ButtonStyle.red,
                ),
                Button(
                    label = "Previous",
                    style = ButtonStyle.gray if page<=1 else ButtonStyle.green,
                    disabled = page<=1,
                    callbacks = (
                        InteractionCallback(
                            func = self.send_remove_playlist_embed,
                            page = page-1,
                        ),
                    ),
                ),
                Button(
                    label = "Next",
                    style = ButtonStyle.gray if page>=last_page else ButtonStyle.green,
                    disabled = page>=last_page,
                    callbacks = (
                        InteractionCallback(
                            func = self.send_remove_playlist_embed,
                            page = page+1,
                        ),
                    ),
                ),
                checks = (InteractionCallback(self.author_check), ),
            ),
            delete_after = self.TIMEOUT,
        )
