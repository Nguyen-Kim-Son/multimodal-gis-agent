from tasks import load_directory


def test_contextgeo_unique35():
    tasks = load_directory("tasks/contextgeo_unique35")
    prompts = [
        " ".join(task.input.prompt.casefold().split())
        for task in tasks
    ]

    assert len(tasks) == 35
    assert len(prompts) == len(set(prompts))


def test_release_07_metrics_present():
    task = load_directory("tasks/contextgeo_unique35")[0]
    metrics = {metric.value for metric in task.evaluation.metrics}

    assert "operation_precision" in metrics
    assert "operation_recall" in metrics
    assert "operation_f1" in metrics
    assert "workflow_order" in metrics
