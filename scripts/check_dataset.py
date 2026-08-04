from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tasks import DatasetManager


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", nargs="?", default="tasks/examples")
    parser.add_argument("--recursive", action="store_true")
    args = parser.parse_args()

    manager = DatasetManager(args.directory, recursive=args.recursive)
    print(manager.summary())
    print("[ OK ] All tasks are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
