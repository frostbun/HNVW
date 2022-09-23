from threading import Thread

from discord.ext.commands import Cog, command

from .user_playlist import UserPlaylist
from .voice_client import VoiceClient


class Music(Cog):

    def __init__(self, bot):
        self.bot = bot

    # start voice section =========================================================================
    @command(brief="Play <url|song name>", aliases=("p", ))
    async def play(self, ctx, *, url: str):
        if not await self.start_voice_client(ctx):
            return
        Thread(target=lambda: VoiceClient.instances[ctx.guild].enqueue(url)).start()

    @command(brief="Search <song name> on youtube", aliases=("s", "find"))
    async def search(self, ctx, *, name: str):
        if not await self.start_voice_client(ctx):
            return
        Thread(target=lambda: VoiceClient.instances[ctx.guild].search(name)).start()

    # playlist section ============================================================================
    @command(brief="Save <url|song name> to your playlist", aliases=("sv", ))
    async def save(self, ctx, *, url: str):
        Thread(target=lambda: UserPlaylist(ctx).search(url)).start()

    @command(brief="Play song from your playlist", aliases=("pl", ))
    async def playlist(self, ctx, page: int = 1):
        await UserPlaylist(ctx).send_playlist_embed(page)

    @command(brief="Remove song from your playlist", aliases=("rm", ))
    async def remove(self, ctx, page: int = 1):
        await UserPlaylist(ctx).send_remove_playlist_embed(page)

    # now playing section =========================================================================
    @command(brief="Now playing", aliases=("np", ))
    async def nowplaying(self, ctx):
        if not await self.is_playing(ctx):
            return
        await VoiceClient.instances[ctx.guild].send_np_embed()

    @command(brief="Skip song at (<index>) or current song")
    async def skip(self, ctx, index: int = 0):
        if not await self.is_playing(ctx):
            return
        await VoiceClient.instances[ctx.guild].skip(index)

    @command(brief="Toggle Loop One/Loop All", aliases=("repeat", "cycle"))
    async def loop(self, ctx):
        if not await self.is_playing(ctx):
            return
        await VoiceClient.instances[ctx.guild].toggle_loop()

    @command(brief="Pause song")
    async def pause(self, ctx):
        if not await self.is_playing(ctx):
            return
        await VoiceClient.instances[ctx.guild].pause()

    @command(brief="Resume song")
    async def resume(self, ctx):
        if not await self.is_playing(ctx):
            return
        await VoiceClient.instances[ctx.guild].resume()

    # queue section ===============================================================================
    @command(brief="Show queue (<page>) (10 per page)", aliases=("q", "list"))
    async def queue(self, ctx, page: int = 1):
        if not await self.is_playing(ctx):
            return
        await VoiceClient.instances[ctx.guild].send_queue_embed(page)

    @command(brief="Move song (<from>) to (<to>)", aliases=("mv", ))
    async def move(self, ctx, fr: int = -1, to: int = 0):
        if not await self.is_playing(ctx):
            return
        await VoiceClient.instances[ctx.guild].move(fr, to)

    @command(brief="Shuffle queue", aliases=("random", ))
    async def shuffle(self, ctx):
        if not await self.is_playing(ctx):
            return
        await VoiceClient.instances[ctx.guild].shuffle()

    @command(brief="Stop and leave", aliases=("leave", ))
    async def stop(self, ctx):
        if not await self.is_playing(ctx):
            return
        await VoiceClient.instances[ctx.guild].stop()

    # checks section ==============================================================================
    async def start_voice_client(self, ctx):
        return await self.is_playing(ctx) or await VoiceClient(ctx).start()

    async def is_playing(self, ctx):
        return ctx.guild in VoiceClient.instances and await self.is_in_voice_channel(ctx)

    async def is_in_voice_channel(self, ctx):
        return ctx.author.voice and ctx.author.voice.channel == VoiceClient.instances[ctx.guild].voice_client.channel
