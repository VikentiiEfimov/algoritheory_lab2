from sports_package import Tournament


def print_player_stats(tournament: Tournament) -> None:
    name = input("Введите имя игрока: ").strip()
    try:
        player, team_name = tournament.get_player(name)
    except KeyError as e:
        print(f"\n[Ошибка] {e}")
        return

    all_players = [p for t in tournament.teams.values() for p in t.players.values()]
    sorted_players = sorted(all_players, key=lambda p: (-p.goals, -p.get_points(), p.name))
    place = next((i for i, p in enumerate(sorted_players, 1) if p is player), "—")

    print(f"\n{'=' * 50}")
    print(f"КАРТОЧКА ИГРОКА: {player.name.upper()}")
    print(f"{'=' * 50}")
    print(player.get_info())
    print(f"{'Команда':<15} {team_name}")
    print(f"{'МвТпГ':<15} {place}")
    print(f"{'=' * 50}\n")


def print_team_stats(tournament: Tournament) -> None:
    name = input("Введите название команды: ").strip()
    try:
        team = tournament.get_team(name)
    except KeyError as e:
        print(f"\n[Ошибка] {e}")
        return

    goals_for, goals_against = tournament.get_team_goals(name)
    win_rate = (team.wins / team.get_total_matches() * 100) if team.get_total_matches() else 0.0
    best = max(team.players.values(), key=lambda p: (p.goals, p.assists), default=None)

    print(f"\n{'=' * 57}")
    print(f"СТАТИСТИКА КОМАНДЫ: {team.name.upper()}")
    print(f"{'=' * 57}")
    print(team.get_info())
    print(f"{'Забито':<15} {goals_for} \n{'Пропущено':<15} {goals_against} \n{'Разница':<15} {goals_for - goals_against:+d}")
    print(f"Процент побед:  {win_rate:.1f}%")
    if best:
        print(f"Лучший игрок: {best.name} (голы: {best.goals}, пасы: {best.assists})")

    print("\n--- Сыгранные матчи ---")
    matches = tournament.get_team_matches(name)
    if not matches:
        print("  Матчей пока не сыграно.")
    else:
        for m in matches:
            print(f"  {m.get_result_info()}")

    print("\n--- Состав ---")
    if not team.players:
        print("  Игроков в команде нет.")
    else:
        print(f"{'Игрок':<20} | {'Голы':<5} | {'Пасы':<5} | {'Очки':<5}")
        print("-" * 45)
        for p in team.players.values():
            print(f"{p.name:<20} | {p.goals:<5} | {p.assists:<5} | {p.get_points():<5}")
    print(f"{'=' * 55}\n")


def print_tournament_stats(tournament: Tournament) -> None:
    for title, headers, rows in tournament.get_report_sections():
        print(f"\n{'=' * 60}")
        print(title.upper())
        print("=" * 60)
        if not rows:
            print("Нет данных.")
            continue

        all_rows = [headers] + rows
        widths = [max(len(str(row[i])) for row in all_rows) for i in range(len(headers))]

        print(" | ".join(f"{h:<{w}}" for h, w in zip(headers, widths)))
        print("-" * (sum(widths) + 3 * (len(widths) - 1)))
        for row in rows:
            print(" | ".join(f"{str(v):<{w}}" for v, w in zip(row, widths)))


def statistics_menu(tournament: Tournament) -> None:
    """Подменю для выбора типа статистики."""
    while True:
        print("\n--- МЕНЮ СТАТИСТИКИ ---")
        print("1. Статистика игрока")
        print("2. Статистика команды")
        print("3. Статистика турнира")
        print("0. Назад в главное меню")

        choice = input("Выберите действие (0-3): ").strip()

        if choice == "1":
            print_player_stats(tournament)
        elif choice == "2":
            print_team_stats(tournament)
        elif choice == "3":
            print_tournament_stats(tournament)
        elif choice == "0":
            break
        else:
            print("Неверный пункт меню.")
