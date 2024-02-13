import os
import asyncio
import discord
from cogs.music import Music
from dotenv import load_dotenv
from discord.ext import commands


load_dotenv()

class Client(commands.Bot):
    intents = discord.Intents.all()

client = Client(help_command=None)
@client.listen()
async def on_ready():
    print(f'Logged on as {client.user}')

@client.slash_command()
async def test(ctx=discord.ApplicationContext):
    await ctx.respond("Working")

client.load_extension('cogs.music')

async def main_bot():
    await client.start(os.getenv("TOKEN"))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(main_bot()))