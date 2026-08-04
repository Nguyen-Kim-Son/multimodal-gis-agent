from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from models.base import ModelResponse
from tasks.enums import Metric
from tasks.schema import Task

from .metrics import code_presence, exact_match, keyword_coverage
from .operations import (
    hallucinated_operation_rate,
    operation_f1,
    operation_precision,
    operation_recall,
    workflow_order_score,
)


@dataclass(slots=True)
class EvaluationResult:
    task_id: str
    scores: dict[str, float]
    overall_score: float
    passed: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class Evaluator:
    NON_SCORING_METRICS = {
        Metric.LATENCY.value,
        Metric.TOKEN_USAGE.value,
        Metric.COST.value,
        Metric.HALLUCINATED_OPERATION_RATE.value,
    }

    def evaluate(
        self,
        task: Task,
        response: ModelResponse,
        *,
        execution_success: bool | None = None,
    ) -> EvaluationResult:
        scores: dict[str, float] = {}

        for metric in task.evaluation.metrics:
            if metric == Metric.EXACT_MATCH:
                scores[metric.value] = exact_match(
                    response.text,
                    task.output.answer,
                )

            elif metric == Metric.KEYWORD_COVERAGE:
                scores[metric.value] = keyword_coverage(
                    response.text,
                    task.output.required_keywords,
                )

            elif metric in {
                Metric.OPERATION_COVERAGE,
                Metric.OPERATION_RECALL,
            }:
                scores[metric.value] = operation_recall(
                    response.text,
                    task.output.expected_operations,
                    task.output.operation_aliases,
                )

            elif metric == Metric.OPERATION_PRECISION:
                scores[metric.value] = operation_precision(
                    response.text,
                    task.output.expected_operations,
                    task.output.operation_aliases,
                )

            elif metric == Metric.OPERATION_F1:
                scores[metric.value] = operation_f1(
                    response.text,
                    task.output.expected_operations,
                    task.output.operation_aliases,
                )

            elif metric == Metric.HALLUCINATED_OPERATION_RATE:
                scores[metric.value] = hallucinated_operation_rate(
                    response.text,
                    task.output.expected_operations,
                    task.output.operation_aliases,
                )

            elif metric == Metric.WORKFLOW_ORDER:
                scores[metric.value] = workflow_order_score(
                    response.text,
                    task.output.expected_operations,
                    task.output.operation_aliases,
                )

            elif metric == Metric.CODE_PRESENCE:
                scores[metric.value] = code_presence(response.text)

            elif metric == Metric.EXECUTION_SUCCESS:
                scores[metric.value] = float(bool(execution_success))

            elif metric == Metric.LATENCY:
                scores[metric.value] = response.latency_seconds

            elif metric == Metric.TOKEN_USAGE:
                scores[metric.value] = float(response.total_tokens or 0)

            elif metric == Metric.COST:
                scores[metric.value] = float(response.cost_usd or 0)

            else:
                scores[metric.value] = 0.0

        scoring_values = [
            value
            for name, value in scores.items()
            if name not in self.NON_SCORING_METRICS
        ]

        overall = (
            sum(scoring_values) / len(scoring_values)
            if scoring_values
            else 0.0
        )

        return EvaluationResult(
            task_id=task.id,
            scores=scores,
            overall_score=overall,
            passed=overall >= task.evaluation.pass_score,
        )
