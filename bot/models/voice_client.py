from random import shuffle as rand
from time import time

from discord import FFmpegOpusAudio

from ..components import Embed, View, Button, Select, ButtonStyle, SelectOption
from ..utils.validator import check_url
from ..utils.formatter import format_duration
from ..utils.extractor import extract_one, extract_all_or_search, youtube_search

from configs import FFMPEG_OPTIONS

class VoiceClient:

    def __init__(self, bot, ctx, voice_client):
        self.bot = bot
        self.ctx = ctx
        self.voice_client = voice_client
        self.queue = []
        self.loop = 0
        self.playing = None
        self.last_active = time()

    def enqueue(self, url):
        songs, song = extract_all_or_search(url)
        self.queue += songs
        self.voice_client.loop.create_task(self.ctx.send(embed=song.get_embed("Added to queue")))
        if not self.voice_client.is_playing():
            self.voice_client.loop.create_task(self.dequeue())

    async def dequeue(self):
        self.last_active = time()
        # no more music, no loop
        if not self.queue and self.loop == 0:
            self.playing = None
            await self.delete_all_message()
            return
        # not playing or no loop => fetch new song
        if not self.playing or self.loop != 1:
            if self.loop == 2 and not self.playing:
                self.queue.append(self.playing)
            self.playing = self.queue.pop(0)
        # 403 forbidden => re download
        while not check_url(self.playing.play_url):
            self.playing = extract_one(self.playing.initial_url)
        # 200 ok
        self.voice_client.play(
            FFmpegOpusAudio(
                self.playing.play_url,
                **FFMPEG_OPTIONS
            ),
            after = lambda e: self.voice_client.loop.create_task(self.dequeue())
        )
        await self.send_np_embed()

    def search(self, name):
        self.last_search = youtube_search(name)
        self.voice_client.loop.create_task(self.send_search_embed())

    async def select(self, index):
        song = self.last_search[index]
        self.queue.append(song)
        await self.ctx.send(embed=song.get_embed("Added to queue"))
        if not self.voice_client.is_playing():
            await self.dequeue()

    # embed =======================================================================================
    async def send_np_embed(self):
        # delete last np message
        try:
            await self.last_np_message.delete()
        except:
            pass
        # send new one
        self.last_np_message = await self.ctx.send(
            embed = self.playing.get_embed("Playing"),
            view = View(
                Button(
                    label = "Stop", 
                    style = ButtonStyle.red,
                    callback = [ self.bot.get_command("stop") ],
                    params = {"context": self.ctx},
                ),
                Button(
                    label = "Resume" if self.voice_client.is_paused() else "Pause",
                    style = ButtonStyle.green if self.voice_client.is_paused() else ButtonStyle.gray,
                    callback = [ self.resume if self.voice_client.is_paused() else self.pause ],
                ),
                Button(
                    style = ButtonStyle.gray,
                    label = "Skip",
                    callback = [ self.skip ],
                ),
                Button(
                    label = "Loop All" if self.loop==2 else "Loop One" if self.loop==1 else "Loop Off",
                    style = ButtonStyle.gray if self.loop==0 else ButtonStyle.green,
                    callback = [ self.toggle_loop ],
                ),
                Button(
                    label = "Queue",
                    style = ButtonStyle.blurple,
                    callback = [ self.send_np_embed, self.send_queue_embed ],
                ),
            ),
        )

    async def send_queue_embed(self, page=1):
        # delete last queue message
        try:
            await self.last_queue_message.delete()
        except:
            pass
        # send new one
        self.last_queue_message = await self.ctx.send(
            embed = Embed(
                title = f"Page {page}",
                desc = "\n".join(
                    f"**[{i+1}. {song.title}]({song.initial_url})**"
                    for i, song in enumerate(self.queue[10*(page-1): 10*page], 10*(page-1))
                ),
                footer = f"Total duration: {format_duration(sum(song.duration for song in self.queue))}"
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
            ),
        )

    async def send_search_embed(self):
        # delete last search message
        try:
            await self.last_search_message.delete()
        except:
            pass
        # send new one
        self.last_search_message = await self.ctx.send(
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
            ),
        )

    # control =====================================================================================
    async def toggle_loop(self):
        self.loop = (self.loop+1)%3
        await self.send_np_embed()

    async def pause(self):
        if not self.voice_client.is_paused():
            self.voice_client.pause()
        await self.send_np_embed()

    async def resume(self):
        if self.voice_client.is_paused():
            self.voice_client.resume()
        await self.send_np_embed()

    async def skip(self, index=0):
        if index == 0 and self.voice_client.is_playing():
            await self.ctx.send(embed=self.playing.get_embed("Skipped"))
            self.voice_client.stop()
        else:
            index -= 1
            if index in range(len(self.queue)):
                self.ctx.send(embed=self.queue.pop(index).get_embed("Skipped"))
        await self.send_np_embed()

    async def shuffle(self):
        rand(self.queue)
        await self.send_queue_embed()

    async def move(self, fr, to):
        fr -= 1
        to -= 1
        rg = range(len(self.queue))
        if fr in rg and to in rg:
            self.queue.insert(to, self.queue.pop(fr))
        await self.send_queue_embed()

    async def stop(self):
        self.queue = []
        self.loop = 0
        await self.delete_all_message()
        await self.voice_client.disconnect()

    async def delete_all_message(self):
        # delete last np message
        try:
            await self.last_np_message.delete()
        except:
            pass
        # delete last queue message
        try:
            await self.last_queue_message.delete()
        except:
            pass
        # delete last search message
        try:
            await self.last_search_message.delete()
        except:
            pass
