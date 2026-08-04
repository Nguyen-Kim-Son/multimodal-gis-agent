from audit import AuditChecker
from tasks import load_directory


def test_audit_finds_draft_markers():
    tasks = load_directory("tasks/examples")
    report = AuditChecker().check(tasks)
    assert report.num_tasks == 5
    assert report.num_errors == 0
