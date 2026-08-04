from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict, Field
from .enums import Category, DatasetProvider, Difficulty, Metric, Modality, OutputType, Platform, ReasoningLevel, Split

class Metadata(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    name: str
    version: str = "1.0"
    benchmark: str = "MMGIS-Bench"
    split: Split = Split.TEST
    category: Category
    difficulty: Difficulty
    author: str = "Nguyen Kim Son"
    created: str
    description: str = ""
    tags: list[str] = Field(default_factory=list)

class Dataset(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    name: str
    provider: DatasetProvider
    asset: str
    resolution: float | None = None
    temporal_resolution: str | None = None
    bands: list[str] = Field(default_factory=list)
    citation: str | None = None

class BoundingBox(BaseModel):
    model_config = ConfigDict(extra="forbid")
    west: float
    south: float
    east: float
    north: float

class TaskInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    modality: Modality = Modality.TEXT
    platform: Platform = Platform.GEE
    dataset: str
    prompt: str
    system_prompt: str | None = None
    image: str | None = None
    voice: str | None = None
    geometry: str | None = None
    bbox: BoundingBox | None = None
    start_date: str | None = None
    end_date: str | None = None

class ExpectedOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    output_type: OutputType = OutputType.TEXT
    answer: str | None = None
    code: str | None = None
    image: str | None = None
    geometry: str | None = None
    table: list[dict[str, Any]] = Field(default_factory=list)
    structured_output: dict[str, Any] = Field(default_factory=dict)
    required_keywords: list[str] = Field(default_factory=list)
    expected_operations: list[str] = Field(default_factory=list)
    operation_aliases: dict[str, list[str]] = Field(default_factory=dict)
    reference_notes: str | None = None
    numeric_value: float | None = None
    numeric_tolerance: float = 0.0

class EvaluationConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    metrics: list[Metric] = Field(default_factory=lambda: [Metric.EXACT_MATCH])
    reasoning_level: ReasoningLevel = ReasoningLevel.RETRIEVAL
    pass_score: float = 1.0
    weight: float = 1.0

class RuntimeConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    timeout: int = 120
    internet: bool = True
    gpu: bool = False
    api_required: bool = True
    memory_gb: float = 4.0
    max_tokens: int = 4096
    temperature: float = 0.0
    retries: int = 1
    cache: bool = True

class Task(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)
    metadata: Metadata
    datasets: list[Dataset] = Field(default_factory=list)
    input: TaskInput
    output: ExpectedOutput
    evaluation: EvaluationConfig = Field(default_factory=EvaluationConfig)
    runtime: RuntimeConfig = Field(default_factory=RuntimeConfig)

    @property
    def id(self) -> str:
        return self.metadata.id

    @property
    def name(self) -> str:
        return self.metadata.name

    def summary(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.metadata.category.value,
            "difficulty": self.metadata.difficulty.value,
            "platform": self.input.platform.value,
            "datasets": len(self.datasets),
            "metrics": [m.value for m in self.evaluation.metrics],
        }
