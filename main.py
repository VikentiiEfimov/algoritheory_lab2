from sports_package import Tournament
from cn_port.cli_actions import create_team, create_player, record_match
from cn_port.stats_view import statistics_menu
from ex_port.exporters import export_to_excel
from im_port.getfiles import import_data_menu
from bd_port.storage_handlers import save_to_db, load_from_db

def main() -> None:
    tournament = Tournament("Футбольный турнир")
    while True:
        print(f"\n=== {tournament.name} ===")
        print("1. Создать команду")
        print("2. Добавить игрока в команду")
        print("3. Зафиксировать результат матча")
        print("4. Показать статистику")
        print("5. Экспортировать отчёт в .xlsx")
        print("6. Загрузить данные из .json")
        print("7. Сохранить в БД (SQLite3)")
        print("8. Загрузить из БД (SQLite3)")
        print("9. Выйти")

        choice = input("Выберите действие (1-9): ").strip()

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
            tournament = import_data_menu(tournament)
        elif choice == "7":
            save_to_db(tournament)
        elif choice == "8":
            tournament = load_from_db()
        elif choice == "9":
            print("Завершение работы программы.")
            break
        else:
            print("Неверный пункт меню.")


if __name__ == "__main__":
    main()