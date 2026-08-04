import json

from contextgeo_import import convert_contextgeo_task
from tasks import load_directory


def test_contextgeo150_count_and_distribution():
    tasks = load_directory("tasks/contextgeo150")

    assert len(tasks) == 150
    assert sum(t.metadata.difficulty.value == "easy" for t in tasks) == 50
    assert sum(t.metadata.difficulty.value == "medium" for t in tasks) == 60
    assert sum(t.metadata.difficulty.value == "hard" for t in tasks) == 40


def test_contextgeo_source_question_is_preserved():
    source = json.loads(
        open(
            "data/contextgeo/tasks_150.json",
            encoding="utf-8",
        ).read()
    )[0]

    converted = convert_contextgeo_task(source)

    assert converted["input"]["prompt"] == source["question"]
    assert (
        converted["output"]["expected_operations"]
        == source["expected_operations"]
    )


def test_expected_operations_not_in_system_prompt():
    task = load_directory("tasks/contextgeo150")[0]

    for operation in task.output.expected_operations:
        assert operation not in (task.input.system_prompt or "")
