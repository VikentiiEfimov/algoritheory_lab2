from sports_package import Tournament
from im_port.loader import load_from_json, get_available_files

def import_data_menu(current_tournament: Tournament) -> Tournament:
    files = get_available_files()
    if not files:
        print("В папке 'im_port' не найдено .json файлов.")
        return current_tournament
    print("\nДоступные файлы:")
    for i, f in enumerate(files, 1):
        print(f"  {i}. {f}")
    choice = input("Введите номер файла или его имя: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(files):
        filename = files[int(choice) - 1]
    else:
        filename = choice if choice.endswith(".json") else choice + ".json"
    new_tournament = load_from_json(filename, current_tournament.name)
    return new_tournament if new_tournament is not None else current_tournament