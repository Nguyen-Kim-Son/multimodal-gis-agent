from __future__ import annotations

from typing import Any

from .base import BaseModelAdapter
from .mock import MockModel
from .ollama import OllamaModel
from .openai_compatible import OpenAICompatibleModel
from .openrouter import OpenRouterModel


def create_model(config: dict[str, Any]) -> BaseModelAdapter:
    provider = str(config["provider"]).casefold()
    model_name = str(config.get("model", ""))

    if provider == "mock":
        return MockModel()

    if provider == "openrouter":
        return OpenRouterModel(
            model_name=model_name,
            base_url=config.get(
                "base_url",
                "https://openrouter.ai/api/v1",
            ),
            max_attempts=int(config.get("max_attempts", 4)),
            provider_preferences=config.get("provider_preferences"),
            reasoning=config.get("reasoning"),
        )

    if provider == "ollama":
        return OllamaModel(
            model_name=model_name,
            base_url=config.get(
                "base_url",
                "http://localhost:11434",
            ),
        )

    if provider in {
        "openai",
        "deepseek",
        "qwen",
        "generic_openai",
    }:
        return OpenAICompatibleModel(
            model_name=model_name,
            base_url=str(config["base_url"]),
            api_key_env=str(
                config.get("api_key_env", "OPENAI_API_KEY")
            ),
            provider_name=provider,
            extra_headers=config.get("extra_headers"),
        )

    raise ValueError(f"Unsupported model provider: {provider}")
