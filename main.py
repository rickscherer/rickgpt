import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        await bot.tree.sync()
        print(f"Synced slash commands.")
    except Exception as e:
        print(f"Error syncing commands: {e}")

# Load cogs
initial_extensions = [
    "cogs.summarize",
    "cogs.ask"
]

for ext in initial_extensions:
    bot.load_extension(ext)

bot.run(DISCORD_TOKEN)
