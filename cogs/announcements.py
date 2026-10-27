import discord
from discord.ext import commands
from discord import app_commands
from config import COLOR_PRIMARY, COLOR_SUCCESS, COLOR_ERROR, COLOR_GOLD, ADMIN_ROLE_ID, ANNOUNCEMENT_CHANNEL_ID
from utils.database import get_active_tournament, get_all_teams, get_all_matches, get_team
from utils.rulebook import RULES, FULL_RULES_SHORT, TOURNAMENT_NAME, ORGANIZER, GAME, FORMAT, REGION


def is_admin():
    async def predicate(interaction: discord.Interaction) -> bool:
        role = interaction.guild.get_role(ADMIN_ROLE_ID)
        if role and role in interaction.user.roles:
            return True
        if interaction.user.guild_permissions.administrator:
            return True
        await interaction.response.send_message(
            embed=discord.Embed(
                title="❌ Access Denied",
                description="You need the **Tournament Admin** role.",
                color=COLOR_ERROR
            ), ephemeral=True
        )
        return False
    return app_commands.check(predicate)


# ── Rulebook Navigation View ──────────────────────────────────────────────────
class RulebookView(discord.ui.View):
    def __init__(self, sections: list, current: int = 0):
        super().__init__(timeout=120)
        self.sections = sections
        self.current = current
        self._update_buttons()

    def _update_buttons(self):
        self.clear_items()
        # Prev button
        prev = discord.ui.Button(
            label="◀ Previous",
            style=discord.ButtonStyle.secondary,
            disabled=(self.current == 0),
            custom_id="prev"
        )
        prev.callback = self.prev_callback
        self.add_item(prev)

        # Page indicator
        page_btn = discord.ui.Button(
            label=f"{self.current + 1} / {len(self.sections)}",
            style=discord.ButtonStyle.primary,
            disabled=True,
            custom_id="page"
        )
        self.add_item(page_btn)

        # Next button
        nxt = discord.ui.Button(
            label="Next ▶",
            style=discord.ButtonStyle.secondary,
            disabled=(self.current == len(self.sections) - 1),
            custom_id="next"
        )
        nxt.callback = self.next_callback
        self.add_item(nxt)

    def build_embed(self) -> discord.Embed:
        key = self.sections[self.current]
        section = RULES[key]
        embed = discord.Embed(
            title=section["title"],
            description=section["content"],
            color=COLOR_GOLD
        )
        embed.set_author(name=f"📘 {TOURNAMENT_NAME} Official Rulebook")
        embed.set_footer(text=f"ZenX Esports | Section {self.current + 1} of {len(self.sections)}")
        return embed

    async def prev_callback(self, interaction: discord.Interaction):
        self.current -= 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    async def next_callback(self, interaction: discord.Interaction):
        self.current += 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)


# ── Section Select View ───────────────────────────────────────────────────────
class RulebookSectionSelect(discord.ui.Select):
    def __init__(self, sections: list):
        self.sections = sections
        options = [
            discord.SelectOption(
                label=RULES[k]["title"].replace("📋 ", "").replace("✅ ", "")
                    .replace("📝 ", "").replace("⚔️ ", "").replace("🎮 ", "")
                    .replace("🗺️ ", "").replace("🤝 ", "").replace("💻 ", "")
                    .replace("❌ ", "").replace("💰 ", "").replace("🔧 ", "")
                    .replace("📜 ", ""),
                value=k,
                description=f"View {k.replace('_', ' ').title()} rules",
                emoji=RULES[k]["title"].split(" ")[0]
            )
            for k in sections
        ]
        super().__init__(placeholder="Jump to a section...", options=options)

    async def callback(self, interaction: discord.Interaction):
        idx = self.sections.index(self.values[0])
        view = RulebookView(self.sections, idx)
        await interaction.response.edit_message(embed=view.build_embed(), view=view)


class RulebookSelectView(discord.ui.View):
    def __init__(self, sections: list):
        super().__init__(timeout=120)
        self.add_item(RulebookSectionSelect(sections))


class Announcements(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ── /announce ────────────────────────────────────────────────────────────
    @app_commands.command(name="announce", description="[Admin] Send a custom announcement to the announcement channel.")
    @app_commands.describe(
        title="Announcement title",
        message="Announcement message",
        ping_everyone="Ping @everyone with this announcement"
    )
    @is_admin()
    async def announce(
        self,
        interaction: discord.Interaction,
        title: str,
        message: str,
        ping_everyone: bool = False
    ):
        await interaction.response.defer(ephemeral=True)

        ann_channel = interaction.guild.get_channel(ANNOUNCEMENT_CHANNEL_ID)
        if not ann_channel:
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ Announcement Channel Not Set",
                description="Set `ANNOUNCEMENT_CHANNEL_ID` in your `.env` file.",
                color=COLOR_ERROR
            ))

        embed = discord.Embed(
            title=f"📢 {title}",
            description=message,
            color=COLOR_GOLD
        )
        embed.set_footer(text=f"Announced by {interaction.user.display_name} | ZenX Esports")

        content = "@everyone" if ping_everyone else None
        await ann_channel.send(content=content, embed=embed)

        await interaction.followup.send(embed=discord.Embed(
            title="✅ Announcement Sent",
            description=f"Message posted in {ann_channel.mention}.",
            color=COLOR_SUCCESS
        ))

    # ── /rules ───────────────────────────────────────────────────────────────
    @app_commands.command(name="rules", description="View the ZENX ICE AGE official tournament rulebook.")
    async def rules(self, interaction: discord.Interaction):
        await interaction.response.defer()

        sections = list(RULES.keys())
        view = RulebookView(sections, 0)

        intro = discord.Embed(
            title=f"📘 {TOURNAMENT_NAME} — Official Rulebook",
            description=(
                f"**Organizer:** {ORGANIZER}\n"
                f"**Game:** {GAME} | **Format:** {FORMAT}\n"
                f"**Region:** {REGION} | **Platform:** PC\n\n"
                f"Use the **◀ ▶ buttons** to navigate sections, or the dropdown to jump directly.\n\n"
                f"> *\"SAME GAME. BIGGER GRIND.\"*"
            ),
            color=COLOR_GOLD
        )
        intro.set_footer(text=f"Rulebook v2.0 | {len(sections)} sections")

        await interaction.followup.send(embed=intro)

        # Send first section with navigation
        section_view = RulebookView(sections, 0)
        select_view = RulebookSelectView(sections)

        await interaction.channel.send(embed=section_view.build_embed(), view=section_view)
        await interaction.channel.send(view=select_view, content="**Jump to a section:**")

    # ── /rules_section ───────────────────────────────────────────────────────
    @app_commands.command(name="rules_section", description="View a specific section of the tournament rules.")
    @app_commands.describe(section="The rulebook section to view")
    @app_commands.choices(section=[
        app_commands.Choice(name="📋 Tournament Overview", value="overview"),
        app_commands.Choice(name="✅ Eligibility", value="eligibility"),
        app_commands.Choice(name="📝 Registration", value="registration"),
        app_commands.Choice(name="⚔️ Tournament Format", value="format"),
        app_commands.Choice(name="🎮 Match Rules", value="match_rules"),
        app_commands.Choice(name="🗺️ Map Veto Process", value="map_veto"),
        app_commands.Choice(name="🤝 Player Conduct", value="conduct"),
        app_commands.Choice(name="💻 Technical Requirements", value="technical"),
        app_commands.Choice(name="❌ Disqualification", value="disqualification"),
        app_commands.Choice(name="💰 Prizes & Payments", value="prizes"),
        app_commands.Choice(name="🔧 Administration & Appeals", value="admin"),
        app_commands.Choice(name="📜 Acceptance & Agreement", value="acceptance"),
    ])
    async def rules_section(self, interaction: discord.Interaction, section: str):
        await interaction.response.defer()

        rule = RULES.get(section)
        if not rule:
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ Section Not Found", color=COLOR_ERROR
            ))

        embed = discord.Embed(
            title=rule["title"],
            description=rule["content"],
            color=COLOR_GOLD
        )
        embed.set_author(name=f"📘 {TOURNAMENT_NAME} Official Rulebook")
        embed.set_footer(text="ZenX Esports | Use /rules to browse all sections")
        await interaction.followup.send(embed=embed)

    # ── /prize ───────────────────────────────────────────────────────────────
    @app_commands.command(name="prize", description="View the current tournament prize pool.")
    async def prize(self, interaction: discord.Interaction):
        await interaction.response.defer()

        tournament = get_active_tournament()
        embed = discord.Embed(
            title=f"💰 Prize Pool — {tournament['name'] if tournament else TOURNAMENT_NAME}",
            description=tournament["prize_pool"] if tournament and tournament.get("prize_pool") else "Prize pool details will be announced soon. Stay tuned! 🏆",
            color=COLOR_GOLD
        )
        embed.add_field(
            name="⚠️ Payment Security",
            value="ZenX Esports will only share payment details through **official channels**. Never share your passwords with anyone.",
            inline=False
        )
        embed.set_footer(text="ZenX Esports | ZENX ICE AGE")
        await interaction.followup.send(embed=embed)

    # ── /tournament_info ─────────────────────────────────────────────────────
    @app_commands.command(name="tournament_info", description="View current tournament information and status.")
    async def tournament_info(self, interaction: discord.Interaction):
        await interaction.response.defer()

        tournament = get_active_tournament()

        embed = discord.Embed(
            title=f"🏆 {tournament['name'] if tournament else TOURNAMENT_NAME}",
            color=COLOR_GOLD
        )

        if tournament:
            teams = get_all_teams(tournament["id"])
            checked_in = sum(1 for t in teams if t["checked_in"])
            status_icons = {
                "registration": "📝 Registration Open",
                "checkin": "✅ Check-in Phase",
                "active": "⚔️ Tournament Active",
                "completed": "🏆 Tournament Complete",
                "cancelled": "❌ Cancelled"
            }
            embed.description = status_icons.get(tournament["status"], tournament["status"])
            embed.add_field(name="🎮 Game", value=tournament["game"], inline=True)
            embed.add_field(name="👥 Team Size", value=f"{tournament['team_size']}v{tournament['team_size']}", inline=True)
            embed.add_field(name="💰 Prize Pool", value=tournament["prize_pool"] or "TBD", inline=True)
            embed.add_field(name="📋 Teams", value=f"{len(teams)} / {tournament['max_teams']}", inline=True)
            embed.add_field(name="✅ Checked In", value=str(checked_in), inline=True)
        else:
            embed.description = (
                f"**Organizer:** {ORGANIZER}\n"
                f"**Game:** {GAME} | **Format:** {FORMAT}\n"
                f"**Region:** {REGION} | **Platform:** PC\n\n"
                "No active tournament right now. Stay tuned for announcements!"
            )

        embed.add_field(
            name="📱 Official Channels",
            value=(
                "🔹 Instagram: [@zenx.0fficial](https://instagram.com/zenx.0fficial)\n"
                "🔹 YouTube: [@ZenXeSportz](https://youtube.com/@ZenXeSportz)\n"
                "🔹 Facebook: [Zenx officiall](https://facebook.com/zenxofficiall)"
            ),
            inline=False
        )
        embed.set_footer(text="ZenX Esports | ZENX ICE AGE v2.0")
        await interaction.followup.send(embed=embed)

    # ── /leaderboard ─────────────────────────────────────────────────────────
    @app_commands.command(name="leaderboard", description="View tournament standings / leaderboard.")
    async def leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer()

        tournament = get_active_tournament()
        if not tournament:
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ No Active Tournament", color=COLOR_ERROR
            ))

        all_matches = get_all_matches(tournament["id"])
        teams = get_all_teams(tournament["id"])

        wins = {}
        for match in all_matches:
            if match["winner_id"]:
                wins[match["winner_id"]] = wins.get(match["winner_id"], 0) + 1

        active = [t for t in teams if not t["eliminated"]]
        sorted_active = sorted(active, key=lambda t: wins.get(t["id"], 0), reverse=True)

        embed = discord.Embed(
            title=f"🏅 Leaderboard — {tournament['name']}",
            color=COLOR_GOLD
        )

        if sorted_active:
            medals = ["🥇", "🥈", "🥉"]
            active_lines = []
            for i, team in enumerate(sorted_active):
                medal = medals[i] if i < 3 else f"`{i+1}.`"
                w = wins.get(team["id"], 0)
                active_lines.append(f"{medal} **{team['name']}** — {w} win(s)")
            embed.add_field(name="🟢 Still In", value="\n".join(active_lines), inline=False)

        elim_teams = [t for t in get_all_teams(tournament["id"]) if t["eliminated"]]
        if elim_teams:
            elim_lines = [f"❌ ~~{t['name']}~~" for t in elim_teams[:15]]
            embed.add_field(name="💀 Eliminated", value="\n".join(elim_lines), inline=False)

        embed.set_footer(text="ZenX Esports | ZENX ICE AGE")
        await interaction.followup.send(embed=embed)

    # ── /help ────────────────────────────────────────────────────────────────
    @app_commands.command(name="help", description="View all available tournament bot commands.")
    async def help(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        embed = discord.Embed(
            title="🤖 ZENX ICE AGE — Bot Commands",
            description="Everything you need to participate in the tournament:",
            color=COLOR_PRIMARY
        )

        embed.add_field(
            name="📝 Registration",
            value=(
                "`/register` — Register your team (5 players)\n"
                "`/unregister` — Withdraw your team\n"
                "`/checkin` — Check in before the tournament starts\n"
                "`/teams` — View all registered teams\n"
                "`/myteam` — View your team details"
            ),
            inline=False
        )
        embed.add_field(
            name="🏆 Tournament",
            value=(
                "`/bracket` — View the bracket\n"
                "`/pending` — View pending matches\n"
                "`/match_info` — View match details\n"
                "`/tournament_info` — Tournament info & status\n"
                "`/leaderboard` — View standings"
            ),
            inline=False
        )
        embed.add_field(
            name="📘 Rules & Info",
            value=(
                "`/rules` — Browse the full official rulebook\n"
                "`/rules_section` — Jump to a specific rule section\n"
                "`/prize` — View prize pool info"
            ),
            inline=False
        )
        embed.add_field(
            name="🔧 Admin Only",
            value=(
                "`/tournament_create` `/open_checkin` `/start_tournament`\n"
                "`/report_win` `/seed_team` `/kick_team`\n"
                "`/update_prize` `/update_rules` `/announce`\n"
                "`/tournament_end` `/cancel_tournament`"
            ),
            inline=False
        )
        embed.add_field(
            name="📱 Official Channels",
            value=(
                "Instagram: @zenx.0fficial | YouTube: @ZenXeSportz | Facebook: Zenx officiall"
            ),
            inline=False
        )
        embed.set_footer(text="ZenX Esports | ZENX ICE AGE | Built with discord.py ❤️")
        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Announcements(bot))
