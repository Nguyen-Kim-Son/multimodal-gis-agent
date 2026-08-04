from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from contextgeo_import import import_contextgeo_tasks


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert the attached ContextGeo 150 tasks into MMGIS-Bench YAML."
    )
    parser.add_argument(
        "--source",
        default="data/contextgeo/tasks_150.json",
    )
    parser.add_argument(
        "--output",
        default="tasks/contextgeo150",
    )
    parser.add_argument(
        "--manifest",
        default="data/contextgeo/import_manifest.json",
    )
    args = parser.parse_args()

    tasks = import_contextgeo_tasks(args.source, args.output)

    manifest = {
        "source": args.source,
        "output": args.output,
        "num_tasks": len(tasks),
        "difficulty": dict(
            Counter(task.metadata.difficulty.value for task in tasks)
        ),
        "category": dict(
            Counter(task.metadata.category.value for task in tasks)
        ),
        "dataset": dict(
            Counter(task.input.dataset for task in tasks)
        ),
        "ground_truth_type": "expected_operations",
    }

    manifest_path = Path(args.manifest)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
