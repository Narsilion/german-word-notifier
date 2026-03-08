from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Settings:
    project_root: Path
    db_path: Path
    default_csv_path: Path
    notification_title_prefix: str
    max_body_length: int
    include_example: bool
    min_hours_between_repeats: int


def load_settings() -> Settings:
    project_root = Path(__file__).resolve().parents[2]
    env_file = project_root / ".env"
    env_values = _parse_env_file(env_file)

    db_path = _resolve_path(project_root, _get_value("GWN_DB_PATH", env_values, "./gwn.db"))
    default_csv = _resolve_path(
        project_root, _get_value("GWN_DEFAULT_CSV", env_values, "./data/words.csv")
    )

    return Settings(
        project_root=project_root,
        db_path=db_path,
        default_csv_path=default_csv,
        notification_title_prefix=_get_value("GWN_NOTIFICATION_TITLE_PREFIX", env_values, ""),
        max_body_length=int(_get_value("GWN_MAX_BODY_LENGTH", env_values, "220")),
        include_example=_get_bool(_get_value("GWN_INCLUDE_EXAMPLE", env_values, "true")),
        min_hours_between_repeats=int(
            _get_value("GWN_MIN_HOURS_BETWEEN_REPEATS", env_values, "8")
        ),
    )


def _get_value(key: str, env_values: dict[str, str], default: str) -> str:
    return os.environ.get(key, env_values.get(key, default))


def _get_bool(raw: str) -> bool:
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _resolve_path(project_root: Path, value: str) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    return project_root / path


def _parse_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip().strip("'\"")
    return values
