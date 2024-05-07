import os, mafic, asyncio, discord, dotenv, traceback, json
from discord.ext import commands
from util import send, get_data, user_has_perm
import mafic.utils

class MyPlayer(mafic.Player):
    def __init__(self, client: commands.Bot, channel: discord.abc.Connectable) -> None:
        super().__init__(client, channel)

        # Mafic does not provide a queue system right now, low priority.
        self.queue: list[dict] = []

    def add(self, track: mafic.Track, ctx: discord.ApplicationContext, index = "last"):
        dict = {
            "name": track.title,
            "author": ctx.author.display_name,
            "track": track
        }
        if index == "last":
            self.queue.append(dict)
        else:
            self.queue.insert(index-1, dict)

    def remove(self, index="first"):
        if index == "first":
            self.queue.pop(0)
        else:
            self.queue.pop(index-1)

    def get_next(self):
        return self.queue.pop(0)

class Music(commands.Cog):
    def __init__(self, client:commands.Bot):
        self.client: commands.Bot = client
        client.Music = self
        self.channels = {}

    def is_dj():
        async def predicate(ctx:discord.ApplicationContext):
            if get_data(ctx.guild_id, "dj_role") != None:
                return ctx.author.get_role(int(get_data(ctx.guild_id, "dj_role"))) or await user_has_perm(ctx.bot, ctx.author, discord.permissions.Permissions(8))
            else:
                return True
        return commands.check(predicate)

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
            label = f"default_node_{self.client.user.name.replace(' ', '_').lower()}"
        )

    @is_dj()
    @commands.slash_command()
    async def join(self, ctx: discord.ApplicationContext):
        """Makes the bot join a voice channel."""
        if ctx.voice_client:
            if len(ctx.voice_client.channel.members) > 1:
                await send(ctx, "I'm already in a voice channel.")
                return
        if ctx.author.voice != None:
            await ctx.author.voice.channel.connect(cls=MyPlayer)
            await send(ctx, "Joining...")
            self.channels[ctx.guild_id] = ctx.channel
        else:
            await send(ctx, "You must be in a voice channel to use that command.")
    
    @is_dj()
    @commands.slash_command()
    async def leave(self, ctx: discord.ApplicationContext):
        """Makes the bot leave a voice channel."""
        if not ctx.guild.voice_client:
            await send(ctx, "I am not in a voice channel.")
        elif not ctx.author.voice:
            await send(ctx, "You must be in a voice channel to use that command.")
        elif ctx.author.voice.channel == ctx.guild.voice_client.channel:
            await send(ctx, "Leaving...")
            await ctx.guild.voice_client.disconnect()
        else:
            await send(ctx, "You must be in the same voice channel to use this command.")

    @is_dj()
    @commands.slash_command()
    @discord.option("song", type=str, parameter_name='search')
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
        
        if player.current == None:
            if isinstance(result, mafic.Playlist):
                for track in result.tracks:
                    player.add(track, ctx)
                await player.play(player.queue.pop(0)["track"])
                await send(ctx, f"Playing {result.name}")
            else:
                result = result[0]
                await player.play(result)  
                await send(ctx, f"Playing {result.title}")
        else:
            if isinstance(result, mafic.Playlist):
                for track in result.tracks:
                    player.add(track, ctx)
                await player.resume()
                await send(ctx, f"Adding {result.name} to queue")
            else:
                result = result[0]
                player.add(result, ctx)
                await player.resume()
                await send(ctx, f"Adding {result.title} to queue")

    @is_dj()
    @commands.slash_command()
    async def stop(self, ctx: discord.ApplicationContext):
        """Stop music playback."""
        player: MyPlayer = ctx.voice_client
        if ctx.author.voice != None and ctx.author.voice.channel == player.channel:
            await player.stop()
            await send(ctx, "Stoping music.")
        else:
            await send(ctx, "You must be in my voice channel to use this command.")

    @is_dj()
    @commands.slash_command()
    async def pause(self, ctx: discord.ApplicationContext):
        """Pause music playback."""
        player = ctx.guild.voice_client
        if ctx.author.voice != None and ctx.author.voice.channel == player.channel:
            await ctx.guild.voice_client.pause()
            await send(ctx, "Pausing.")
        else:
            await send(ctx, "You must be in my voice channel to use this command.")

    @is_dj()
    @commands.slash_command()
    async def resume(self, ctx: discord.ApplicationContext):
        """Resume music playback."""
        player: MyPlayer = ctx.guild.voice_client
        if ctx.author.voice != None and ctx.author.voice.channel == player.channel:
            await player.resume()
            await send(ctx, "Resuming.")
            self.channels[ctx.guild_id] = ctx.channel
        else:
            await send(ctx, "You must be in my voice channel to use this command.")

    @is_dj()
    @commands.slash_command()
    async def volume(self, ctx: discord.ApplicationContext, volume:int):
        """Set music playback volume."""
        player:MyPlayer = ctx.guild.voice_client
        if ctx.author.voice != None and ctx.author.voice.channel == player.channel:
            await player.set_volume(volume)
            await send(ctx, f"Setting volume to {volume}.")
        else:
            await send(ctx, "You must be in my voice channel to use this command.")

    @is_dj()
    @commands.slash_command()
    async def skip(self, ctx: discord.ApplicationContext):
        """Skip the current song."""
        player:MyPlayer = ctx.guild.voice_client

        if len(player.queue) == 0:
            return await send(ctx, "No songs in queue.")

        if ctx.author.voice != None and ctx.author.voice.channel == player.channel:
            track = player.queue[0]["track"]
            await player.seek(track.length-1)
            await send(ctx, "Skipping song.")
            await send(ctx, f"Now playing {track.title}")
        else:
            await send(ctx, "You must be in my voice channel to use this command.")

    @commands.slash_command()
    async def playing(self, ctx: discord.ApplicationContext):
        """Get current song."""
        player: MyPlayer = ctx.voice_client
        if player == None:
            await send( ctx, "Not playing right now.")
        else:
            track = player.current
            if track == None:
                await send(ctx, 'Not playing right now.')
            else:
                await send(ctx, f"Currently playing {track.title}")

    queue = discord.SlashCommandGroup(name= "queue", description= "View the queue.", guild_only=True)

    @queue.command()
    async def list(self, ctx: discord.ApplicationContext):
        player: MyPlayer = ctx.voice_client
        
        if not player:
            return await send(ctx, "Not playing anything.")

        if len(player.queue) == 0:
            return await send(ctx, "Nothing in queue")
        else:
            return await send(ctx, "Queue", player.queue)
    
    @queue.command()
    @discord.option(name="songs", parameter_name= "args")
    @discord.option("index", type=int, required = False, min_value = 1)
    async def add(self, ctx:discord.ApplicationContext, args, index):
        player: MyPlayer = ctx.voice_client
        result = await player.fetch_tracks(args)

        if isinstance(result, mafic.Playlist):
            for i in range(len(result.tracks)):
                player.add(result.tracks[i], ctx, index+i)
            self.queue(self, ctx)
        else:
            result = result[0] 
            await send(ctx, f"Adding {result.title} to queue.")  
            player.add(result, ctx, index)

    @queue.command()
    @discord.option("index", type=int, min_value = 1 )
    async def remove(self,ctx:discord.ApplicationContext, index):
        player : MyPlayer = ctx.voice_client
        if not player:
            return await send(ctx, "Not playing anything.")
        await send(ctx, f"Removing {player.queue[index-1]['name']} from queue.")  
        player.remove(index)

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
            track = event.player.get_next()["track"]
            await event.player.play(track)

    @commands.Cog.listener("on_node_ready")
    async def on_node_ready(self, node: mafic.Node):
        print(f"Music: Connected to {node.label}")
    
    @commands.Cog.listener("on_node_unavailable")
    async def on_node_unavailable(self, node:mafic.Node):
        print(f"Music: {node.label} unavailable.")

    async def cog_command_error(self, ctx, error):
        if(isinstance(error, discord.errors.CheckFailure)):
            await send(ctx, "You dont have access to this command.")
        else:
            print(traceback.format_exc())

def setup(client):
    client.add_cog(Music(client))