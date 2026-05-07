import sqlite3
from datetime import datetime

from app.config import DB_PATH


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS recommendations (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                username    TEXT NOT NULL,
                series      TEXT NOT NULL,
                series_ru   TEXT NOT NULL,
                genre       TEXT,
                reason      TEXT,
                providers   TEXT,
                created_at  TEXT NOT NULL
            )
        """)
        conn.commit()


def save_recommendation(
    username: str,
    recommendation: dict,
    providers: list[str],
) -> None:
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO recommendations
                (username, series, series_ru, genre, reason, providers, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                username,
                recommendation.get("series_title", ""),
                recommendation.get("series_title_ru", ""),
                recommendation.get("genre", ""),
                recommendation.get("reason", ""),
                ", ".join(providers),
                datetime.utcnow().isoformat(),
            ),
        )
        conn.commit()


def get_history(username: str) -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM recommendations WHERE username = ? ORDER BY created_at DESC",
            (username,),
        ).fetchall()
    return [dict(row) for row in rows]
