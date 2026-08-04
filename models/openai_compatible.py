from __future__ import annotations

import os
from time import perf_counter

import requests

from .base import BaseModelAdapter, ModelResponse


class OpenAICompatibleModel(BaseModelAdapter):
    """Adapter for OpenAI-compatible chat-completions APIs."""

    provider = "openai_compatible"

    def __init__(
        self,
        model_name: str,
        *,
        base_url: str,
        api_key: str | None = None,
        api_key_env: str = "OPENAI_API_KEY",
        provider_name: str = "openai_compatible",
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.getenv(api_key_env)
        self.provider = provider_name
        self.extra_headers = extra_headers or {}

        if not self.api_key:
            raise ValueError(
                f"API key is missing. Set environment variable {api_key_env}."
            )

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
            messages.append(
                {"role": "system", "content": system_prompt}
            )

        messages.append(
            {"role": "user", "content": prompt}
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            **self.extra_headers,
        }

        start = perf_counter()

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json={
                "model": self.model_name,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
            timeout=timeout,
        )

        response.raise_for_status()
        data = response.json()
        latency = perf_counter() - start

        usage = data.get("usage", {})
        text = data["choices"][0]["message"]["content"]

        return ModelResponse(
            text=text,
            model=self.model_name,
            provider=self.provider,
            latency_seconds=latency,
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
            total_tokens=usage.get("total_tokens"),
            raw=data,
        )
