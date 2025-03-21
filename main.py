import os
import discord
import openai
from discord.ext import commands
from datetime import datetime, timedelta

# Load environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Set up OpenAI API
openai.api_key = OPENAI_API_KEY

# Set up Discord bot
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command(name="summarize")
async def summarize(ctx):
    channel = ctx.channel
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)
    
    messages = []
    async for message in channel.history(limit=1000, after=yesterday):
        messages.append(f"{message.author.name}: {message.content}")
    
    if not messages:
        await ctx.send("No messages from the past 24 hours to summarize.")
        return
    
    text = "\n".join(messages)
    
    # Send to OpenAI for summarization
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Summarize the following Discord conversation."},
            {"role": "user", "content": text}
        ]
    )
    
    summary = response["choices"][0]["message"]["content"]
    
    await ctx.send(f"**Summary of the last 24 hours:**\n{summary}")

# Run bot
bot.run(DISCORD_TOKEN)
