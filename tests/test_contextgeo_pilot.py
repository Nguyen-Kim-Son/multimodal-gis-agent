from tasks import load_directory


def test_contextgeo_pilot_has_unique_questions():
    tasks = load_directory("tasks/contextgeo_pilot")
    prompts = [
        " ".join(task.input.prompt.casefold().split())
        for task in tasks
    ]

    assert len(tasks) == 10
    assert len(prompts) == len(set(prompts))
