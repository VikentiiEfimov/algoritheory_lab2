import os
import sqlite3
from sports_package import Player, Team, Tournament

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(DB_DIR, "tournament.db")


def get_connection(db_path: str = DB_NAME) -> sqlite3.Connection:
    """Открывает соединение с БД."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """Создаёт таблицы, если их ещё нет."""
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            position TEXT NOT NULL,
            team_id INTEGER NOT NULL,
            FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,
            home_goals INTEGER NOT NULL,
            away_goals INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS match_player_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER NOT NULL,
            player_name TEXT NOT NULL,
            goals INTEGER DEFAULT 0,
            assists INTEGER DEFAULT 0,
            FOREIGN KEY (match_id) REFERENCES matches(id) ON DELETE CASCADE
        );
    """)
    conn.commit()


def save_tournament(tournament: Tournament, conn: sqlite3.Connection) -> None:
    """Полностью сохраняет состояние турнира в БД (перезаписывая)."""
    cursor = conn.cursor()
    cursor.executescript("""
        DELETE FROM match_player_stats;
        DELETE FROM matches;
        DELETE FROM players;
        DELETE FROM teams;
    """)

    try:
        cursor.execute(
            "DELETE FROM sqlite_sequence WHERE name IN (?, ?, ?, ?)",
            ("match_player_stats", "matches", "players", "teams"),
        )
    except sqlite3.OperationalError:
        pass

    # 1. Сохраняем команды и игроков
    for team in tournament.teams.values():
        cursor.execute("INSERT INTO teams (name) VALUES (?)", (team.name,))
        team_id = cursor.lastrowid
        for player in team.players.values():
            cursor.execute(
                "INSERT INTO players (name, position, team_id) VALUES (?, ?, ?)",
                (player.name, player.position, team_id),
            )

    # 2. Сохраняем матчи и статистику игроков в них
    for match in tournament.matches:
        cursor.execute(
            """INSERT INTO matches (home_team, away_team, home_goals, away_goals)
               VALUES (?, ?, ?, ?)""",
            (match.home_team.name, match.away_team.name,
             match._home_goals, match._away_goals),
        )
        match_id = cursor.lastrowid

        for p_name, (goals, assists) in match.player_stats.items():
            cursor.execute(
                """INSERT INTO match_player_stats (match_id, player_name, goals, assists)
                   VALUES (?, ?, ?, ?)""",
                (match_id, p_name, goals, assists),
            )

    conn.commit()
    print(
        f"[БД] Турнир сохранён в '{os.path.basename(DB_NAME)}' "
        f"(команд: {len(tournament.teams)}, "
        f"игроков: {sum(len(t.players) for t in tournament.teams.values())}, "
        f"матчей: {len(tournament.matches)})."
    )


def load_tournament(
    conn: sqlite3.Connection,
    tournament: Tournament | None = None,
    tournament_name: str = "Футбольный турнир",
) -> Tournament:
    """Загружает турнир из БД по аналогии с JSON-загрузчиком."""
    if tournament is None:
        tournament = Tournament(tournament_name)

    cursor = conn.cursor()

    # 1. Команды и игроки
    teams_rows = cursor.execute("SELECT id, name FROM teams").fetchall()
    for t_row in teams_rows:
        t_name = t_row["name"]
        tournament.add_team(Team(t_name))

        players_rows = cursor.execute(
            "SELECT name, position FROM players WHERE team_id = ?",
            (t_row["id"],),
        ).fetchall()

        for p_row in players_rows:
            tournament.get_team(t_name).add_player(
                Player(p_row["name"], p_row["position"])
            )

    # 2. Матчи и статистика игроков
    loaded_matches = 0
    matches_rows = cursor.execute(
        "SELECT id, home_team, away_team, home_goals, away_goals FROM matches"
    ).fetchall()

    for m_row in matches_rows:
        stats_rows = cursor.execute(
            "SELECT player_name, goals, assists FROM match_player_stats WHERE match_id = ?",
            (m_row["id"],),
        ).fetchall()

        player_stats: dict = {
            s_row["player_name"]: (s_row["goals"], s_row["assists"])
            for s_row in stats_rows
        }

        tournament.play_match(
            m_row["home_team"],
            m_row["away_team"],
            m_row["home_goals"],
            m_row["away_goals"],
            player_stats if player_stats else None,
        )
        loaded_matches += 1

    print(
        f"[БД] Загружено из '{os.path.basename(DB_NAME)}': "
        f"команд — {len(tournament.teams)}, матчей — {loaded_matches}."
    )
    return tournament