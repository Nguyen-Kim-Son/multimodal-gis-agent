from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from benchmark import BenchmarkRunner
from models import create_model
from tasks import load_directory

LOGGER = logging.getLogger(__name__)


class ExperimentMatrixRunner:
    def __init__(
        self,
        config: dict[str, Any],
        *,
        project_root: str | Path = ".",
    ) -> None:
        self.config = config
        self.project_root = Path(project_root).resolve()

    def run(self) -> Path:
        experiment = self.config["experiment"]

        tasks_dir = self.project_root / str(
            experiment.get(
                "tasks",
                "tasks/reviewed_pilot",
            )
        )

        output_root = self.project_root / str(
            experiment.get(
                "output_root",
                "outputs/experiments",
            )
        )

        repeats = int(
            experiment.get("repeats", 1)
        )

        cache = bool(
            experiment.get("cache", True)
        )

        resume = bool(
            experiment.get("resume", True)
        )

        run_id = experiment.get("run_id")

        tasks = load_directory(tasks_dir)

        if not tasks:
            raise ValueError(
                f"No tasks were found in {tasks_dir}."
            )

        timestamp = datetime.now(
            timezone.utc
        ).strftime("%Y%m%dT%H%M%SZ")

        experiment_name = str(
            experiment.get(
                "name",
                "mmgis_experiment",
            )
        )

        if run_id:
            directory_name = (
                f"{experiment_name}_{run_id}"
            )
        else:
            directory_name = (
                f"{experiment_name}_{timestamp}"
            )

        run_root = (
            output_root
            / directory_name
        )

        run_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        manifest = {
            "name": experiment_name,
            "created_utc": timestamp,
            "tasks_dir": str(tasks_dir),
            "num_tasks": len(tasks),
            "repeats": repeats,
            "resume": resume,
            "cache": cache,
            "models": list(
                self.config["models"].keys()
            ),
        }

        (
            run_root
            / "manifest.json"
        ).write_text(
            json.dumps(
                manifest,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        all_records_path = (
            run_root
            / "matrix_results.jsonl"
        )

        completed_keys = (
            self._load_completed_keys(
                all_records_path
            )
            if resume
            else set()
        )

        matrix_mode = (
            "a"
            if resume
            and all_records_path.exists()
            else "w"
        )

        with all_records_path.open(
            matrix_mode,
            encoding="utf-8",
        ) as matrix_stream:
            for model_key, model_config in (
                self.config["models"].items()
            ):
                if not bool(
                    model_config.get(
                        "enabled",
                        True,
                    )
                ):
                    continue

                LOGGER.info(
                    "Model: %s",
                    model_key,
                )

                model = create_model(
                    model_config
                )

                for repeat_index in range(
                    1,
                    repeats + 1,
                ):
                    repeat_dir = (
                        run_root
                        / model_key
                        / f"repeat_{repeat_index:02d}"
                    )

                    pending_tasks = [
                        task
                        for task in tasks
                        if (
                            model_key,
                            repeat_index,
                            task.id,
                        )
                        not in completed_keys
                    ]

                    if not pending_tasks:
                        LOGGER.info(
                            "Skipping completed model=%s repeat=%d",
                            model_key,
                            repeat_index,
                        )
                        continue

                    runner = BenchmarkRunner(
                        model,
                        output_dir=repeat_dir,
                        cache=cache,
                        resume=resume,
                    )

                    records = runner.run(
                        pending_tasks
                    )

                    for task, record in zip(
                        pending_tasks,
                        records,
                        strict=True,
                    ):
                        evaluation = (
                            record.evaluation
                            or {}
                        )

                        response = (
                            record.response
                            or {}
                        )

                        matrix_record = {
                            "experiment": experiment_name,
                            "model_key": model_key,
                            "provider": record.provider,
                            "model": record.model,
                            "repeat": repeat_index,
                            "task_id": task.id,
                            "task_name": task.name,
                            "category": (
                                task.metadata.category.value
                            ),
                            "difficulty": (
                                task.metadata.difficulty.value
                            ),
                            "platform": (
                                task.input.platform.value
                            ),
                            "passed": bool(
                                evaluation.get(
                                    "passed",
                                    False,
                                )
                            ),
                            "overall_score": float(
                                evaluation.get(
                                    "overall_score",
                                    0.0,
                                )
                            ),
                            "scores": evaluation.get(
                                "scores",
                                {},
                            ),
                            "latency_seconds": (
                                response.get(
                                    "latency_seconds"
                                )
                            ),
                            "prompt_tokens": response.get(
                                "prompt_tokens"
                            ),
                            "completion_tokens": response.get(
                                "completion_tokens"
                            ),
                            "total_tokens": response.get(
                                "total_tokens"
                            ),
                            "cost_usd": response.get(
                                "cost_usd"
                            ),
                            "upstream_provider": (
                                (response.get("raw") or {}).get("provider")
                                or (response.get("raw") or {}).get("provider_name")
                            ),
                            "error": record.error,
                        }

                        matrix_stream.write(
                            json.dumps(
                                matrix_record,
                                ensure_ascii=False,
                            )
                            + "\n"
                        )

                        matrix_stream.flush()

                        completed_keys.add(
                            (
                                model_key,
                                repeat_index,
                                task.id,
                            )
                        )

        return run_root

    @staticmethod
    def _load_completed_keys(
        path: Path,
    ) -> set[tuple[str, int, str]]:
        if not path.exists():
            return set()

        completed: set[
            tuple[str, int, str]
        ] = set()

        with path.open(
            "r",
            encoding="utf-8",
        ) as stream:
            for line in stream:
                if not line.strip():
                    continue

                try:
                    record = json.loads(
                        line
                    )
                except json.JSONDecodeError:
                    continue

                model_key = record.get(
                    "model_key"
                )
                repeat = record.get(
                    "repeat"
                )
                task_id = record.get(
                    "task_id"
                )

                if (
                    model_key is not None
                    and repeat is not None
                    and task_id is not None
                ):
                    completed.add(
                        (
                            str(model_key),
                            int(repeat),
                            str(task_id),
                        )
                    )

        return completed
