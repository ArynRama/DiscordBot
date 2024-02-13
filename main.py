import os
import discord

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}')

intents = discord.Intents.all()
intents.message_content = True

client = MyClient(intents=intents)
print(os.environ.items())