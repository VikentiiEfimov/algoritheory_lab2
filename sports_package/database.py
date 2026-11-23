import sqlite3
from .player import Player
from .team import Team
from .match import Match
from .tournament import Tournament

DB_NAME = "tournament.db"


def get_connection(db_path: str = DB_NAME) -> sqlite3.Connection:
    """Открывает соединение с БД."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # позволяет обращаться по имени колонки
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """Создаёт таблицы, если их ещё нет."""
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            wins INTEGER DEFAULT 0,
            draws INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            position TEXT NOT NULL,
            team_id INTEGER NOT NULL,
            goals INTEGER DEFAULT 0,
            assists INTEGER DEFAULT 0,
            matches_played INTEGER DEFAULT 0,
            FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,
            home_goals INTEGER NOT NULL,
            away_goals INTEGER NOT NULL
        );
    """)
    conn.commit()


def save_tournament(tournament: Tournament, conn: sqlite3.Connection) -> None:
    """Полностью сохраняет состояние турнира в БД (перезаписывая)."""
    cursor = conn.cursor()
    # Очищаем всё перед сохранением — самый простой и надёжный способ
    cursor.executescript("""
        DELETE FROM players;
        DELETE FROM matches;
        DELETE FROM teams;
    """)

    # Сохраняем команды и игроков
    for team in tournament.teams.values():
        cursor.execute(
            "INSERT INTO teams (name, wins, draws, losses) VALUES (?, ?, ?, ?)",
            (team.name, team.wins, team._draws, team._losses),
        )
        team_id = cursor.lastrowid
        for player in team.players.values():
            cursor.execute(
                """INSERT INTO players
                   (name, position, team_id, goals, assists, matches_played)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (player.name, player.position, team_id,
                 player.goals, player.assists, player._matches_played),
            )

    # Сохраняем матчи
    for match in tournament.matches:
        cursor.execute(
            """INSERT INTO matches
               (home_team, away_team, home_goals, away_goals)
               VALUES (?, ?, ?, ?)""",
            (match.home_team.name, match.away_team.name,
             match._home_goals, match._away_goals),
        )

    conn.commit()
    print(f"[БД] Турнир сохранён в '{DB_NAME}' "
          f"(команд: {len(tournament.teams)}, "
          f"игроков: {sum(len(t.players) for t in tournament.teams.values())}, "
          f"матчей: {len(tournament.matches)}).")


def load_tournament(conn: sqlite3.Connection, tournament_name: str = "Футбольный турнир") -> Tournament:
    """Загружает турнир из БД в новый объект Tournament."""
    tournament = Tournament(tournament_name)
    cursor = conn.cursor()

    # Команды
    for row in cursor.execute("SELECT * FROM teams"):
        team = Team(row["name"])
        team._wins = row["wins"]
        team._draws = row["draws"]
        team._losses = row["losses"]
        tournament.add_team(team)

    # Игроки
    for row in cursor.execute("SELECT * FROM players"):
        team = tournament.teams.get(
            cursor.execute("SELECT name FROM teams WHERE id = ?",
                           (row["team_id"],)).fetchone()["name"]
        )
        if team:
            player = Player(row["name"], row["position"])
            player._goals = row["goals"]
            player._assists = row["assists"]
            player._matches_played = row["matches_played"]
            team.players[player.name] = player

    # Матчи (восстанавливаем без пересчёта очков — они уже в teams)
    for row in cursor.execute("SELECT * FROM matches"):
        home = tournament.teams.get(row["home_team"])
        away = tournament.teams.get(row["away_team"])
        if home and away:
            # Создаём матч, но не вызываем _process_match повторно
            match = Match.__new__(Match)
            match.home_team = home
            match.away_team = away
            match._home_goals = row["home_goals"]
            match._away_goals = row["away_goals"]
            match.player_stats = {}
            tournament.matches.append(match)

    print(f"[БД] Турнир загружен: команд — {len(tournament.teams)}, "
          f"матчей — {len(tournament.matches)}.")
    return tournament