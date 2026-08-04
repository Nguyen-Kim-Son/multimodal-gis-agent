from __future__ import annotations

import os
import time
from time import perf_counter
from typing import Any

import requests

from .base import BaseModelAdapter, ModelResponse


class OpenRouterModel(BaseModelAdapter):
    provider = "openrouter"

    def __init__(
        self,
        model_name: str,
        *,
        api_key: str | None = None,
        base_url: str = "https://openrouter.ai/api/v1",
        max_attempts: int = 4,
        provider_preferences: dict[str, Any] | None = None,
        reasoning: dict[str, Any] | None = None,
    ) -> None:
        self.model_name = model_name
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = base_url.rstrip("/")
        self.max_attempts = max(1, max_attempts)
        self.provider_preferences = provider_preferences or {}
        self.reasoning = reasoning

        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is not configured.")

    @staticmethod
    def _extract_text(message: dict[str, Any]) -> str:
        content = message.get("content")

        if isinstance(content, str):
            return content.strip()

        if isinstance(content, list):
            parts: list[str] = []
            for block in content:
                if isinstance(block, str):
                    parts.append(block)
                elif isinstance(block, dict):
                    text = block.get("text") or block.get("content")
                    if isinstance(text, str):
                        parts.append(text)
            return "\n".join(parts).strip()

        return ""

    def generate(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.0,
        timeout: int = 120,
    ) -> ModelResponse:
        messages: list[dict[str, str]] = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        payload: dict[str, Any] = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if self.provider_preferences:
            payload["provider"] = self.provider_preferences

        if self.reasoning is not None:
            payload["reasoning"] = self.reasoning

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/MMGIS-Bench/MMGIS-Bench",
            "X-Title": "MMGIS-Bench",
        }

        start = perf_counter()
        response: requests.Response | None = None

        for attempt in range(1, self.max_attempts + 1):
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=timeout,
            )

            if response.status_code not in {408, 429, 502, 503, 504}:
                break

            if attempt >= self.max_attempts:
                break

            retry_after = response.headers.get("Retry-After")
            try:
                delay = float(retry_after)
            except (TypeError, ValueError):
                delay = min(15.0 * (2 ** (attempt - 1)), 120.0)

            time.sleep(delay)

        assert response is not None

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise RuntimeError(
                "OpenRouter request failed. "
                f"status={response.status_code}; "
                f"model={self.model_name}; "
                f"retry_after={response.headers.get('Retry-After')}; "
                f"response={response.text[:4000]}"
            ) from exc

        data = response.json()
        choices = data.get("choices")

        if not isinstance(choices, list) or not choices:
            raise RuntimeError(
                f"OpenRouter returned no choices for {self.model_name}: {data}"
            )

        choice = choices[0]
        message = choice.get("message") or {}
        text = self._extract_text(message)

        if not text:
            raise RuntimeError(
                "OpenRouter returned an empty final answer. "
                f"model={self.model_name}; "
                f"finish_reason={choice.get('finish_reason')}"
            )

        usage = data.get("usage") or {}

        return ModelResponse(
            text=text,
            model=str(data.get("model") or self.model_name),
            provider=self.provider,
            latency_seconds=perf_counter() - start,
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
            total_tokens=usage.get("total_tokens"),
            cost_usd=usage.get("cost"),
            raw=data,
        )
