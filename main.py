import os
import discord
from cogs.music import Music
from dotenv import load_dotenv
import discord.ext.commands as commands


load_dotenv()
token = os.getenv("TOKEN")

intents = discord.Intents.all()
intents.message_content = True

client = commands.Bot(intents=intents)

@client.event
async def on_ready():
    print(f'Logged on as {client.user}')

client.add_cog(Music(client))
client.run(token)