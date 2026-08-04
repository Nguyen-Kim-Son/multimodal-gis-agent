import json

from benchmark import BenchmarkRunner
from models import MockModel
from tasks import load_directory


def test_runner_resume_skips_completed_tasks(tmp_path):
    tasks = load_directory("tasks/examples")[:2]

    runner = BenchmarkRunner(
        MockModel(),
        output_dir=tmp_path,
        cache=False,
        resume=True,
    )

    first = runner.run(tasks)
    second = runner.run(tasks)

    assert len(first) == 2
    assert second == []

    rows = [
        json.loads(line)
        for line in (
            tmp_path / "results.jsonl"
        ).read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]

    assert len(rows) == 2
