from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent

# USD per million tokens. Verify against live OpenRouter pages before the run.
DEFAULT_PRICING = {
    "openai/gpt-oss-20b:free": (0.0, 0.0),
    "google/gemma-4-26b-a4b-it:free": (0.0, 0.0),
    "openai/gpt-5-mini": (0.25, 2.00),
    "google/gemini-2.5-flash": (0.30, 2.50),
    "qwen/qwen3-coder": (0.22, 1.80),
    "anthropic/claude-sonnet-4": (3.00, 15.00),
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Estimate experiment cost using conservative token assumptions."
    )
    parser.add_argument("--config", default="configs/paper_unique35.yaml")
    parser.add_argument("--input-tokens", type=int, default=1000)
    parser.add_argument("--output-tokens", type=int, default=3000)
    parser.add_argument("--budget", type=float, default=9.91)
    parser.add_argument(
        "--output",
        default="reports/paper_cost_estimate.csv",
    )
    args = parser.parse_args()

    config = yaml.safe_load(
        (PROJECT_ROOT / args.config).read_text(encoding="utf-8")
    )
    task_dir = PROJECT_ROOT / config["experiment"]["tasks"]
    num_tasks = len(list(task_dir.glob("*.yaml")))
    repeats = int(config["experiment"].get("repeats", 1))
    calls = num_tasks * repeats
    rows = []

    for model_key, model in config["models"].items():
        if not model.get("enabled", True):
            continue

        model_id = str(model["model"])
        input_rate, output_rate = DEFAULT_PRICING.get(
            model_id,
            (float("nan"), float("nan")),
        )

        estimated = (
            calls * args.input_tokens * input_rate / 1_000_000
            + calls * args.output_tokens * output_rate / 1_000_000
        )

        rows.append(
            {
                "model_key": model_key,
                "model": model_id,
                "calls": calls,
                "input_tokens_per_call": args.input_tokens,
                "output_tokens_per_call": args.output_tokens,
                "input_usd_per_million": input_rate,
                "output_usd_per_million": output_rate,
                "estimated_cost_usd": estimated,
            }
        )

    frame = pd.DataFrame(rows)
    total = frame["estimated_cost_usd"].sum()

    output = PROJECT_ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output, index=False)

    print(frame.to_string(index=False))
    print(f"Estimated total: ${total:.4f}")
    print(f"Budget:          ${args.budget:.2f}")
    print(f"Remaining:       ${args.budget - total:.4f}")
    print(f"Saved: {output}")

    return int(total > args.budget)


if __name__ == "__main__":
    raise SystemExit(main())
