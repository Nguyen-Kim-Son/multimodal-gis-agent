from experiments.statistics import (
    aggregate_runs,
    confidence_interval_95,
)


def test_confidence_interval_single_value():
    assert confidence_interval_95([0.5]) == (0.5, 0.5)


def test_aggregate_runs():
    records = [
        {
            "model_key": "a",
            "task_id": "T1",
            "category": "discovery",
            "overall_score": 1.0,
            "passed": True,
            "latency_seconds": 1.0,
            "total_tokens": 10,
            "error": None,
        },
        {
            "model_key": "a",
            "task_id": "T1",
            "category": "discovery",
            "overall_score": 0.0,
            "passed": False,
            "latency_seconds": 3.0,
            "total_tokens": 20,
            "error": None,
        },
    ]

    aggregated = aggregate_runs(records)

    assert len(aggregated) == 1
    assert aggregated[0]["mean_score"] == 0.5
    assert aggregated[0]["pass_rate"] == 0.5
    assert aggregated[0]["mean_latency_seconds"] == 2.0
