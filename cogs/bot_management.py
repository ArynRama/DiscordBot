import discord
from util import set_data, send
from discord.ext import commands

class Bot_Management(commands.Cog):

    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.slash_command()
    async def dj(self, ctx: discord.ApplicationContext, value:discord.Role|None):
        await send(ctx, f"DJ role set to {value}")
        if value == None:
            set_data(ctx.guild_id, 'dj_role', value)
        else:
            set_data(ctx.guild_id, 'dj_role', value.id)

def setup(client):
    client.add_cog(Bot_Management(client))