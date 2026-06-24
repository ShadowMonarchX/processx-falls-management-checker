from __future__ import annotations

import json
import os
import subprocess
import time
from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from src.core.models import StructuredExtractionModel


@dataclass(frozen=True)
class LLMResponse:
    payload: StructuredExtractionModel
    provider: str
    model: str
    latency_ms: int
    token_usage: dict[str, int] | None = None


class LLMClient:
    def __init__(self) -> None:
        self.provider_order = ["gemini", "claude", "openai", "local"]

    def select_provider(self) -> str:
        if os.getenv("GEMINI_API_KEY"):
            return "gemini"
        if os.getenv("ANTHROPIC_API_KEY"):
            return "claude"
        if os.getenv("OPENAI_API_KEY"):
            return "openai"
        return "local"

    def extract(self, prompt: str, fallback_payload: dict[str, Any]) -> LLMResponse:
        provider = self.select_provider()
        start = time.perf_counter()
        raw: str
        model = "structured-fallback"
        token_usage: dict[str, int] | None = None
        if provider == "openai":
            raw, model, token_usage = self._call_openai(prompt)
        elif provider == "claude":
            raw, model, token_usage = self._call_claude(prompt)
        elif provider == "gemini":
            raw, model, token_usage = self._call_gemini(prompt)
        else:
            raw, model = self._call_local(prompt)
        latency_ms = int((time.perf_counter() - start) * 1000)
        payload = self._parse_or_fallback(raw, fallback_payload)
        return LLMResponse(
            payload=payload,
            provider=provider,
            model=model,
            latency_ms=latency_ms,
            token_usage=token_usage,
        )

    def _parse_or_fallback(self, raw: str, fallback_payload: dict[str, Any]) -> StructuredExtractionModel:
        try:
            data = json.loads(raw)
            return StructuredExtractionModel.model_validate(data)
        except (json.JSONDecodeError, ValidationError, TypeError):
            return StructuredExtractionModel.model_validate(fallback_payload)

    def _call_openai(self, prompt: str) -> tuple[str, str, dict[str, int] | None]:
        try:
            from openai import OpenAI

            client = OpenAI()
            response = client.responses.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
                input=prompt,
            )
            usage = getattr(response, "usage", None)
            token_usage = None
            if usage is not None:
                token_usage = {
                    "input": getattr(usage, "input_tokens", 0) or 0,
                    "output": getattr(usage, "output_tokens", 0) or 0,
                }
            return response.output_text, getattr(response, "model", "gpt-4.1-mini"), token_usage
        except Exception:
            raw, model = self._call_local(prompt)
            return raw, model, None

    def _call_claude(self, prompt: str) -> tuple[str, str, dict[str, int] | None]:
        try:
            from anthropic import Anthropic

            client = Anthropic()
            response = client.messages.create(
                model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest"),
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            text = "".join(block.text for block in response.content if hasattr(block, "text"))
            usage = getattr(response, "usage", None)
            token_usage = None
            if usage is not None:
                token_usage = {
                    "input": getattr(usage, "input_tokens", 0) or 0,
                    "output": getattr(usage, "output_tokens", 0) or 0,
                }
            return text, getattr(response, "model", "claude-3-5-sonnet-latest"), token_usage
        except Exception:
            raw, model = self._call_local(prompt)
            return raw, model, None

    def _call_gemini(self, prompt: str) -> tuple[str, str, dict[str, int] | None]:
        try:
            import google.generativeai as genai

            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-2.5-pro"))
            response = model.generate_content(prompt)
            usage = getattr(response, "usage_metadata", None)
            token_usage = None
            if usage is not None:
                token_usage = {
                    "input": getattr(usage, "prompt_token_count", 0) or 0,
                    "output": getattr(usage, "candidates_token_count", 0) or 0,
                }
            return response.text or "", getattr(model, "model_name", "gemini-2.5-pro"), token_usage
        except Exception:
            raw, model = self._call_local(prompt)
            return raw, model, None

    def _call_local(self, prompt: str) -> tuple[str, str]:
        ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5:3b-instruct")
        try:
            completed = subprocess.run(
                ["ollama", "run", ollama_model, prompt],
                check=False,
                capture_output=True,
                text=True,
            )
            if completed.stdout.strip():
                return completed.stdout, ollama_model
        except Exception:
            pass
        return "{}", f"local:{ollama_model}"
