from time import perf_counter
import requests
from .base import BaseModelAdapter, ModelResponse

class OllamaModel(BaseModelAdapter):
    provider = "ollama"

    def __init__(self, model_name: str, *, base_url: str = "http://localhost:11434") -> None:
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")

    def generate(self, prompt: str, *, system_prompt: str | None = None, max_tokens: int = 4096, temperature: float = 0.0, timeout: int = 120) -> ModelResponse:
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        start = perf_counter()
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={"model": self.model_name, "prompt": full_prompt, "stream": False, "options": {"temperature": temperature, "num_predict": max_tokens}},
            timeout=timeout,
        )
        response.raise_for_status()
        data = response.json()
        prompt_tokens = data.get("prompt_eval_count")
        completion_tokens = data.get("eval_count")
        return ModelResponse(
            text=data.get("response", ""),
            model=self.model_name,
            provider=self.provider,
            latency_seconds=perf_counter() - start,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=(prompt_tokens or 0) + (completion_tokens or 0),
            raw=data,
        )
