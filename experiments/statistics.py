from __future__ import annotations

import math
import statistics
from collections import defaultdict
from typing import Any


def confidence_interval_95(
    values: list[float],
) -> tuple[float, float]:
    if not values:
        return 0.0, 0.0

    mean = statistics.fmean(values)

    if len(values) == 1:
        return mean, mean

    standard_error = (
        statistics.stdev(values)
        / math.sqrt(len(values))
    )

    margin = 1.96 * standard_error
    return mean - margin, mean + margin


def aggregate_runs(
    records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    grouped: dict[
        tuple[str, str, str],
        list[dict[str, Any]],
    ] = defaultdict(list)

    for record in records:
        key = (
            str(record["model_key"]),
            str(record["task_id"]),
            str(record["category"]),
        )
        grouped[key].append(record)

    output: list[dict[str, Any]] = []

    for (
        model_key,
        task_id,
        category,
    ), group in sorted(grouped.items()):
        scores = [
            float(item["overall_score"])
            for item in group
        ]
        latencies = [
            float(item["latency_seconds"])
            for item in group
            if item.get("latency_seconds") is not None
        ]
        lower, upper = confidence_interval_95(scores)

        output.append(
            {
                "model_key": model_key,
                "task_id": task_id,
                "category": category,
                "repeats": len(group),
                "mean_score": statistics.fmean(scores),
                "score_std": (
                    statistics.stdev(scores)
                    if len(scores) > 1
                    else 0.0
                ),
                "score_ci95_lower": lower,
                "score_ci95_upper": upper,
                "pass_rate": statistics.fmean(
                    float(item["passed"])
                    for item in group
                ),
                "mean_latency_seconds": (
                    statistics.fmean(latencies)
                    if latencies
                    else None
                ),
                "mean_total_tokens": statistics.fmean(
                    float(item.get("total_tokens") or 0)
                    for item in group
                ),
                "failure_rate": statistics.fmean(
                    float(bool(item.get("error")))
                    for item in group
                ),
            }
        )

    return output
