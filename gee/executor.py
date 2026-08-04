import contextlib
import io
import os
from dataclasses import asdict, dataclass
from time import perf_counter
from typing import Any

@dataclass(slots=True)
class ExecutionResult:
    success: bool
    latency_seconds: float
    stdout: str = ""
    error: str | None = None
    result: Any = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

class GEEPythonExecutor:
    def __init__(self, project: str | None = None) -> None:
        self.project = project or os.getenv("GEE_PROJECT")

    def execute(self, code: str) -> ExecutionResult:
        start = perf_counter()
        stdout = io.StringIO()
        try:
            import ee
            ee.Initialize(project=self.project)
            namespace = {"ee": ee}
            with contextlib.redirect_stdout(stdout):
                exec(compile(code, "<generated-gee-code>", "exec"), namespace)
            return ExecutionResult(True, perf_counter() - start, stdout.getvalue())
        except Exception as exc:
            return ExecutionResult(False, perf_counter() - start, stdout.getvalue(), f"{type(exc).__name__}: {exc}")
