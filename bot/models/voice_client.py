from asyncio import sleep
from random import shuffle as rand

from discord import FFmpegOpusAudio

from ..components import Embed, View, Button, Select, ButtonStyle, SelectOption, InteractionCallback
from ..utils.validator import check_url
from ..utils.formatter import format_duration
from ..utils.extractor import extract_one, extract_all_or_search, youtube_search

class VoiceClient:

    TIMEOUT = 60
    FFMPEG_OPTIONS = {"bitrate": 128, "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", "options": "-vn"}
    
    instances = {}

    def __init__(self, ctx):
        self.ctx = ctx
        self.bot = ctx.bot
        self.guild = ctx.guild

    def enqueue(self, url: str):
        song, songs = extract_all_or_search(url)
        self.queue += songs
        self.bot.loop.create_task(self.ctx.send(embed = song.get_embed("Added to queue")))
        if not self.voice_client.is_playing(): self.bot.loop.create_task(self.dequeue())

    async def dequeue(self):
        # no more music, no loop
        if not self.queue and not self.loop: return await self.delete_last_np_message()
        # not playing or no loop => fetch new song
        if not self.playing or self.loop != 1:
            if self.loop == 2 and self.playing: self.queue.append(self.playing)
            self.playing = self.queue.pop(0)
        # 403 forbidden => redownload
        while not check_url(self.playing.play_url): self.playing = extract_one(self.playing.initial_url)
        # 200 ok
        self.voice_client.play(
            FFmpegOpusAudio(
                self.playing.play_url,
                **self.FFMPEG_OPTIONS
            ),
            after = lambda _: self.bot.loop.create_task(self.dequeue())
        )
        await self.send_np_embed()

    def search(self, name: str):
        self.last_search = youtube_search(name)
        self.bot.loop.create_task(self.send_search_embed())

    async def select(self, index: int):
        song = self.last_search[index]
        self.queue.append(song)
        await self.ctx.send(embed = song.get_embed("Added to queue"))
        if not self.voice_client.is_playing(): await self.dequeue()

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
        try: await self.last_np_message.delete()
        except Exception: pass

    async def send_np_embed(self):
        await self.delete_last_np_message()
        self.last_np_message = await self.ctx.send(
            embed = self.playing.get_embed("Playing"),
            view = View(
                Button(
                    label = "Stop", 
                    style = ButtonStyle.red,
                    callbacks = (InteractionCallback(self.stop), ),
                ),
                Button(
                    label = "Resume" if self.voice_client.is_paused() else "Pause",
                    style = ButtonStyle.green if self.voice_client.is_paused() else ButtonStyle.gray,
                    callbacks = (InteractionCallback(self.resume if self.voice_client.is_paused() else self.pause), ),
                ),
                Button(
                    label = "Skip",
                    callbacks = (InteractionCallback(self.skip), ),
                ),
                Button(
                    label = "Loop All" if self.loop==2 else "Loop One" if self.loop==1 else "Loop Off",
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
        await self.ctx.send(
            embed = Embed(
                title = f"Page {page}",
                desc = "\n".join(
                    f"**[{i+1}. {song.title}]({song.initial_url})**"
                    for i, song in enumerate(self.queue[10*(page-1): 10*page], 10*(page-1))
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
                    style = ButtonStyle.gray if page>=(len(self.queue)+9)//10 else ButtonStyle.green,
                    disabled = page>=(len(self.queue)+9)//10,
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

    # control =====================================================================================
    async def toggle_loop(self):
        self.loop = (self.loop+1) % 3
        await self.send_np_embed()

    async def pause(self):
        if not self.voice_client.is_paused(): self.voice_client.pause()
        await self.send_np_embed()

    async def resume(self):
        if self.voice_client.is_paused(): self.voice_client.resume()
        await self.send_np_embed()

    async def skip(self, index: int = 0):
        if not index:
            if not self.voice_client.is_playing(): return
            await self.ctx.send(embed=self.playing.get_embed("Skipped"))
            self.voice_client.stop()
        else:
            if not self.queue: return
            index = (index-1) % len(self.queue)
            await self.ctx.send(embed=self.queue.pop(index).get_embed("Skipped"))

    async def shuffle(self):
        rand(self.queue)
        await self.send_queue_embed()

    async def move(self, fr: int, to: int):
        if not self.queue: return
        fr = fr % len(self.queue)
        to = to % len(self.queue)
        self.queue.insert(to, self.queue.pop(fr))
        await self.send_queue_embed()

    # start/stop ==================================================================================
    async def start(self) -> bool:
        if self.guild in self.instances: return True
        if not self.ctx.author.voice: return False
        if self.guild.voice_client: await self.guild.voice_client.disconnect()
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
        await self.voice_client.disconnect()
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
            if (
                len(self.voice_client.channel.members) < 2\
                or (
                    not self.voice_client.is_playing()\
                    and not self.queue\
                    and not self.loop
                )
            ): await self.stop()
