from threading import Thread
from time import time

from discord.ext import tasks
from discord.ext.commands import Cog, command

from ..components import Embed
from ..models import VoiceClient, UserSaved

class MusicCog(Cog):

    def __init__(self, bot):
        self.bot = bot
        self.voice_client = {}
        self.user_saved = {}
        self.music_autoclean.start()

    # start voice section =========================================================================
    @command(brief="Play <youtube url/song name>", aliases=["p"])
    async def play(self, ctx, *, url):
        if not await self.init_voice_client(ctx):
            return
        Thread(target=lambda: self.voice_client[ctx.guild.id].enqueue(url)).start()

    @command(brief="Search <song name> on youtube", aliases=["s", "find"])
    async def search(self, ctx, *, name):
        if not await self.init_voice_client(ctx):
            return
        Thread(target=lambda: self.voice_client[ctx.guild.id].search(name)).start()

    # playlist section ============================================================================
    @command(brief="Save <youtube url/song name> to your playlist", aliases=["sv"])
    async def save(self, ctx, *, url):
        if not await self.init_user_saved(ctx):
            return
        Thread(target=lambda: self.user_saved[ctx.author.id].search(url)).start()

    @command(brief="Play songs you saved", aliases=["pl"])
    async def playlist(self, ctx, page:int=1):
        if not await self.init_user_saved(ctx):
            return
        await self.user_saved[ctx.author.id].send_playlist_embed(page)

    @command(brief="Remove song from your playlist", aliases=["rm"])
    async def remove(self, ctx, page:int=1):
        if not await self.init_user_saved(ctx):
            return
        await self.user_saved[ctx.author.id].send_remove_playlist_embed(page)

    # now playing section =========================================================================
    @command(brief="Now playing", aliases=["np"])
    async def nowplaying(self, ctx):
        if not await self.is_playing(ctx):
            return
        await self.voice_client[ctx.guild.id].send_np_embed()

    @command(brief="Skip song at (<index>) or current song")
    async def skip(self, ctx, index:int=0):
        if not await self.is_playing(ctx):
            return
        await self.voice_client[ctx.guild.id].skip(index)

    @command(brief="Toggle Loop One/Loop All", aliases=["repeat", "cycle"])
    async def loop(self, ctx):
        if not await self.is_playing(ctx):
            return
        await self.voice_client[ctx.guild.id].toggle_loop()

    @command(brief="Pause song")
    async def pause(self, ctx):
        if not await self.is_playing(ctx):
            return
        await self.voice_client[ctx.guild.id].pause()

    @command(brief="Resume song")
    async def resume(self, ctx):
        if not await self.is_playing(ctx):
            return
        await self.voice_client[ctx.guild.id].resume()

    # queue section ===============================================================================
    @command(brief="Show queue (<page>) (10 per page)", aliases=["q", "list"])
    async def queue(self, ctx, page:int=1):
        if not await self.is_playing(ctx):
            return
        await self.voice_client[ctx.guild.id].send_queue_embed(page)

    @command(brief="Move song (<from>) to (<to>)", aliases=["mv"])
    async def move(self, ctx, fr:int=0, to:int=1):
        if not await self.is_playing(ctx):
            return
        await self.voice_client[ctx.guild.id].move(fr, to)

    @command(brief="Shuffle queue", aliases=["random"])
    async def shuffle(self, ctx):
        if not await self.is_playing(ctx):
            return
        await self.voice_client[ctx.guild.id].shuffle()

    @command(brief="Stop", aliases=["leave"])
    async def stop(self, ctx):
        if not await self.is_playing(ctx):
            return
        await self.del_voice_client(ctx.guild.id)

    # tasks section ===============================================================================
    async def init_voice_client(self, ctx):
        id = ctx.guild.id
        if id in self.voice_client:
            return True
        try:
            # join
            self.voice_client[id] = VoiceClient(self.bot, ctx, await ctx.author.voice.channel.connect())
            await ctx.send(
                embed = Embed(
                    title = "Hello",
                    desc = self.bot.user,
                    thumbnail = self.bot.user.avatar.url
                )
            )
            print(f"Added guild {id} to voice_client")
            return True
        except:
            # failed to join
            await self.del_voice_client(id)
            await ctx.send(
                embed = Embed(
                    title = "Opsss",
                    desc = "You are not\nin a voice channel",
                    footer = self.bot.user,
                    thumbnail = self.bot.user.avatar.url
                )
            )
            return False

    async def init_user_saved(self, ctx):
        id = ctx.author.id
        if id in self.user_saved:
            # in case user changed his channel
            await self.user_saved[id].check_ctx(ctx)
            return True
        self.user_saved[id] = UserSaved(self.bot, ctx, id)
        print(f"Added user {id} to user_saved")
        return True

    async def is_playing(self, ctx):
        id = ctx.guild.id
        if id in self.voice_client:
            return True
        await ctx.send(
            embed = Embed(
                title = "Opsss",
                desc = "You are not\nplaying anything",
                footer = self.bot.user,
                thumbnail = self.bot.user.avatar.url
            )
        )
        return False

    async def del_voice_client(self, id):
        try:
            vc = self.voice_client.pop(id)
            await vc.stop()
            await vc.ctx.send(
                embed = Embed(
                    title = "Goodbye",
                    desc = self.bot.user,
                    thumbnail = self.bot.user.avatar.url
                )
            )
        except:
            pass
    
    async def del_user_saved(self, id):
        await self.user_saved.pop(id).stop()

    @tasks.loop(minutes=10)
    async def music_autoclean(self):
        print("Cleaning up...")
        for id, vc in self.voice_client.copy().items():
            try:
                # no one in voice channel                       not playing, no song in queue, deactive time > 5mins
                if len(vc.voice_client.channel.members) < 2 or (not vc.voice_client.is_playing() and not vc.queue and time()-vc.last_active > 300):
                    await self.del_voice_client(id)
                    print(f"Removed guild {id} from voice_client")
                
            except:
                pass
        for id, us in self.user_saved.copy().items():
            try:
                if time()-us.last_active > 300:
                    await self.del_user_saved(id)
                    print(f"Removed user {id} from user_saved")
            except:
                pass
