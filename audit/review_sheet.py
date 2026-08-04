from __future__ import annotations

from pathlib import Path

import pandas as pd

from tasks.schema import Task


REVIEW_COLUMNS = [
    "task_id",
    "name",
    "category",
    "difficulty",
    "prompt",
    "dataset",
    "expected_answer",
    "expected_code",
    "review_status",
    "reviewer",
    "notes",
]


def build_review_sheet(tasks: list[Task], output_path: str | Path) -> Path:
    rows = []
    for task in tasks:
        rows.append({
            "task_id": task.id,
            "name": task.name,
            "category": task.metadata.category.value,
            "difficulty": task.metadata.difficulty.value,
            "prompt": task.input.prompt,
            "dataset": task.input.dataset,
            "expected_answer": task.output.answer,
            "expected_code": task.output.code,
            "review_status": "pending",
            "reviewer": "",
            "notes": "",
        })

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows, columns=REVIEW_COLUMNS).to_csv(path, index=False)
    return path
