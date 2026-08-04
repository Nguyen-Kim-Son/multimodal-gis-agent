from audit import create_balanced_pilot
from tasks import load_directory


def test_pilot_creation(tmp_path):
    tasks = load_directory("tasks/examples")
    selected = create_balanced_pilot(
        tasks,
        tmp_path,
        per_category=1,
        seed=42,
    )
    assert len(selected) == 5
    assert len(list(tmp_path.glob("*.yaml"))) == 5
