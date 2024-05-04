import os, mafic, signal, discord, asyncio
from dotenv import load_dotenv
from discord.ext import commands
from tracemalloc import start as trace
from cogs.music import Music

trace()
load_dotenv()

client = commands.Bot(command_prefix=commands.when_mentioned, help_command=None, intent=discord.Intents.all())

client.load_extension('cogs.music')

async def main_bot():
    await client.start(os.getenv("TOKEN"))

async def shutdown():
    client.unload_extension('cogs.music')
    await client.pool.close()
    await client.close()
    print("Shut down.")

@client.listen()
async def on_ready():
    print("Getting Ready...")
    loop = asyncio.get_event_loop()
    try:
        loop.add_signal_handler(signal.SIGINT, lambda: asyncio.create_task(shutdown()))
        loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task(shutdown()))
    except:
        pass
    print(f'Logged on as {client.user}')
        
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(asyncio.gather(main_bot()))
    except:
        loop.run_until_complete(shutdown())
    finally:
        print("Program shutdown.")