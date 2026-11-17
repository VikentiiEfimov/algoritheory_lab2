from .player import Player

class Team:
    HEADER_LABELS = ["Команда", "Игры", "Очки", "Победы", "Ничьи", "Поражения"]

    def __init__(self, name: str):
        self.name = name
        self.players = {}
        self.wins = 0
        self.draws = 0
        self.losses = 0

    def add_player(self, player: Player):
        if player.name in self.players:
            raise ValueError(f"Игрок '{player.name}' уже участвует в команде")
        self.players[player.name] = player

    def add_match_result(self, outcome: str):
        if outcome == "win":
            self.wins += 1
        elif outcome == "draw":
            self.draws += 1
        elif outcome == "loss":
            self.losses += 1

    def get_points(self) -> int:
        """3 очка за победу, 1 за ничью"""
        return (self.wins * 3) + (self.draws * 1)

    def get_total_matches(self) -> int:
        return self.wins + self.draws + self.losses

    def to_excel_row(self) -> list:
        """Возвращает список значений команды для строки Excel."""
        return [
            self.name,
            self.get_total_matches(),
            self.get_points(),
            self.wins,
            self.draws,
            self.losses
        ]

    def get_info(self) -> str:
        """Собирает строку для консоли, соединяя заголовки и значения через zip."""
        pairs = [f"{label}: {val}" for label, val in zip(self.HEADER_LABELS, self.to_excel_row())]
        return "\n".join(pairs)