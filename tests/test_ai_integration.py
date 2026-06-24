from pathlib import Path

from openpyxl import load_workbook

from src.ai.llm_client import LLMClient
from src.ai.prompt_builder import PromptBuilder
from src.core.models import PolicyRuleModel, StructuredExtractionModel


def test_provider_selection_prefers_env(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    client = LLMClient()
    assert client.select_provider() == "local"
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    assert client.select_provider() == "openai"


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


def test_output_workbook_populated():
    workbook = load_workbook(Path("data/raw/Your_Output_File.xlsx"))
    assert workbook["Alice Nguyen - Your Output"]["A4"].value is not None
    assert workbook["Thomas Brennan - Your Output"]["A4"].value is not None
