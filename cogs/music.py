import asyncio
import discord
from discord.ext import commands

class Music(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client
    
    @commands.slash_command()
    async def join(self, ctx: discord.ApplicationContext):
        """Makes the bot join a voice channel."""
        if ctx.voice_client:
            if len(ctx.author.voice.channel.members) > 1:
                await ctx.respond("I'm already in a voice channel.")
                return
        if ctx.author.voice != None:
            await ctx.author.voice.channel.connect()
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
            ctx.guild.voice_client.disconnect()
        else:
            await ctx.respond("You must be in the same voice channel to use this command.")
            
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