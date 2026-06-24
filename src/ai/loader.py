from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from src.ai.device import detect_device
from src.ai.model_registry import ModelSpec, get_model_spec
from src.core.constants import BASE_DIR
from src.core.environment import get_env, normalize_optional_env


MODELS_DIR = Path(get_env("MODEL_CACHE_DIR", str(BASE_DIR / "models")) or (BASE_DIR / "models"))


def _download_model(spec: ModelSpec, model_dir: Path) -> Path:
    from huggingface_hub import hf_hub_download

    model_dir.mkdir(parents=True, exist_ok=True)
    token = normalize_optional_env(get_env("HF_TOKEN"))
    local_dir = model_dir
    logger = __import__("logging").getLogger("processx")
    # Log metadata only after token normalization so an empty credential never
    # propagates into the Hugging Face client as a malformed Bearer header.
    logger.info(
        "model_download_started",
        extra={
            "event": "model_download_started",
            "repo_id": spec.repo_id,
            "model_filename": spec.filename,
            "model_dir": str(model_dir),
            "token_present": bool(token),
        },
    )
    return Path(
        _download_hub_model(spec, local_dir, token)
    )


def _download_hub_model(spec: ModelSpec, local_dir: Path, token: str | None) -> str:
    from huggingface_hub import hf_hub_download

    try:
        # Only include the token parameter when a real credential exists so
        # anonymous downloads remain valid and empty strings are never sent.
        download_kwargs: dict[str, object] = {
            "repo_id": spec.repo_id,
            "filename": spec.filename,
            "local_dir": local_dir,
        }
        if token is not None:
            download_kwargs["token"] = token
        path = hf_hub_download(
            **download_kwargs,
        )
        __import__("logging").getLogger("processx").info(
            "model_download_completed",
            extra={
                "event": "model_download_completed",
                "repo_id": spec.repo_id,
                "model_filename": spec.filename,
                "path": str(path),
            },
        )
        return path
    except Exception as exc:
        __import__("logging").getLogger("processx").error(
            "model_download_failed",
            extra={
                "event": "model_download_failed",
                "repo_id": spec.repo_id,
                "model_filename": spec.filename,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            },
        )
        raise


@lru_cache(maxsize=1)
def load_model(model_key: str = "llama-3.2-1b"):
    spec = get_model_spec(model_key)
    model_dir = MODELS_DIR / spec.key
    model_path = model_dir / spec.filename
    if not model_path.exists():
        auto_download = get_env("LOCAL_GGUF_AUTO_DOWNLOAD", "true") in {"1", "true", "True"}
        if auto_download:
            # Download on-demand so the first successful run can bootstrap an
            # empty cache without requiring a manual prefetch step.
            model_path = _download_model(spec, model_dir)
        else:
            raise FileNotFoundError(str(model_path))

    device_info = detect_device()
    # llama.cpp layer placement is device-sensitive: GPU-backed local runtimes
    # should offload all layers, while CPU remains conservative.
    n_gpu_layers = -1 if device_info.device in {"cuda", "mps"} else 0

    from llama_cpp import Llama

    return Llama(
        model_path=str(model_path),
        n_ctx=spec.context_length,
        n_gpu_layers=n_gpu_layers,
        verbose=False,
    )
