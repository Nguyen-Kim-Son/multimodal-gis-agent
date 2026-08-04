from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from reports import build_reports


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("results")
    parser.add_argument("--output", default="reports/latest")
    args = parser.parse_args()

    for name, path in build_reports(args.results, args.output).items():
        print(f"[ OK ] {name:10}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
