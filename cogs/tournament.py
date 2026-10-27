import discord
from discord.ext import commands
from discord import app_commands
from config import COLOR_PRIMARY, COLOR_SUCCESS, COLOR_ERROR, COLOR_WARNING, COLOR_GOLD, ADMIN_ROLE_ID
from utils.database import (
    get_active_tournament, get_all_teams, get_team, get_team_members,
    get_pending_matches, get_match, set_match_winner, get_all_matches,
    get_matches_for_round, update_tournament_status
)
from utils.bracket import (
    generate_bracket, advance_winner, get_bracket_display,
    get_round_name, next_power_of_two
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
                description="You need the **Tournament Admin** role.",
                color=COLOR_ERROR
            ), ephemeral=True
        )
        return False
    return app_commands.check(predicate)


class Tournament(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ── /bracket ─────────────────────────────────────────────────────────────
    @app_commands.command(name="bracket", description="View the current tournament bracket.")
    async def bracket(self, interaction: discord.Interaction):
        await interaction.response.defer()

        tournament = get_active_tournament()
        if not tournament:
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ No Active Tournament", color=COLOR_ERROR
            ))

        if tournament["status"] not in ("active", "completed"):
            return await interaction.followup.send(embed=discord.Embed(
                title="⏳ Bracket Not Generated",
                description="The bracket hasn't been generated yet. Wait for the tournament to start.",
                color=COLOR_WARNING
            ))

        bracket = get_bracket_display(tournament["id"])
        if not bracket:
            return await interaction.followup.send(embed=discord.Embed(
                title="📊 Empty Bracket", color=COLOR_WARNING
            ))

        total_rounds = max(bracket.keys())
        embeds = []

        for round_num in sorted(bracket.keys()):
            round_name = get_round_name(round_num, total_rounds)
            embed = discord.Embed(
                title=f"🏆 {tournament['name']} — {round_name}",
                color=COLOR_PRIMARY
            )

            for match in bracket[round_num]:
                t1 = get_team(match["team1_id"]) if match["team1_id"] else None
                t2 = get_team(match["team2_id"]) if match["team2_id"] else None
                winner = get_team(match["winner_id"]) if match["winner_id"] else None

                t1_name = f"**{t1['name']}**" if t1 else "TBD"
                t2_name = f"**{t2['name']}**" if t2 else "TBD"

                if match["status"] == "bye":
                    val = f"{t1_name or t2_name} → **BYE** ✅"
                elif match["status"] == "completed":
                    loser = t2 if winner and winner["id"] == (t1["id"] if t1 else None) else t1
                    t1_str = f"~~{t1['name']}~~" if t1 and (not winner or winner["id"] != t1["id"]) else (f"**✅ {t1['name']}**" if t1 else "TBD")
                    t2_str = f"~~{t2['name']}~~" if t2 and (not winner or winner["id"] != t2["id"]) else (f"**✅ {t2['name']}**" if t2 else "TBD")
                    val = f"{t1_str}  vs  {t2_str}"
                else:
                    val = f"{t1_name}  ⚔️  {t2_name}"

                embed.add_field(
                    name=f"Match #{match['match_number']} — `ID: {match['id']}`",
                    value=val,
                    inline=False
                )

            embeds.append(embed)

        # Send all round embeds
        for i, embed in enumerate(embeds):
            if i == 0:
                await interaction.followup.send(embed=embed)
            else:
                await interaction.channel.send(embed=embed)

    # ── /match_info ──────────────────────────────────────────────────────────
    @app_commands.command(name="match_info", description="Get detailed information about a specific match.")
    @app_commands.describe(match_id="The match ID (shown in /bracket)")
    async def match_info(self, interaction: discord.Interaction, match_id: int):
        await interaction.response.defer()

        match = get_match(match_id)
        if not match:
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ Match Not Found", color=COLOR_ERROR
            ))

        t1 = get_team(match["team1_id"]) if match["team1_id"] else None
        t2 = get_team(match["team2_id"]) if match["team2_id"] else None
        winner = get_team(match["winner_id"]) if match["winner_id"] else None

        tournament = get_active_tournament()
        total_rounds = max(m["round"] for m in get_all_matches(match["tournament_id"])) if get_all_matches(match["tournament_id"]) else 1

        embed = discord.Embed(
            title=f"⚔️ Match #{match['match_number']} — {get_round_name(match['round'], total_rounds)}",
            color=COLOR_PRIMARY
        )
        embed.add_field(name="🔴 Team 1", value=t1["name"] if t1 else "TBD", inline=True)
        embed.add_field(name="🔵 Team 2", value=t2["name"] if t2 else "TBD", inline=True)
        embed.add_field(name="📊 Status", value=match["status"].capitalize(), inline=True)

        if winner:
            embed.add_field(name="🏆 Winner", value=f"**{winner['name']}**", inline=False)

        if match["completed_at"]:
            embed.add_field(name="✅ Completed", value=match["completed_at"][:19], inline=True)

        embed.set_footer(text=f"Match ID: {match_id} | Round {match['round']}")
        await interaction.followup.send(embed=embed)

    # ── /pending ─────────────────────────────────────────────────────────────
    @app_commands.command(name="pending", description="View all pending matches in the current tournament.")
    async def pending(self, interaction: discord.Interaction):
        await interaction.response.defer()

        tournament = get_active_tournament()
        if not tournament:
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ No Active Tournament", color=COLOR_ERROR
            ))

        matches = get_pending_matches(tournament["id"])
        if not matches:
            return await interaction.followup.send(embed=discord.Embed(
                title="✅ No Pending Matches",
                description="All matches have been completed!",
                color=COLOR_SUCCESS
            ))

        total_rounds = max(m["round"] for m in get_all_matches(tournament["id"])) if get_all_matches(tournament["id"]) else 1

        embed = discord.Embed(
            title=f"⏳ Pending Matches — {tournament['name']}",
            color=COLOR_WARNING
        )

        for match in matches:
            t1 = get_team(match["team1_id"]) if match["team1_id"] else None
            t2 = get_team(match["team2_id"]) if match["team2_id"] else None
            round_name = get_round_name(match["round"], total_rounds)

            embed.add_field(
                name=f"Match `{match['id']}` — {round_name}",
                value=f"**{t1['name'] if t1 else 'TBD'}** ⚔️ **{t2['name'] if t2 else 'TBD'}**",
                inline=False
            )

        embed.set_footer(text="Use /report_win to report a result (Admins only)")
        await interaction.followup.send(embed=embed)

    # ── /report_win (admin) ──────────────────────────────────────────────────
    @app_commands.command(name="report_win", description="[Admin] Report the winner of a match.")
    @app_commands.describe(
        match_id="The match ID",
        winner_team_name="Exact name of the winning team"
    )
    @is_admin()
    async def report_win(self, interaction: discord.Interaction, match_id: int, winner_team_name: str):
        await interaction.response.defer()

        tournament = get_active_tournament()
        if not tournament:
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ No Active Tournament", color=COLOR_ERROR
            ))

        match = get_match(match_id)
        if not match:
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ Match Not Found", color=COLOR_ERROR
            ))

        if match["status"] == "completed":
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ Already Completed",
                description="This match has already been reported.",
                color=COLOR_ERROR
            ))

        # Find winner team
        t1 = get_team(match["team1_id"]) if match["team1_id"] else None
        t2 = get_team(match["team2_id"]) if match["team2_id"] else None

        winner = None
        if t1 and t1["name"].lower() == winner_team_name.lower():
            winner = t1
        elif t2 and t2["name"].lower() == winner_team_name.lower():
            winner = t2

        if not winner:
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ Team Not Found",
                description=f"No team named **{winner_team_name}** is in this match.\nTeams: **{t1['name'] if t1 else 'N/A'}** vs **{t2['name'] if t2 else 'N/A'}**",
                color=COLOR_ERROR
            ))

        result, error = advance_winner(tournament["id"], match_id, winner["id"], interaction.user.id)

        if error:
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ Error", description=error, color=COLOR_ERROR
            ))

        embed = discord.Embed(
            title="✅ Match Result Recorded",
            description=f"🏆 **{winner['name']}** wins Match `{match_id}`!",
            color=COLOR_SUCCESS
        )

        if result == "tournament_over":
            embed.add_field(
                name="🎉 Tournament Complete!",
                value=f"**{winner['name']}** is the champion! Use `/tournament_end` to finalize.",
                inline=False
            )
            update_tournament_status(tournament["id"], "completed")
        elif result:
            embed.add_field(
                name="➡️ Next Round Generated",
                value=f"**{len(result)}** new match(es) have been created. Use `/bracket` to view.",
                inline=False
            )

            # DM captains of next round matches
            for next_match in result:
                if next_match["status"] == "pending":
                    nt1 = get_team(next_match["team1_id"]) if next_match["team1_id"] else None
                    nt2 = get_team(next_match["team2_id"]) if next_match["team2_id"] else None
                    for team in [nt1, nt2]:
                        if team:
                            try:
                                captain = await interaction.guild.fetch_member(team["captain_id"])
                                opponent = nt2 if team["id"] == (nt1["id"] if nt1 else None) else nt1
                                dm_embed = discord.Embed(
                                    title="⚔️ Your Next Match is Ready!",
                                    description=(
                                        f"**Tournament:** {tournament['name']}\n"
                                        f"**Your Team:** {team['name']}\n"
                                        f"**Opponent:** {opponent['name'] if opponent else 'TBD'}\n"
                                        f"**Match ID:** `{next_match['id']}`\n\n"
                                        f"Good luck! 🎮"
                                    ),
                                    color=COLOR_PRIMARY
                                )
                                await captain.send(embed=dm_embed)
                            except Exception:
                                pass

        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Tournament(bot))
