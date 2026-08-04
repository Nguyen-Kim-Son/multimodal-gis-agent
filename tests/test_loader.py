from tasks.loader import load_directory

def test_loader():
    tasks = load_directory("tasks/examples")
    assert len(tasks) == 5
    assert len({task.id for task in tasks}) == 5
