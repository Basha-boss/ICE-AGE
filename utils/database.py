import sqlite3
import json
from datetime import datetime
from config import DB_PATH


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """Initialize database tables."""
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS tournaments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                game TEXT NOT NULL,
                status TEXT DEFAULT 'registration',
                -- status: registration | checkin | active | completed | cancelled
                prize_pool TEXT DEFAULT '',
                rules TEXT DEFAULT '',
                max_teams INTEGER DEFAULT 16,
                team_size INTEGER DEFAULT 1,
                checkin_start TEXT,
                tournament_start TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER
            );

            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tournament_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                captain_id INTEGER NOT NULL,
                seed INTEGER DEFAULT 0,
                checked_in INTEGER DEFAULT 0,
                eliminated INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tournament_id) REFERENCES tournaments(id)
            );

            CREATE TABLE IF NOT EXISTS team_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                FOREIGN KEY (team_id) REFERENCES teams(id)
            );

            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tournament_id INTEGER NOT NULL,
                round INTEGER NOT NULL,
                match_number INTEGER NOT NULL,
                team1_id INTEGER,
                team2_id INTEGER,
                winner_id INTEGER,
                status TEXT DEFAULT 'pending',
                -- status: pending | active | completed | bye
                scheduled_time TEXT,
                completed_at TEXT,
                reported_by INTEGER,
                FOREIGN KEY (tournament_id) REFERENCES tournaments(id),
                FOREIGN KEY (team1_id) REFERENCES teams(id),
                FOREIGN KEY (team2_id) REFERENCES teams(id),
                FOREIGN KEY (winner_id) REFERENCES teams(id)
            );
        """)
    print("[DB] Database initialized.")


# ── Tournament CRUD ──────────────────────────────────────────────────────────

def create_tournament(name, game, prize_pool, rules, max_teams, team_size, created_by):
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO tournaments (name, game, prize_pool, rules, max_teams, team_size, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (name, game, prize_pool, rules, max_teams, team_size, created_by)
        )
        return cur.lastrowid


def get_active_tournament():
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM tournaments WHERE status NOT IN ('completed', 'cancelled') ORDER BY id DESC LIMIT 1"
        ).fetchone()
        return dict(row) if row else None


def get_tournament(tournament_id):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM tournaments WHERE id = ?", (tournament_id,)).fetchone()
        return dict(row) if row else None


def update_tournament_status(tournament_id, status):
    with get_connection() as conn:
        conn.execute("UPDATE tournaments SET status = ? WHERE id = ?", (status, tournament_id))


def update_tournament_field(tournament_id, field, value):
    allowed = {"prize_pool", "rules", "checkin_start", "tournament_start", "status", "name", "game"}
    if field not in allowed:
        raise ValueError(f"Field '{field}' not allowed.")
    with get_connection() as conn:
        conn.execute(f"UPDATE tournaments SET {field} = ? WHERE id = ?", (value, tournament_id))


# ── Team CRUD ────────────────────────────────────────────────────────────────

def register_team(tournament_id, name, captain_id):
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO teams (tournament_id, name, captain_id) VALUES (?, ?, ?)",
            (tournament_id, name, captain_id)
        )
        return cur.lastrowid


def add_team_member(team_id, user_id, username):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO team_members (team_id, user_id, username) VALUES (?, ?, ?)",
            (team_id, user_id, username)
        )


def get_team(team_id):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM teams WHERE id = ?", (team_id,)).fetchone()
        return dict(row) if row else None


def get_team_by_captain(tournament_id, captain_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM teams WHERE tournament_id = ? AND captain_id = ?",
            (tournament_id, captain_id)
        ).fetchone()
        return dict(row) if row else None


def get_team_by_name(tournament_id, name):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM teams WHERE tournament_id = ? AND name = ? COLLATE NOCASE",
            (tournament_id, name)
        ).fetchone()
        return dict(row) if row else None


def get_team_members(team_id):
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM team_members WHERE team_id = ?", (team_id,)).fetchall()
        return [dict(r) for r in rows]


def get_all_teams(tournament_id, only_checked_in=False):
    with get_connection() as conn:
        query = "SELECT * FROM teams WHERE tournament_id = ? AND eliminated = 0"
        params = [tournament_id]
        if only_checked_in:
            query += " AND checked_in = 1"
        query += " ORDER BY seed ASC, id ASC"
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]


def checkin_team(team_id):
    with get_connection() as conn:
        conn.execute("UPDATE teams SET checked_in = 1 WHERE id = ?", (team_id,))


def set_team_seed(team_id, seed):
    with get_connection() as conn:
        conn.execute("UPDATE teams SET seed = ? WHERE id = ?", (seed, team_id))


def eliminate_team(team_id):
    with get_connection() as conn:
        conn.execute("UPDATE teams SET eliminated = 1 WHERE id = ?", (team_id,))


def unregister_team(team_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM team_members WHERE team_id = ?", (team_id,))
        conn.execute("DELETE FROM teams WHERE id = ?", (team_id,))


# ── Match CRUD ───────────────────────────────────────────────────────────────

def create_match(tournament_id, round_num, match_number, team1_id, team2_id, status="pending"):
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO matches (tournament_id, round, match_number, team1_id, team2_id, status)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (tournament_id, round_num, match_number, team1_id, team2_id, status)
        )
        return cur.lastrowid


def get_match(match_id):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM matches WHERE id = ?", (match_id,)).fetchone()
        return dict(row) if row else None


def get_matches_for_round(tournament_id, round_num):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM matches WHERE tournament_id = ? AND round = ? ORDER BY match_number",
            (tournament_id, round_num)
        ).fetchall()
        return [dict(r) for r in rows]


def get_all_matches(tournament_id):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM matches WHERE tournament_id = ? ORDER BY round, match_number",
            (tournament_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def set_match_winner(match_id, winner_id, reported_by):
    with get_connection() as conn:
        conn.execute(
            """UPDATE matches SET winner_id = ?, status = 'completed', completed_at = ?, reported_by = ?
               WHERE id = ?""",
            (winner_id, datetime.utcnow().isoformat(), reported_by, match_id)
        )


def set_match_status(match_id, status):
    with get_connection() as conn:
        conn.execute("UPDATE matches SET status = ? WHERE id = ?", (status, match_id))


def get_current_round(tournament_id):
    with get_connection() as conn:
        row = conn.execute(
            """SELECT MAX(round) as r FROM matches
               WHERE tournament_id = ? AND status != 'bye'""",
            (tournament_id,)
        ).fetchone()
        return row["r"] if row and row["r"] else 1


def get_pending_matches(tournament_id):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM matches WHERE tournament_id = ? AND status IN ('pending', 'active') ORDER BY round, match_number",
            (tournament_id,)
        ).fetchall()
        return [dict(r) for r in rows]
