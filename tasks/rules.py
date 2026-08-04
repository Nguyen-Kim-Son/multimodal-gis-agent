from datetime import date
from .schema import Task

class RuleValidationError(ValueError):
    pass

def _date(value: str, name: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise RuleValidationError(f"{name} must use YYYY-MM-DD.") from exc

def validate_rules(task: Task) -> None:
    if not task.metadata.id.strip():
        raise RuleValidationError("metadata.id cannot be empty.")
    if not task.input.prompt.strip():
        raise RuleValidationError("input.prompt cannot be empty.")
    if not task.input.dataset.strip():
        raise RuleValidationError("input.dataset cannot be empty.")
    if task.datasets and task.input.dataset not in {d.asset for d in task.datasets}:
        raise RuleValidationError("input.dataset must match an asset in datasets[].")
    if task.input.bbox:
        b = task.input.bbox
        if not (-180 <= b.west < b.east <= 180):
            raise RuleValidationError("Invalid longitude range.")
        if not (-90 <= b.south < b.north <= 90):
            raise RuleValidationError("Invalid latitude range.")
    start, end = task.input.start_date, task.input.end_date
    if (start is None) != (end is None):
        raise RuleValidationError("start_date and end_date must be provided together.")
    if start and end and _date(start, "start_date") > _date(end, "end_date"):
        raise RuleValidationError("start_date must not exceed end_date.")
    out = task.output
    if not any([out.answer is not None, out.code is not None, out.image is not None, out.geometry is not None, bool(out.table), bool(out.structured_output), out.numeric_value is not None]):
        raise RuleValidationError("At least one expected output is required.")
    if not task.evaluation.metrics:
        raise RuleValidationError("At least one metric is required.")
    if not 0 <= task.evaluation.pass_score <= 1:
        raise RuleValidationError("pass_score must be between 0 and 1.")
    if task.runtime.timeout <= 0 or task.runtime.max_tokens <= 0:
        raise RuleValidationError("Runtime limits must be positive.")
