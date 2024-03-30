import re, os, mafic, asyncio, discord
from discord.ext import commands

url_rx = re.compile(r'https?://(?:www\.)?.+')

class Music(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client
        client.Music = self
    
    @commands.Cog.listener('on_ready')
    async def connect_mafic(self):
        self.pool: mafic.NodePool= mafic.NodePool(self.client)
        self.client.loop.create_task(self.add_nodes())
        
    async def add_nodes(self):
        await self.pool.create_node(
            host = os.getenv('HOST'),
            port = int(os.getenv('PORT')),
            password = os.getenv('PASSWORD'),
            label= self.client.user.name
        )

    @commands.slash_command()
    async def join(self, ctx: discord.ApplicationContext):
        """Makes the bot join a voice channel."""
        if ctx.voice_client:
            if len(ctx.voice_client.channel.members) > 1:
                await ctx.respond("I'm already in a voice channel.")
                return
        if ctx.author.voice != None:
            await ctx.author.voice.channel.connect(cls=mafic.Player)
            await ctx.respond("Joining...")
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
        await ctx.defer()
        player = ctx.guild.voice_client
        result = await player.fetch_tracks(search)
        result = result[0]
        print(result)
        await player.play(result)
        await ctx.respond(f"Playing {result.title}")
            
    @commands.slash_command()
    async def stop(self, ctx: discord.ApplicationContext):
        await ctx.voice_client.stop()

    @commands.slash_command()
    async def pause(Self, ctx: discord.ApplicationContext):
        await ctx.guild.voice_client.pause()
        await ctx.respond("Pausing.")

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

def setup(client):
    client.add_cog(Music(client))