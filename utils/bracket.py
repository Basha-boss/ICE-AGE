import math
from utils.database import (
    get_all_teams, create_match, set_match_winner,
    get_match, get_matches_for_round, get_all_matches,
    eliminate_team, get_team, checkin_team, get_pending_matches
)


def next_power_of_two(n):
    """Return the smallest power of 2 >= n."""
    if n <= 1:
        return 1
    return 2 ** math.ceil(math.log2(n))


def generate_bracket(tournament_id):
    """
    Generate a single-elimination bracket from checked-in teams.
    Returns list of round-1 match dicts.
    """
    teams = get_all_teams(tournament_id, only_checked_in=True)
    if not teams:
        return []

    # Sort by seed (lower seed = better)
    teams.sort(key=lambda t: (t["seed"] if t["seed"] > 0 else 9999, t["id"]))

    total_slots = next_power_of_two(len(teams))
    byes_needed = total_slots - len(teams)

    # Classic bracket pairing: 1 vs last, 2 vs second-last, etc.
    # Pad with None for byes
    padded = teams + [None] * byes_needed

    matches = []
    match_number = 1
    half = total_slots // 2

    for i in range(half):
        t1 = padded[i]
        t2 = padded[total_slots - 1 - i]

        t1_id = t1["id"] if t1 else None
        t2_id = t2["id"] if t2 else None

        status = "pending"
        if t2 is None:
            status = "bye"  # t1 gets a free win
        elif t1 is None:
            status = "bye"  # t2 gets a free win

        mid = create_match(tournament_id, 1, match_number, t1_id, t2_id, status)
        matches.append(get_match(mid))
        match_number += 1

    return matches


def advance_winner(tournament_id, match_id, winner_id, reported_by):
    """
    Record a match winner, eliminate the loser, and advance to the next round.
    Returns the next match (if any) or None if tournament is over.
    """
    match = get_match(match_id)
    if not match:
        return None, "Match not found."
    if match["status"] == "completed":
        return None, "Match already completed."

    # Determine loser
    loser_id = match["team1_id"] if match["team2_id"] == winner_id else match["team2_id"]

    set_match_winner(match_id, winner_id, reported_by)
    if loser_id:
        eliminate_team(loser_id)

    # Check if all matches in this round are done
    round_matches = get_matches_for_round(tournament_id, match["round"])
    all_done = all(m["status"] in ("completed", "bye") for m in round_matches)

    if not all_done:
        return None, None  # Round still in progress

    # Collect winners from this round to build next round
    winners = []
    for m in round_matches:
        if m["status"] == "bye":
            # The non-None team advances
            bye_winner = m["team1_id"] if m["team1_id"] else m["team2_id"]
            winners.append(bye_winner)
        else:
            winners.append(m["winner_id"])

    if len(winners) == 1:
        return "tournament_over", winners[0]

    # Build next round matches
    next_round = match["round"] + 1
    next_matches = []
    for i in range(0, len(winners), 2):
        t1 = winners[i]
        t2 = winners[i + 1] if i + 1 < len(winners) else None
        status = "bye" if t2 is None else "pending"
        mid = create_match(tournament_id, next_round, (i // 2) + 1, t1, t2, status)
        next_matches.append(get_match(mid))

    return next_matches, None


def get_bracket_display(tournament_id):
    """
    Return a structured bracket dict for display.
    { round_number: [match_dict, ...], ... }
    """
    all_matches = get_all_matches(tournament_id)
    bracket = {}
    for m in all_matches:
        r = m["round"]
        if r not in bracket:
            bracket[r] = []
        bracket[r].append(m)
    return bracket


def get_round_name(round_num, total_rounds):
    """Return a human-friendly round name."""
    rounds_left = total_rounds - round_num
    if rounds_left == 0:
        return "🏆 Grand Final"
    elif rounds_left == 1:
        return "🥊 Semi-Finals"
    elif rounds_left == 2:
        return "⚔️ Quarter-Finals"
    else:
        return f"Round {round_num}"
