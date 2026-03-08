from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from app.models import WordRecord


SCHEMA = """
CREATE TABLE IF NOT EXISTS words (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  word TEXT NOT NULL UNIQUE,
  translation TEXT,
  short_definition TEXT,
  part_of_speech TEXT,
  example_de TEXT,
  example_translation TEXT,
  source TEXT,
  tags TEXT,
  difficulty INTEGER,
  times_shown INTEGER NOT NULL DEFAULT 0,
  last_shown_at TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  is_active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS notification_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  word_id INTEGER NOT NULL,
  shown_at TEXT NOT NULL,
  status TEXT NOT NULL,
  message TEXT,
  FOREIGN KEY (word_id) REFERENCES words(id)
);
"""


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def init_db(connection: sqlite3.Connection) -> None:
    connection.executescript(SCHEMA)
    connection.commit()


def upsert_word(connection: sqlite3.Connection, payload: dict[str, object]) -> None:
    now = _now()
    connection.execute(
        """
        INSERT INTO words (
          word, translation, short_definition, part_of_speech, example_de,
          example_translation, source, tags, difficulty, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(word) DO UPDATE SET
          translation = excluded.translation,
          short_definition = excluded.short_definition,
          part_of_speech = excluded.part_of_speech,
          example_de = excluded.example_de,
          example_translation = excluded.example_translation,
          source = COALESCE(excluded.source, words.source),
          tags = excluded.tags,
          difficulty = excluded.difficulty,
          updated_at = excluded.updated_at
        """,
        (
            payload["word"],
            payload.get("translation"),
            payload.get("short_definition"),
            payload.get("part_of_speech"),
            payload.get("example_de"),
            payload.get("example_translation"),
            payload.get("source"),
            payload.get("tags"),
            payload.get("difficulty"),
            now,
            now,
        ),
    )
    connection.commit()


def fetch_all_words(connection: sqlite3.Connection, limit: int | None = None) -> list[WordRecord]:
    query = """
        SELECT *
        FROM words
        ORDER BY word COLLATE NOCASE ASC
    """
    params: tuple[object, ...] = ()
    if limit is not None:
        query += " LIMIT ?"
        params = (limit,)
    rows = connection.execute(query, params).fetchall()
    return [_row_to_word(row) for row in rows]


def fetch_candidate_words(
    connection: sqlite3.Connection, min_hours_between_repeats: int
) -> list[WordRecord]:
    rows = connection.execute(
        """
        SELECT *
        FROM words
        WHERE is_active = 1
          AND (
            last_shown_at IS NULL OR
            datetime(last_shown_at) <= datetime('now', '-' || ? || ' hours')
          )
        ORDER BY times_shown ASC, COALESCE(last_shown_at, '1970-01-01T00:00:00+00:00') ASC
        """,
        (min_hours_between_repeats,),
    ).fetchall()
    return [_row_to_word(row) for row in rows]


def fetch_any_active_words(connection: sqlite3.Connection) -> list[WordRecord]:
    rows = connection.execute(
        """
        SELECT *
        FROM words
        WHERE is_active = 1
        ORDER BY times_shown ASC, COALESCE(last_shown_at, '1970-01-01T00:00:00+00:00') ASC
        """
    ).fetchall()
    return [_row_to_word(row) for row in rows]


def record_notification_result(
    connection: sqlite3.Connection, word_id: int, status: str, message: str | None = None
) -> None:
    connection.execute(
        """
        INSERT INTO notification_log (word_id, shown_at, status, message)
        VALUES (?, ?, ?, ?)
        """,
        (word_id, _now(), status, message),
    )
    connection.commit()


def mark_word_shown(connection: sqlite3.Connection, word_id: int) -> None:
    now = _now()
    connection.execute(
        """
        UPDATE words
        SET times_shown = times_shown + 1,
            last_shown_at = ?,
            updated_at = ?
        WHERE id = ?
        """,
        (now, now, word_id),
    )
    connection.commit()


def get_stats(connection: sqlite3.Connection) -> dict[str, int]:
    total_words = connection.execute("SELECT COUNT(*) FROM words").fetchone()[0]
    active_words = connection.execute("SELECT COUNT(*) FROM words WHERE is_active = 1").fetchone()[0]
    shown_words = connection.execute("SELECT COUNT(*) FROM words WHERE times_shown > 0").fetchone()[0]
    notifications_sent = connection.execute(
        "SELECT COUNT(*) FROM notification_log WHERE status = 'sent'"
    ).fetchone()[0]
    notification_failures = connection.execute(
        "SELECT COUNT(*) FROM notification_log WHERE status = 'failed'"
    ).fetchone()[0]
    return {
        "total_words": total_words,
        "active_words": active_words,
        "shown_words": shown_words,
        "notifications_sent": notifications_sent,
        "notification_failures": notification_failures,
    }


def _row_to_word(row: sqlite3.Row) -> WordRecord:
    return WordRecord(
        id=row["id"],
        word=row["word"],
        translation=row["translation"],
        short_definition=row["short_definition"],
        part_of_speech=row["part_of_speech"],
        example_de=row["example_de"],
        example_translation=row["example_translation"],
        source=row["source"],
        tags=row["tags"],
        difficulty=row["difficulty"],
        times_shown=row["times_shown"],
        last_shown_at=row["last_shown_at"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        is_active=row["is_active"],
    )


def _now() -> str:
    return datetime.now(UTC).isoformat()
