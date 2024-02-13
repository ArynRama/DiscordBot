import discord
import discord.ext.commands as commands

class Music(commands.Cog):
    def __init__(self, client, message, bot, view):
        self.client = client
    
    @commands.command()
    async def join(self, ctx=commands.Context()):
        """Joins a voice channel"""
        if ctx.author.voice != None:
            ctx.author.voice.connect
            await ctx.reply("Joining...")
        else:
            await ctx.reply("You must be in a voice channel")