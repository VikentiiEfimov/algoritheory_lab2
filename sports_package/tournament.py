from .base import BaseEntity
from .player import Player
from .team import Team
from .match import Match

class Tournament(BaseEntity):
    def __init__(self, name: str, created_at: str | None = None):
        super().__init__(created_at)
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
        created_at: str | None = None,
        update_timestamps: bool = True,
    ) -> Match:
        """Создаёт, регистрирует и возвращает матч."""
        home = self.get_team(home_name)
        away = self.get_team(away_name)
        match = Match(home, away, home_goals, away_goals, created_at=created_at)

        stats = player_stats or {}
        for team in (home, away):
            for player in team.players.values():
                goals, assists = stats.get(player.name, (0, 0))
                player.add_stats(goals, assists)
                if update_timestamps and (goals > 0 or assists > 0):
                    player.touch()
        if player_stats:
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
        return [p for _, p in self.get_top_scorers_with_team(top_n)]

    def get_top_scorers_with_team(self, top_n: int = 10) -> list[tuple[str, Player]]:
        players_with_team = [
            (t.name, p) for t in self.teams.values() for p in t.players.values()
        ]
        scorers = [pt for pt in players_with_team if pt[1].goals > 0]
        return sorted(
            scorers,
            key=lambda pt: (-pt[1].goals, -pt[1].get_points(), pt[1].name),
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


    # вспомогательные методы для статистики ---
    def get_top_assisters_with_team(self, top_n: int = 10) -> list[tuple[str, Player]]:
        """Топ игроков по голевым передачам."""
        players_with_team = [
            (t.name, p) for t in self.teams.values() for p in t.players.values()
        ]
        assisters = [pt for pt in players_with_team if pt[1].assists > 0]
        return sorted(
            assisters,
            key=lambda pt: (-pt[1].assists, -pt[1].get_points(), pt[1].name),
        )[:top_n]

    def get_top_points_with_team(self, top_n: int = 10) -> list[tuple[str, Player]]:
        """Топ игроков по системе Гол + Пас."""
        players_with_team = [
            (t.name, p) for t in self.teams.values() for p in t.players.values()
        ]
        active_players = [pt for pt in players_with_team if pt[1].get_points() > 0]
        return sorted(
            active_players,
            key=lambda pt: (-pt[1].get_points(), -pt[1].goals, pt[1].name),
        )[:top_n]

    def get_position_stats(self) -> list[list]:
        """Статистика результативности по игровым позициям."""
        stats = {pos: {"players": 0, "goals": 0, "assists": 0} for pos in Player.VALID_POSITIONS}
        for team in self.teams.values():
            for p in team.players.values():
                stats[p.position]["players"] += 1
                stats[p.position]["goals"] += p.goals
                stats[p.position]["assists"] += p.assists

        rows = []
        for pos, data in sorted(stats.items(), key=lambda x: -(x[1]["goals"] + x[1]["assists"])):
            total_pts = data["goals"] + data["assists"]
            rows.append([pos, data["players"], data["goals"], data["assists"], total_pts])
        return rows
    

    def get_report_sections(self, include_timestamps: bool = False) -> list[tuple[str, list[str], list[list]]]:
        sections = []

        # 1. Расширенная сводка турнира
        total_matches = len(self.matches)
        total_goals = sum(m.home_goals + m.away_goals for m in self.matches)
        avg_goals = round(total_goals / total_matches, 2) if total_matches else 0.0

        summary_rows = [
            ["Команд", len(self.teams)],
            ["Матчей", total_matches],
            ["Голов", total_goals],
            ["Среднее голов за матч", avg_goals],
        ]

        if self.matches:
            # Самый результативный матч
            top_match = max(self.matches, key=lambda m: m.home_goals + m.away_goals)
            summary_rows.append([
                "Самый результативный матч",
                f"{top_match.get_result_info()} (всего голов: {top_match.home_goals + top_match.away_goals})"
            ])

        if self.teams:
            # Лучшая атака и защита (среди команд, сыгравших хотя бы 1 матч)
            active_teams = [t for t in self.teams.values() if t.get_total_matches() > 0]
            if active_teams:
                best_attack = max(active_teams, key=lambda t: self.get_team_goals(t.name)[0])
                gf_att, _ = self.get_team_goals(best_attack.name)
                summary_rows.append(["Лучшая атака", f"{best_attack.name} ({gf_att} гол.)"])

                best_defense = min(active_teams, key=lambda t: self.get_team_goals(t.name)[1] / t.get_total_matches())
                _, ga_def = self.get_team_goals(best_defense.name)
                summary_rows.append(["Лучшая оборона", f"{best_defense.name} (пропущено: {ga_def})"])

        sections.append(("Сводка турнира", ["Параметр", "Значение"], summary_rows))

        # 2. Расширенная турнирная таблица (добавлены ЗМ, ПМ, РМ, % побед)
        table_headers = ["Место"] + list(Team.HEADER_LABELS) + ["ЗМ", "ПМ", "РМ", "% побед"]
        if include_timestamps:
            table_headers.append("Создана")
            
        # Сортируем с учётом разницы мячей и забитых голов
        sorted_teams = sorted(
            self.teams.values(),
            key=lambda t: (
                -t.get_points(),
                -(self.get_team_goals(t.name)[0] - self.get_team_goals(t.name)[1]),
                -self.get_team_goals(t.name)[0],
                t.name
            )
        )

        table_rows = []
        for i, team in enumerate(sorted_teams, 1):
            gf, ga = self.get_team_goals(team.name)
            gd = f"{gf - ga:+d}" if gf != ga else "0"
            win_rate = f"{(team.wins / team.get_total_matches() * 100):.1f}%" if team.get_total_matches() else "0.0%"
            
            row = [i] + team.to_excel_row() + [gf, ga, gd, win_rate]
            if include_timestamps:
                row.append(team.created_at)
            table_rows.append(row)
        sections.append(("Турнирная таблица", table_headers, table_rows))

        # 3. Топ-10 по системе Гол + Пас (с указанием команды)
        pts_headers = ["Команда"] + list(Player.HEADER_LABELS)
        if include_timestamps:
            pts_headers.append("Создан")
        pts_rows = []
        for t_name, p in self.get_top_points_with_team(10):
            row = [t_name] + list(p.to_excel_row())
            if include_timestamps:
                row.append(p.created_at)
            pts_rows.append(row)
        sections.append(("Лучшие по системе Гол + Пас (Топ-10)", pts_headers, pts_rows))

        # 4. Лучшие бомбардиры (Топ-10)
        scorer_headers = ["Команда"] + list(Player.HEADER_LABELS)
        if include_timestamps:
            scorer_headers.append("Создан")
        scorer_rows = []
        for t_name, p in self.get_top_scorers_with_team(10):
            row = [t_name] + list(p.to_excel_row())
            if include_timestamps:
                row.append(p.created_at)
            scorer_rows.append(row)
        sections.append(("Лучшие бомбардиры (Топ-10)", scorer_headers, scorer_rows))

        # 5. Лучшие ассистенты (Топ-10)
        assist_headers = ["Команда"] + list(Player.HEADER_LABELS)
        if include_timestamps:
            assist_headers.append("Создан")
        assist_rows = []
        for t_name, p in self.get_top_assisters_with_team(10):
            row = [t_name] + list(p.to_excel_row())
            if include_timestamps:
                row.append(p.created_at)
            assist_rows.append(row)
        sections.append(("Лучшие ассистенты (Топ-10)", assist_headers, assist_rows))

        # 6. Статистика по позициям
        sections.append((
            "Статистика по позициям",
            ["Позиция", "Всего игроков", "Голы", "Пасы", "Всего очков (Г+П)"],
            self.get_position_stats()
        ))

        # 7. История матчей
        match_headers = ["№", "Хозяева", "Счёт", "Гости"]
        if include_timestamps:
            match_headers.append("Создан")
        match_rows = []
        for i, m in enumerate(self.matches, 1):
            row = [i, m.home_team.name, f"{m.home_goals}:{m.away_goals}", m.away_team.name]
            if include_timestamps:
                row.append(m.created_at)
            match_rows.append(row)
        sections.append(("История матчей", match_headers, match_rows))

        # 8. Составы
        roster_headers = list(Player.HEADER_LABELS)
        if include_timestamps:
            roster_headers.append("Создан")
        for team in self.teams.values():
            rows = []
            for p in team.players.values():
                row = list(p.to_excel_row())
                if include_timestamps:
                    row.append(p.created_at)
                rows.append(row)
            if not rows:
                empty_row = ["Игроков нет"] + [""] * (len(roster_headers) - 1)
                rows = [empty_row]
            sections.append((f"Состав: {team.name}", roster_headers, rows))

        return sections


    # --- Реализация методов абстрактного класса ---
    def to_excel_row(self) -> list:
        return [self.name, len(self.teams), len(self.matches)]

    def get_info(self) -> str:
        return f"Турнир: {self.name} (Команд: {len(self.teams)}, Матчей: {len(self.matches)})"

    # --- Dunder-методы ---
    def __str__(self) -> str:
        return self.get_info()

    def __len__(self) -> int:
        return len(self.teams)