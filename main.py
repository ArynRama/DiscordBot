import os, sys, signal, discord, asyncio
from dotenv import load_dotenv
from discord.ext import commands
from tracemalloc import start as trace

trace()
load_dotenv()

client = commands.Bot(command_prefix=commands.when_mentioned(), help_command=None, intent=discord.Intents.all())

@client.slash_command()
async def test(ctx=discord.ApplicationContext):
    await ctx.respond("Working")

client.load_extension('cogs.music')

async def main_bot():
    await client.start(os.getenv("TOKEN"))

async def shutdown():
    print('Shuting Down...')
    for command in client.walk_application_commands():
        client.remove_application_command(command)
        print(f"Removing Command: {command.name}")
    await client.close()
    asyncio.get_event_loop().stop()
    print("Shut down.")
    sys.exit(0)

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
    loop.run_until_complete(asyncio.gather(main_bot()))