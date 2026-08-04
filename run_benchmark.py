from __future__ import annotations

import argparse

from dotenv import load_dotenv

from benchmark import BenchmarkRunner
from mmgis_logging import configure_logging
from models import MockModel, OllamaModel, OpenRouterModel
from tasks import load_directory


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--model",
        choices=[
            "mock",
            "openrouter",
            "ollama",
        ],
        default="mock",
    )

    parser.add_argument(
        "--model-name",
        default=None,
    )

    parser.add_argument(
        "--tasks",
        default="tasks/examples",
    )

    parser.add_argument(
        "--output",
        default="outputs/run",
    )

    parser.add_argument(
        "--no-cache",
        action="store_true",
    )

    parser.add_argument(
        "--no-resume",
        action="store_true",
    )

    parser.add_argument(
        "--log-level",
        default="INFO",
    )

    return parser.parse_args()


def build_model(
    args: argparse.Namespace,
):
    if args.model == "mock":
        return MockModel()

    if args.model == "openrouter":
        return OpenRouterModel(
            args.model_name
            or "openai/gpt-oss-20b:free"
        )

    return OllamaModel(
        args.model_name
        or "qwen2.5-coder:7b"
    )


def main() -> int:
    load_dotenv()
    args = parse_args()

    configure_logging(
        level=args.log_level,
        log_file="logs/benchmark.log",
    )

    tasks = load_directory(
        args.tasks
    )

    runner = BenchmarkRunner(
        build_model(args),
        output_dir=args.output,
        cache=not args.no_cache,
        resume=not args.no_resume,
    )

    records = runner.run(
        tasks
    )

    failures = sum(
        record.error is not None
        for record in records
    )

    print(
        f"Processed {len(records)} new tasks; "
        f"failures={failures}"
    )

    return int(
        failures > 0
    )


if __name__ == "__main__":
    raise SystemExit(main())
