from .player import Player
from .team import Team
from .match import Match

class Tournament:
    def __init__(self, name: str):
        self.name = name
        self.teams: dict[str, Team] = {}
        self.matches: list[Match] = []

    def add_team(self, team: Team) -> None:
        self.teams[team.name] = team

    def get_team(self, name: str) -> Team:
        if name not in self.teams:
            raise KeyError(f"Команда '{name}' не найдена в турнире")
        return self.teams[name]

    def get_player(self, player_name: str):
        """Ищет игрока по имени во всех командах турнира."""
        for team in self.teams.values():
            if player_name in team.players:
                return team.players[player_name], team.name
        raise KeyError(f"Игрок '{player_name}' не найден в турнире.")

    def play_match(
        self,
        home_name: str,
        away_name: str,
        home_goals: int,
        away_goals: int,
        player_stats: dict | None = None,
    ) -> Match:
        """Создаёт, регистрирует и возвращает матч."""
        home = self.get_team(home_name)
        away = self.get_team(away_name)
        match = Match(home, away, home_goals, away_goals)

        if player_stats:
            for team in (home, away):
                for player in team.players.values():
                    if player.name in player_stats:
                        goals, assists = player_stats[player.name]
                        player.add_stats(goals, assists)
            match.set_player_stats(player_stats)

        self.matches.append(match)
        return match

    def get_team_matches(self, team_name: str) -> list:
        self.get_team(team_name)  # проверка существования
        return [
            m for m in self.matches
            if m.home_team.name == team_name or m.away_team.name == team_name
        ]
    
    def get_table(self) -> list[Team]:
        """Турнирная таблица: список команд, отсортированных по очкам."""
        return sorted(
            self.teams.values(),
            key=lambda t: (-t.get_points(), -t.wins, t.name),
        )
        
    def get_top_scorers(self, top_n: int = 10) -> list[Player]:
        """Лучшие бомбардиры турнира."""
        players = [p for t in self.teams.values() for p in t.players.values()]
        scorers = [p for p in players if p.goals > 0]
        return sorted(
            scorers,
            key=lambda p: (-p.goals, -p.get_points(), p.name),
        )[:top_n]

    def get_team_goals(self, team_name: str) -> tuple[int, int]:
        """Возвращает (забито, пропущено) для команды по всем матчам."""
        team = self.get_team(team_name)
        goals_for = goals_against = 0
        for m in self.matches:
            if m.home_team is team:
                goals_for += m.home_goals
                goals_against += m.away_goals
            elif m.away_team is team:
                goals_for += m.away_goals
                goals_against += m.home_goals
        return goals_for, goals_against


    def get_report_sections(self) -> list[tuple[str, list[str], list[list]]]:
        """Список секций отчёта: (заголовок, шапка, строки).
        Один источник данных для консоли и Excel."""
        sections = []

        # 1. Сводка
        total_matches = len(self.matches)
        total_goals = sum(m.home_goals + m.away_goals for m in self.matches)
        avg_goals = round(total_goals / total_matches, 2) if total_matches else 0.0
        sections.append((
            "Сводка турнира",
            ["Параметр", "Значение"],
            [
                ["Команд", len(self.teams)],
                ["Матчей", total_matches],
                ["Голов", total_goals],
                ["Среднее голов за матч", avg_goals],
            ],
        ))

        # 2. Турнирная таблица — переиспользуем Team.to_excel_row()
        table_headers = ["Место"] + Team.HEADER_LABELS
        table_rows = [[i] + team.to_excel_row() for i, team in enumerate(self.get_table(), 1)]
        sections.append(("Турнирная таблица", table_headers, table_rows))

        # 3. Бомбардиры — переиспользуем Player.to_excel_row()
        scorers = [p.to_excel_row() for p in self.get_top_scorers(10)]
        sections.append(("Лучшие бомбардиры (Топ-10)", Player.HEADER_LABELS, scorers))

        # 4. История матчей
        match_rows = [
            [i, m.home_team.name, f"{m.home_goals}:{m.away_goals}", m.away_team.name]
            for i, m in enumerate(self.matches, 1)
        ]
        sections.append(("История матчей", ["№", "Хозяева", "Счёт", "Гости"], match_rows))

        # 5. Составы команд
        for team in self.teams.values():
            rows = [p.to_excel_row() for p in team.players.values()] or [["Игроков нет"]]
            sections.append((f"Состав: {team.name}", Player.HEADER_LABELS, rows))

        return sections

