from __future__ import annotations

from pathlib import Path

from src.ai.device import get_device_info
import src.ai.loader as loader
from src.ai.model_registry import get_model_spec
from src.core.environment import get_env


def check_local_model(model_key: str = "llama-3.2-1b") -> dict[str, object]:
    spec = get_model_spec(model_key)
    model_path = Path(loader.MODELS_DIR) / spec.key / spec.filename
    cached = model_path.exists()
    size_mb = round(model_path.stat().st_size / (1024 * 1024), 2) if cached else 0.0
    return {
        "model_available": cached or get_env("LOCAL_GGUF_AUTO_DOWNLOAD", "0") in {"1", "true", "True"},
        "cached": cached,
        "device": get_device_info().device,
        "path": str(model_path),
        "size_mb": size_mb,
    }


def check_cloud_providers() -> dict[str, str]:
    status: dict[str, str] = {}
    status["gemini"] = "ready" if get_env("GEMINI_API_KEY") else "missing_key"
    status["claude"] = "ready" if get_env("ANTHROPIC_API_KEY") else "missing_key"
    status["openai"] = "ready" if get_env("OPENAI_API_KEY") else "missing_key"
    status["ollama"] = "reachable" if get_env("OLLAMA_HOST") else "unreachable"
    return status


def check_provider_chain() -> dict[str, str]:
    local = check_local_model()
    return {
        "local_gguf": "healthy" if local["model_available"] else "missing_model",
        **check_cloud_providers(),
    }


def check_ai_stack() -> dict[str, object]:
    return {
        "local_model": check_local_model(),
        "provider_chain": check_provider_chain(),
        "cloud_providers": check_cloud_providers(),
    }
