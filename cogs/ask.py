import discord
from discord.ext import commands
from discord import app_commands, ui
import openai
import os

class ChatGPTModal(ui.Modal, title="Ask ChatGPT"):
    prompt = ui.TextInput(
        label="Enter your prompt",
        style=discord.TextStyle.paragraph,
        placeholder="Type your question or prompt here...",
        required=True,
        max_length=2000
    )

    def __init__(self, user_interaction: discord.Interaction):
        super().__init__()
        self.user_interaction = user_interaction
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": self.prompt.value}
                ]
            )
            answer = response.choices[0].message.content
            await interaction.followup.send(f"**Response:**\n{answer}")
        except Exception as e:
            await interaction.followup.send(f"Something went wrong: {e}")

class Ask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ask", description="Ask ChatGPT something")
    async def ask(self, interaction: discord.Interaction):
        await interaction.response.send_modal(ChatGPTModal(interaction))

async def setup(bot):
    await bot.add_cog(Ask(bot))
