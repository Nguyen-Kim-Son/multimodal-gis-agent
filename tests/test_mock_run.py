from benchmark import BenchmarkRunner
from models import MockModel
from tasks import load_directory

def test_mock_run(tmp_path):
    tasks = load_directory("tasks/examples")[:1]
    records = BenchmarkRunner(MockModel(), output_dir=tmp_path, cache=False).run(tasks)
    assert len(records) == 1
    assert records[0].error is None
