import re
from time import perf_counter
from .base import BaseModelAdapter, ModelResponse

class MockModel(BaseModelAdapter):
    provider = "mock"
    model_name = "deterministic-mock"

    def generate(self, prompt: str, *, system_prompt: str | None = None, max_tokens: int = 4096, temperature: float = 0.0, timeout: int = 120) -> ModelResponse:
        start = perf_counter()
        assets = ["LANDSAT/LC08/C02/T1_L2", "COPERNICUS/S2_SR_HARMONIZED", "MODIS/061/MOD13Q1", "FAO/GAUL/2015/level2", "USGS/SRTMGL1_003"]
        text = next((a for a in assets if a in prompt), "Mock response.")
        if "code" in prompt.lower() or "javascript" in prompt.lower():
            text = "```javascript\nvar collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED');\nprint(collection.size());\n```"
        latency = perf_counter() - start
        return ModelResponse(text=text, model=self.model_name, provider=self.provider, latency_seconds=latency, prompt_tokens=len(prompt.split()), completion_tokens=len(text.split()), total_tokens=len(prompt.split()) + len(text.split()), raw={"mock": True})
