import asyncio
import discord
from discord.ext import commands

class Music(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.slash_command()
    async def join(self, ctx):
        """Joins a voice channel"""
        if ctx.author.voice != None:
            await ctx.author.voice.channel.connect()
            await ctx.respond("Joining...")
        else:
            await ctx.respond("You must be in a voice channel")
        
    # @commands.slash_command()
    # @commands.has_guild_permissions(administrator=True)
    # async def test2(self, ctx=discord.ApplicationContext):
    #     await ctx.respond("Okay")
    #     print(self.client.voice_clients[0].guild)
    
            
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