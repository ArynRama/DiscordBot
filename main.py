import os
import discord
from dotenv import load_dotenv

load_dotenv()

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}')

intents = discord.Intents.all()
intents.message_content = True

client = MyClient(intents=intents)
client.run(os.getenv("TOKEN"))