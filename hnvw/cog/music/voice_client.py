from asyncio import sleep
from random import shuffle as rand
from typing import Any

from discord import FFmpegOpusAudio
from discord_component import (Button, ButtonStyle, Embed, InteractionCallback,
                               Select, SelectOption, View)

from ...util.extractor import (extract_all_or_search, extract_one,
                               youtube_search)
from ...util.formatter import format_duration
from ...util.validator import check_url


class VoiceClient:

    TIMEOUT = 60
    PAGE_SIZE = 10
    FFMPEG_OPTIONS = {"bitrate": 128, "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", "options": "-vn"}

    instances: dict[Any, "VoiceClient"] = {}

    def __init__(self, ctx):
        self.ctx = ctx
        self.bot = ctx.bot
        self.guild = ctx.guild

    async def enqueue(self, url: str):
        try:
            song, songs = await extract_all_or_search(url)
            self.queue += songs
            await self.ctx.send(embed=song.get_embed("Added to queue"))
            if not self.voice_client.is_playing():
                await self.dequeue()
        except Exception:
            await self.send_error_embed("Something went wrong while downloading your song")

    async def dequeue(self):
        # no more music, no loop
        if not self.queue and not self.loop:
            return await self.delete_last_np_message()
        # not playing or no loop => fetch new song
        if not self.playing or self.loop != 1:
            if self.loop == 2 and self.playing:
                self.queue.append(self.playing)
            self.playing = self.queue.pop(0)
        # 403 forbidden => redownload
        while not await check_url(self.playing.play_url):
            self.playing = extract_one(self.playing.initial_url)
        # 200 ok
        self.voice_client.play(
            FFmpegOpusAudio(
                self.playing.play_url,
                **self.FFMPEG_OPTIONS
            ),
            after = lambda _: self.bot.loop.create_task(self.dequeue())
        )
        await self.send_np_embed()

    async def search(self, name: str):
        try:
            self.last_search = await youtube_search(name)
            await self.send_search_embed()
        except Exception:
            await self.send_error_embed("Something went wrong while downloading your song")

    async def select(self, index: int):
        song = self.last_search[index]
        self.queue.append(song)
        await self.ctx.send(embed = song.get_embed("Added to queue"))
        if not self.voice_client.is_playing():
            await self.dequeue()

    # embed =======================================================================================
    async def voice_channel_check(self, interaction) -> bool:
        if not interaction.user.voice or interaction.user.voice.channel != self.voice_client.channel:
            await interaction.response.send_message(
                content = "It's not yours",
                ephemeral = True,
                delete_after = 10,
            )
            return False
        return True

    async def delete_last_np_message(self):
        try:
            await self.last_np_message.delete()
        except Exception:
            pass

    async def send_np_embed(self):
        await self.delete_last_np_message()
        paused = self.voice_client.is_paused()
        self.last_np_message = await self.ctx.send(
            embed = self.playing.get_embed("Playing"),
            view = View(
                Button(
                    label = "Stop", 
                    style = ButtonStyle.red,
                    callbacks = (InteractionCallback(self.stop), ),
                ),
                Button(
                    label = "Resume" if paused else "Pause",
                    style = ButtonStyle.green if paused else ButtonStyle.gray,
                    callbacks = (InteractionCallback(self.resume if paused else self.pause), ),
                ),
                Button(
                    label = "Skip",
                    callbacks = (InteractionCallback(self.skip), ),
                ),
                Button(
                    label = ("Loop Off", "Loop One", "Loop All")[self.loop],
                    style = ButtonStyle.gray if not self.loop else ButtonStyle.green,
                    callbacks = (InteractionCallback(self.toggle_loop), ),
                ),
                Button(
                    label = "Queue",
                    style = ButtonStyle.blurple,
                    callbacks = (InteractionCallback(self.send_np_embed), InteractionCallback(self.send_queue_embed)),
                ),
                checks = (InteractionCallback(self.voice_channel_check), ),
            ),
        )

    async def send_queue_embed(self, page=1):
        last_page = (len(self.queue)+self.PAGE_SIZE-1)//self.PAGE_SIZE
        if page < 1 or page > last_page:
            await self.send_error_embed("Your queue is empty")
            return
        await self.ctx.send(
            embed = Embed(
                title = f"Page {page}/{last_page}",
                desc = "\n".join(
                    f"**[{i+1}. {song.title}]({song.initial_url})**"
                    for i, song in enumerate(
                        self.queue[
                            self.PAGE_SIZE*(page-1):
                            self.PAGE_SIZE*page
                        ],
                        self.PAGE_SIZE*(page-1)
                    )
                ),
                footer_text = f"Total duration: {format_duration(sum(song.duration for song in self.queue))}"
            ),
            view = View(
                Button(
                    label = "Previous",
                    style = ButtonStyle.gray if page<=1 else ButtonStyle.green,
                    disabled = page<=1,
                    callbacks = (
                        InteractionCallback(
                            func = self.send_queue_embed,
                            page = page-1,
                        ),
                    ),
                ),
                Button(
                    label = "Shuffle",
                    style = ButtonStyle.blurple,
                    callbacks = (InteractionCallback(self.shuffle), ),
                ),
                Button(
                    label = "Next",
                    style = ButtonStyle.gray if page>=last_page else ButtonStyle.green,
                    disabled = page>=last_page,
                    callbacks = (
                        InteractionCallback(
                            func = self.send_queue_embed,
                            page = page+1,
                        ),
                    ),
                ),
                checks = (InteractionCallback(self.voice_channel_check), ),
            ),
            delete_after = self.TIMEOUT,
        )

    async def send_search_embed(self):
        await self.ctx.send(
            "**Choose a song:**",
            view = View(
                Select(
                    placeholder = "Song goes here",
                    options = [
                        SelectOption(
                            label = song.title,
                            description = format_duration(song.duration),
                            value = i,
                        ) for i, song in enumerate(self.last_search)
                    ],
                    callbacks = (
                        InteractionCallback(
                            func = self.select,
                            default_arg_name = "index",
                            default_arg_type = int,
                        ),
                    ),
                ),
                Button(
                    label = "Cancel",
                    style = ButtonStyle.red,
                ),
                checks = (InteractionCallback(self.voice_channel_check), ),
            ),
            delete_after = self.TIMEOUT,
        )

    async def send_error_embed(self, desc):
        await self.ctx.send(
            embed = Embed(
                title = "Opsss...",
                desc = desc,
            ),
            delete_after = 10,
        )

    # control =====================================================================================
    async def toggle_loop(self):
        self.loop = (self.loop+1) % 3
        await self.send_np_embed()

    async def pause(self):
        if not self.voice_client.is_paused():
            self.voice_client.pause()
        await self.send_np_embed()

    async def resume(self):
        if self.voice_client.is_paused():
            self.voice_client.resume()
        await self.send_np_embed()

    async def skip(self, index: int = 0):
        if not index:
            if not self.voice_client.is_playing():
                return
            await self.ctx.send(embed=self.playing.get_embed("Skipped"))
            self.voice_client.stop()
        else:
            if not self.queue:
                return
            index = (index-1) % len(self.queue)
            await self.ctx.send(embed=self.queue.pop(index).get_embed("Skipped"))

    async def shuffle(self):
        rand(self.queue)
        await self.send_queue_embed()

    async def move(self, fr: int, to: int):
        if not self.queue:
            return
        fr = fr % len(self.queue)
        to = to % len(self.queue)
        self.queue.insert(to, self.queue.pop(fr))
        await self.send_queue_embed()

    # start/stop ==================================================================================
    async def start(self) -> bool:
        if self.guild in self.instances:
            return True
        if not self.ctx.author.voice:
            return False
        if self.guild.voice_client:
            await self.guild.voice_client.disconnect(force=True)
        self.voice_client = await self.ctx.author.voice.channel.connect()
        self.instances[self.guild] = self
        await self.ctx.send(
            embed = Embed(
                title = "Hello",
                desc = self.bot.user,
                thumbnail = self.bot.user.avatar.url
            )
        )
        self.queue = []
        self.loop = 0
        self.playing = None
        self.bot.loop.create_task(self.autostop())
        return True

    async def stop(self):
        self.queue = []
        self.loop = 0
        await self.delete_last_np_message()
        await self.voice_client.disconnect(force=True)
        del self.instances[self.guild]
        await self.ctx.send(
            embed = Embed(
                title = "Goodbye",
                desc = self.bot.user,
                thumbnail = self.bot.user.avatar.url
            )
        )

    async def autostop(self):
        while self.guild in self.instances:
            await sleep(600)
            if self.guild not in self.instances: return
            if (
                len(self.voice_client.channel.members) < 2\
                or (
                    not self.voice_client.is_playing()\
                    and not self.queue\
                    and not self.loop
                )
            ): await self.stop()
