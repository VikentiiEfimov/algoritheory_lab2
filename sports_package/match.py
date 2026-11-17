from .base import BaseEntity
from .team import Team

class Match(BaseEntity):
    def __init__(self, home_team: Team, away_team: Team, home_goals: int, away_goals: int):
        self.home_team = home_team
        self.away_team = away_team
        self.home_goals = home_goals
        self.away_goals = away_goals
        self.player_stats: dict = {}
        self._process_match()

    # --- Managed атрибуты ---
    @property
    def home_goals(self) -> int:
        return self._home_goals

    @home_goals.setter
    def home_goals(self, value: int):
        if value < 0:
            raise ValueError("Количество голов хозяев не может быть отрицательным.")
        self._home_goals = value

    @property
    def away_goals(self) -> int:
        return self._away_goals

    @away_goals.setter
    def away_goals(self, value: int):
        if value < 0:
            raise ValueError("Количество голов гостей не может быть отрицательным.")
        self._away_goals = value

    # --- Логика ---
    def _process_match(self):
        if self.home_goals > self.away_goals:
            self.home_team.add_match_result("win")
            self.away_team.add_match_result("loss")
        elif self.home_goals < self.away_goals:
            self.home_team.add_match_result("loss")
            self.away_team.add_match_result("win")
        else:
            self.home_team.add_match_result("draw")
            self.away_team.add_match_result("draw")

    def set_player_stats(self, stats: dict) -> None:
        self.player_stats.update(stats)

    def get_result_info(self) -> str:
        return f"{self.home_team.name} {self.home_goals} : {self.away_goals} {self.away_team.name}"

    # --- Реализация методов абстрактного класса ---
    def to_excel_row(self) -> list:
        return [self.home_team.name, f"{self.home_goals}:{self.away_goals}", self.away_team.name]

    def get_info(self) -> str:
        return f"Матч: {self.get_result_info()}"

    # --- Dunder-методы ---
    def __str__(self) -> str:
        return f"Матч: {self.get_result_info()}"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Match):
            return NotImplemented
        return (self.home_team == other.home_team and 
                self.away_team == other.away_team and 
                self.home_goals == other.home_goals and 
                self.away_goals == other.away_goals)
