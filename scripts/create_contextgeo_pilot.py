from __future__ import annotations

import argparse
import random
import shutil
import sys
from collections import defaultdict
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tasks import load_directory


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Create a stratified ContextGeo pilot by task type and difficulty."
        )
    )
    parser.add_argument(
        "source",
        nargs="?",
        default="tasks/contextgeo150",
    )
    parser.add_argument(
        "--output",
        default="tasks/contextgeo_pilot",
    )
    parser.add_argument(
        "--per-stratum",
        type=int,
        default=2,
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
    )
    args = parser.parse_args()

    source_root = Path(args.source)
    tasks = load_directory(source_root)

    source_by_id: dict[str, Path] = {}

    for file_path in source_root.glob("*.yaml"):
        payload = yaml.safe_load(file_path.read_text(encoding="utf-8"))
        source_by_id[payload["metadata"]["id"]] = file_path

    strata: dict[tuple[str, str], list] = defaultdict(list)

    for task in tasks:
        key = (
            task.metadata.category.value,
            task.metadata.difficulty.value,
        )
        strata[key].append(task)

    rng = random.Random(args.seed)
    selected = []

    used_prompts: set[str] = set()

    for key in sorted(strata):
        candidates = list(strata[key])
        rng.shuffle(candidates)

        chosen = []

        for task in candidates:
            normalized_prompt = " ".join(
                task.input.prompt.casefold().split()
            )

            if normalized_prompt in used_prompts:
                continue

            chosen.append(task)
            used_prompts.add(normalized_prompt)

            if len(chosen) >= args.per_stratum:
                break

        selected.extend(chosen)

    target = Path(args.output)
    target.mkdir(parents=True, exist_ok=True)

    for file_path in target.glob("*.yaml"):
        file_path.unlink()

    for index, task in enumerate(selected, start=1):
        source_path = source_by_id[task.id]
        shutil.copy2(
            source_path,
            target / f"pilot{index:03d}.yaml",
        )

    print(
        f"Created {len(selected)} tasks across "
        f"{len(strata)} non-empty type/difficulty strata in {target}."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
