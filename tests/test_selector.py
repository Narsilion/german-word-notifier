from app.models import WordRecord


def test_placeholder() -> None:
    word = WordRecord(
        id=1,
        word="Haus",
        translation="house",
        short_definition="A building",
        part_of_speech="noun",
        example_de=None,
        example_translation=None,
        source="test",
        tags=None,
        difficulty=None,
        times_shown=0,
        last_shown_at=None,
        created_at="",
        updated_at="",
        is_active=1,
    )
    assert word.word == "Haus"
