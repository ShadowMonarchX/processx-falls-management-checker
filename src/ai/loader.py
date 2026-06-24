from __future__ import annotations

from pathlib import Path

from src.ai.device import detect_device
from src.ai.model_registry import ModelSpec, get_model_spec
from src.core.constants import BASE_DIR


MODELS_DIR = BASE_DIR / "models"


def _download_model(spec: ModelSpec, model_dir: Path) -> Path:
    from huggingface_hub import hf_hub_download

    model_dir.mkdir(parents=True, exist_ok=True)
    return Path(
        hf_hub_download(
            repo_id=spec.repo_id,
            filename=spec.filename,
            local_dir=model_dir,
            local_dir_use_symlinks=False,
            resume_download=True,
        )
    )


def load_model(model_key: str = "llama-3.2-1b"):
    spec = get_model_spec(model_key)
    model_dir = MODELS_DIR / spec.key
    model_path = model_dir / spec.filename
    if not model_path.exists():
        model_path = _download_model(spec, model_dir)

    device_info = detect_device()
    n_gpu_layers = -1 if device_info.device in {"cuda", "mps"} else 0

    from llama_cpp import Llama

    return Llama(
        model_path=str(model_path),
        n_ctx=spec.context_length,
        n_gpu_layers=n_gpu_layers,
        verbose=False,
    )
