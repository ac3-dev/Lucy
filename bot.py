import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import keep_alive

# Reads the token securely from the environment/Render
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# --- SERVER CONFIGURATION (REPLACE WITH YOUR DISCORD IDS) ---
HONEYPOT_CHANNEL_ID = 1560512591304859719  # Replace with honeypot channel ID
EDGERUNNER_ROLE_ID = 1560511451624513596   # Replace with "Edgerunner" role ID

# Basic blocked phrases list
BLOCKED_WORDS = [
    "fuck",
    "nigger",
    "bitch",
]
# -------------------------------------------------------------

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class LucyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Starts the keep-alive server for 24/7 uptime on Render
        await keep_alive.start_server()
        await self.tree.sync()

bot = LucyBot()

@bot.event
async def on_ready():
    print(f"[SECURITY] Lucy online as {bot.user} (ID: {bot.user.id})")

# Auto-assign Edgerunner role on join
@bot.event
async def on_member_join(member: discord.Member):
    role = member.guild.get_role(EDGERUNNER_ROLE_ID)
    if role:
        try:
            await member.add_roles(role, reason="Lucy auto-role on join")
            print(f"Assigned {role.name} to {member.name}")
        except discord.Forbidden:
            print("Permission error: Lucy's role must be higher than the Edgerunner role in Server Settings.")

# Bot trap & chat filter
@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    # 1. Honeypot Trap
    if message.channel.id == HONEYPOT_CHANNEL_ID:
        try:
            await message.delete()
            duration = discord.utils.utcnow() + discord.utils.timedelta(days=1)
            await message.author.timeout(duration, reason="Triggered honeypot bot trap")
            print(f"Honeypot triggered by {message.author.name}. Timed out.")
        except discord.Forbidden:
            print("Permission error: Missing moderation permissions to timeout user.")
        return

    # 2. Chat Filter
    content_lower = message.content.lower()
    for bad_phrase in BLOCKED_WORDS:
        if bad_phrase in content_lower:
            try:
                await message.delete()
                await message.channel.send(
                    f"⚠️ {message.author.mention}, that message was removed by Lucy's security protocol.",
                    delete_after=5
                )
            except discord.Forbidden:
                print("Permission error: Missing 'Manage Messages' permission.")
            return

    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(TOKEN)
