import json
import os
from sports_package import Player, Team, Tournament
DATA_DIR = os.path.dirname(os.path.abspath(__file__))


def get_available_files() -> list[str]:
    """Возвращает список всех .json файлов в папке data."""
    if not os.path.exists(DATA_DIR):
        return []
    return [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]

def load_from_json(filename: str, tournament_name: str = "Футбольный турнир") -> Tournament | None:
    filepath = filename if os.path.isabs(filename) else os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        print(f"Ошибка: файл не найден по пути '{filepath}'.")
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError:
        print(f"Ошибка: файл '{filename}' имеет неверный формат JSON.")
        return None

    # Создаём новый пустой турнир
    tournament = Tournament(data.get("name", tournament_name))

    # 1. Команды и игроки
    for team_data in data.get("teams", []):
        t_name = team_data["name"]
        tournament.add_team(Team(t_name))
        for p_data in team_data.get("players", []):
            tournament.get_team(t_name).add_player(
                Player(p_data["name"], p_data["position"])
            )

    # 2. Матчи
    loaded_matches = 0
    for match_data in data.get("matches", []):
        home_name = match_data["home_team"]
        away_name = match_data["away_team"]
        player_stats: dict = {}
        for players_stats in match_data.get("player_stats", {}).values():
            for p_name, stats in players_stats.items():
                player_stats[p_name] = (
                    stats.get("goals", 0),
                    stats.get("assists", 0),
                )
        tournament.play_match(
            home_name,
            away_name,
            match_data["home_goals"],
            match_data["away_goals"],
            player_stats if player_stats else None,
        )
        loaded_matches += 1

    print(
        f"Загружено из '{os.path.basename(filepath)}': "
        f"команд — {len(tournament.teams)}, матчей — {loaded_matches}."
    )
    return tournament
