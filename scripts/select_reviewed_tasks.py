from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import pandas as pd
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(description="Promote manually approved YAML tasks.")
    parser.add_argument("source", nargs="?", default="tasks/pilot20")
    parser.add_argument("--review-sheet", default="reports/task_audit/review_sheet.csv")
    parser.add_argument("--output", default="tasks/reviewed_pilot")
    parser.add_argument("--approved-value", default="approved")
    args = parser.parse_args()

    frame = pd.read_csv(args.review_sheet).fillna("")
    approved_ids = set(
        frame.loc[
            frame["review_status"].astype(str).str.casefold()
            == args.approved_value.casefold(),
            "task_id",
        ].astype(str)
    )

    source_root = Path(args.source)
    target = Path(args.output)
    target.mkdir(parents=True, exist_ok=True)

    for existing in target.glob("*.yaml"):
        existing.unlink()

    copied = 0
    for source_file in sorted(source_root.glob("*.yaml")):
        payload = yaml.safe_load(source_file.read_text(encoding="utf-8"))
        task_id = payload.get("metadata", {}).get("id")
        if task_id in approved_ids:
            shutil.copy2(source_file, target / source_file.name)
            copied += 1

    print(f"Copied {copied} approved tasks to {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
