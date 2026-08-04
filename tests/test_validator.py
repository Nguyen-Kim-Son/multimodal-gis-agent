import pytest
from tasks.validator import TaskValidationError, validate_task

def test_invalid_prompt():
    payload = {
        "metadata": {"id":"BAD-1","name":"Bad","category":"discovery","difficulty":"easy","created":"2026-08-01"},
        "datasets": [],
        "input": {"dataset":"X","prompt":" "},
        "output": {"answer":"X"}
    }
    with pytest.raises(TaskValidationError):
        validate_task(payload)
