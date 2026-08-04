from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from .statistics import aggregate_runs


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    with Path(path).open("r", encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                records.append(json.loads(line))

    return records


def _escape_latex(value: object) -> str:
    text = "" if value is None else str(value)

    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }

    for source, target in replacements.items():
        text = text.replace(source, target)

    return text


def _format_number(value: object) -> str:
    if value is None:
        return "--"

    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return _escape_latex(value)

    if pd.isna(numeric):
        return "--"

    return f"{numeric:.3f}"


def model_summary_to_latex(model_frame: pd.DataFrame) -> str:
    if model_frame.empty:
        return "% No experiment results available.\n"

    lines = [
        r"\begin{tabular}{lrrrr}",
        r"\toprule",
        r"Model & Mean score & Pass rate & Latency (s) & Failure rate \\",
        r"\midrule",
    ]

    for _, row in model_frame.iterrows():
        lines.append(
            " & ".join(
                [
                    _escape_latex(row["model_key"]),
                    _format_number(row["mean_score"]),
                    _format_number(row["pass_rate"]),
                    _format_number(row["mean_latency_seconds"]),
                    _format_number(row["failure_rate"]),
                ]
            )
            + r" \\"
        )

    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            "",
        ]
    )

    return "\n".join(lines)


def build_experiment_report(
    matrix_results: str | Path,
    output_dir: str | Path,
) -> dict[str, Path]:
    matrix_path = Path(matrix_results)

    if not matrix_path.is_file():
        raise FileNotFoundError(
            f"Matrix results file not found: {matrix_path}"
        )

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    records = read_jsonl(matrix_path)

    if not records:
        raise ValueError(
            f"No experiment records found in {matrix_path}."
        )

    aggregate = aggregate_runs(records)

    raw_frame = pd.DataFrame(records)
    task_frame = pd.DataFrame(aggregate)

    raw_csv = output / "all_runs.csv"
    task_csv = output / "task_aggregates.csv"

    raw_frame.to_csv(raw_csv, index=False)
    task_frame.to_csv(task_csv, index=False)

    model_rows: list[dict[str, Any]] = []

    for model_key, group in task_frame.groupby("model_key"):
        latencies = group["mean_latency_seconds"].dropna()

        model_rows.append(
            {
                "model_key": model_key,
                "num_tasks": len(group),
                "mean_score": group["mean_score"].mean(),
                "pass_rate": group["pass_rate"].mean(),
                "mean_latency_seconds": (
                    latencies.mean()
                    if not latencies.empty
                    else None
                ),
                "mean_total_tokens": group[
                    "mean_total_tokens"
                ].mean(),
                "failure_rate": group["failure_rate"].mean(),
            }
        )

    model_frame = pd.DataFrame(model_rows).sort_values(
        by=["mean_score", "pass_rate"],
        ascending=False,
    )

    model_csv = output / "model_summary.csv"
    model_frame.to_csv(model_csv, index=False)

    category_frame = (
        task_frame.groupby(
            ["model_key", "category"],
            as_index=False,
        )
        .agg(
            mean_score=("mean_score", "mean"),
            pass_rate=("pass_rate", "mean"),
            mean_latency_seconds=(
                "mean_latency_seconds",
                "mean",
            ),
            failure_rate=("failure_rate", "mean"),
        )
        .sort_values(["model_key", "category"])
    )

    category_csv = output / "category_summary.csv"
    category_frame.to_csv(category_csv, index=False)

    difficulty_frame = (
        raw_frame.groupby(
            ["model_key", "difficulty"],
            as_index=False,
        )
        .agg(
            mean_score=("overall_score", "mean"),
            pass_rate=("passed", "mean"),
            mean_latency_seconds=(
                "latency_seconds",
                "mean",
            ),
        )
        .sort_values(["model_key", "difficulty"])
    )

    difficulty_csv = output / "difficulty_summary.csv"
    difficulty_frame.to_csv(difficulty_csv, index=False)

    summary_json = output / "summary.json"
    summary_json.write_text(
        json.dumps(
            {
                "matrix_results": str(matrix_path),
                "num_run_records": len(records),
                "num_models": int(model_frame.shape[0]),
                "num_tasks": int(task_frame["task_id"].nunique()),
                "model_summary": model_frame.to_dict(
                    orient="records"
                ),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    latex_path = output / "model_comparison.tex"
    latex_path.write_text(
        model_summary_to_latex(model_frame),
        encoding="utf-8",
    )

    return {
        "all_runs": raw_csv,
        "task_aggregates": task_csv,
        "model_summary": model_csv,
        "category_summary": category_csv,
        "difficulty_summary": difficulty_csv,
        "summary": summary_json,
        "latex": latex_path,
    }
