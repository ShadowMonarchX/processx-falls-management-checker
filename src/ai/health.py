from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path

import src.ai.loader as loader
from src.ai.device import get_device_info
from src.ai.model_registry import get_model_spec
from src.core.environment import get_env

# Verifies whether the GGUF model is already cached locally and determines
# if automatic download can be used as a fallback when the model is missing.


def check_local_model(model_key: str = "llama-3.2-1b") -> dict[str, object]:
    spec = get_model_spec(model_key)
    model_path = Path(loader.MODELS_DIR) / spec.key / spec.filename
    cached = model_path.exists()

    # File size is collected for diagnostics and helps detect incomplete
    # or corrupted model downloads.

    size_mb = round(model_path.stat().st_size / (1024 * 1024), 2) if cached else 0.0
    return {
        "model_available": cached
        or get_env("LOCAL_GGUF_AUTO_DOWNLOAD", "0") in {"1", "true", "True"},
        "cached": cached,
        "device": get_device_info().device,
        "path": str(model_path),
        "size_mb": size_mb,
    }


# Validates cloud provider readiness before runtime requests are attempted.


def check_cloud_providers() -> dict[str, str]:
    status: dict[str, str] = {}

    # Skip expensive provider initialization when required credentials
    # are not configured.

    status["gemini"] = "ready" if get_env("GEMINI_API_KEY") else "missing_key"
    status["claude"] = "ready" if get_env("ANTHROPIC_API_KEY") else "missing_key"
    status["openai"] = "ready" if get_env("OPENAI_API_KEY") else "missing_key"
    ollama_exe = shutil.which("ollama")

    # Verify Ollama is installed before attempting local inference calls.

    if not ollama_exe:
        status["ollama"] = "not_installed"
    else:
        try:

            # Confirm the Ollama service is reachable to avoid request failures
            # during provider fallback execution.

            subprocess.run(
                [ollama_exe, "list"],
                check=True,
                capture_output=True,
                text=True,
                timeout=5,
            )
            status["ollama"] = "reachable"
        except Exception:
            status["ollama"] = "unreachable"
    return status


# Builds the effective provider execution order used by the fallback system.


def check_provider_chain() -> dict[str, str]:
    local = check_local_model()
    return {
        "local_gguf": "healthy" if local["model_available"] else "missing_model",
        **check_cloud_providers(),
    }


# Returns a complete snapshot of AI infrastructure health for diagnostics,
# startup validation, and troubleshooting.


def check_ai_stack() -> dict[str, object]:
    return {
        "local_model": check_local_model(),
        "provider_chain": check_provider_chain(),
        "cloud_providers": check_cloud_providers(),
    }


# Generates structured provider health information used by logging,
# monitoring, and provider selection logic.


def provider_diagnostics() -> list[dict[str, object]]:
    local = check_local_model()
    cloud = check_cloud_providers()
    # Emit a uniform shape so CLI health output and startup logs can share the
    # same provider readiness snapshot without separate formatting logic.
    return [
        {
            "provider": "local_gguf",
            "healthy": bool(local["model_available"]),
            "model_found": bool(local["cached"]),
            "model_path": local["path"],
        },
        {
            "provider": "gemini",
            "healthy": cloud["gemini"] == "ready",
            "api_key_present": cloud["gemini"] == "ready",
        },
        {
            "provider": "claude",
            "healthy": cloud["claude"] == "ready",
            "api_key_present": cloud["claude"] == "ready",
        },
        {
            "provider": "openai",
            "healthy": cloud["openai"] == "ready",
            "api_key_present": cloud["openai"] == "ready",
        },
        {
            "provider": "ollama",
            "healthy": cloud["ollama"] == "reachable",
            "ollama_installed": shutil.which("ollama") is not None,
            "ollama_running": cloud["ollama"] == "reachable",
        },
    ]


# Emits structured diagnostics during startup so provider readiness can
# be inspected before processing begins.


def log_provider_diagnostics(logger: logging.Logger | None = None) -> None:
    logger = logger or logging.getLogger("processx")
    for diagnostic in provider_diagnostics():
        logger.info("provider_diagnostic", extra=diagnostic)
