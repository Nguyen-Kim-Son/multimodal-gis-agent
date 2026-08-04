from pathlib import Path
from typing import Any
import yaml
from .schema import Task
from .validator import TaskValidationError, validate_task

class TaskLoadError(Exception):
    pass

def _read(path: Path) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise TaskLoadError(f"Invalid YAML in {path}: {exc}") from exc

def load_yaml(path: str | Path) -> list[Task]:
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(file_path)
    raw = _read(file_path)
    if raw is None:
        return []
    items = [raw] if isinstance(raw, dict) else raw
    if not isinstance(items, list):
        raise TaskLoadError("YAML root must be a mapping or list.")
    tasks = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise TaskLoadError(f"Item {index} is not a mapping.")
        try:
            tasks.append(validate_task(item, source=f"{file_path}:{index}"))
        except TaskValidationError as exc:
            raise TaskLoadError(str(exc)) from exc
    return tasks

def load_directory(directory: str | Path, *, recursive: bool = False) -> list[Task]:
    root = Path(directory)
    if not root.is_dir():
        raise FileNotFoundError(root)
    patterns = ("**/*.yaml", "**/*.yml") if recursive else ("*.yaml", "*.yml")
    files = []
    for pattern in patterns:
        files.extend(root.glob(pattern))
    tasks = []
    for file_path in sorted(set(files)):
        tasks.extend(load_yaml(file_path))
    return tasks
