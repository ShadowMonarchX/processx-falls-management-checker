from __future__ import annotations

import json
import os
import subprocess
import time
from dataclasses import dataclass
import logging
from typing import Any

from pydantic import ValidationError

from src.ai.device import get_device_info
from src.ai.loader import MODELS_DIR, load_model
from src.ai.model_registry import get_model_spec
from src.core.models import StructuredExtractionModel


@dataclass(frozen=True)
class LLMResponse:
    payload: StructuredExtractionModel
    provider: str
    model: str
    latency_ms: int
    token_usage: dict[str, int] | None = None


class ProviderHealthCache:
    def __init__(self, cooldown_seconds: int = 600) -> None:
        self.cooldown_seconds = cooldown_seconds
        self._failure_state: dict[str, float] = {}

    def is_healthy(self, provider: str) -> bool:
        failed_at = self._failure_state.get(provider)
        if failed_at is None:
            return True
        return (time.time() - failed_at) >= self.cooldown_seconds

    def mark_failed(self, provider: str) -> None:
        self._failure_state[provider] = time.time()

    def mark_healthy(self, provider: str) -> None:
        self._failure_state.pop(provider, None)


class LLMClient:
    def __init__(self) -> None:
        self.provider_order = ["local_gguf", "gemini", "claude", "openai", "ollama"]
        self.timeout_seconds = float(os.getenv("LLM_TIMEOUT_SECONDS", "120"))
        self.retry_count = int(os.getenv("LLM_RETRY_COUNT", "3"))
        self.logger = logging.getLogger("processx")
        self.provider_health = ProviderHealthCache(
            cooldown_seconds=int(os.getenv("PROVIDER_HEALTH_COOLDOWN_SECONDS", "600"))
        )

    def select_provider(self) -> str:
        if os.getenv("LOCAL_GGUF_ENABLED", "1") not in {"0", "false", "False"}:
            return "local_gguf"
        if os.getenv("GEMINI_API_KEY"):
            return "gemini"
        if os.getenv("ANTHROPIC_API_KEY"):
            return "claude"
        if os.getenv("OPENAI_API_KEY"):
            return "openai"
        return "ollama"

    def extract(self, prompt: str, fallback_payload: dict[str, Any]) -> LLMResponse:
        start = time.perf_counter()
        raw = "{}"
        model = "structured-fallback"
        token_usage: dict[str, int] | None = None
        selected_provider = "fallback"
        for provider in self.provider_order:
            if not self.provider_health.is_healthy(provider):
                self.logger.info(
                    "provider_skipped_unhealthy",
                    extra={"event": "provider_skipped_unhealthy", "provider": provider},
                )
                continue
            self.logger.info(
                "provider_attempt",
                extra={"event": "provider_attempt", "provider": provider},
            )
            if provider == "local_gguf" and os.getenv("LOCAL_GGUF_ENABLED", "1") in {"0", "false", "False"}:
                continue
            if provider == "gemini" and not os.getenv("GEMINI_API_KEY"):
                continue
            if provider == "claude" and not os.getenv("ANTHROPIC_API_KEY"):
                continue
            if provider == "openai" and not os.getenv("OPENAI_API_KEY"):
                continue
            try:
                raw, model, token_usage = self._call_with_retries(provider, prompt)
                selected_provider = provider
                self.provider_health.mark_healthy(provider)
                self.logger.info(
                    "provider_success",
                    extra={
                        "event": "provider_success",
                        "provider": provider,
                        "model": model,
                        "latency_ms": int((time.perf_counter() - start) * 1000),
                    },
                )
                break
            except TimeoutError as exc:
                next_provider = self._next_provider(provider)
                self.logger.warning(
                    "provider_failure",
                    extra={
                        "event": "provider_failure",
                        "provider": provider,
                        "error": "timeout",
                        "next_provider": next_provider,
                    },
                )
                self.provider_health.mark_failed(provider)
                continue
            except RuntimeError as exc:
                next_provider = self._next_provider(provider)
                self.logger.warning(
                    "provider_failure",
                    extra={
                        "event": "provider_failure",
                        "provider": provider,
                        "error": str(exc),
                        "next_provider": next_provider,
                    },
                )
                self.provider_health.mark_failed(provider)
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
        for attempt in range(1, self.retry_count + 1):
            try:
                if provider == "local_gguf":
                    return self._call_local_gguf(prompt)
                if provider == "openai":
                    return self._call_openai(prompt)
                if provider == "claude":
                    return self._call_claude(prompt)
                if provider == "gemini":
                    return self._call_gemini(prompt)
                result = self._call_local(prompt)
                if len(result) == 2:
                    return result[0], result[1], None
                return result
            except ValidationError as exc:
                raise RuntimeError("schema validation error") from exc
            except Exception as exc:
                if self._is_non_retryable(exc):
                    raise RuntimeError(str(exc)) from exc
                if attempt < self.retry_count and self._is_retryable(exc):
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
                raise RuntimeError(str(exc)) from exc
        raise RuntimeError("retry exhaustion")

    def _is_retryable(self, exc: Exception) -> bool:
        retryable = (
            TimeoutError,
            ConnectionError,
            subprocess.SubprocessError,
        )
        message = str(exc).lower()
        return isinstance(exc, retryable) or "rate limit" in message or "429" in message

    def _is_non_retryable(self, exc: Exception) -> bool:
        message = str(exc).lower()
        return isinstance(exc, (ValueError, json.JSONDecodeError, ValidationError)) or "invalid api key" in message or "authentication" in message

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

    def _call_local_gguf(self, prompt: str) -> tuple[str, str, dict[str, int] | None]:
        spec = get_model_spec("llama-3.2-1b")
        model_path = MODELS_DIR / spec.key / spec.filename
        auto_download = os.getenv("LOCAL_GGUF_AUTO_DOWNLOAD", "true") in {"1", "true", "True"}
        self.logger.info(
            "local_model_status",
            extra={
                "event": "local_model_status",
                "cached": model_path.exists(),
                "model_exists": model_path.exists(),
                "model_path": str(model_path),
                "device": get_device_info().device,
            },
        )
        if not model_path.exists() and not auto_download:
            raise RuntimeError(f"local gguf model not cached: {model_path}")
        try:
            llm = load_model()
        except Exception as exc:
            raise RuntimeError(f"local gguf load failed: {exc}") from exc
        response = llm(
            prompt,
            max_tokens=1024,
            temperature=0.0,
            stop=["```"],
        )
        text = ""
        if isinstance(response, dict):
            choices = response.get("choices") or []
            if choices:
                text = choices[0].get("text") or choices[0].get("message", {}).get("content", "")
        if not text and hasattr(response, "choices"):
            choice = response.choices[0]
            text = getattr(choice, "text", "") or getattr(getattr(choice, "message", None), "content", "")
        if not text:
            raise RuntimeError("local gguf returned empty output")
        return text, "llama-3.2-1b", None

    def _call_local(self, prompt: str) -> tuple[str, str, dict[str, int] | None]:
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
                return completed.stdout, ollama_model, None
        except subprocess.TimeoutExpired as exc:
            raise TimeoutError("ollama timeout") from exc
        except Exception as exc:
            raise RuntimeError(str(exc)) from exc
        return "{}", f"local:{ollama_model}", None
