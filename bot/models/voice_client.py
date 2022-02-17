from asyncio import sleep
from random import shuffle as rand

from discord import FFmpegOpusAudio

from ..components import Embed, View, Button, Select, ButtonStyle, SelectOption
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

    def enqueue(self, url):
        songs, song = extract_all_or_search(url)
        self.queue += songs
        self.bot.loop.create_task(self.ctx.send(embed=song.get_embed("Added to queue")))
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
                **VoiceClient.FFMPEG_OPTIONS
            ),
            after = lambda e: self.bot.loop.create_task(self.dequeue())
        )
        await self.send_np_embed()

    def search(self, name):
        self.last_search = youtube_search(name)
        self.bot.loop.create_task(self.send_search_embed())

    async def select(self, index):
        song = self.last_search[index]
        self.queue.append(song)
        await self.ctx.send(embed=song.get_embed("Added to queue"))
        if not self.voice_client.is_playing(): await self.dequeue()

    # embed =======================================================================================
    async def voice_channel_check(self, i):
        if not i.user.voice or i.user.voice.channel != self.voice_client.channel:
            await i.response.send_message(
                content = "It's not yours",
                ephemeral = True,
                delete_after = 10,
            )
            return False
        return True

    async def delete_last_np_message(self):
        try: await self.last_np_message.delete()
        except Exception: ...

    async def send_np_embed(self):
        await self.delete_last_np_message()
        self.last_np_message = await self.ctx.send(
            embed = self.playing.get_embed("Playing"),
            view = View(
                Button(
                    label = "Stop", 
                    style = ButtonStyle.red,
                    callback = [ self.stop ],
                ),
                Button(
                    label = "Resume" if self.voice_client.is_paused() else "Pause",
                    style = ButtonStyle.green if self.voice_client.is_paused() else ButtonStyle.gray,
                    callback = [ self.resume if self.voice_client.is_paused() else self.pause ],
                ),
                Button(
                    label = "Skip",
                    callback = [ self.skip ],
                ),
                Button(
                    label = "Loop All" if self.loop==2 else "Loop One" if self.loop==1 else "Loop Off",
                    style = ButtonStyle.gray if not self.loop else ButtonStyle.green,
                    callback = [ self.toggle_loop ],
                ),
                Button(
                    label = "Queue",
                    style = ButtonStyle.blurple,
                    callback = [ self.send_np_embed, self.send_queue_embed ],
                ),
                check = [ self.voice_channel_check ],
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
                    callback = [ self.send_queue_embed ],
                    params = {"page": page-1},
                ),
                Button(
                    label = "Shuffle",
                    style = ButtonStyle.blurple,
                    callback = [ self.shuffle ],
                ),
                Button(
                    label = "Next",
                    style = ButtonStyle.gray if page>=(len(self.queue)+9)//10 else ButtonStyle.green,
                    disabled = page>=(len(self.queue)+9)//10,
                    callback = [ self.send_queue_embed ],
                    params = {"page": page+1},
                ),
                check = [ self.voice_channel_check ],
            ),
            delete_after = VoiceClient.TIMEOUT,
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
                    callback = [ self.select ],
                ),
                Button(
                    label = "Cancel",
                    style = ButtonStyle.red,
                ),
                check = [ self.voice_channel_check ],
            ),
            delete_after = VoiceClient.TIMEOUT,
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

    async def skip(self, index=0):
        if not index:
            if not self.voice_client.is_playing(): return
            await self.ctx.send(embed=self.playing.get_embed("Skipped"))
            self.voice_client.stop()
        else:
            if not self.queue: return
            index = (index-1) % len(self.queue)
            await self.ctx.send(embed=self.queue.pop(index).get_embed("Skipped"))
            await self.send_np_embed()

    async def shuffle(self):
        rand(self.queue)
        await self.send_queue_embed()

    async def move(self, fr, to):
        if not self.queue: return
        fr = (fr-1) % len(self.queue)
        to = (to-1) % len(self.queue)
        self.queue.insert(to, self.queue.pop(fr))
        await self.send_queue_embed()

    # start/stop ==================================================================================
    async def start(self):
        if self.guild in VoiceClient.instances: return True
        if not self.ctx.author.voice: return False
        if self.guild.voice_client: await self.guild.voice_client.disconnect()
        self.voice_client = await self.ctx.author.voice.channel.connect()
        VoiceClient.instances[self.guild] = self
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
        del VoiceClient.instances[self.guild]
        await self.ctx.send(
            embed = Embed(
                title = "Goodbye",
                desc = self.bot.user,
                thumbnail = self.bot.user.avatar.url
            )
        )

    async def autostop(self):
        while self.guild in VoiceClient.instances:
            await sleep(600)
            if len(self.voice_client.channel.members) < 2\
                or (
                    not self.voice_client.is_playing()\
                    and not self.queue\
                    and not self.loop\
                )\
            : await self.stop()
