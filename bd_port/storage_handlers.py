from sports_package import Tournament
from bd_port import database


def save_to_db(tournament: Tournament) -> None:
    """Сохраняет турнир в SQLite3."""
    try:
        conn = database.get_connection()
        database.init_db(conn)
        database.save_tournament(tournament, conn)
        conn.close()
    except Exception as e:
        print(f"[Ошибка БД] {e}")


def load_from_db() -> Tournament:
    """Загружает турнир из SQLite3."""
    try:
        conn = database.get_connection()
        database.init_db(conn)
        tournament = database.load_tournament(conn)
        conn.close()
        return tournament
    except Exception as e:
        print(f"[Ошибка БД] {e}")
        return Tournament("Футбольный турнир")
