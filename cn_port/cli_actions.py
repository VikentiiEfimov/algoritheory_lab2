from sports_package import Player, Team, Tournament


def create_team(tournament: Tournament) -> None:
    name = input("Введите название команды: ").strip()
    if not name:
        print("Название не может быть пустым.")
        return
    if name in tournament.teams:
        print("Такая команда уже существует!")
        return
    tournament.add_team(Team(name))
    print(f"Команда '{name}' успешно создана.")


def create_player(tournament: Tournament) -> None:
    if not tournament.teams:
        print("Сначала создайте хотя бы одну команду!")
        return
    t_name = input("В какую команду добавить игрока?: ").strip()
    if t_name not in tournament.teams:
        print("Команда не найдена!")
        return
    p_name = input("Введите имя игрока: ").strip()
    position = input("Введите позицию (Нападающий/Защитник/Вратарь,Полузащитник): ").strip()
    try:
        tournament.get_team(t_name).add_player(Player(p_name, position))
        print(f"Игрок {p_name} добавлен в команду {t_name}.")
    except ValueError as e:
        print(f"Ошибка: {e}")


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


def record_match(tournament: Tournament) -> None:
    match_teams = select_match_teams(tournament)
    if not match_teams:
        return
    home, away = match_teams
    try:
        home_goals = int(input(f"Сколько голов забила команда {home.name}?: ") or 0)
        away_goals = int(input(f"Сколько голов забила команда {away.name}?: ") or 0)
    except ValueError:
        print("Ошибка: счёт должен быть числом.")
        return

    player_stats: dict = {}
    player_stats.update(input_player_stats(home))
    player_stats.update(input_player_stats(away))

    match = tournament.play_match(home.name, away.name, home_goals, away_goals, player_stats)
    print(match.get_result_info())