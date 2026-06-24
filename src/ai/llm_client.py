from __future__ import annotations

import json
import os
import subprocess
import time
from dataclasses import dataclass
import logging
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
        self.timeout_seconds = float(os.getenv("LLM_TIMEOUT_SECONDS", "30"))
        self.retry_count = int(os.getenv("LLM_RETRY_COUNT", "3"))
        self.logger = logging.getLogger("processx")

    def select_provider(self) -> str:
        if os.getenv("GEMINI_API_KEY"):
            return "gemini"
        if os.getenv("ANTHROPIC_API_KEY"):
            return "claude"
        if os.getenv("OPENAI_API_KEY"):
            return "openai"
        return "local"

    def extract(self, prompt: str, fallback_payload: dict[str, Any]) -> LLMResponse:
        start = time.perf_counter()
        raw = "{}"
        model = "structured-fallback"
        token_usage: dict[str, int] | None = None
        selected_provider = "local"
        for provider in self.provider_order:
            self.logger.info(
                "provider_attempted",
                extra={"provider": provider, "status": "attempted"},
            )
            if provider == "gemini" and not os.getenv("GEMINI_API_KEY"):
                continue
            if provider == "claude" and not os.getenv("ANTHROPIC_API_KEY"):
                continue
            if provider == "openai" and not os.getenv("OPENAI_API_KEY"):
                continue
            try:
                raw, model, token_usage = self._call_with_retries(provider, prompt)
                selected_provider = provider
                self.logger.info(
                    "provider_succeeded",
                    extra={
                        "provider": provider,
                        "status": "success",
                        "model": model,
                        "latency_ms": int((time.perf_counter() - start) * 1000),
                    },
                )
                break
            except TimeoutError as exc:
                next_provider = self._next_provider(provider)
                self.logger.warning(
                    "provider_timeout",
                    extra={
                        "provider": provider,
                        "status": "failed",
                        "reason": "timeout",
                        "next_provider": next_provider,
                    },
                )
                continue
            except RuntimeError as exc:
                next_provider = self._next_provider(provider)
                self.logger.warning(
                    "provider_failed",
                    extra={
                        "provider": provider,
                        "status": "failed",
                        "reason": str(exc),
                        "next_provider": next_provider,
                    },
                )
                continue
        latency_ms = int((time.perf_counter() - start) * 1000)
        payload = self._parse_or_fallback(raw, fallback_payload)
        return LLMResponse(
            payload=payload,
            provider=selected_provider,
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

    def _next_provider(self, provider: str) -> str:
        index = self.provider_order.index(provider)
        return self.provider_order[min(index + 1, len(self.provider_order) - 1)]

    def _call_with_retries(
        self, provider: str, prompt: str
    ) -> tuple[str, str, dict[str, int] | None]:
        retryable_errors: tuple[type[Exception], ...] = (
            TimeoutError,
            ConnectionError,
            RuntimeError,
            subprocess.SubprocessError,
        )
        for attempt in range(1, self.retry_count + 1):
            try:
                if provider == "openai":
                    return self._call_openai(prompt)
                if provider == "claude":
                    return self._call_claude(prompt)
                if provider == "gemini":
                    return self._call_gemini(prompt)
                return (*self._call_local(prompt), None)
            except ValidationError as exc:
                raise RuntimeError("schema validation error") from exc
            except Exception as exc:
                if isinstance(exc, retryable_errors) and attempt < self.retry_count:
                    sleep_seconds = 2 ** (attempt - 1)
                    self.logger.warning(
                        "provider_retry",
                        extra={
                            "provider": provider,
                            "attempt": attempt,
                            "retry_count": self.retry_count,
                            "sleep_seconds": sleep_seconds,
                            "reason": str(exc),
                        },
                    )
                    time.sleep(sleep_seconds)
                    continue
                if isinstance(exc, TimeoutError):
                    raise
                if isinstance(exc, (ValueError, json.JSONDecodeError)):
                    raise RuntimeError("malformed request or output") from exc
                raise RuntimeError(str(exc)) from exc
        raise RuntimeError("retry exhaustion")

    def _call_openai(self, prompt: str) -> tuple[str, str, dict[str, int] | None]:
        try:
            from openai import OpenAI

            client = OpenAI(timeout=self.timeout_seconds)
            response = client.responses.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
                input=prompt,
                timeout=self.timeout_seconds,
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
            raise

    def _call_claude(self, prompt: str) -> tuple[str, str, dict[str, int] | None]:
        try:
            from anthropic import Anthropic

            client = Anthropic(timeout=self.timeout_seconds)
            response = client.messages.create(
                model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest"),
                max_tokens=1024,
                timeout=self.timeout_seconds,
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
            raise

    def _call_gemini(self, prompt: str) -> tuple[str, str, dict[str, int] | None]:
        try:
            import google.generativeai as genai

            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-2.5-pro"))
            response = model.generate_content(
                prompt,
                generation_config={"temperature": 0},
                request_options={"timeout": self.timeout_seconds},
            )
            usage = getattr(response, "usage_metadata", None)
            token_usage = None
            if usage is not None:
                token_usage = {
                    "input": getattr(usage, "prompt_token_count", 0) or 0,
                    "output": getattr(usage, "candidates_token_count", 0) or 0,
                }
            return response.text or "", getattr(model, "model_name", "gemini-2.5-pro"), token_usage
        except Exception:
            raise

    def _call_local(self, prompt: str) -> tuple[str, str]:
        ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5:3b-instruct")
        try:
            completed = subprocess.run(
                ["ollama", "run", ollama_model, prompt],
                check=True,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
            )
            if completed.stdout.strip():
                return completed.stdout, ollama_model
        except subprocess.TimeoutExpired as exc:
            raise TimeoutError("ollama timeout") from exc
        except Exception as exc:
            raise RuntimeError(str(exc)) from exc
        return "{}", f"local:{ollama_model}"
