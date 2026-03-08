from __future__ import annotations

import subprocess

from app.config import Settings
from app.models import WordRecord


class NotificationError(RuntimeError):
    """Raised when a native macOS notification cannot be sent."""


def build_notification_payload(word: WordRecord, settings: Settings) -> tuple[str, str, str]:
    title = f"{settings.notification_title_prefix}{word.word}"
    subtitle = word.translation or word.part_of_speech or "German word"

    body_parts: list[str] = []
    if word.short_definition:
        body_parts.append(word.short_definition.strip())
    if settings.include_example and word.example_de:
        body_parts.append(f"Example: {word.example_de.strip()}")
    body = " ".join(body_parts).strip() or "Open the CLI for details."

    if len(body) > settings.max_body_length:
        body = body[: settings.max_body_length - 1].rstrip() + "…"

    return title, subtitle, body


def send_notification(settings: Settings, title: str, subtitle: str, body: str) -> None:
    full_body = f"{subtitle}\n{body}".strip() if subtitle else body
    result = subprocess.run(
        [
            "osascript",
            "-e",
            "on run argv",
            "-e",
            "display notification (item 2 of argv) with title (item 1 of argv)",
            "-e",
            "end run",
            "--",
            title,
            full_body,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise NotificationError(result.stderr.strip() or "osascript failed")
