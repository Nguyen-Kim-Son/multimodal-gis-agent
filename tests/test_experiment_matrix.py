import json

from experiments.matrix import ExperimentMatrixRunner


def test_mock_experiment_matrix(tmp_path):
    config = {
        "experiment": {
            "name": "test_matrix",
            "tasks": "tasks/examples",
            "output_root": str(tmp_path),
            "repeats": 2,
            "cache": False,
        },
        "models": {
            "mock": {
                "enabled": True,
                "provider": "mock",
                "model": "deterministic-mock",
            }
        },
    }

    run_root = ExperimentMatrixRunner(
        config,
        project_root=".",
    ).run()

    matrix_path = run_root / "matrix_results.jsonl"

    assert matrix_path.exists()

    rows = [
        json.loads(line)
        for line in matrix_path.read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]

    assert len(rows) == 10
    assert {row["repeat"] for row in rows} == {1, 2}
