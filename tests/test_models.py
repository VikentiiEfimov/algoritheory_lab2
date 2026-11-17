import pytest
from sports_package import Player, Team, Match, Tournament

def test_player_valid_creation():
    p = Player("Иван", "Нападающий")
    assert p.name == "Иван"
    assert p.position == "Нападающий"
    assert p.goals == 0

def test_player_invalid_position():
    with pytest.raises(ValueError, match="Недопустимая позиция"):
        Player("Петр", "Судья")

def test_player_negative_goals():
    p = Player("Олег", "Защитник")
    with pytest.raises(ValueError, match="Количество голов не может быть отрицательным"):
        p.goals = -5

def test_player_dunder_methods():
    p1 = Player("Иван", "Нападающий")
    p2 = Player("Иван", "Нападающий")
    p3 = Player("Петр", "Вратарь")
    assert str(p1) == "Игрок Иван (Нападающий)"
    assert p1 == p2
    assert p1 != p3

def test_team_add_player_and_len():
    t = Team("Спартак")
    assert len(t) == 0
    t.add_player(Player("Иван", "Нападающий"))
    assert len(t) == 1
    with pytest.raises(ValueError, match="уже участвует в команде"):
        t.add_player(Player("Иван", "Защитник"))

def test_match_processing_and_validation():
    t1 = Team("Хозяева")
    t2 = Team("Гости")
    m = Match(t1, t2, 3, 1)
    
    assert t1.wins == 1
    assert t2.losses == 1
    assert m.home_goals == 3
    assert m.away_goals == 1
    assert str(m) == "Матч: Хозяева 3 : 1 Гости"

    with pytest.raises(ValueError, match="не может быть отрицательным"):
        Match(t1, t2, -1, 0)

def test_tournament_play_match():
    tournament = Tournament("Лига")
    t1 = Team("А")
    t2 = Team("Б")
    t1.add_player(Player("Игрок1", "Нападающий"))
    
    tournament.add_team(t1)
    tournament.add_team(t2)
    
    tournament.play_match("А", "Б", 2, 0, {"Игрок1": (2, 0)})
    
    assert len(tournament) == 2
    assert t1.get_points() == 3
    assert t1.players["Игрок1"].goals == 2

def test_tournament_analytics_and_reports():
    tournament = Tournament("Кубок")
    t1 = Team("Зенит")
    t2 = Team("ЦСКА")
    p1 = Player("Артём", "Нападающий")
    p2 = Player("Игорь", "Вратарь")
    
    t1.add_player(p1)
    t2.add_player(p2)
    tournament.add_team(t1)
    tournament.add_team(t2)
    
    tournament.play_match("Зенит", "ЦСКА", 2, 1, {"Артём": (2, 0)})
    
    # Проверка подсчёта голов команды
    assert tournament.get_team_goals("Зенит") == (2, 1)
    assert tournament.get_team_goals("ЦСКА") == (1, 2)
    
    # Проверка турнирной таблицы и бомбардиров
    table = tournament.get_table()
    assert table[0].name == "Зенит"
    
    scorers = tournament.get_top_scorers(5)
    assert len(scorers) == 1
    assert scorers[0].name == "Артём"
    
    # Проверка формирования секций отчёта (для консоли и Excel)
    sections = tournament.get_report_sections()
    assert len(sections) >= 4
    assert sections[0][0] == "Сводка турнира"
