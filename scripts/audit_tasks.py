from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from audit import AuditChecker
from audit.review_sheet import build_review_sheet
from tasks import load_directory


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit MMGIS-Bench tasks before model evaluation.")
    parser.add_argument("directory", nargs="?", default="tasks/pilot20")
    parser.add_argument("--output", default="reports/task_audit")
    args = parser.parse_args()

    tasks = load_directory(args.directory)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    report = AuditChecker().check(tasks)
    (output / "audit.json").write_text(
        json.dumps(report.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    build_review_sheet(tasks, output / "review_sheet.csv")

    print("=" * 60)
    print("MMGIS-Bench Task Audit")
    print("=" * 60)
    print(f"Tasks    : {report.num_tasks}")
    print(f"Errors   : {report.num_errors}")
    print(f"Warnings : {report.num_warnings}")
    print(f"Passed   : {report.passed}")
    print(f"Report   : {output / 'audit.json'}")
    print(f"Review   : {output / 'review_sheet.csv'}")

    return int(not report.passed)


if __name__ == "__main__":
    raise SystemExit(main())
