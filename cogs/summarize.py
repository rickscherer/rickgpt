import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta, UTC
import openai
import os

class SummarizeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print(f"🔑 Registered commands: {[cmd.name for cmd in self.bot.tree.get_commands()]}")

        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    @app_commands.command(name="summarize", description="Summarizes messages from the past X hours")
    async def summarize(self, interaction: discord.Interaction, hours: int = 24):
        await interaction.response.defer()
        
        if hours <= 0:
            await interaction.followup.send("Please enter a positive number of hours.")
            return

        channel = interaction.channel
        now = datetime.now(UTC)
        lookback_time = now - timedelta(hours=hours)

        messages = []
        async for message in channel.history(limit=1000, after=lookback_time):
            messages.append(f"{message.author.name}: {message.content}")

        if not messages:
            await interaction.followup.send(f"No messages from the past {hours} hours to summarize.")
            return

        text = "\n".join(messages)

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Summarize the following Discord chatroom. "},
                {"role": "user", "content": text}
            ]
        )

        summary = response.choices[0].message.content
        await interaction.followup.send(f"**Summary of the last {hours} hours:**\n{summary}")

async def setup(bot):
    await bot.add_cog(SummarizeCog(bot))
