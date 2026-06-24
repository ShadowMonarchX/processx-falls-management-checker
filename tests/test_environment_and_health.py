from __future__ import annotations

import importlib
from pathlib import Path

import src.ai.loader as loader
from src.ai.device import get_device_info
from src.ai.health import check_ai_stack, check_local_model
from src.core.environment import load_env_file
from openpyxl import load_workbook


def test_load_env_file_parses_values(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("A=1\nB='two'\n# comment\nC=three\n", encoding="utf-8")
    assert load_env_file(env_file) == {"A": "1", "B": "two", "C": "three"}


def test_model_cache_dir_can_be_configured(tmp_path, monkeypatch):
    monkeypatch.setenv("MODEL_CACHE_DIR", str(tmp_path / "cache"))
    reloaded = importlib.reload(loader)
    assert reloaded.MODELS_DIR == Path(tmp_path / "cache")


def test_load_model_uses_cache_and_does_not_redownload(tmp_path, monkeypatch):
    monkeypatch.setenv("MODEL_CACHE_DIR", str(tmp_path))
    monkeypatch.setenv("LOCAL_GGUF_AUTO_DOWNLOAD", "0")
    reloaded = importlib.reload(loader)
    spec = reloaded.get_model_spec("llama-3.2-1b")
    model_path = reloaded.MODELS_DIR / spec.key / spec.filename
    model_path.parent.mkdir(parents=True, exist_ok=True)
    model_path.write_text("cached-model", encoding="utf-8")

    called = {"download": False}

    def fake_download(*args, **kwargs):
        called["download"] = True
        return model_path

    monkeypatch.setattr(reloaded, "_download_model", fake_download)
    try:
        reloaded.load_model()
    except Exception:
        pass
    assert called["download"] is False


def test_hf_token_can_be_supplied_securely(tmp_path, monkeypatch):
    from src.ai.model_registry import get_model_spec

    monkeypatch.setenv("HF_TOKEN", "secret-token")
    spec = get_model_spec("llama-3.2-1b")
    captured = {}

    def fake_hf_hub_download(**kwargs):
        captured.update(kwargs)
        return str(tmp_path / spec.filename)

    monkeypatch.setattr("huggingface_hub.hf_hub_download", fake_hf_hub_download)
    path = loader._download_model(spec, tmp_path)
    assert path.name == spec.filename
    assert captured["token"] == "secret-token"


def test_device_info_exposes_diagnostics():
    info = get_device_info()
    assert info.device in {"cuda", "mps", "cpu"}
    assert info.cpu_cores is None or info.cpu_cores > 0


def test_local_model_health_structure(tmp_path, monkeypatch):
    monkeypatch.setenv("MODEL_CACHE_DIR", str(tmp_path))
    monkeypatch.setenv("LOCAL_GGUF_AUTO_DOWNLOAD", "0")
    reloaded = importlib.reload(loader)
    spec = reloaded.get_model_spec("llama-3.2-1b")
    model_path = reloaded.MODELS_DIR / spec.key / spec.filename
    model_path.parent.mkdir(parents=True, exist_ok=True)
    model_path.write_bytes(b"x" * 1024)

    status = check_local_model()
    assert set(status) == {"model_available", "cached", "device", "path", "size_mb"}
    assert status["cached"] is True
    assert status["path"] == str(model_path)


def test_ai_stack_reports_all_providers(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    stack = check_ai_stack()
    assert set(stack) == {"local_gguf", "gemini", "claude", "openai", "ollama"}


def test_submission_workbook_is_written_in_place():
    workbook = load_workbook(Path("data/raw/Your_Output_File.xlsx"))
    assert workbook["Alice Nguyen - Your Output"]["A4"].value is not None
    assert workbook["Thomas Brennan - Your Output"]["A4"].value is not None
