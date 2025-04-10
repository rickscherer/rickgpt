import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_IDS = os.getenv("GUILD_IDS")
guild_ids = [int(gid.strip()) for gid in GUILD_IDS.split(",")] if GUILD_IDS else []

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} ({bot.user.id})")

    try:
        if guild_ids:
            for gid in guild_ids:
                synced = await bot.tree.sync(guild=discord.Object(id=gid))
                print(f"🔁 Synced {len(synced)} commands to guild {gid}")
        else:
            synced = await bot.tree.sync()
            print(f"🌐 Synced {len(synced)} global commands")
    except Exception as e:
        print(f"❌ Error syncing commands: {e}")

async def main():
    initial_extensions = [
        "cogs.summarize",
        "cogs.ask"
    ]

    for ext in initial_extensions:
        await bot.load_extension(ext)

    await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
