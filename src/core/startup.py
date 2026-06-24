from __future__ import annotations

import logging
from pathlib import Path

from src.core.constants import INPUT_WORKBOOK_PATH, LOGS_DIR, POLICY_PATH
from src.core.environment import get_env


def validate_startup(logger: logging.Logger | None = None) -> None:
    logger = logger or logging.getLogger("processx")
    checks = {
        "policy_document": POLICY_PATH,
        "input_workbook": INPUT_WORKBOOK_PATH,
        "logs_dir": LOGS_DIR,
    }
    for name, path in checks.items():
        if not Path(path).exists():
            logger.warning("startup_validation_missing", extra={"resource": name, "path": str(path)})

    cache_dir = Path(get_env("MODEL_CACHE_DIR", "models") or "models")
    if not cache_dir.exists():
        cache_dir.mkdir(parents=True, exist_ok=True)
        logger.warning("startup_validation_created_cache_dir", extra={"path": str(cache_dir)})

    monitored_envs = [
        "GEMINI_API_KEY",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "HF_TOKEN",
        "OLLAMA_HOST",
        "LOCAL_GGUF_AUTO_DOWNLOAD",
        "MODEL_CACHE_DIR",
        "LOG_LEVEL",
        "LLM_TIMEOUT_SECONDS",
        "LLM_RETRY_COUNT",
    ]
    for key in monitored_envs:
        if get_env(key) is None:
            logger.warning("startup_validation_env_missing", extra={"env_var": key})
