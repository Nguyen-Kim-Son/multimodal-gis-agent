from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Any

@dataclass(slots=True)
class ModelResponse:
    text: str
    model: str
    provider: str
    latency_seconds: float
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    cost_usd: float | None = None
    raw: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

class BaseModelAdapter(ABC):
    provider: str
    model_name: str

    @abstractmethod
    def generate(self, prompt: str, *, system_prompt: str | None = None, max_tokens: int = 4096, temperature: float = 0.0, timeout: int = 120) -> ModelResponse:
        raise NotImplementedError
