from sports_package import Player, Team, Tournament
from bd_port.storage_handlers import save_to_db


def create_team(tournament: Tournament) -> bool:
    name = input("Введите название команды: ").strip()
    if not name:
        print("Название не может быть пустым.")
        return False
    if name in tournament.teams:
        print("Такая команда уже существует!")
        return False
    tournament.add_team(Team(name))
    print(f"Команда '{name}' успешно создана.")
    return True


def create_player(tournament: Tournament) -> bool:
    if not tournament.teams:
        print("Сначала создайте хотя бы одну команду!")
        return False
    t_name = input("В какую команду добавить игрока?: ").strip()
    if t_name not in tournament.teams:
        print("Команда не найдена!")
        return False
    p_name = input("Введите имя игрока: ").strip()
    position = input("Введите позицию (Нападающий/Защитник/Вратарь/Полузащитник): ").strip()
    try:
        tournament.get_team(t_name).add_player(Player(p_name, position))
        print(f"Игрок {p_name} добавлен в команду {t_name}.")
        return True
    except ValueError as e:
        print(f"Ошибка: {e}")
        return False


def select_match_teams(tournament: Tournament):
    """Возвращает (home, away) или None при некорректном выборе."""
    if len(tournament.teams) < 2:
        print("Для проведения матча нужно минимум 2 команды!")
        return None
    home_name = input("Хозяева (название команды): ").strip()
    away_name = input("Гости (название команды): ").strip()
    if (home_name not in tournament.teams
        or away_name not in tournament.teams
        or home_name == away_name):
        print("Некорректный выбор команд!")
        return None
    return tournament.get_team(home_name), tournament.get_team(away_name)


def input_player_stats(team: Team) -> dict:
    """Собирает статистику игроков команды за матч."""
    player_stats: dict = {}
    print(f"\n--- Статистика игроков команды {team.name} в этом матче ---")
    for player in team.players.values():
        try:
            goals = int(input(f"Голов забил {player.name}: ") or 0)
            assists = int(input(f"Пасов отдал {player.name}: ") or 0)
            player_stats[player.name] = (goals, assists)
        except ValueError:
            print(f"Неверный ввод, статистика для {player.name} пропущена.")
            player_stats[player.name] = (0, 0)
    return player_stats


def record_match(tournament: Tournament) -> bool:
    match_teams = select_match_teams(tournament)
    if not match_teams:
        return False
    home, away = match_teams
    try:
        home_goals = int(input(f"Сколько голов забила команда {home.name}?: ") or 0)
        away_goals = int(input(f"Сколько голов забила команда {away.name}?: ") or 0)
    except ValueError:
        print("Ошибка: счёт должен быть числом.")
        return False

    player_stats: dict = {}
    player_stats.update(input_player_stats(home))
    player_stats.update(input_player_stats(away))

    match = tournament.play_match(home.name, away.name, home_goals, away_goals, player_stats)
    print(match.get_result_info())
    return True


def input_data_menu(tournament: Tournament) -> None:
    """Подменю для внесения данных вручную."""
    while True:
        print("\n--- МЕНЮ ВВОДА ДАННЫХ ---")
        print("1. Создать команду")
        print("2. Добавить игрока в команду")
        print("3. Зафиксировать результат матча")
        print("0. Назад в главное меню")

        choice = input("Выберите действие (0-3): ").strip()

        if choice == "1":
            if create_team(tournament):
                save_to_db(tournament)
        elif choice == "2":
            if create_player(tournament):
                save_to_db(tournament)
        elif choice == "3":
            if record_match(tournament):
                save_to_db(tournament)
        elif choice == "0":
            break
        else:
            print("Неверный пункт меню.")
