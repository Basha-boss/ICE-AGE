import discord
from discord.ext import commands
from discord import app_commands
from config import (
    COLOR_PRIMARY, COLOR_SUCCESS, COLOR_ERROR, COLOR_WARNING, COLOR_GOLD,
    ADMIN_ROLE_ID, ANNOUNCEMENT_CHANNEL_ID
)
from utils.database import (
    create_tournament, get_active_tournament, get_all_teams,
    update_tournament_field, update_tournament_status,
    set_team_seed, get_team_by_name, get_team, get_team_members,
    unregister_team, get_all_matches, get_match, get_tournament
)
from utils.bracket import generate_bracket


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


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ── /tournament_create ───────────────────────────────────────────────────
    @app_commands.command(name="tournament_create", description="[Admin] Create a new tournament.")
    @app_commands.describe(
        name="Tournament name",
        game="Game being played",
        prize_pool="Prize pool description (e.g. $100, Discord Nitro)",
        rules="Tournament rules",
        max_teams="Maximum number of teams (4/8/16/32/64)",
        team_size="Players per team (1-5)"
    )
    @is_admin()
    async def tournament_create(
        self,
        interaction: discord.Interaction,
        name: str,
        game: str,
        prize_pool: str = "TBD",
        rules: str = "Standard rules apply.",
        max_teams: int = 16,
        team_size: int = 1
    ):
        await interaction.response.defer(ephemeral=True)

        existing = get_active_tournament()
        if existing:
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ Active Tournament Exists",
                description=f"**{existing['name']}** is already running. End it first with `/tournament_end`.",
                color=COLOR_ERROR
            ))

        if max_teams not in (4, 8, 16, 32, 64):
            max_teams = 16

        team_size = max(1, min(5, team_size))

        tid = create_tournament(name, game, prize_pool, rules, max_teams, team_size, interaction.user.id)

        embed = discord.Embed(
            title="🏆 Tournament Created!",
            description=f"**{name}** has been created and registration is now open!",
            color=COLOR_SUCCESS
        )
        embed.add_field(name="🎮 Game", value=game, inline=True)
        embed.add_field(name="👥 Team Size", value=f"{team_size} player(s)", inline=True)
        embed.add_field(name="🔢 Max Teams", value=str(max_teams), inline=True)
        embed.add_field(name="💰 Prize Pool", value=prize_pool, inline=True)
        embed.add_field(name="📋 Rules", value=rules[:500], inline=False)
        embed.set_footer(text=f"Tournament ID: {tid} | Use /announce to notify players")

        await interaction.followup.send(embed=embed)

        # Announce in announcement channel
        ann_channel = interaction.guild.get_channel(ANNOUNCEMENT_CHANNEL_ID)
        if ann_channel:
            pub_embed = discord.Embed(
                title=f"🏆 {name} — Registration Open!",
                description=f"A new tournament is starting! Register your team now.",
                color=COLOR_GOLD
            )
            pub_embed.add_field(name="🎮 Game", value=game, inline=True)
            pub_embed.add_field(name="👥 Team Size", value=f"{team_size} player(s)", inline=True)
            pub_embed.add_field(name="🔢 Max Teams", value=str(max_teams), inline=True)
            pub_embed.add_field(name="💰 Prize Pool", value=prize_pool, inline=True)
            pub_embed.add_field(name="📋 Rules", value=rules[:500], inline=False)
            pub_embed.add_field(name="📝 How to Register", value="Use `/register` to sign up your team!", inline=False)
            await ann_channel.send(embed=pub_embed)

    # ── /tournament_status ───────────────────────────────────────────────────
    @app_commands.command(name="tournament_status", description="View current tournament information.")
    async def tournament_status(self, interaction: discord.Interaction):
        await interaction.response.defer()

        tournament = get_active_tournament()
        if not tournament:
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ No Active Tournament",
                description="There is no active tournament right now.",
                color=COLOR_ERROR
            ))

        teams = get_all_teams(tournament["id"])
        checked_in = sum(1 for t in teams if t["checked_in"])

        status_icons = {
            "registration": "📝",
            "checkin": "✅",
            "active": "⚔️",
            "completed": "🏆",
            "cancelled": "❌"
        }
        icon = status_icons.get(tournament["status"], "❓")

        embed = discord.Embed(
            title=f"🏆 {tournament['name']}",
            description=f"{icon} **Status:** {tournament['status'].capitalize()}",
            color=COLOR_PRIMARY
        )
        embed.add_field(name="🎮 Game", value=tournament["game"], inline=True)
        embed.add_field(name="👥 Team Size", value=f"{tournament['team_size']}v{tournament['team_size']}", inline=True)
        embed.add_field(name="💰 Prize Pool", value=tournament["prize_pool"] or "TBD", inline=True)
        embed.add_field(name="📋 Teams", value=f"{len(teams)} / {tournament['max_teams']}", inline=True)
        embed.add_field(name="✅ Checked In", value=str(checked_in), inline=True)
        if tournament["rules"]:
            embed.add_field(name="📜 Rules", value=tournament["rules"][:500], inline=False)
        embed.set_footer(text=f"Tournament ID: {tournament['id']}")
        await interaction.followup.send(embed=embed)

    # ── /open_checkin ────────────────────────────────────────────────────────
    @app_commands.command(name="open_checkin", description="[Admin] Open check-in phase.")
    @is_admin()
    async def open_checkin(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        tournament = get_active_tournament()
        if not tournament or tournament["status"] != "registration":
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ Cannot Open Check-in",
                description="No tournament in registration phase.",
                color=COLOR_ERROR
            ))

        update_tournament_status(tournament["id"], "checkin")
        await interaction.followup.send(embed=discord.Embed(
            title="✅ Check-in Opened",
            description="Teams can now use `/checkin` to confirm their participation.",
            color=COLOR_SUCCESS
        ))

        ann_channel = interaction.guild.get_channel(ANNOUNCEMENT_CHANNEL_ID)
        if ann_channel:
            await ann_channel.send(embed=discord.Embed(
                title=f"✅ Check-in is NOW OPEN — {tournament['name']}",
                description="**All registered teams must check in using `/checkin` to secure their spot!**\nTeams that don't check in will be removed from the bracket.",
                color=COLOR_WARNING
            ))

    # ── /start_tournament ────────────────────────────────────────────────────
    @app_commands.command(name="start_tournament", description="[Admin] Generate bracket and start the tournament.")
    @is_admin()
    async def start_tournament(self, interaction: discord.Interaction):
        await interaction.response.defer()

        tournament = get_active_tournament()
        if not tournament:
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ No Active Tournament", color=COLOR_ERROR
            ))

        if tournament["status"] not in ("registration", "checkin"):
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ Cannot Start",
                description=f"Tournament is already **{tournament['status']}**.",
                color=COLOR_ERROR
            ))

        checked_in_teams = get_all_teams(tournament["id"], only_checked_in=(tournament["status"] == "checkin"))
        if len(checked_in_teams) < 2:
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ Not Enough Teams",
                description="You need at least **2 checked-in teams** to start.",
                color=COLOR_ERROR
            ))

        update_tournament_status(tournament["id"], "active")
        matches = generate_bracket(tournament["id"])

        embed = discord.Embed(
            title=f"⚔️ {tournament['name']} has STARTED!",
            description=f"Bracket generated with **{len(checked_in_teams)}** teams across **{len(matches)}** first-round matches.",
            color=COLOR_SUCCESS
        )
        embed.add_field(name="💰 Prize Pool", value=tournament["prize_pool"] or "TBD", inline=True)
        embed.add_field(name="📊 Use `/bracket`", value="To view the full bracket", inline=True)
        embed.set_footer(text="Good luck to all teams! 🎮")
        await interaction.followup.send(embed=embed)

        # DM all team captains their round 1 opponent
        for match in matches:
            if match["status"] == "pending":
                t1 = get_team(match["team1_id"]) if match["team1_id"] else None
                t2 = get_team(match["team2_id"]) if match["team2_id"] else None
                for team, opponent in [(t1, t2), (t2, t1)]:
                    if team:
                        try:
                            captain = await interaction.guild.fetch_member(team["captain_id"])
                            dm = discord.Embed(
                                title="🎮 Tournament Started — Your First Match!",
                                description=(
                                    f"**Tournament:** {tournament['name']}\n"
                                    f"**Your Team:** {team['name']}\n"
                                    f"**Opponent:** {opponent['name'] if opponent else 'BYE (Free Win)'}\n"
                                    f"**Match ID:** `{match['id']}`\n\n"
                                    "Good luck! 🏆"
                                ),
                                color=COLOR_GOLD
                            )
                            await captain.send(embed=dm)
                        except Exception:
                            pass

        ann_channel = interaction.guild.get_channel(ANNOUNCEMENT_CHANNEL_ID)
        if ann_channel:
            await ann_channel.send(embed=embed)

    # ── /seed_team ───────────────────────────────────────────────────────────
    @app_commands.command(name="seed_team", description="[Admin] Set a team's seed number.")
    @app_commands.describe(team_name="Team name", seed="Seed number (1 = top seed)")
    @is_admin()
    async def seed_team(self, interaction: discord.Interaction, team_name: str, seed: int):
        await interaction.response.defer(ephemeral=True)

        tournament = get_active_tournament()
        if not tournament:
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ No Active Tournament", color=COLOR_ERROR
            ))

        team = get_team_by_name(tournament["id"], team_name)
        if not team:
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ Team Not Found",
                description=f"No team named **{team_name}** found.",
                color=COLOR_ERROR
            ))

        set_team_seed(team["id"], seed)
        await interaction.followup.send(embed=discord.Embed(
            title="✅ Seed Set",
            description=f"**{team_name}** is now seeded **#{seed}**.",
            color=COLOR_SUCCESS
        ))

    # ── /update_prize ────────────────────────────────────────────────────────
    @app_commands.command(name="update_prize", description="[Admin] Update the tournament prize pool.")
    @app_commands.describe(prize="New prize pool description")
    @is_admin()
    async def update_prize(self, interaction: discord.Interaction, prize: str):
        await interaction.response.defer(ephemeral=True)

        tournament = get_active_tournament()
        if not tournament:
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ No Active Tournament", color=COLOR_ERROR
            ))

        update_tournament_field(tournament["id"], "prize_pool", prize)
        await interaction.followup.send(embed=discord.Embed(
            title="✅ Prize Pool Updated",
            description=f"Prize pool is now: **{prize}**",
            color=COLOR_SUCCESS
        ))

    # ── /update_rules ────────────────────────────────────────────────────────
    @app_commands.command(name="update_rules", description="[Admin] Update the tournament rules.")
    @app_commands.describe(rules="New rules text")
    @is_admin()
    async def update_rules(self, interaction: discord.Interaction, rules: str):
        await interaction.response.defer(ephemeral=True)

        tournament = get_active_tournament()
        if not tournament:
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ No Active Tournament", color=COLOR_ERROR
            ))

        update_tournament_field(tournament["id"], "rules", rules)
        await interaction.followup.send(embed=discord.Embed(
            title="✅ Rules Updated",
            description="Tournament rules have been updated.",
            color=COLOR_SUCCESS
        ))

    # ── /kick_team ───────────────────────────────────────────────────────────
    @app_commands.command(name="kick_team", description="[Admin] Remove a team from the tournament.")
    @app_commands.describe(team_name="Team name to remove")
    @is_admin()
    async def kick_team(self, interaction: discord.Interaction, team_name: str):
        await interaction.response.defer(ephemeral=True)

        tournament = get_active_tournament()
        if not tournament:
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ No Active Tournament", color=COLOR_ERROR
            ))

        team = get_team_by_name(tournament["id"], team_name)
        if not team:
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ Team Not Found",
                description=f"No team named **{team_name}**.",
                color=COLOR_ERROR
            ))

        unregister_team(team["id"])
        await interaction.followup.send(embed=discord.Embed(
            title="✅ Team Removed",
            description=f"**{team_name}** has been removed from the tournament.",
            color=COLOR_SUCCESS
        ))

    # ── /tournament_end ──────────────────────────────────────────────────────
    @app_commands.command(name="tournament_end", description="[Admin] End and finalize the current tournament.")
    @app_commands.describe(champion="Name of the champion team (optional)")
    @is_admin()
    async def tournament_end(self, interaction: discord.Interaction, champion: str = None):
        await interaction.response.defer()

        tournament = get_active_tournament()
        if not tournament:
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ No Active Tournament", color=COLOR_ERROR
            ))

        update_tournament_status(tournament["id"], "completed")

        embed = discord.Embed(
            title=f"🏆 {tournament['name']} — Tournament Complete!",
            color=COLOR_GOLD
        )
        if champion:
            embed.add_field(name="👑 Champion", value=f"**{champion}**", inline=False)
        embed.add_field(name="💰 Prize Pool", value=tournament["prize_pool"] or "TBD", inline=True)
        embed.add_field(name="🎮 Game", value=tournament["game"], inline=True)
        embed.set_footer(text="Thanks to all participants! 🎉")

        await interaction.followup.send(embed=embed)

        ann_channel = interaction.guild.get_channel(ANNOUNCEMENT_CHANNEL_ID)
        if ann_channel and ann_channel != interaction.channel:
            await ann_channel.send(embed=embed)

    # ── /cancel_tournament ───────────────────────────────────────────────────
    @app_commands.command(name="cancel_tournament", description="[Admin] Cancel the current tournament.")
    @app_commands.describe(reason="Reason for cancellation")
    @is_admin()
    async def cancel_tournament(self, interaction: discord.Interaction, reason: str = "No reason provided."):
        await interaction.response.defer(ephemeral=True)

        tournament = get_active_tournament()
        if not tournament:
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ No Active Tournament", color=COLOR_ERROR
            ))

        update_tournament_status(tournament["id"], "cancelled")
        await interaction.followup.send(embed=discord.Embed(
            title="✅ Tournament Cancelled",
            description=f"**{tournament['name']}** has been cancelled.\nReason: {reason}",
            color=COLOR_ERROR
        ))

        ann_channel = interaction.guild.get_channel(ANNOUNCEMENT_CHANNEL_ID)
        if ann_channel:
            await ann_channel.send(embed=discord.Embed(
                title=f"❌ {tournament['name']} — Tournament Cancelled",
                description=f"**Reason:** {reason}",
                color=COLOR_ERROR
            ))


async def setup(bot):
    await bot.add_cog(Admin(bot))
