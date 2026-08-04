from collections import Counter
from collections.abc import Iterator
from pathlib import Path
from .enums import Category, Difficulty, Platform, Split
from .loader import load_directory
from .schema import Task

class DuplicateTaskIDError(ValueError):
    pass

class DatasetManager:
    def __init__(self, root: str | Path, *, recursive: bool = False) -> None:
        self.root = Path(root)
        self.tasks = load_directory(self.root, recursive=recursive)
        self._by_id = {}
        for task in self.tasks:
            if task.id in self._by_id:
                raise DuplicateTaskIDError(task.id)
            self._by_id[task.id] = task

    def __len__(self) -> int:
        return len(self.tasks)

    def __iter__(self) -> Iterator[Task]:
        return iter(self.tasks)

    def get(self, task_id: str) -> Task | None:
        return self._by_id.get(task_id)

    def filter_category(self, value: Category | str) -> list[Task]:
        target = Category(value)
        return [t for t in self.tasks if t.metadata.category == target]

    def filter_difficulty(self, value: Difficulty | str) -> list[Task]:
        target = Difficulty(value)
        return [t for t in self.tasks if t.metadata.difficulty == target]

    def filter_split(self, value: Split | str) -> list[Task]:
        target = Split(value)
        return [t for t in self.tasks if t.metadata.split == target]

    def filter_platform(self, value: Platform | str) -> list[Task]:
        target = Platform(value)
        return [t for t in self.tasks if t.input.platform == target]

    def summary(self) -> dict[str, object]:
        return {
            "root": str(self.root),
            "num_tasks": len(self.tasks),
            "categories": dict(Counter(t.metadata.category.value for t in self.tasks)),
            "difficulties": dict(Counter(t.metadata.difficulty.value for t in self.tasks)),
            "splits": dict(Counter(t.metadata.split.value for t in self.tasks)),
        }
