import discord
import asyncio
import logging
import sys
from discord.ext import commands
from config import DISCORD_TOKEN, GUILD_ID
from utils.database import init_db

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8")
    ]
)
log = logging.getLogger("TournamentBot")

# ── Intents ───────────────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.members = True
intents.message_content = True


class TournamentBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",   # Prefix kept but slash commands are primary
            intents=intents,
            help_command=None
        )
        self.guild_id = GUILD_ID

    async def setup_hook(self):
        # Load all cogs
        cogs = [
            "cogs.registration",
            "cogs.tournament",
            "cogs.admin",
            "cogs.announcements",
        ]
        for cog in cogs:
            try:
                await self.load_extension(cog)
                log.info(f"Loaded cog: {cog}")
            except Exception as e:
                log.error(f"Failed to load cog {cog}: {e}")

        # Sync slash commands to guild (instant) and globally
        guild = discord.Object(id=self.guild_id) if self.guild_id else None
        if guild:
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            log.info(f"Slash commands synced to guild {self.guild_id}")
        else:
            await self.tree.sync()
            log.info("Slash commands synced globally (may take up to 1 hour)")

    async def on_ready(self):
        log.info(f"Bot ready! Logged in as {self.user} (ID: {self.user.id})")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="🏆 Tournaments | /help"
            )
        )

    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            return  # Already handled in predicates
        log.error(f"Slash command error: {error}")
        try:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="❌ An Error Occurred",
                    description=str(error),
                    color=0xED4245
                ),
                ephemeral=True
            )
        except Exception:
            pass


# Re-import for error handling
from discord import app_commands


async def main():
    init_db()
    bot = TournamentBot()

    if not DISCORD_TOKEN:
        log.error("DISCORD_TOKEN not set! Create a .env file from .env.example")
        sys.exit(1)

    async with bot:
        await bot.start(DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
