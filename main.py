import discord
import openai
import os
from discord.ext import commands
from datetime import datetime, timedelta, UTC

# Load environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Set up bot
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)
tree = bot.tree  # Slash command tree

@tree.command(name="summarize", description="Summarizes messages from the past X hours in this channel")
async def summarize(interaction: discord.Interaction, hours: int = 24):  
    """Summarizes messages from the past 'hours' (default 24) in the channel."""

    await interaction.response.defer()  # Acknowledge interaction to avoid timeout

    # Validate input (Discord commands enforce positive integers, but adding extra safety)
    if hours <= 0:
        await interaction.followup.send("Please enter a positive number of hours.")
        return

    channel = interaction.channel
    now = datetime.now(UTC)
    lookback_time = now - timedelta(hours=hours)  # Dynamically set lookback period

    messages = []
    async for message in channel.history(limit=1000, after=lookback_time):
        messages.append(f"{message.author.name}: {message.content}")

    if not messages:
        await interaction.followup.send(f"No messages from the past {hours} hours to summarize.")
        return

    text = "\n".join(messages)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Summarize the following Discord conversation in a bullet-point list highlighting key topics."},
            {"role": "user", "content": text}
        ]
    )

    summary = response.choices[0].message.content

    await interaction.followup.send(f"**Summary of the last {hours} hours:**\n{summary}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await tree.sync()
        print(f"Synced {len(synced)} command(s) successfully.")
    except Exception as e:
        print(f"Error syncing commands: {e}")

bot.run(DISCORD_TOKEN)
