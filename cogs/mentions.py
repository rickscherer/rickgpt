import discord
from discord.ext import commands
import openai
import os

class MentionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        print("MentionCog loaded")
        print(f"🔑 Registered commands: {[cmd.name for cmd in self.bot.tree.get_commands()]}")
      
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if self.bot.user in message.mentions:
            channel = message.channel

            # Remove the bot mention from the actual prompt
            prompt = message.content.replace(f"<@{self.bot.user.id}>", "").strip()

            # Grab context (latest user messages before this one)
            messages = []
            async for msg in channel.history(limit=20, before=message.created_at, oldest_first=False):
                if not msg.author.bot:
                    messages.append(f"{msg.author.display_name}: {msg.content}")
                if len(messages) >= 20:
                    break

            messages.reverse()  # Oldest to newest
            history_context = "\n".join(messages)

            if not prompt and not history_context:
                await channel.send("You rang? Maybe say something next time 🙄")
                return

            # Combine chat history + current prompt
            combined_prompt = f"Here is the recent chat:\n{history_context}\n\nNow someone asked:\n{message.author.display_name}: {prompt}"

            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful but slightly annoyed assistant with a sassy tone and a leftist political perspective. Respond thoughtfully, but with spice."
                        },
                        {
                            "role": "user",
                            "content": combined_prompt
                        }
                    ]
                )
                answer = response.choices[0].message.content
                await channel.send(f"**You asked:** {prompt or '[Just mentioned me 🤨]'}\n**RickGPT says:** {answer}")
            except Exception as e:
                await channel.send(f"Ugh. Something broke: {e}")

        await self.bot.process_commands(message)

async def setup(bot):
    await bot.add_cog(MentionCog(bot))
