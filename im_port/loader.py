import json
import os
from pathlib import Path
from sports_package import Player, Team, Tournament

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR))


def get_search_dirs() -> list[Path]:
    """
    Каталоги поиска .json в порядке приоритета:
    1. DATA_DIR — единая папка данных (Docker: /app/data, локально: im_port/);
    2. IMPORT_DIRS — доп. каталоги (os.pathsep-разделённый список, Docker: /app/im_port);
    3. BASE_DIR — папка пакета (фолбэк).
    Дубликаты и несуществующие каталоги отбрасываются.
    """
    candidates: list[Path] = [DATA_DIR]
    raw = os.getenv("IMPORT_DIRS", "")
    candidates.extend(Path(p) for p in raw.split(os.pathsep) if p.strip())
    candidates.append(BASE_DIR)

    result: list[Path] = []
    seen: set[Path] = set()
    for d in candidates:
        try:
            rp = d.resolve()
        except OSError:
            continue
        if rp in seen or not d.is_dir():
            continue
        seen.add(rp)
        result.append(d)
    return result


def get_available_files() -> list[str]:
    """Уникальные имена .json из всех каталогов поиска (без дублей)."""
    names: list[str] = []
    seen: set[str] = set()
    for d in get_search_dirs():
        for f in sorted(os.listdir(d)):
            if f.endswith(".json") and f not in seen:
                seen.add(f)
                names.append(f)
    return names


def _resolve_path(filename: str) -> Path | None:
    if os.path.isabs(filename):
        p = Path(filename)
        return p if p.is_file() else None
    for d in get_search_dirs():
        p = d / filename
        if p.is_file():
            return p
    return None


def load_from_json(filename: str, tournament_name: str = "Футбольный турнир") -> Tournament | None:
    filepath = _resolve_path(filename)
    if filepath is None:
        searched = ", ".join(str(d) for d in get_search_dirs()) or "<нет каталогов>"
        print(f"Ошибка: файл '{filename}' не найден. Искали в: {searched}.")
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError:
        print(f"Ошибка: файл '{filepath}' имеет неверный формат JSON.")
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
        player_stats: dict = {}
        for players_stats in match_data.get("player_stats", {}).values():
            for p_name, stats in players_stats.items():
                player_stats[p_name] = (
                    stats.get("goals", 0),
                    stats.get("assists", 0),
                )
        tournament.play_match(
            match_data["home_team"],
            match_data["away_team"],
            match_data["home_goals"],
            match_data["away_goals"],
            player_stats if player_stats else None,
        )
        loaded_matches += 1

    print(
        f"Загружено из '{filepath.name}': "
        f"команд — {len(tournament.teams)}, матчей — {loaded_matches}."
    )
    return tournament