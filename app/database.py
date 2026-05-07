import sqlite3
from datetime import datetime, timezone

from app.config import DB_PATH
from app.models import Recommendation, HistoryRecord


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _now() -> datetime:
    return datetime.now(timezone.utc)


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
    recommendation: Recommendation,
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
                recommendation.series_title,
                recommendation.series_title_ru,
                recommendation.genre,
                recommendation.reason,
                ", ".join(providers),
                _now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            ),
        )
        conn.commit()


def get_history(username: str) -> list[HistoryRecord]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM recommendations WHERE username = ? ORDER BY created_at DESC",
            (username,),
        ).fetchall()
    return [HistoryRecord.model_validate(dict(row)) for row in rows]
