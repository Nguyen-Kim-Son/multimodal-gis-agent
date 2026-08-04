from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from evaluation import Evaluator
from models.base import BaseModelAdapter, ModelResponse
from tasks.schema import Task

from .cache import ResponseCache

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class RunRecord:
    task_id: str
    task_name: str
    model: str
    provider: str
    prediction: str | None
    response: dict[str, Any] | None
    evaluation: dict[str, Any] | None
    error: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class BenchmarkRunner:
    def __init__(
        self,
        model: BaseModelAdapter,
        *,
        output_dir: str | Path,
        cache: bool = True,
        resume: bool = True,
    ) -> None:
        self.model = model
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results_path = self.output_dir / "results.jsonl"
        self.cache_enabled = cache
        self.resume = resume
        self.cache = ResponseCache()
        self.evaluator = Evaluator()

    def _load_completed_ids(self) -> set[str]:
        if not self.resume or not self.results_path.exists():
            return set()

        completed: set[str] = set()

        with self.results_path.open("r", encoding="utf-8") as stream:
            for line in stream:
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                task_id = record.get("task_id")
                if task_id:
                    completed.add(str(task_id))

        return completed

    def _generate(self, task: Task) -> ModelResponse:
        key = self.cache.key(
            self.model.model_name,
            task.input.prompt,
            task.input.system_prompt,
        )

        if self.cache_enabled:
            cached = self.cache.get(key)
            if cached:
                return ModelResponse(**cached)

        response = self.model.generate(
            task.input.prompt,
            system_prompt=task.input.system_prompt,
            max_tokens=task.runtime.max_tokens,
            temperature=task.runtime.temperature,
            timeout=task.runtime.timeout,
        )

        if self.cache_enabled:
            self.cache.set(key, response.to_dict())

        return response

    def run_task(self, task: Task) -> RunRecord:
        try:
            response = self._generate(task)
            evaluation = self.evaluator.evaluate(task, response)

            return RunRecord(
                task_id=task.id,
                task_name=task.name,
                model=response.model,
                provider=response.provider,
                prediction=response.text,
                response=response.to_dict(),
                evaluation=evaluation.to_dict(),
                error=None,
            )

        except Exception as exc:
            LOGGER.exception("Task failed: %s", task.id)

            return RunRecord(
                task_id=task.id,
                task_name=task.name,
                model=self.model.model_name,
                provider=self.model.provider,
                prediction=None,
                response=None,
                evaluation=None,
                error=f"{type(exc).__name__}: {exc}",
            )

    def run(self, tasks: list[Task]) -> list[RunRecord]:
        completed_ids = self._load_completed_ids()
        pending = [task for task in tasks if task.id not in completed_ids]

        if completed_ids:
            LOGGER.info(
                "Resume enabled: skipping %d completed tasks.",
                len(completed_ids),
            )

        mode = "a" if self.resume and self.results_path.exists() else "w"
        records: list[RunRecord] = []

        with self.results_path.open(mode, encoding="utf-8") as stream:
            for index, task in enumerate(pending, start=1):
                LOGGER.info(
                    "[%d/%d] %s: %s",
                    index,
                    len(pending),
                    task.id,
                    task.name,
                )

                record = self.run_task(task)
                records.append(record)

                stream.write(
                    json.dumps(record.to_dict(), ensure_ascii=False) + "\n"
                )
                stream.flush()

        return records
