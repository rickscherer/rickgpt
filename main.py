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

@tree.command(name="summarize", description="Summarizes the last 24 hours of messages in this channel")
async def summarize(interaction: discord.Interaction):
    channel = interaction.channel
    now = datetime.now(UTC)  # ✅ Fixed UTC time handling
    yesterday = now - timedelta(days=1)

    messages = []
    async for message in channel.history(limit=1000, after=yesterday):
        messages.append(f"{message.author.name}: {message.content}")

    if not messages:
        await interaction.response.send_message("No messages from the past 24 hours to summarize.", ephemeral=True)
        return

    text = "\n".join(messages)

    # ✅ Updated OpenAI API call
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Summarize the following Discord conversation, provide me with a bullet point list highlighting the top topics."},
            {"role": "user", "content": text}
        ]
    )

    summary = response.choices[0].message.content

    await interaction.response.send_message(f"**Summary of the last 24 hours:**\n{summary}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await tree.sync()
        print(f"Synced {len(synced)} command(s) successfully.")
    except Exception as e:
        print(f"Error syncing commands: {e}")

bot.run(DISCORD_TOKEN)
