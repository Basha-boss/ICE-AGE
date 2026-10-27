# 🏆 Discord Tournament Bot

A fully-featured Discord Tournament Bot built with Python (`discord.py`) supporting **Single Elimination** brackets, team registration, seeding, check-in, automated announcements, and prize pool tracking.

---

## 📋 Features

| Feature | Command |
|---|---|
| Team Registration | `/register` |
| Team Check-in | `/checkin` |
| Auto Bracket Generation | `/start_tournament` |
| Match Reporting | `/report_win` |
| Seeding | `/seed_team` |
| Prize Pool | `/prize`, `/update_prize` |
| DM Notifications | Automatic on match start |
| Announcements | `/announce` |
| Admin Controls | Full admin suite |

---

## 🚀 Setup

### 1. Install Dependencies
```bash
cd tournament-bot
pip install -r requirements.txt
```

### 2. Create `.env` File
Copy `.env.example` to `.env` and fill in your values:
```bash
copy .env.example .env
```

```env
DISCORD_TOKEN=your_bot_token_here
GUILD_ID=your_server_id_here
ADMIN_ROLE_ID=your_admin_role_id_here
ANNOUNCEMENT_CHANNEL_ID=your_announcement_channel_id_here
TOURNAMENT_CHANNEL_ID=your_tournament_channel_id_here
```

### 3. Get Your Bot Token
1. Go to https://discord.com/developers/applications
2. Create a New Application
3. Go to **Bot** → **Reset Token** → copy the token
4. Enable **SERVER MEMBERS INTENT** and **MESSAGE CONTENT INTENT**

### 4. Invite the Bot
Use this URL (replace `CLIENT_ID`):
```
https://discord.com/oauth2/authorize?client_id=CLIENT_ID&permissions=8&scope=bot+applications.commands
```

### 5. Run the Bot
```bash
python bot.py
```

---

## 🗂️ Project Structure

```
tournament-bot/
├── bot.py                  # Main entry point
├── config.py               # Configuration
├── requirements.txt        # Dependencies
├── .env.example            # Environment template
├── cogs/
│   ├── registration.py     # /register /unregister /checkin /teams /myteam
│   ├── tournament.py       # /bracket /pending /match_info /report_win
│   ├── admin.py            # Full admin command suite
│   └── announcements.py    # /announce /rules /prize /leaderboard /help
└── utils/
    ├── database.py         # SQLite CRUD layer
    └── bracket.py          # Bracket generation logic
```

---

## 🎮 Tournament Flow

```
1. Admin: /tournament_create  →  Registration opens
2. Players: /register         →  Teams sign up
3. Admin: /seed_team          →  (Optional) Set seedings
4. Admin: /open_checkin       →  Check-in phase begins
5. Players: /checkin          →  Teams confirm attendance
6. Admin: /start_tournament   →  Bracket generated, DMs sent
7. Admin: /report_win         →  Record match results
8. (Repeat step 7 each round)
9. Admin: /tournament_end     →  Announce champion!
```

---

## ⚙️ Configuration

Edit `config.py` to adjust:
- `MAX_TEAMS` — Maximum bracket size
- `MIN_TEAM_SIZE` / `MAX_TEAM_SIZE` — Team composition limits
- `CHECKIN_DURATION` — Check-in window duration
- Embed colors

---

## 🔒 Permissions Required

The bot needs these Discord permissions:
- `Send Messages`
- `Embed Links`
- `Read Message History`
- `Send Messages in Threads`
- `Use Slash Commands`
- `Manage Channels` (optional, for auto-creating channels)
