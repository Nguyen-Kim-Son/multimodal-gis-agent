from __future__ import annotations

import argparse
import ast
import json
import random
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def bootstrap_ci(
    values: list[float],
    *,
    seed: int = 42,
    samples: int = 5000,
) -> tuple[float, float]:
    if not values:
        return 0.0, 0.0

    if len(values) == 1:
        return values[0], values[0]

    rng = random.Random(seed)
    means = []

    for _ in range(samples):
        draw = [rng.choice(values) for _ in values]
        means.append(sum(draw) / len(draw))

    means.sort()
    lower = means[int(0.025 * (samples - 1))]
    upper = means[int(0.975 * (samples - 1))]
    return lower, upper


def parse_scores(value: Any) -> dict[str, float]:
    if isinstance(value, dict):
        return value

    if not isinstance(value, str) or not value:
        return {}

    try:
        parsed = ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return {}

    return parsed if isinstance(parsed, dict) else {}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build paper-ready MMGIS-Bench tables from all_runs.csv."
    )
    parser.add_argument("all_runs")
    parser.add_argument("--output", default="reports/paper")
    args = parser.parse_args()

    source = Path(args.all_runs)
    frame = pd.read_csv(source)
    output = PROJECT_ROOT / args.output
    output.mkdir(parents=True, exist_ok=True)

    valid = frame[frame["error"].isna() | (frame["error"] == "")].copy()
    valid["scores_dict"] = valid["scores"].map(parse_scores)

    metric_names = sorted(
        {
            metric
            for scores in valid["scores_dict"]
            for metric in scores
        }
    )

    for metric in metric_names:
        valid[metric] = valid["scores_dict"].map(
            lambda values: values.get(metric)
        )

    model_rows = []

    for model_key, group in valid.groupby("model_key"):
        scores = group["overall_score"].astype(float).tolist()
        lower, upper = bootstrap_ci(scores)

        model_rows.append(
            {
                "model_key": model_key,
                "model": group["model"].iloc[0],
                "n_records": len(group),
                "n_unique_tasks": group["task_id"].nunique(),
                "mean_score": group["overall_score"].mean(),
                "ci95_lower": lower,
                "ci95_upper": upper,
                "pass_rate": group["passed"].astype(float).mean(),
                "mean_latency_seconds": group["latency_seconds"].mean(),
                "mean_prompt_tokens": group.get(
                    "prompt_tokens", pd.Series(dtype=float)
                ).mean(),
                "mean_completion_tokens": group.get(
                    "completion_tokens", pd.Series(dtype=float)
                ).mean(),
                "mean_total_tokens": group["total_tokens"].mean(),
                "total_cost_usd": group["cost_usd"].fillna(0).sum(),
                "failure_rate": 1.0 - len(group) / len(
                    frame[frame["model_key"] == model_key]
                ),
                **{
                    f"mean_{metric}": group[metric].dropna().mean()
                    for metric in metric_names
                },
            }
        )

    leaderboard = pd.DataFrame(model_rows).sort_values(
        ["mean_score", "pass_rate"],
        ascending=False,
    )
    leaderboard.insert(0, "rank", range(1, len(leaderboard) + 1))
    leaderboard.to_csv(output / "leaderboard.csv", index=False)

    category = (
        valid.groupby(["model_key", "category"], as_index=False)
        .agg(
            mean_score=("overall_score", "mean"),
            pass_rate=("passed", "mean"),
            mean_latency_seconds=("latency_seconds", "mean"),
            total_cost_usd=("cost_usd", lambda x: x.fillna(0).sum()),
        )
        .sort_values(["category", "mean_score"], ascending=[True, False])
    )
    category.to_csv(output / "category_table.csv", index=False)

    difficulty = (
        valid.groupby(["model_key", "difficulty"], as_index=False)
        .agg(
            mean_score=("overall_score", "mean"),
            pass_rate=("passed", "mean"),
            mean_latency_seconds=("latency_seconds", "mean"),
        )
        .sort_values(["difficulty", "mean_score"], ascending=[True, False])
    )
    difficulty.to_csv(output / "difficulty_table.csv", index=False)

    task = (
        valid.groupby(
            ["model_key", "task_id", "task_name", "category", "difficulty"],
            as_index=False,
        )
        .agg(
            mean_score=("overall_score", "mean"),
            score_std=("overall_score", "std"),
            pass_rate=("passed", "mean"),
            mean_latency_seconds=("latency_seconds", "mean"),
        )
    )
    task.to_csv(output / "task_table.csv", index=False)

    markdown_columns = [
        "rank",
        "model_key",
        "mean_score",
        "ci95_lower",
        "ci95_upper",
        "pass_rate",
        "mean_latency_seconds",
        "total_cost_usd",
    ]
    markdown_lines = [
        "# MMGIS-Bench Leaderboard",
        "",
        "| Rank | Model | Mean score | CI95 low | CI95 high | Pass rate | Latency (s) | Cost (USD) |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]

    for _, row in leaderboard[markdown_columns].iterrows():
        markdown_lines.append(
            "| {rank} | {model} | {score:.3f} | {low:.3f} | {high:.3f} | "
            "{pass_rate:.3f} | {latency:.3f} | {cost:.4f} |".format(
                rank=int(row["rank"]),
                model=row["model_key"],
                score=float(row["mean_score"]),
                low=float(row["ci95_lower"]),
                high=float(row["ci95_upper"]),
                pass_rate=float(row["pass_rate"]),
                latency=float(row["mean_latency_seconds"]),
                cost=float(row["total_cost_usd"]),
            )
        )

    (output / "leaderboard.md").write_text(
        "\n".join(markdown_lines) + "\n",
        encoding="utf-8",
    )

    latex_lines = [
        r"\begin{tabular}{lrrrrrr}",
        r"\toprule",
        r"Model & Mean & CI low & CI high & Pass rate & Latency & Cost \\",
        r"\midrule",
    ]

    for _, row in leaderboard.iterrows():
        model_name = str(row["model_key"]).replace("_", r"\_")
        latex_lines.append(
            f"{model_name} & "
            f"{float(row['mean_score']):.3f} & "
            f"{float(row['ci95_lower']):.3f} & "
            f"{float(row['ci95_upper']):.3f} & "
            f"{float(row['pass_rate']):.3f} & "
            f"{float(row['mean_latency_seconds']):.3f} & "
            f"{float(row['total_cost_usd']):.4f} \\\\"
        )

    latex_lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    (output / "table_main.tex").write_text(
        "\n".join(latex_lines),
        encoding="utf-8",
    )

    summary = {
        "source": str(source),
        "num_models": int(valid["model_key"].nunique()),
        "num_unique_tasks": int(valid["task_id"].nunique()),
        "num_valid_records": int(len(valid)),
        "num_failed_records": int(len(frame) - len(valid)),
        "metric_columns": metric_names,
    }
    (output / "paper_summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    print(f"[ OK ] leaderboard : {output / 'leaderboard.csv'}")
    print(f"[ OK ] markdown    : {output / 'leaderboard.md'}")
    print(f"[ OK ] category    : {output / 'category_table.csv'}")
    print(f"[ OK ] difficulty  : {output / 'difficulty_table.csv'}")
    print(f"[ OK ] task        : {output / 'task_table.csv'}")
    print(f"[ OK ] latex       : {output / 'table_main.tex'}")
    print(f"[ OK ] summary     : {output / 'paper_summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
