from sports_package import Tournament
from cn_port.cli_actions import input_data_menu
from cn_port.stats_view import statistics_menu
from ex_port.exporters import export_to_excel
from im_port.getfiles import import_data_menu
from bd_port.storage_handlers import save_to_db, load_from_db


def main() -> None:
    tournament = Tournament("Футбольный турнир")
    while True:
        print(f"\n=== {tournament.name} ===")
        print("1. Ввод данных (команды, игроки, матчи)")
        print("2. Показать статистику")
        print("3. Экспортировать отчёт в .xlsx")
        print("4. Загрузить данные из .json")
        print("5. Сохранить в БД (SQLite3)")
        print("6. Загрузить из БД (SQLite3)")
        print("0. Выйти")

        choice = input("Выберите действие (0-6): ").strip()

        if choice == "1":
            input_data_menu(tournament)
        elif choice == "2":
            statistics_menu(tournament)
        elif choice == "3":
            export_to_excel(tournament)
        elif choice == "4":
            tournament = import_data_menu(tournament)
            save_to_db(tournament)
        elif choice == "5":
            save_to_db(tournament)
        elif choice == "6":
            tournament = load_from_db()
        elif choice == "0":
            print("Завершение работы программы.")
            break
        else:
            print("Неверный пункт меню.")


if __name__ == "__main__":
    main()
