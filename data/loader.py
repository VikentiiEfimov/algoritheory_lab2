import json
import os
from sports_package import Player, Team, Match

# Определяем абсолютный путь к папке 'data', где лежит этот скрипт
DATA_DIR = os.path.dirname(os.path.abspath(__file__))

def get_available_files():
    """Возвращает список всех .json файлов в папке data."""
    if not os.path.exists(DATA_DIR):
        return []
    return [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]

def load_from_json(filename: str, teams_db: dict):
    """Загружает данные из JSON-файла, расположенного в папке data."""
    # Если передано только имя (например, 'data_shaybu.json'), склеиваем его с путем к папке data
    if not os.path.isabs(filename):
        filepath = os.path.join(DATA_DIR, filename)
    else:
        filepath = filename

    if not os.path.exists(filepath):
        print(f"Ошибка: файл не найден по пути '{filepath}'.")
        return

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError:
        print(f"Ошибка: файл '{filename}' имеет неверный формат JSON.")
        return

    # 1. Загружаем команды и игроков
    for team_data in data.get("teams", []):
        t_name = team_data["name"]
        if t_name not in teams_db:
            teams_db[t_name] = Team(t_name)
        
        team_obj = teams_db[t_name]
        for p_data in team_data.get("players", []):
            p_name = p_data["name"]
            if p_name not in team_obj.players:
                team_obj.add_player(Player(p_name, p_data["position"]))

    # 2. Обрабатываем матчи и статистику
    for match_data in data.get("matches", []):
        home_name = match_data["home_team"]
        away_name = match_data["away_team"]
        
        if home_name not in teams_db or away_name not in teams_db:
            print(f"Пропуск матча {home_name} - {away_name}: команда не найдена.")
            continue

        Match(
            teams_db[home_name],
            teams_db[away_name],
            match_data["home_goals"],
            match_data["away_goals"]
        )

        stats_by_team = match_data.get("player_stats", {})
        for t_name, players_stats in stats_by_team.items():
            if t_name in teams_db:
                team_obj = teams_db[t_name]
                for p_name, stats in players_stats.items():
                    if p_name in team_obj.players:
                        team_obj.players[p_name].add_stats(
                            stats.get("goals", 0),
                            stats.get("assists", 0)
                        )

    print(f"Данные из '{os.path.basename(filepath)}' успешно загружены!")
