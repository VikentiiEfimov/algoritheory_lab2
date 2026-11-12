import os
from openpyxl import Workbook
from openpyxl.styles import Font
from sports_package import Player, Team, Match

# Временная "база данных" в памяти для демонстрации работы интерфейса
teams = {}

def create_team():
    name = input("Введите название команды: ").strip()
    if name in teams:
        print("Такая команда уже существует!")
    else:
        teams[name] = Team(name)
        print(f"Команда '{name}' успешно создана.")

def create_player():
    if not teams:
        print("Сначала создайте хотя бы одну команду!")
        return
    
    t_name = input("В какую команду добавить игрока?: ").strip()
    if t_name not in teams:
        print("Команда не найдена!")
        return
        
    p_name = input("Введите имя игрока: ").strip()
    position = input("Введите позицию (Нападающий/Защитник/Вратарь): ").strip()
    
    player = Player(p_name, position)
    teams[t_name].add_player(player)
    print(f"Игрок {p_name} добавлен в команду {t_name}.")

def record_match():
    if len(teams) < 2:
        print("Для проведения матча нужно минимум 2 команды!")
        return
        
    t1_name = input("Хозяева (название команды): ").strip()
    t2_name = input("Гости (название команды): ").strip()
    
    if t1_name not in teams or t2_name not in teams or t1_name == t2_name:
        print("Некорректный выбор команд!")
        return
        
    try:
        g1 = int(input(f"Сколько голов забила команда {t1_name}?: "))
        g2 = int(input(f"Сколько голов забила команда {t2_name}?: "))
    except ValueError:
        print("Ошибка: счет должен быть числом.")
        return

    # Регистрируем матч
    team1 = teams[t1_name]
    team2 = teams[t2_name]
    Match(team1, team2, g1, g2)
    print("Матч успешно зафиксирован!")
    
    # Ввод статистики игроков для этого матча
    print(f"\n--- Статистика игроков команды {t1_name} в этом матче ---")
    for p in team1.players.values():
        try:
            goals = int(input(f"Голов забил {p.name}: ") or 0)
            assists = int(input(f"Пасов отдал {p.name}: ") or 0)
            p.add_stats(goals, assists)
        except ValueError:
            print("Неверный ввод, статистика для этого игрока пропущена.")

    print(f"\n--- Статистика игроков команды {t2_name} в этом матче ---")
    for p in team2.players.values():
        try:
            goals = int(input(f"Голов забил {p.name}: ") or 0)
            assists = int(input(f"Пасов отдал {p.name}: ") or 0)
            p.add_stats(goals, assists)
        except ValueError:
            print("Неверный ввод, статистика для этого игрока пропущена.")

def show_stats():
    if not teams:
        print("Данные отсутствуют.")
        return
        
    print("\n====== ТЕКУЩАЯ СТАТИСТИКА ТУРНИРА ======")
    for team in teams.values():
        print(f"\nКоманда: {team.name} | Игры: {team.get_total_matches()} | Очки: {team.get_points()}")
        print(f"Победы: {team.wins}, Ничьи: {team.draws}, Поражения: {team.losses}")
        if team.players:
            print("  Игроки:")
            for p in team.players.values():
                print(f"    - {p.name} ({p.position}): Матчей: {p.matches_played}, Голы: {p.goals}, Пасы: {p.assists}, Очки(Г+П): {p.get_points()}, Ср. голов за матч: {p.get_avg_goals()}")
        else:
            print("  Игроков в составе пока нет.")

def export_to_excel():
    if not teams:
        print("Нет данных для экспорта.")
        return
        
    wb = Workbook()
    ws = wb.active
    ws.title = "Статистика турнира"
    
    # Заголовок отчета
    ws.append(['Отчет о футбольном турнире'])
    ws['A1'].font = Font(size=14, bold=True)
    ws.append([]) # Пустая строка для отступа
    
    for team in teams.values():
        # Информация о команде
        ws.append([f"Команда: {team.name}"])
        ws.cell(row=ws.max_row, column=1).font = Font(size=12, bold=True)
        
        ws.append([
            f"Сыграно матчей: {team.get_total_matches()}",
            f"Победы: {team.wins}",
            f"Ничьи: {team.draws}",
            f"Поражения: {team.losses}",
            f"Всего очков: {team.get_points()}"
        ])
        
        # Шапка таблицы игроков
        headers = ['Имя игрока', 'Позиция', 'Матчи', 'Гол + Пас', 'Ср. голов']
        ws.append(headers)
        for col_num in range(1, len(headers) + 1):
            ws.cell(row=ws.max_row, column=col_num).font = Font(bold=True)
        
        # Строки с игроками
        if team.players:
            for p in team.players.values():
                ws.append([
                    p.name,
                    p.position,
                    p.matches_played,
                    f"{p.goals} + {p.assists} ({p.get_points()})",
                    p.get_avg_goals()
                ])
        else:
            ws.append(["Игроков в составе нет"])
            
        ws.append([]) # Пустая строка между командами

    # Автоматическая подгонка ширины столбцов для читаемости
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        ws.column_dimensions[column].width = max_length + 3

    filename = "tournament_report.xlsx"
    wb.save(filename)
    print(f"Отчет успешно сохранен в файл '{filename}'!")

def main():
    while True:
        print("\n=== Панель управления турниром ===")
        print("1. Создать команду")
        print("2. Добавить игрока в команду")
        print("3. Зафиксировать результат матча")
        print("4. Показать текущую статистику")
        print("5. Экспортировать отчет в .xlsx")
        print("6. Выйти")
        
        choice = input("Выберите действие (1-6): ").strip()
        
        if choice == "1":
            create_team()
        elif choice == "2":
            create_player()
        elif choice == "3":
            record_match()
        elif choice == "4":
            show_stats()
        elif choice == "5":
            export_to_excel()
        elif choice == "6":
            print("Завершение работы программы.")
            break
        else:
            print("Неверный пункт меню, попробуйте снова.")

if __name__ == "__main__":
    main()
