from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import yaml


def normalize_prompt(value: str) -> str:
    return " ".join(value.casefold().split())


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create one task per unique ContextGeo question."
    )
    parser.add_argument(
        "source",
        nargs="?",
        default="tasks/contextgeo150",
    )
    parser.add_argument(
        "--output",
        default="tasks/contextgeo_unique35",
    )
    args = parser.parse_args()

    source = Path(args.source)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    for existing in output.glob("*.yaml"):
        existing.unlink()

    seen: set[str] = set()
    selected: list[Path] = []

    for path in sorted(source.glob("*.yaml")):
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        prompt = normalize_prompt(payload["input"]["prompt"])

        if prompt in seen:
            continue

        seen.add(prompt)
        selected.append(path)

    for index, source_path in enumerate(selected, start=1):
        shutil.copy2(
            source_path,
            output / f"task{index:03d}.yaml",
        )

    print(f"Created {len(selected)} unique tasks in {output}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
