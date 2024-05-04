import os, mafic, asyncio, discord
from typing import Union
from discord.ext import commands
import mafic.utils

class MyPlayer(mafic.Player):
    def __init__(self, client: commands.Bot, channel: discord.abc.Connectable) -> None:
        super().__init__(client, channel)

        # Mafic does not provide a queue system right now, low priority.
        self.queue: list[mafic.Track] = []

    def add(self, track: mafic.Track):
        self.queue.append(track)

    def get_next(self):
        return self.queue.pop(0)
class Music(commands.Cog):
    def __init__(self, client:commands.Bot):
        self.client: commands.Bot = client
        client.Music = self
        self.channels = {}
    
    @commands.Cog.listener('on_ready')
    async def connect_mafic(self):
        self.pool: mafic.NodePool= mafic.NodePool(self.client)
        self.client.loop.create_task(self.add_nodes())
        self.client.pool = self.pool
    
    async def add_nodes(self):
        await self.pool.create_node(
            host = os.getenv('HOST'),
            port = int(os.getenv('PORT')),
            password = os.getenv('PASSWORD'),
            label = f"default_node_{self.client.user.name.replace(" ", "_").lower()}",
            resume_key="BeepBop"
        )

    @commands.slash_command()
    async def join(self, ctx: discord.ApplicationContext):
        """Makes the bot join a voice channel."""
        if ctx.voice_client:
            if len(ctx.voice_client.channel.members) > 1:
                await ctx.respond("I'm already in a voice channel.")
                return
        if ctx.author.voice != None:
            await ctx.author.voice.channel.connect(cls=MyPlayer)
            await ctx.respond("Joining...")
            self.channels[ctx.guild_id] = ctx.channel
        else:
            await ctx.respond("You must be in a voice channel to use that command.")
    
    @commands.slash_command()
    async def leave(self, ctx: discord.ApplicationContext):
        """Makes the bot leave a voice channel."""
        if not ctx.guild.voice_client:
            await ctx.respond("I am not in a voice channel.")
        elif not ctx.author.voice:
            await ctx.respond("You must be in a voice channel to use that command.")
        elif ctx.author.voice.channel == ctx.guild.voice_client.channel:
            await ctx.respond("Leaving...")
            await ctx.guild.voice_client.disconnect()
        else:
            await ctx.respond("You must be in the same voice channel to use this command.")

    @commands.slash_command()
    async def play(self, ctx: discord.ApplicationContext, *, search:str):
        """Makes the bot play your favorite song."""
        ctx.defer
        if ctx.guild.voice_client:
            player: MyPlayer = ctx.guild.voice_client
            self.channels[ctx.guild_id] = ctx.channel
        else:
            await self.join(ctx)
            player: MyPlayer = ctx.guild.voice_client
        result = await player.fetch_tracks(search)
        
        if isinstance(result, mafic.Playlist):
            for track in result.tracks:
                player.add(track)
            await player.play(player.queue.pop(0))
            await ctx.respond(f"Playing {result.tracks[0].title}")
        else:
            result = result[0]
            await player.play(result)  
            await ctx.respond(f"Playing {result.title}")
            
    @commands.slash_command()
    async def stop(self, ctx: discord.ApplicationContext):
        """Stop music playback."""
        player: MyPlayer = ctx.voice_client
        if ctx.author.voice != None and ctx.author.voice.channel == player.channel:
            await player.stop()
            await ctx.respond("Stoping music.")
        else:
            await ctx.respond("You must be in my voice channel to use this command.")

    @commands.slash_command()
    async def pause(self, ctx: discord.ApplicationContext):
        """Pause music playback."""
        player = ctx.guild.voice_client
        if ctx.author.voice != None and ctx.author.voice.channel == player.channel:
            await ctx.guild.voice_client.pause()
            await ctx.respond("Pausing.")
        else:
            await ctx.respond("You must be in my voice channel to use this command.")

    @commands.slash_command()
    async def resume(self, ctx: discord.ApplicationContext):
        """Resume music playback."""
        player: MyPlayer = ctx.guild.voice_client
        if ctx.author.voice != None and ctx.author.voice.channel == player.channel:
            await player.resume()
            await ctx.respond("Resuming.")
            self.channels[ctx.guild_id] = ctx.channel
        else:
            await ctx.respond("You must be in my voice channel to use this command.")

    @commands.slash_command()
    async def volume(self, ctx: discord.ApplicationContext, volume:int):
        """Set music playback volume."""
        player:MyPlayer = ctx.guild.voice_client
        if ctx.author.voice != None and ctx.author.voice.channel == player.channel:
            await player.set_volume(volume)
            await ctx.respond(f"Setting volume to {volume}.")
        else:
            await ctx.respond("You must be in my voice channel to use this command.")

    @commands.slash_command()
    async def skip(self, ctx: discord.ApplicationContext):
        """Skip the current song."""
        player:MyPlayer = ctx.guild.voice_client

        if len(player.queue) == 0:
            return await ctx.respond("No songs in queue.")

        if ctx.author.voice != None and ctx.author.voice.channel == player.channel:
            track = player.queue[0]
            await player.seek(track.length-1)
            await ctx.respond("Skipping song.")
            await ctx.respond(f"Now playing {track.title}")
        else:
            await ctx.respond("You must be in my voice channel to use this command.")

    @commands.Cog.listener(name="on_voice_state_update")
    async def LeaveAfter5(self=commands.Bot, member=discord.Member, before=discord.VoiceState, after=discord.VoiceState):
        if member.id != self.client.user.id and before.channel != None:
            channel = await self.client.fetch_channel(before.channel.id)
            members = channel.members
            if after.channel == None and len(members) == 1:

                await asyncio.sleep(3)
                channel = await self.client.fetch_channel(before.channel.id)
                members = channel.members
                if len(members) == 1:
                    await channel.guild.voice_client.disconnect()

    @commands.Cog.listener('on_track_end')
    @commands.Cog.listener('on_track_stuck')
    @commands.Cog.listener('on_track_exception')
    async def next_song(self, event: mafic.TrackStuckEvent|mafic.TrackEndEvent|mafic.TrackExceptionEvent):
        assert isinstance(event.player, MyPlayer)

        if event.player.queue:
            track = event.player.get_next()
            await event.player.play(track)

    @commands.Cog.listener("on_node_ready")
    async def on_node_ready(self, node: mafic.Node):
        print(f"Music: Connected to {node.label}")
    
    @commands.Cog.listener("on_node_unavailable")
    async def on_node_unavailable(self, node:mafic.Node):
        print(f"Music: {node.label} unavailable.")


def setup(client):
    client.add_cog(Music(client))