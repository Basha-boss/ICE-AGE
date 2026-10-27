"""
ZENX ICE AGE — Official Tournament Rulebook (v2.0)
Parsed and embedded from the official rulebook document.
"""

TOURNAMENT_NAME = "ZENX ICE AGE"
ORGANIZER = "ZenX Esports"
GAME = "VALORANT"
FORMAT = "5v5 Single Elimination"
REGION = "India"
PLATFORM = "PC"
MAX_TEAMS = 16

# ── Full rulebook sections ───────────────────────────────────────────────────
RULES = {
    "overview": {
        "title": "📋 Tournament Overview",
        "content": (
            "The **ZENX ICE AGE** Tournament is an online 5v5 VALORANT community competition organized by **ZenX Esports**.\n\n"
            "The tournament provides Indian VALORANT players and teams with a **competitive, organized and fair environment**.\n\n"
            "**Format:** 16-team Single Elimination bracket played over two days.\n"
            "**Region:** India | **Platform:** PC\n\n"
            "> *\"SAME GAME. BIGGER GRIND.\"*\n\n"
            "⚠️ This is an **independent** community competition — not affiliated with, sponsored by, or endorsed by Riot Games or VALORANT Esports."
        )
    },
    "eligibility": {
        "title": "✅ Eligibility",
        "content": (
            "• Players must have a valid **VALORANT PC account** in the **India region**.\n"
            "• Each team must have **5 registered players** (a starting five) and may include **up to 2 substitutes** (max 7 per roster).\n"
            "• All players must be registered before the registration deadline.\n"
            "• A player may only compete for **one team** in this tournament.\n"
            "• Players must follow the **Riot Games Terms of Service** and VALORANT game rules at all times.\n"
            "• Teams must have a designated **Team Captain** who will be the primary contact with ZenX Esports."
        )
    },
    "registration": {
        "title": "📝 Registration",
        "content": (
            "• Registration is open during the announced registration window.\n"
            "• Teams must submit a complete roster before the deadline.\n"
            "• Each player must provide their **VALORANT in-game name (IGN)** and **Riot ID**.\n"
            "• Incomplete or inaccurate registrations may be rejected.\n"
            "• The Team Captain is responsible for the accuracy of all submitted information.\n"
            "• ZenX Esports reserves the right to verify player eligibility.\n"
            "• Roster changes after registration closes require organizer approval."
        )
    },
    "format": {
        "title": "⚔️ Tournament Format",
        "content": (
            "• **Format:** Single Elimination (16 teams)\n"
            "• **Match Format:** Best of 1 (BO1) for group/early rounds; **Best of 3 (BO3)** for Semi-Finals and Finals.\n"
            "• **Map Selection:** Standard competitive map pool; veto process applies.\n"
            "• **Server:** Official Riot India servers.\n"
            "• **Game Mode:** Standard Competitive (Tournament Custom).\n"
            "• **Bracket:** Will be published after registration closes.\n"
            "• Byes may be assigned if fewer than 16 teams are confirmed."
        )
    },
    "match_rules": {
        "title": "🎮 Match Rules",
        "content": (
            "• Teams must be **ready to play at the scheduled match time**.\n"
            "• A grace period of **10 minutes** is allowed before a forfeit is declared.\n"
            "• Teams must have a **minimum of 5 players** to start a match (no stand-ins without approval).\n"
            "• **Lobby creation:** The higher-seeded or designated team creates the custom lobby.\n"
            "• All players must use their **registered VALORANT accounts** — no smurfing or account sharing.\n"
            "• **Cheating, hacking, or use of unauthorized software** results in immediate disqualification.\n"
            "• Match results must be reported to the tournament admin with **screenshot proof**.\n"
            "• In the event of a dispute, administrators have final authority."
        )
    },
    "map_veto": {
        "title": "🗺️ Map Veto Process",
        "content": (
            "**Best of 1:**\n"
            "• Team 1 bans 1 map → Team 2 bans 1 map → Team 1 bans 1 → Team 2 bans 1 → Team 1 bans 1 → Team 2 bans 1 → Remaining map is played.\n\n"
            "**Best of 3:**\n"
            "• Team 1 bans 1 → Team 2 bans 1 → Team 1 picks 1 → Team 2 picks 1 → Team 1 bans 1 → Team 2 bans 1 → Remaining map is played as Map 3 (if needed).\n\n"
            "• Coin flip or seeding determines which team is 'Team 1' for veto purposes.\n"
            "• Map veto must be completed within **5 minutes** of match time."
        )
    },
    "conduct": {
        "title": "🤝 Player Conduct",
        "content": (
            "All participants must maintain **respectful behavior** at all times:\n\n"
            "• No harassment, hate speech, or discriminatory language.\n"
            "• No excessive toxicity, flaming, or unsportsmanlike conduct.\n"
            "• No intentional feeding, throwing, or match manipulation.\n"
            "• Treat all players, admins, and spectators with respect.\n"
            "• **Violations may result in:** warnings → match forfeit → disqualification → tournament ban.\n\n"
            "ZenX Esports reserves the right to penalize any conduct that damages the tournament's integrity."
        )
    },
    "technical": {
        "title": "💻 Technical Requirements",
        "content": (
            "Each player is responsible for:\n"
            "• **Working PC** with VALORANT installed and updated.\n"
            "• **Stable internet connection** — connection failures are the player's responsibility.\n"
            "• **Updated VALORANT client** (latest patch).\n"
            "• **Functional peripherals** (keyboard, mouse, headset).\n"
            "• **Microphone** (required for in-game communication).\n"
            "• **Discord access** for tournament communication.\n\n"
            "ZenX Esports is **not responsible** for personal hardware or internet failures.\n\n"
            "**Disconnections:** If a player disconnects, the team may continue if the game state permits. Repeated failures may result in forfeit."
        )
    },
    "disqualification": {
        "title": "❌ Disqualification",
        "content": (
            "A team **may be disqualified** for:\n"
            "• Cheating / hacking / use of unauthorized software.\n"
            "• Match fixing or fraud.\n"
            "• Impersonation of players.\n"
            "• Serious harassment or misconduct.\n"
            "• Using **unregistered or unauthorized players**.\n"
            "• Refusing administrator instructions.\n"
            "• Providing **false registration information**.\n"
            "• Conduct that materially damages tournament integrity.\n\n"
            "**Disqualification after winning:** ZenX Esports may remove the team from final standings, reassign standings, and withhold prize payment."
        )
    },
    "prizes": {
        "title": "💰 Prize Pool & Payments",
        "content": (
            "• Prize pool details will be announced officially by ZenX Esports.\n"
            "• Prizes are paid to the **Team Captain** on behalf of the team.\n"
            "• Payment details will be shared through **official ZenX channels only**.\n"
            "• Prize money **may be forfeited** if a team is found to have violated a serious rule.\n"
            "• Verify all payment information before any transfers — ZenX will never request passwords.\n\n"
            "⚠️ Never share your Riot password, email password, MFA code, or recovery code with anyone."
        )
    },
    "admin": {
        "title": "🔧 Administration & Appeals",
        "content": (
            "• ZenX Esports administrators have **final authority** over all tournament decisions.\n"
            "• If an admin makes an error (incorrect bracket placement, score, match time), it will be corrected as soon as reasonably possible.\n"
            "• **Rule changes** may be made due to: Riot policy changes, game updates, legal requirements, or unforeseen circumstances. Material changes will be communicated.\n"
            "• **Force Majeure:** ZenX is not responsible for delays caused by major internet outages, platform failures, natural disasters, or government restrictions.\n"
            "• Only information published through **official ZenX channels** is considered official."
        )
    },
    "acceptance": {
        "title": "📜 Acceptance & Agreement",
        "content": (
            "By registering for ZENX ICE AGE, all teams acknowledge that:\n\n"
            "• They have **read and understood** these rules.\n"
            "• They agree to follow all tournament rules.\n"
            "• All registered players agree to follow these rules.\n"
            "• They will follow **administrator instructions**.\n"
            "• Serious violations can result in **disqualification**.\n"
            "• ZenX Esports has **final authority** over tournament administration.\n\n"
            "**Team Captain Confirmation:**\n"
            "*\"I confirm that I have read and understood the ZENX ICE AGE Tournament Rulebook and agree that my team and its registered players will follow all tournament rules, Riot Games requirements, and instructions issued by ZenX Esports.\"*"
        )
    }
}

# Quick-access full rulebook text for /rules command
FULL_RULES_SHORT = (
    "**ZENX ICE AGE** — Official Tournament Rules (v2.0)\n"
    "🎮 5v5 VALORANT | 🌏 India | 💻 PC | 16-Team Single Elimination\n\n"
    "Use the buttons below to view each section, or `/rules_full` for all sections."
)

RULE_SECTIONS = list(RULES.keys())
