from __future__ import annotations

import os
from pathlib import Path


def load_env_file(path: Path | str = ".env") -> dict[str, str]:
    env_path = Path(path)
    values: dict[str, str] = {}
    if not env_path.exists():
        return values

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key:
            continue
        values[key] = value.strip().strip("'\"")
    return values


def get_env(key: str, default: str | None = None) -> str | None:
    return os.getenv(key, default)


def apply_env_file(path: Path | str = ".env") -> dict[str, str]:
    values = load_env_file(path)
    for key, value in values.items():
        os.environ.setdefault(key, value)
    return values
