import discord
from discord.ext import commands
import json
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure logging
logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load config
with open("config.json") as f:
    config = json.load(f)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=config["prefix"], intents=intents)
bot.locked_channel_id = None
lock_activated = False
copying = False
copycat = ""

def get_mods():
    with open("mods.txt") as f:
        return [line.strip() for line in f]

@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user.name}")

@bot.event
async def on_message(message):

    with open("words.txt") as file:
        words = file.read().splitlines()

    for word in words:
        if word.lower() in message.content.lower():
            await message.delete()
            with open("response.txt") as response_file:
                response = response_file.read()
            await message.channel.send(response)
            with open("logs.txt", "a") as logs_file:
                logs_file.write(f"Deleted message: {message.content}\n")
            return

    with open("us.txt") as file:
        names = file.read().splitlines()

    for name in names:
        if name.lower() in message.author.name.lower():
            await message.delete()
            with open("response.txt") as response_file:
                response = response_file.read()
            await message.channel.send(response)
            with open("logs.txt", "a") as logs_file:
                logs_file.write(f"Deleted message: {message.content}\n")
            return

    if lock_activated:
        if message.channel.id == bot.locked_channel_id:
            if message.author.name not in get_mods() and message.author != bot.user:
                await message.delete()
                return
    if copying and message.author.name == copycat:
          await message.channel.send(message.content)

    await bot.process_commands(message)

@bot.command()
async def truelock(ctx):
    if ctx.author.name in get_mods():
        global lock_activated
        lock_activated = True
        bot.locked_channel_id = ctx.channel.id
        await ctx.send("Channel locking activated. Only the designated locked channel is accessible.")
        await ctx.message.delete()
    else:
        await ctx.send("You do not have permission to use this command.")

@bot.command()
async def trueunlock(ctx):
    if ctx.author.name in get_mods():
        global lock_activated
        lock_activated = False
        bot.locked_channel_id = None
        await ctx.send("Channel locking deactivated.")
        await ctx.message.delete()
    else:
        await ctx.send("You do not have permission to use this command.")

@bot.command()
async def purge(ctx, amount: int):
    if ctx.author.name in get_mods():
        await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"Successfully purged {amount} messages.")
    else:
        await ctx.send("You do not have permission to use this command.")

class ConfigChangeHandler(FileSystemEventHandler):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

@bot.command()
async def send(ctx, *, message):
    if ctx.author.name in get_mods():

        await ctx.send(message)
        await ctx.message.delete()
    else:
        await ctx.send("You do not have permission to use this command.")


@bot.command()
async def copy(ctx, member: discord.Member):
    global copying, copycat
    if ctx.author.name in get_mods():
        copying = True
        copycat = member.name
        await ctx.message.delete()
    else:
        await ctx.send("You do not have permission to use this command.")
@bot.command()
async def unban(ctx, *, message):
    if ctx.author.name in get_mods():
        with open("us.txt", "r") as file:
            lines = file.readlines()
        with open("us.txt", "w") as file:
            for line in lines:
                if line != f"{str}\n":
                    file.write(line)
        await ctx.send(f"{message} has been unbanned.")
    else:
        await ctx.send("You do not have permission to use this command.")
        
@bot.command()
async def ban(ctx, *, message):
    if ctx.author.name in get_mods():
        with open("us.txt", "a") as file:
            file.write(f"{message}\n")
        await ctx.send(f"{message} has been banned.")
    else:
        await ctx.send("You do not have permission to use this command.")
        
@bot.command()
async def restart(ctx):
    if ctx.author.name in get_mods():
        await ctx.send("Restarting...")
        await bot.logout()
        os.system("python3 main.py")
    else:
        await ctx.send("You do not have permission to use this command.")
        
@copy.error
async def copy_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("Invalid user.")

observer = Observer()
observer.schedule(ConfigChangeHandler(bot), path="./", recursive=False)
observer.start()

try:
    bot.run(config["token"])
except KeyboardInterrupt:
    observer.stop()

observer.join()
