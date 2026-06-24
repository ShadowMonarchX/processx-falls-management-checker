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


def check_ai_stack() -> dict[str, dict[str, object]]:
    local = check_local_model()
    return {
        "local_gguf": local,
        "gemini": {"available": bool(get_env("GEMINI_API_KEY")), "model": get_env("GEMINI_MODEL", "gemini-2.5-pro")},
        "claude": {"available": bool(get_env("ANTHROPIC_API_KEY")), "model": get_env("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")},
        "openai": {"available": bool(get_env("OPENAI_API_KEY")), "model": get_env("OPENAI_MODEL", "gpt-4.1-mini")},
        "ollama": {"available": True, "host": get_env("OLLAMA_HOST", "http://127.0.0.1:11434")},
    }
