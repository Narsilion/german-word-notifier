from __future__ import annotations

import csv
from pathlib import Path

from app import db


REQUIRED_COLUMNS = {"word", "translation", "short_definition"}
OPTIONAL_COLUMNS = {
    "article",
    "part_of_speech",
    "example_de",
    "example_translation",
    "tags",
    "difficulty",
    "source",
}


def import_csv(connection, csv_path: Path) -> int:
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("CSV file is empty or missing a header row.")

        fieldnames = {name.strip() for name in reader.fieldnames if name}
        missing = REQUIRED_COLUMNS - fieldnames
        if missing:
            raise ValueError(f"CSV file is missing required columns: {', '.join(sorted(missing))}")

        imported = 0
        for row in reader:
            if not row.get("word", "").strip():
                continue

            payload = {
                "word": row["word"].strip(),
                "article": _clean(row.get("article")),
                "translation": _clean(row.get("translation")),
                "short_definition": _clean(row.get("short_definition")),
                "part_of_speech": _clean(row.get("part_of_speech")),
                "example_de": _clean(row.get("example_de")),
                "example_translation": _clean(row.get("example_translation")),
                "tags": _clean(row.get("tags")),
                "source": _clean(row.get("source")) or "csv-import",
                "difficulty": _parse_int(row.get("difficulty")),
            }
            db.upsert_word(connection, payload)
            imported += 1

    return imported


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _parse_int(value: str | None) -> int | None:
    cleaned = _clean(value)
    if cleaned is None:
        return None
    return int(cleaned)
