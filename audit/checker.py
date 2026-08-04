from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from tasks.schema import Task


@dataclass(slots=True)
class AuditIssue:
    task_id: str
    severity: str
    code: str
    message: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class AuditReport:
    num_tasks: int
    num_errors: int
    num_warnings: int
    issues: list[AuditIssue]

    @property
    def passed(self) -> bool:
        return self.num_errors == 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "num_tasks": self.num_tasks,
            "num_errors": self.num_errors,
            "num_warnings": self.num_warnings,
            "passed": self.passed,
            "issues": [issue.to_dict() for issue in self.issues],
        }


class AuditChecker:
    TEMPLATE_MARKERS = (
        "ground-truth template",
        "requires human audit",
        "automatically generated draft",
        "mock response",
    )

    def check(self, tasks: list[Task]) -> AuditReport:
        issues: list[AuditIssue] = []
        id_counts = Counter(task.id for task in tasks)
        prompt_counts = Counter(task.input.prompt.strip() for task in tasks)

        for task in tasks:
            if id_counts[task.id] > 1:
                issues.append(AuditIssue(task.id, "error", "duplicate_id", f"Task ID occurs {id_counts[task.id]} times."))

            if prompt_counts[task.input.prompt.strip()] > 1:
                issues.append(AuditIssue(task.id, "warning", "duplicate_prompt", "Prompt is duplicated in the dataset."))

            combined = " ".join(
                value for value in (
                    task.metadata.description,
                    task.output.answer or "",
                    task.output.code or "",
                )
                if value
            ).casefold()

            for marker in self.TEMPLATE_MARKERS:
                if marker in combined:
                    issues.append(AuditIssue(task.id, "warning", "draft_marker", f"Contains draft marker: {marker}"))

            if task.output.required_keywords and task.output.answer:
                missing = [
                    keyword for keyword in task.output.required_keywords
                    if keyword.casefold() not in task.output.answer.casefold()
                ]
                if missing:
                    issues.append(AuditIssue(task.id, "warning", "keyword_ground_truth_mismatch", f"Expected answer misses keywords: {missing}"))

            if task.metadata.category.value == "multimodal" and task.input.modality.value == "text":
                issues.append(AuditIssue(task.id, "warning", "modality_mismatch", "Multimodal task has text-only input."))

            if task.metadata.category.value in {"code_generation", "visualization", "temporal", "change_detection"} and task.output.code is None:
                issues.append(AuditIssue(task.id, "error", "missing_code_ground_truth", "Code-oriented task has no expected code."))

        return AuditReport(
            num_tasks=len(tasks),
            num_errors=sum(issue.severity == "error" for issue in issues),
            num_warnings=sum(issue.severity == "warning" for issue in issues),
            issues=issues,
        )
