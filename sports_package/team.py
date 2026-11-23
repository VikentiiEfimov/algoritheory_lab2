from .base import BaseEntity
from .player import Player

class Team(BaseEntity):
    HEADER_LABELS = ["Команда", "Игры", "Очки", "Победы", "Ничьи", "Поражения"]

    def __init__(self, name: str):
        self.name = name
        self.players = {}
        self._wins = 0
        self._draws = 0
        self._losses = 0

    # --- Managed атрибуты ---
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        if not value or not value.strip():
            raise ValueError("Название команды не может быть пустым.")
        self._name = value.strip()

    @property
    def wins(self) -> int:
        return self._wins

    @wins.setter
    def wins(self, value: int):
        if value < 0:
            raise ValueError("Количество побед не может быть отрицательным.")
        self._wins = value

    @property
    def draws(self) -> int:
        return self._draws
    
    @draws.setter
    def draws(self, value: int):
        if value < 0:
            raise ValueError("Количество ничьих не может быть отрицательным.")
        self._draws = value

    @property
    def losses(self) -> int:
        return self._losses

    @losses.setter
    def losses(self, value: int):
        if value < 0:
            raise ValueError("Количество поражений не может быть отрицательным.")
        self._losses = value

    # --- Логика ---
    def add_player(self, player: Player):
        if player.name in self.players:
            raise ValueError(f"Игрок '{player.name}' уже участвует в команде")
        self.players[player.name] = player

    def add_match_result(self, outcome: str):
        if outcome == "win":
            self.wins += 1
        elif outcome == "draw":
            self._draws += 1
        elif outcome == "loss":
            self._losses += 1

    def get_points(self) -> int:
        return (self.wins * 3) + (self._draws * 1)

    def get_total_matches(self) -> int:
        return self.wins + self._draws + self._losses

    # --- Реализация методов абстрактного класса ---
    def to_excel_row(self) -> list:
        return [self.name, self.get_total_matches(), self.get_points(),
                self.wins, self._draws, self._losses]

    def get_info(self) -> str:
        pairs = [f"{label:<15} {val}" for label, val in zip(self.HEADER_LABELS, self.to_excel_row())]
        return "\n".join(pairs)

    # --- Dunder-методы ---
    def __str__(self) -> str:
        return f"Команда {self.name} (игроков: {len(self.players)})"

    def __len__(self) -> int:
        return len(self.players)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Team):
            return NotImplemented
        return self.name == other.name