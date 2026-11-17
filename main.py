from openpyxl import Workbook
from openpyxl.styles import Font

from sports_package import Player, Team, Tournament
from data.loader import load_from_json, get_available_files


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
    position = input("Введите позицию (Нападающий/Защитник/Вратарь): ").strip()
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
    print(f"Команда: {team_name}")
    print(f"Место в турнире по голам: {place}")
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

    print(f"\n{'=' * 55}")
    print(f"СТАТИСТИКА КОМАНДЫ: {team.name.upper()}")
    print(f"{'=' * 55}")
    print(team.get_info())
    print(f"Забито: {goals_for} \nПропущено: {goals_against} \nРазница: {goals_for - goals_against:+d}")
    print(f"Процент побед: {win_rate:.1f}%")
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

        # Вычисляем ширину колонок для ровного вывода
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

def export_to_excel(tournament: Tournament) -> None:
    if not tournament.teams:
        print("Нет данных для экспорта.")
        return

    wb = Workbook()
    ws = wb.active
    ws.title = "Отчёт"

    ws.append([f"Отчёт о турнире: {tournament.name}"])
    ws["A1"].font = Font(size=14, bold=True)
    ws.append([])

    for title, headers, rows in tournament.get_report_sections():
        ws.append([title])
        ws.cell(row=ws.max_row, column=1).font = Font(size=12, bold=True)
        ws.append(headers)
        for cell in ws[ws.max_row]:
            cell.font = Font(bold=True)
        for row in rows:
            ws.append(row)
        ws.append([])

    # Автоширина
    for col in ws.columns:
        max_length = 0
        column_letter = col[0].column_letter
        for cell in col:
            if cell.value is not None:
                max_length = max(max_length, len(str(cell.value)))
        ws.column_dimensions[column_letter].width = max_length + 3

    wb.save("tournament_report.xlsx")
    print("Отчёт сохранён в файл 'tournament_report.xlsx'.")


def import_data_menu(tournament: Tournament) -> None:
    files = get_available_files()
    if not files:
        print("В папке 'data' не найдено .json файлов.")
        return
    print("\nДоступные файлы:")
    for i, f in enumerate(files, 1):
        print(f"  {i}. {f}")
    choice = input("Введите номер файла или его имя: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(files):
        filename = files[int(choice) - 1]
    else:
        filename = choice if choice.endswith(".json") else choice + ".json"
    load_from_json(filename, tournament)

def main() -> None:
    tournament = Tournament("Футбольный турнир")
    while True:
        print(f"\n=== {tournament.name} ===")
        print("1. Создать команду")
        print("2. Добавить игрока в команду")
        print("3. Зафиксировать результат матча")
        print("4. Показать статистику (Игрок / Команда / Турнир)")
        print("5. Экспортировать отчёт в .xlsx")
        print("6. Загрузить данные из .json")
        print("7. Выйти")
        
        choice = input("Выберите действие (1-7): ").strip()

        if choice == "1":
            create_team(tournament)
        elif choice == "2":
            create_player(tournament)
        elif choice == "3":
            record_match(tournament)
        elif choice == "4":
            statistics_menu(tournament) 
        elif choice == "5":
            export_to_excel(tournament)
        elif choice == "6":
            import_data_menu(tournament)
        elif choice == "7":
            print("Завершение работы программы.")
            break
        else:
            print("Неверный пункт меню.")


if __name__ == "__main__":
    main()