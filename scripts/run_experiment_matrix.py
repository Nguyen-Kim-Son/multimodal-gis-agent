from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.config import load_experiment_config
from experiments.matrix import ExperimentMatrixRunner
from mmgis_logging import configure_logging


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run a fair multi-model experiment matrix."
        )
    )

    parser.add_argument(
        "--config",
        default="configs/experiment_matrix.yaml",
    )

    parser.add_argument(
        "--log-level",
        default="INFO",
    )

    args = parser.parse_args()

    load_dotenv()

    configure_logging(
        level=args.log_level,
        log_file=(
            PROJECT_ROOT
            / "logs"
            / "experiment_matrix.log"
        ),
    )

    config = load_experiment_config(
        args.config
    )

    run_root = ExperimentMatrixRunner(
        config,
        project_root=PROJECT_ROOT,
    ).run()

    print(
        f"Experiment completed: {run_root}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
