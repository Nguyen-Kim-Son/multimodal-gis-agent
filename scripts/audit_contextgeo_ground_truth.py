from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tasks import load_directory


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit operation-level ContextGeo ground truth."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default="tasks/contextgeo150",
    )
    parser.add_argument(
        "--output",
        default="reports/contextgeo_ground_truth_audit.json",
    )
    args = parser.parse_args()

    tasks = load_directory(args.directory)

    issues = []
    operation_counts = Counter()
    prompt_counts = Counter(
        " ".join(task.input.prompt.casefold().split())
        for task in tasks
    )

    for task in tasks:
        operations = task.output.expected_operations

        if not operations:
            issues.append(
                {
                    "task_id": task.id,
                    "severity": "error",
                    "message": "Missing expected_operations.",
                }
            )

        if len(operations) != len(set(operations)):
            issues.append(
                {
                    "task_id": task.id,
                    "severity": "warning",
                    "message": "Duplicate expected operation.",
                }
            )

        for operation in operations:
            operation_counts[operation] += 1

    report = {
        "num_tasks": len(tasks),
        "num_errors": sum(
            issue["severity"] == "error"
            for issue in issues
        ),
        "num_warnings": sum(
            issue["severity"] == "warning"
            for issue in issues
        ),
        "difficulty": dict(
            Counter(
                task.metadata.difficulty.value
                for task in tasks
            )
        ),
        "category": dict(
            Counter(
                task.metadata.category.value
                for task in tasks
            )
        ),
        "dataset": dict(
            Counter(task.input.dataset for task in tasks)
        ),
        "expected_operation_counts": dict(
            sorted(operation_counts.items())
        ),
        "num_unique_questions": len(prompt_counts),
        "num_duplicated_question_patterns": sum(
            count > 1 for count in prompt_counts.values()
        ),
        "maximum_question_repetition": max(
            prompt_counts.values(), default=0
        ),
        "issues": issues,
    }

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return int(report["num_errors"] > 0)


if __name__ == "__main__":
    raise SystemExit(main())
