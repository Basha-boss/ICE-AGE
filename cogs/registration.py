import discord
from discord.ext import commands
from discord import app_commands
from config import (
    COLOR_PRIMARY, COLOR_SUCCESS, COLOR_ERROR, COLOR_WARNING,
    ADMIN_ROLE_ID, MAX_TEAM_SIZE, MIN_TEAM_SIZE
)
from utils.database import (
    get_active_tournament, register_team, add_team_member,
    get_team_by_captain, get_team_by_name, get_team_members,
    get_all_teams, unregister_team, checkin_team, get_team,
    get_team_by_captain
)


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
                description="You need the **Tournament Admin** role to use this command.",
                color=COLOR_ERROR
            ), ephemeral=True
        )
        return False
    return app_commands.check(predicate)


class Registration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ── /register ────────────────────────────────────────────────────────────
    @app_commands.command(name="register", description="Register your team for the current tournament.")
    @app_commands.describe(
        team_name="Your team's name",
        member2="Team member 2 (optional)",
        member3="Team member 3 (optional)",
        member4="Team member 4 (optional)",
        member5="Team member 5 (optional)",
    )
    async def register(
        self,
        interaction: discord.Interaction,
        team_name: str,
        member2: discord.Member = None,
        member3: discord.Member = None,
        member4: discord.Member = None,
        member5: discord.Member = None,
    ):
        await interaction.response.defer(ephemeral=True)

        tournament = get_active_tournament()
        if not tournament:
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ No Active Tournament",
                description="There is no active tournament to register for.",
                color=COLOR_ERROR
            ))

        if tournament["status"] != "registration":
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ Registration Closed",
                description=f"Registration is currently **{tournament['status']}**. You can no longer register.",
                color=COLOR_ERROR
            ))

        # Collect members
        members = [interaction.user]
        for m in [member2, member3, member4, member5]:
            if m and m not in members:
                members.append(m)

        team_size = tournament["team_size"]
        if len(members) > team_size:
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ Too Many Members",
                description=f"This tournament allows **{team_size}** player(s) per team.",
                color=COLOR_ERROR
            ))

        # Check name availability
        if get_team_by_name(tournament["id"], team_name):
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ Name Taken",
                description=f"A team named **{team_name}** is already registered.",
                color=COLOR_ERROR
            ))

        # Check if captain already registered
        if get_team_by_captain(tournament["id"], interaction.user.id):
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ Already Registered",
                description="You are already registered as a team captain in this tournament.",
                color=COLOR_ERROR
            ))

        # Check max teams
        existing = get_all_teams(tournament["id"])
        if len(existing) >= tournament["max_teams"]:
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ Tournament Full",
                description=f"The tournament is full ({tournament['max_teams']} teams).",
                color=COLOR_ERROR
            ))

        # Register team
        team_id = register_team(tournament["id"], team_name, interaction.user.id)
        for member in members:
            add_team_member(team_id, member.id, str(member))

        member_list = "\n".join(f"• {m.mention}" for m in members)
        embed = discord.Embed(
            title="✅ Team Registered!",
            description=f"**{team_name}** has been successfully registered for **{tournament['name']}**!",
            color=COLOR_SUCCESS
        )
        embed.add_field(name="👥 Team Members", value=member_list, inline=False)
        embed.add_field(name="🏷️ Team ID", value=f"`{team_id}`", inline=True)
        embed.add_field(name="🎮 Game", value=tournament["game"], inline=True)
        embed.set_footer(text="Check in when check-in opens using /checkin")
        await interaction.followup.send(embed=embed)

    # ── /unregister ──────────────────────────────────────────────────────────
    @app_commands.command(name="unregister", description="Withdraw your team from the tournament.")
    async def unregister(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        tournament = get_active_tournament()
        if not tournament or tournament["status"] != "registration":
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ Cannot Unregister",
                description="Registration is closed or no active tournament.",
                color=COLOR_ERROR
            ))

        team = get_team_by_captain(tournament["id"], interaction.user.id)
        if not team:
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ Not Registered",
                description="You are not registered as a team captain.",
                color=COLOR_ERROR
            ))

        unregister_team(team["id"])
        await interaction.followup.send(embed=discord.Embed(
            title="✅ Unregistered",
            description=f"Team **{team['name']}** has been removed from the tournament.",
            color=COLOR_SUCCESS
        ))

    # ── /checkin ─────────────────────────────────────────────────────────────
    @app_commands.command(name="checkin", description="Check your team in for the upcoming tournament.")
    async def checkin(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        tournament = get_active_tournament()
        if not tournament:
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ No Active Tournament", color=COLOR_ERROR
            ))

        if tournament["status"] != "checkin":
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ Check-in Not Open",
                description=f"Check-in is not currently open. Tournament status: **{tournament['status']}**",
                color=COLOR_ERROR
            ))

        team = get_team_by_captain(tournament["id"], interaction.user.id)
        if not team:
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ Not Registered",
                description="You must be a team captain to check in.",
                color=COLOR_ERROR
            ))

        if team["checked_in"]:
            return await interaction.followup.send(embed=discord.Embed(
                title="ℹ️ Already Checked In",
                description=f"**{team['name']}** is already checked in!",
                color=COLOR_WARNING
            ))

        checkin_team(team["id"])
        await interaction.followup.send(embed=discord.Embed(
            title="✅ Checked In!",
            description=f"**{team['name']}** is confirmed for the tournament. Good luck! 🎮",
            color=COLOR_SUCCESS
        ))

    # ── /teams ───────────────────────────────────────────────────────────────
    @app_commands.command(name="teams", description="View all registered teams.")
    async def teams(self, interaction: discord.Interaction):
        await interaction.response.defer()

        tournament = get_active_tournament()
        if not tournament:
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ No Active Tournament", color=COLOR_ERROR
            ))

        teams = get_all_teams(tournament["id"])
        if not teams:
            return await interaction.followup.send(embed=discord.Embed(
                title="📋 No Teams Yet",
                description="No teams have registered yet.",
                color=COLOR_PRIMARY
            ))

        embed = discord.Embed(
            title=f"📋 Registered Teams — {tournament['name']}",
            description=f"**{len(teams)}** / **{tournament['max_teams']}** teams registered",
            color=COLOR_PRIMARY
        )

        team_lines = []
        for i, team in enumerate(teams, 1):
            seed_str = f" `[#{team['seed']}]`" if team["seed"] > 0 else ""
            checkin_str = " ✅" if team["checked_in"] else ""
            team_lines.append(f"`{i:02d}.` **{team['name']}**{seed_str}{checkin_str}")

        # Split into pages of 20 per embed field
        chunks = [team_lines[i:i+20] for i in range(0, len(team_lines), 20)]
        for chunk in chunks:
            embed.add_field(name="\u200b", value="\n".join(chunk), inline=False)

        embed.set_footer(text="✅ = Checked in")
        await interaction.followup.send(embed=embed)

    # ── /myteam ──────────────────────────────────────────────────────────────
    @app_commands.command(name="myteam", description="View your team's registration details.")
    async def myteam(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        tournament = get_active_tournament()
        if not tournament:
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ No Active Tournament", color=COLOR_ERROR
            ))

        team = get_team_by_captain(tournament["id"], interaction.user.id)
        if not team:
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ Not Registered",
                description="You are not registered as a team captain in this tournament.",
                color=COLOR_ERROR
            ))

        members = get_team_members(team["id"])
        member_list = "\n".join(f"• <@{m['user_id']}>" for m in members)

        embed = discord.Embed(
            title=f"🏷️ {team['name']}",
            color=COLOR_PRIMARY
        )
        embed.add_field(name="👥 Members", value=member_list or "None", inline=False)
        embed.add_field(name="🏆 Tournament", value=tournament["name"], inline=True)
        embed.add_field(name="🎯 Seed", value=f"#{team['seed']}" if team["seed"] > 0 else "Unseeded", inline=True)
        embed.add_field(name="✅ Checked In", value="Yes" if team["checked_in"] else "No", inline=True)
        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Registration(bot))
