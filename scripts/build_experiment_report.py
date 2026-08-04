from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.report import build_experiment_report


def _latest_matrix_result(
    output_root: str | Path,
) -> Path:
    root = Path(output_root)

    candidates = sorted(
        root.glob("*/matrix_results.jsonl"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    if not candidates:
        raise FileNotFoundError(
            f"No matrix_results.jsonl found under {root}."
        )

    return candidates[0]


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Aggregate repeated multi-model experiments."
        )
    )

    parser.add_argument(
        "matrix_results",
        nargs="?",
        default=None,
        help=(
            "Path to matrix_results.jsonl. "
            "Omit it with --latest to use the newest run."
        ),
    )

    parser.add_argument(
        "--latest",
        action="store_true",
        help="Use the newest experiment under --experiments-root.",
    )

    parser.add_argument(
        "--experiments-root",
        default="outputs/experiments",
    )

    parser.add_argument(
        "--output",
        default="reports/experiment_comparison",
    )

    args = parser.parse_args()

    if args.latest:
        matrix_results = _latest_matrix_result(
            args.experiments_root
        )
    elif args.matrix_results:
        matrix_results = Path(args.matrix_results)
    else:
        parser.error(
            "Provide matrix_results or use --latest."
        )

    generated = build_experiment_report(
        matrix_results,
        args.output,
    )

    print(f"Source: {matrix_results}")

    for name, path in generated.items():
        print(f"[ OK ] {name:20}: {path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
