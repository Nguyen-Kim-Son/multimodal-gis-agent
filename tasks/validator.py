from typing import Any
from pydantic import ValidationError
from .rules import RuleValidationError, validate_rules
from .schema import Task

class TaskValidationError(Exception):
    pass

def validate_task(task_dict: dict[str, Any], *, source: str | None = None) -> Task:
    location = f" in {source}" if source else ""
    try:
        task = Task.model_validate(task_dict)
        validate_rules(task)
        return task
    except ValidationError as exc:
        raise TaskValidationError(f"Schema validation failed{location}:\n{exc}") from exc
    except RuleValidationError as exc:
        raise TaskValidationError(f"Rule validation failed{location}: {exc}") from exc
