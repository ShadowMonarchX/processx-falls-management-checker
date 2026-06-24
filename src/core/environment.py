from __future__ import annotations

import os
from pathlib import Path


def load_env_file(path: Path | str = ".env") -> dict[str, str]:
    env_path = Path(path)
    values: dict[str, str] = {}
    if not env_path.exists():
        return values

    # Parse key/value pairs without mutating process state so callers can
    # decide when to apply values and keep startup side effects explicit.
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
    # Callers use this thin wrapper so environment access stays centralized and
    # easier to audit when startup behavior or provider selection changes.
    return os.getenv(key, default)


def apply_env_file(path: Path | str = ".env") -> dict[str, str]:
    values = load_env_file(path)
    # Keep existing process values authoritative so shell overrides and test
    # fixtures are not accidentally clobbered by a local .env file.
    for key, value in values.items():
        os.environ.setdefault(key, value)
    return values


def normalize_optional_env(value: str | None) -> str | None:
    # Empty strings and whitespace-only strings must behave like "unset"
    # because several downstream SDKs interpret "" as a real credential value.
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None
