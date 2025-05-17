import discord
from discord.ext import commands
from discord import app_commands, ui
import openai
import os

class ChatGPTModal(ui.Modal, title="Ask RickGPT"):
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

        # Capture the prompt value from the modal
        user_prompt = self.prompt.value

        try:
            # Send the user prompt to ChatGPT for processing
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You're the best personal assistant, use your full ability to respond to the request."},
                    {"role": "user", "content": user_prompt}
                ]
            )

            # Get the response from ChatGPT
            answer = response.choices[0].message.content

            # Send both the question and the response
            await interaction.followup.send(
                f"**Question:**\n{user_prompt}\n\n**Response:**\n{answer}"
            )

        except Exception as e:
            await interaction.followup.send(f"Something went wrong: {e}")

class AskCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("AskCog loaded")
        print(f"🔑 Registered commands: {[cmd.name for cmd in self.bot.tree.get_commands()]}")
    
    @app_commands.command(name="ask", description="Ask ChatGPT something")
    async def ask(self, interaction: discord.Interaction):
        await interaction.response.send_modal(ChatGPTModal(interaction))

async def setup(bot):
    await bot.add_cog(AskCog(bot))
