from .team import Team

class Match:
    def __init__(self, home_team: Team, away_team: Team, home_goals: int, away_goals: int):
        self.home_team = home_team
        self.away_team = away_team
        self.home_goals = home_goals
        self.away_goals = away_goals
        self._process_match()

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
    