from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

from app import db, notifier, selector
from app.config import load_settings
from app.models import WordRecord
from app.services.importer import import_csv


def main() -> int:
    settings = load_settings()
    parser = build_parser()
    args = parser.parse_args()

    try:
        return dispatch(args, settings)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except sqlite3.Error as exc:
        print(f"Database error: {exc}", file=sys.stderr)
        return 1
    except notifier.NotificationError as exc:
        print(f"Notification error: {exc}", file=sys.stderr)
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gwn", description="German Word Notifier CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init-db", help="Create the SQLite schema")

    import_parser = subparsers.add_parser("import-csv", help="Import words from CSV")
    import_parser.add_argument("path", nargs="?", help="CSV file path")

    list_parser = subparsers.add_parser("list-words", help="List words in the database")
    list_parser.add_argument("--limit", type=int, default=20, help="Maximum number of words to display")

    subparsers.add_parser("stats", help="Show database and notification statistics")

    show_parser = subparsers.add_parser("show-notification", help="Send a manual macOS notification")
    show_parser.add_argument("--word", required=True)
    show_parser.add_argument("--translation")
    show_parser.add_argument("--definition")
    show_parser.add_argument("--example")
    show_parser.add_argument("--dry-run", action="store_true")

    run_parser = subparsers.add_parser("run-once", help="Select a word and send one notification")
    run_parser.add_argument("--dry-run", action="store_true")

    return parser


def dispatch(args: argparse.Namespace, settings) -> int:
    connection = db.connect(settings.db_path)
    if args.command == "init-db":
        db.init_db(connection)
        print(f"Initialized database at {settings.db_path}")
        return 0

    db.init_db(connection)

    if args.command == "import-csv":
        csv_path = Path(args.path).expanduser() if args.path else settings.default_csv_path
        if not csv_path.is_absolute():
            csv_path = settings.project_root / csv_path
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        imported = import_csv(connection, csv_path)
        print(f"Imported {imported} words from {csv_path}")
        return 0

    if args.command == "list-words":
        return _list_words(connection, limit=args.limit)

    if args.command == "stats":
        return _print_stats(connection)

    if args.command == "show-notification":
        word = _manual_word_record(args)
        return _notify_word(connection, word, settings, dry_run=args.dry_run, persist=False)

    if args.command == "run-once":
        chosen_word = selector.choose_next_word(
            connection,
            min_hours_between_repeats=settings.min_hours_between_repeats,
        )
        if chosen_word is None:
            print("No active words available. Import or enrich data first.", file=sys.stderr)
            return 1
        return _notify_word(connection, chosen_word, settings, dry_run=args.dry_run, persist=True)

    raise ValueError(f"Unsupported command: {args.command}")


def _list_words(connection: sqlite3.Connection, *, limit: int) -> int:
    words = db.fetch_all_words(connection, limit=limit)
    if not words:
        print("No words found.")
        return 0

    for word in words:
        print(
            f"{word.word} | translation={word.translation or '-'} | "
            f"shown={word.times_shown} | last_shown_at={word.last_shown_at or '-'}"
        )
    return 0


def _print_stats(connection: sqlite3.Connection) -> int:
    stats = db.get_stats(connection)
    for key, value in stats.items():
        print(f"{key}: {value}")
    return 0


def _manual_word_record(args: argparse.Namespace) -> WordRecord:
    return WordRecord(
        id=0,
        word=args.word,
        translation=args.translation,
        short_definition=args.definition,
        part_of_speech=None,
        example_de=args.example,
        example_translation=None,
        source="manual",
        tags=None,
        difficulty=None,
        times_shown=0,
        last_shown_at=None,
        created_at="",
        updated_at="",
        is_active=1,
    )


def _notify_word(
    connection: sqlite3.Connection,
    word: WordRecord,
    settings,
    *,
    dry_run: bool,
    persist: bool,
) -> int:
    title, subtitle, body = notifier.build_notification_payload(word, settings)

    if dry_run:
        print(f"title: {title}")
        print(f"subtitle: {subtitle}")
        print(f"body: {body}")
        return 0

    try:
        notifier.send_notification(settings, title, subtitle, body)
        if persist and word.id:
            db.mark_word_shown(connection, word.id)
            db.record_notification_result(connection, word.id, "sent", body)
    except notifier.NotificationError as exc:
        if persist and word.id:
            db.record_notification_result(connection, word.id, "failed", str(exc))
        raise

    print(f"Sent notification for '{word.word}'")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
