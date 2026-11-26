import os
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from sports_package import Tournament

def _setup_sheet(ws, tournament_name: str, subtitle: str) -> None:
    """Оформляет шапку нового листа."""
    ws.append([f"{tournament_name} — {subtitle}"])
    ws["A1"].font = Font(size=14, bold=True)
    ws.append([])

def _write_section(ws, title: str, headers: list, rows: list, header_fill, thin_border) -> None:
    """Записывает одну таблицу (секцию) на указанный лист."""
    ws.append([title])
    ws.cell(row=ws.max_row, column=1).font = Font(size=12, bold=True)

    num_cols = len(headers)

    ws.append(headers)
    # Ограничиваем оформление только количеством колонок текущей таблицы
    for cell in ws[ws.max_row][:num_cols]:
        cell.font = Font(bold=True)
        cell.fill = header_fill
        cell.border = thin_border
        cell.alignment = Alignment(horizontal="center")

    for row in rows:
        ws.append(row)
        # Здесь тоже ограничиваем цикл по num_cols
        for cell in ws[ws.max_row][:num_cols]:
            cell.border = thin_border

    ws.append([])  # Пустая строка после таблицы


def export_to_excel(tournament: Tournament) -> None:
    if not tournament.teams:
        print("Нет данных для экспорта.")
        return

    wb = Workbook()

    # Создаём 4 тематических листа
    ws_main = wb.active
    ws_main.title = "Сводка и таблица"
    _setup_sheet(ws_main, tournament.name, "Общая статистика")

    ws_players = wb.create_sheet(title="Рейтинги игроков")
    _setup_sheet(ws_players, tournament.name, "Индивидуальная статистика")

    ws_matches = wb.create_sheet(title="История матчей")
    _setup_sheet(ws_matches, tournament.name, "Результаты игр")

    ws_rosters = wb.create_sheet(title="Составы команд")
    _setup_sheet(ws_rosters, tournament.name, "Заявки и статистика игроков")

    # Стили оформления
    header_fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin"),
    )

    # Распределяем секции по листам
    for title, headers, rows in tournament.get_report_sections(include_timestamps=True):
        if title in ("Сводка турнира", "Турнирная таблица"):
            target_ws = ws_main
        elif title.startswith("Лучшие") or title == "Статистика по позициям":
            target_ws = ws_players
        elif title == "История матчей":
            target_ws = ws_matches
        else:  # Все секции вида "Состав: <Команда>"
            target_ws = ws_rosters

        _write_section(target_ws, title, headers, rows, header_fill, thin_border)

    for ws in wb.worksheets:
        for col in ws.columns:
            max_length = 0
            column_letter = col[0].column_letter
            for cell in col:
                if cell.row == 1:
                    continue
                if cell.value is not None:
                    max_length = max(max_length, len(str(cell.value)))
            ws.column_dimensions[column_letter].width = max(max_length + 4, 12)

    base_dir = Path(__file__).resolve().parent
    data_dir = Path(os.getenv("DATA_DIR", base_dir))
    #os.makedirs(data_dir, exist_ok=True)
    report_path = os.path.join(data_dir, "tournament_report.xlsx")
    wb.save(report_path)
    print(f"Отчёт сохранён в файл '{report_path}'.")
