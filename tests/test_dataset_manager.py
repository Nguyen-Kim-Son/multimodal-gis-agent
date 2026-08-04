from tasks import DatasetManager

def test_manager():
    manager = DatasetManager("tasks/examples")
    assert len(manager) == 5
    assert len(manager.filter_category("discovery")) == 1
    assert manager.get("MMGIS-0005") is not None
