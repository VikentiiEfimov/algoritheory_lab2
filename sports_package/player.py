class Player:
    HEADER_LABELS = ["Игрок", "Позиция", "Матчи", "Гол + Пас", "Ср. голов"]

    def __init__(self, name: str, position: str):
        self.name = name
        self.position = position
        self.goals = 0
        self.assists = 0
        self.matches_played = 0

    def add_stats(self, goals: int, assists: int):
        self.goals += goals
        self.assists += assists
        self.matches_played += 1

    def get_points(self) -> int:
        """Очки по системе гол+пас"""
        return self.goals + self.assists

    def get_avg_goals(self) -> float:
        if self.matches_played == 0:
            return 0.0
        return round(self.goals / self.matches_played, 2)

    def to_excel_row(self) -> list:
        """Возвращает список значений игрока для строки Excel."""
        return [
            self.name,
            self.position,
            self.matches_played,
            f"{self.goals} + {self.assists} ({self.get_points()})",
            self.get_avg_goals()
        ]

    def get_info(self) -> str:
        """Собирает строку для консоли, соединяя заголовки и значения через zip."""
        pairs = [f"{label}: {val}" for label, val in zip(self.HEADER_LABELS, self.to_excel_row())]
        return "\n".join(pairs)