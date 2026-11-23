from .base import BaseEntity

class Player(BaseEntity):
    HEADER_LABELS = ["Игрок", "Позиция", "Матчи", "Гол + Пас", "Ср. голов"]
    VALID_POSITIONS = {"Нападающий", "Защитник", "Вратарь", "Полузащитник"}

    def __init__(self, name: str, position: str):
        self.name = name
        self.position = position
        self._goals = 0
        self._assists = 0
        self._matches_played = 0

    # --- Managed атрибуты (Properties) ---
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        if not value or not value.strip():
            raise ValueError("Имя игрока не может быть пустым.")
        self._name = value.strip()

    @property
    def position(self) -> str:
        return self._position

    @position.setter
    def position(self, value: str):
        if value not in self.VALID_POSITIONS:
            raise ValueError(f"Недопустимая позиция: '{value}'. Разрешены: {', '.join(self.VALID_POSITIONS)}")
        self._position = value

    @property
    def goals(self) -> int:
        return self._goals

    @goals.setter
    def goals(self, value: int):
        if value < 0:
            raise ValueError("Количество голов не может быть отрицательным.")
        self._goals = value

    @property
    def assists(self) -> int:
        return self._assists

    @assists.setter
    def assists(self, value: int):
        if value < 0:
            raise ValueError("Количество пасов не может быть отрицательным.")
        self._assists = value

    # --- Логика ---
    def add_stats(self, goals: int, assists: int):
        self.goals += goals
        self.assists += assists
        self._matches_played += 1

    def get_points(self) -> int:
        return self.goals + self.assists

    def get_avg_goals(self) -> float:
        if self._matches_played == 0:
            return 0.0
        return round(self.goals / self._matches_played, 2)

    # --- Реализация методов абстрактного класса ---
    def to_excel_row(self) -> list:
        return [self.name, self.position, self._matches_played,
                f"{self.goals} + {self.assists} ({self.get_points()})", self.get_avg_goals()]

    def get_info(self) -> str:
        pairs = [f"{label:<15} {val}" for label, val in zip(self.HEADER_LABELS, self.to_excel_row())]
        return "\n".join(pairs)

    # --- Dunder-методы ---
    def __str__(self) -> str:
        return f"Игрок {self.name} ({self.position})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Player):
            return NotImplemented
        return self.name == other.name and self.position == other.position