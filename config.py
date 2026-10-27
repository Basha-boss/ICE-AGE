import os
from dotenv import load_dotenv

load_dotenv()

# Bot configuration
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", 0))
ADMIN_ROLE_ID = int(os.getenv("ADMIN_ROLE_ID", 0))
ANNOUNCEMENT_CHANNEL_ID = int(os.getenv("ANNOUNCEMENT_CHANNEL_ID", 0))
TOURNAMENT_CHANNEL_ID = int(os.getenv("TOURNAMENT_CHANNEL_ID", 0))

# Tournament settings — ZENX ICE AGE defaults
MAX_TEAMS = 16          # 16-team single elimination bracket
MIN_TEAM_SIZE = 5       # Minimum players per team (5v5 VALORANT)
MAX_TEAM_SIZE = 7       # Max 7 per roster (5 starters + 2 subs)
CHECKIN_DURATION = 30   # Check-in window in minutes before tournament start

# Embed colors
COLOR_PRIMARY   = 0x5865F2   # Discord blurple
COLOR_SUCCESS   = 0x57F287   # Green
COLOR_WARNING   = 0xFEE75C   # Yellow
COLOR_ERROR     = 0xED4245   # Red
COLOR_INFO      = 0x5865F2   # Blurple
COLOR_GOLD      = 0xFFD700   # Gold

# Database
DB_PATH = "tournament.db"
