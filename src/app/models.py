from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class WordRecord:
    id: int
    word: str
    article: str | None
    translation: str | None
    short_definition: str | None
    part_of_speech: str | None
    example_de: str | None
    example_translation: str | None
    source: str | None
    tags: str | None
    difficulty: int | None
    times_shown: int
    last_shown_at: str | None
    created_at: str
    updated_at: str
    is_active: int

    @property
    def display_word(self) -> str:
        if self.article:
            return f"{self.article} {self.word}"
        return self.word
