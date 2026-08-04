from tasks.loader import load_yaml
from tasks.schema import Task

def test_schema():
    tasks = load_yaml("tasks/examples/task001.yaml")
    assert len(tasks) == 1
    assert isinstance(tasks[0], Task)
    assert tasks[0].id == "MMGIS-0001"
