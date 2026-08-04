from __future__ import annotations

import random
from collections import defaultdict
from pathlib import Path

import yaml

from tasks.schema import Task


def create_balanced_pilot(
    tasks: list[Task],
    output_dir: str | Path,
    *,
    per_category: int = 2,
    seed: int = 42,
) -> list[Task]:
    groups: dict[str, list[Task]] = defaultdict(list)
    for task in tasks:
        groups[task.metadata.category.value].append(task)

    rng = random.Random(seed)
    selected: list[Task] = []

    for category in sorted(groups):
        candidates = list(groups[category])
        rng.shuffle(candidates)
        candidates.sort(key=lambda task: task.metadata.difficulty.value)
        selected.extend(candidates[:per_category])

    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)

    for old_file in target.glob("*.yaml"):
        old_file.unlink()

    for index, task in enumerate(selected, start=1):
        payload = task.model_dump(mode="json", exclude_none=True)
        (target / f"pilot{index:03d}.yaml").write_text(
            yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )

    return selected
