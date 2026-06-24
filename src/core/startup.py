from __future__ import annotations

import logging
from pathlib import Path

from src.core.constants import INPUT_WORKBOOK_PATH, LOGS_DIR, POLICY_PATH
from src.core.environment import get_env


def validate_startup(logger: logging.Logger | None = None) -> None:
    logger = logger or logging.getLogger("processx")
    # Validate file availability early so the application can warn on missing
    # inputs without crashing before the operator sees a useful diagnosis.
    required_paths = {
        "policy_document": POLICY_PATH,
        "input_workbook": INPUT_WORKBOOK_PATH,
        "logs_dir": LOGS_DIR,
    }
    missing_paths = {
        name: str(path)
        for name, path in required_paths.items()
        if not Path(path).exists()
    }

    cache_dir = Path(get_env("MODEL_CACHE_DIR", "models") or "models")
    if not cache_dir.exists():
        # Create the cache directory eagerly so first-run model downloads and
        # cache reuse both point at the same deterministic filesystem location.
        cache_dir.mkdir(parents=True, exist_ok=True)
        created_cache_dir = True
    else:
        created_cache_dir = False

    required_envs = [
        "MODEL_CACHE_DIR",
        "LOG_LEVEL",
        "LLM_TIMEOUT_SECONDS",
        "LLM_RETRY_COUNT",
    ]
    optional_envs = [
        "GEMINI_API_KEY",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "HF_TOKEN",
        "OLLAMA_HOST",
        "LOCAL_GGUF_AUTO_DOWNLOAD",
    ]
    missing_required_envs = [key for key in required_envs if get_env(key) is None]
    missing_optional_envs = [key for key in optional_envs if get_env(key) is None]

    logger.info(
        "startup_validation_defaults",
        extra={
            "event": "startup_validation_defaults",
            "existing_env_var_count": len(required_envs) + len(optional_envs) - len(missing_required_envs) - len(missing_optional_envs),
            "required_env_var_count": len(required_envs),
            "optional_env_var_count": len(optional_envs),
            "missing_required_env_vars": missing_required_envs,
            "missing_optional_env_vars": missing_optional_envs,
            "missing_path_count": len(missing_paths),
            "missing_paths": missing_paths,
            "cache_dir": str(cache_dir),
            "cache_dir_created": created_cache_dir,
        },
    )
    if missing_required_envs or missing_paths:
        logger.warning(
            "startup_validation",
            extra={
                "event": "startup_validation",
                "missing_required_env_vars": missing_required_envs,
                "missing_optional_env_vars": missing_optional_envs,
                "existing_env_var_count": len(required_envs) + len(optional_envs) - len(missing_required_envs) - len(missing_optional_envs),
                "required_env_var_count": len(required_envs),
                "optional_env_var_count": len(optional_envs),
                "missing_path_count": len(missing_paths),
                "missing_paths": missing_paths,
                "cache_dir": str(cache_dir),
                "cache_dir_created": created_cache_dir,
            },
        )
