from .player import Player

class Team:
    def __init__(self, name: str):
        self.name = name
        self.players = {}  # Словарь {имя_игрока: объект Player}
        self.wins = 0
        self.draws = 0
        self.losses = 0

    def add_player(self, player: Player):
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
