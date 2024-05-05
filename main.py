import os, signal, discord, asyncio
from dotenv import load_dotenv
from discord.ext import commands
from tracemalloc import start as trace

trace()
load_dotenv()

client = commands.Bot(command_prefix=commands.when_mentioned, intent=discord.Intents.all())

for cog in os.listdir('./cogs'):
    if cog.endswith('.py'):
        client.load_extension(f'cogs.{cog[:-3]}')
        

async def main_bot():
    await client.start(os.getenv("TOKEN"))

async def shutdown():
    for cog in os.listdir('./cogs'):
        if cog.endswith('.py'):
            client.unload_extension(f'cogs.{cog[:-3]}')
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