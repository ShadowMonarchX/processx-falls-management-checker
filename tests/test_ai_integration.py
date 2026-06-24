from pathlib import Path

from openpyxl import load_workbook
import pytest

from src.ai.llm_client import LLMClient
from src.ai.prompt_builder import PromptBuilder
from src.core.models import PolicyRuleModel, StructuredExtractionModel


@pytest.fixture(autouse=True)
def disable_local_model_auto_download(monkeypatch):
    monkeypatch.setenv("LOCAL_GGUF_AUTO_DOWNLOAD", "0")


def test_provider_selection_prefers_env(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    client = LLMClient()
    assert client.select_provider() == "local_gguf"
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    assert client.select_provider() == "local_gguf"


def test_sequential_fallback_gemini_to_claude(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "g")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "a")
    monkeypatch.setenv("OPENAI_API_KEY", "o")
    client = LLMClient()
    monkeypatch.setattr(client, "_call_gemini", lambda prompt: (_ for _ in ()).throw(TimeoutError("gemini timeout")))
    monkeypatch.setattr(client, "_call_claude", lambda prompt: ('{"resident_name":"Alice Nguyen","day":"Day 1","observations":{},"evidence":[],"missing_items":[],"confidence":0.9}', "claude-model", None))
    result = client.extract("prompt", {"resident_name": "fallback", "day": "Day 1", "observations": {}, "evidence": [], "missing_items": [], "confidence": 0.1})
    assert result.provider == "claude"


def test_sequential_fallback_claude_to_openai(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "a")
    monkeypatch.setenv("OPENAI_API_KEY", "o")
    client = LLMClient()
    monkeypatch.setattr(client, "_call_claude", lambda prompt: (_ for _ in ()).throw(RuntimeError("claude failed")))
    monkeypatch.setattr(client, "_call_openai", lambda prompt: ('{"resident_name":"Alice Nguyen","day":"Day 1","observations":{},"evidence":[],"missing_items":[],"confidence":0.8}', "openai-model", None))
    result = client.extract("prompt", {"resident_name": "fallback", "day": "Day 1", "observations": {}, "evidence": [], "missing_items": [], "confidence": 0.1})
    assert result.provider == "openai"


def test_sequential_fallback_openai_to_local(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "o")
    client = LLMClient()
    monkeypatch.setattr(client, "_call_local_gguf", lambda prompt: (_ for _ in ()).throw(RuntimeError("local gguf failed")))
    monkeypatch.setattr(client, "_call_openai", lambda prompt: (_ for _ in ()).throw(RuntimeError("openai failed")))
    monkeypatch.setattr(client, "_call_local", lambda prompt: ('{"resident_name":"Alice Nguyen","day":"Day 1","observations":{},"evidence":[],"missing_items":[],"confidence":0.7}', "local-model"))
    result = client.extract("prompt", {"resident_name": "fallback", "day": "Day 1", "observations": {}, "evidence": [], "missing_items": [], "confidence": 0.1})
    assert result.provider == "ollama"


def test_local_gguf_has_highest_priority(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    client = LLMClient()
    monkeypatch.setattr(client, "_call_local_gguf", lambda prompt: ('{"resident_name":"Alice Nguyen","day":"Day 1","observations":{},"evidence":[],"missing_items":[],"confidence":0.95}', "local-gguf", None))
    result = client.extract("prompt", {"resident_name": "fallback", "day": "Day 1", "observations": {}, "evidence": [], "missing_items": [], "confidence": 0.1})
    assert result.provider == "local_gguf"


def test_all_providers_fail_returns_structured_fallback(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "g")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "a")
    monkeypatch.setenv("OPENAI_API_KEY", "o")
    client = LLMClient()
    monkeypatch.setattr(client, "_call_gemini", lambda prompt: (_ for _ in ()).throw(TimeoutError("gemini failed")))
    monkeypatch.setattr(client, "_call_claude", lambda prompt: (_ for _ in ()).throw(RuntimeError("claude failed")))
    monkeypatch.setattr(client, "_call_openai", lambda prompt: (_ for _ in ()).throw(RuntimeError("openai failed")))
    monkeypatch.setattr(client, "_call_local", lambda prompt: (_ for _ in ()).throw(RuntimeError("local failed")))
    fallback = {"resident_name": "Alice Nguyen", "day": "Day 1", "observations": {}, "evidence": [], "missing_items": [], "confidence": 0.2}
    result = client.extract("prompt", fallback)
    assert result.payload.resident_name == "Alice Nguyen"
    assert result.payload.confidence == 0.2


def test_prompt_builder_returns_json_instruction():
    prompt = PromptBuilder().build_extraction_prompt(
        resident_name="Alice Nguyen",
        day="Day 1",
        note_text="Resident found on floor near bed.",
        rules=[
            PolicyRuleModel(
                rule_id="D1_FALL_DETAILS",
                day=1,
                requirement="Document fall details.",
                explanation_template="x",
            )
        ],
    )
    assert "JSON only" in prompt
    assert "Do not invent facts" in prompt


def test_structured_extraction_model_validates():
    model = StructuredExtractionModel.model_validate(
        {
            "resident_name": "Alice Nguyen",
            "day": "Day 1",
            "observations": {},
            "evidence": [],
            "missing_items": [],
            "confidence": 0.5,
        }
    )
    assert model.confidence == 0.5


def test_malformed_ai_output_falls_back(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "o")
    client = LLMClient()
    monkeypatch.setattr(client, "_call_openai", lambda prompt: ("not-json", "openai-model", None))
    fallback = {"resident_name": "Alice Nguyen", "day": "Day 1", "observations": {}, "evidence": [], "missing_items": [], "confidence": 0.2}
    result = client.extract("prompt", fallback)
    assert result.payload.resident_name == "Alice Nguyen"
    assert result.payload.confidence == 0.2


def test_output_workbook_populated():
    workbook = load_workbook(Path("data/raw/Your_Output_File.xlsx"))
    assert workbook["Alice Nguyen - Your Output"]["A4"].value is not None
    assert workbook["Thomas Brennan - Your Output"]["A4"].value is not None


def test_logging_events_emitted(caplog, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "o")
    client = LLMClient()
    monkeypatch.setattr(client, "_call_openai", lambda prompt: ('{"resident_name":"Alice Nguyen","day":"Day 1","observations":{},"evidence":[],"missing_items":[],"confidence":0.8}', "openai-model", None))
    with caplog.at_level("INFO", logger="processx"):
        client.extract("prompt", {"resident_name": "fallback", "day": "Day 1", "observations": {}, "evidence": [], "missing_items": [], "confidence": 0.1})
    messages = [record.message for record in caplog.records]
    assert "provider_attempt" in messages
    assert "provider_success" in messages
