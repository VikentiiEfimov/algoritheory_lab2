from openpyxl import Workbook
from openpyxl.styles import Font

from sports_package import Tournament


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

    wb.save("ex_port/tournament_report.xlsx")
    print("Отчёт сохранён в файл 'tournament_report.xlsx'.")