from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelSpec:
    key: str
    repo_id: str
    filename: str
    context_length: int
    description: str


MODEL_REGISTRY: dict[str, ModelSpec] = {
    "llama-3.2-1b": ModelSpec(
        key="llama-3.2-1b",
        repo_id="bartowski/Llama-3.2-1B-Instruct-GGUF",
        filename="Llama-3.2-1B-Instruct-Q4_K_M.gguf",
        context_length=131072,
        description="Fast local inference with large context window.",
    )
}


def get_model_spec(key: str = "llama-3.2-1b") -> ModelSpec:
    try:
        return MODEL_REGISTRY[key]
    except KeyError as exc:
        raise KeyError(f"Unknown model key: {key}") from exc
