from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from audit import create_balanced_pilot
from tasks import load_directory


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a category-balanced pilot task set.")
    parser.add_argument("source", nargs="?", default="tasks/core150")
    parser.add_argument("--output", default="tasks/pilot20")
    parser.add_argument("--per-category", type=int, default=2)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    tasks = load_directory(args.source)
    selected = create_balanced_pilot(
        tasks,
        args.output,
        per_category=args.per_category,
        seed=args.seed,
    )
    print(f"Created {len(selected)} pilot tasks in {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
