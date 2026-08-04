from __future__ import annotations

import re
from dataclasses import dataclass


DEFAULT_OPERATION_ALIASES: dict[str, list[str]] = {
    "load_osm": [
        "load osm", "openstreetmap", "osm data", "read osm",
        "query overpass", "overpass api", "osmnx",
    ],
    "load_census": [
        "load census", "census data", "american community survey",
        "acs data", "census api",
    ],
    "load_sentinel": [
        "load sentinel", "sentinel-2", "sentinel 2", "copernicus",
        "imagecollection",
    ],
    "load_multiple": [
        "load multiple", "multiple datasets", "multi-source",
        "integrate osm", "combine datasets", "join datasets",
    ],
    "filter": [
        "filter", "subset", "select features", "query features",
        "where clause",
    ],
    "count": [
        "count", "number of", "feature count", "len(", ".size(",
    ],
    "aggregate": [
        "aggregate", "group by", "summarize", "sum", "zonal statistics",
    ],
    "calculate": [
        "calculate", "compute", "derive", "estimate",
    ],
    "buffer": [
        "buffer", "500 m", "500m", "proximity zone",
    ],
    "spatial_join": [
        "spatial join", "sjoin", "join by location",
        "intersecting features",
    ],
    "calculate_distance": [
        "calculate distance", "distance", "nearest",
        "average distance", "mean distance",
    ],
    "calculate_density": [
        "calculate density", "population density", "density",
        "population / area", "population per",
    ],
    "sort": [
        "sort", "rank", "order by", "descending", "ascending",
    ],
    "calculate_ndvi": [
        "calculate ndvi", "compute ndvi",
        "normalized difference vegetation index",
        "normalizeddifference", "(nir - red)",
    ],
    "threshold": [
        "threshold", "greater than", "less than",
        "gte", "lte", "binary mask",
    ],
    "extract": [
        "extract", "clip", "mask", "select pixels", "identify areas",
    ],
    "overlay_analysis": [
        "overlay", "intersect", "combine layers", "merge layers",
        "weighted overlay", "raster overlay",
    ],
    "multi_criteria_evaluation": [
        "multi-criteria", "multicriteria", "weighted criteria",
        "weighted score", "suitability", "composite index",
    ],
    "temporal_analysis": [
        "temporal analysis", "time series", "trend",
        "change over time", "yearly", "monthly",
    ],
    "correlation": [
        "correlation", "pearson", "spearman", "correlate",
    ],
    "regression": [
        "regression", "linear model", "predictor", "coefficient",
    ],
    "visualization": [
        "visualization", "visualize", "map", "chart", "plot", "addlayer",
    ],
}


def normalize_operation_text(value: str | None) -> str:
    if value is None:
        return ""

    value = value.casefold().replace("_", " ").replace("-", " ")
    return re.sub(r"\s+", " ", value).strip()


@dataclass(slots=True)
class OperationMatch:
    operation: str
    matched: bool
    matched_alias: str | None = None


@dataclass(slots=True)
class OperationMetrics:
    detected: set[str]
    expected: set[str]
    true_positive: set[str]
    false_positive: set[str]
    false_negative: set[str]

    @property
    def precision(self) -> float:
        denominator = len(self.true_positive) + len(self.false_positive)
        return len(self.true_positive) / denominator if denominator else 0.0

    @property
    def recall(self) -> float:
        denominator = len(self.true_positive) + len(self.false_negative)
        return len(self.true_positive) / denominator if denominator else 0.0

    @property
    def f1(self) -> float:
        denominator = self.precision + self.recall
        return (
            2 * self.precision * self.recall / denominator
            if denominator
            else 0.0
        )

    @property
    def hallucinated_rate(self) -> float:
        return (
            len(self.false_positive) / len(self.detected)
            if self.detected
            else 0.0
        )


def aliases_for(
    operation: str,
    custom_aliases: dict[str, list[str]] | None = None,
) -> list[str]:
    custom_aliases = custom_aliases or {}

    return [
        operation,
        operation.replace("_", " "),
        *DEFAULT_OPERATION_ALIASES.get(operation, []),
        *custom_aliases.get(operation, []),
    ]


def _alias_in_text(normalized_text: str, alias: str) -> bool:
    normalized_alias = normalize_operation_text(alias)

    if not normalized_alias:
        return False

    # Avoid substring false positives such as "map" in "OpenStreetMap".
    if re.fullmatch(r"[a-z0-9 ]+", normalized_alias):
        pattern = r"(?<![a-z0-9])" + re.escape(normalized_alias) + r"(?![a-z0-9])"
        return re.search(pattern, normalized_text) is not None

    return normalized_alias in normalized_text


def detect_operations(
    prediction: str | None,
    custom_aliases: dict[str, list[str]] | None = None,
) -> set[str]:
    normalized_prediction = normalize_operation_text(prediction)
    custom_aliases = custom_aliases or {}
    operation_names = set(DEFAULT_OPERATION_ALIASES) | set(custom_aliases)
    detected: set[str] = set()

    for operation in operation_names:
        if any(
            _alias_in_text(normalized_prediction, alias)
            for alias in aliases_for(operation, custom_aliases)
        ):
            detected.add(operation)

    # Suppress generic parent operations when a specific child operation
    # already explains the same phrase.
    specific_calculations = {
        "calculate_distance",
        "calculate_density",
        "calculate_ndvi",
    }
    if detected & specific_calculations:
        detected.discard("calculate")

    return detected


def operation_metrics(
    prediction: str | None,
    expected_operations: list[str],
    custom_aliases: dict[str, list[str]] | None = None,
) -> OperationMetrics:
    expected = set(expected_operations)
    detected = detect_operations(prediction, custom_aliases)

    return OperationMetrics(
        detected=detected,
        expected=expected,
        true_positive=detected & expected,
        false_positive=detected - expected,
        false_negative=expected - detected,
    )


def match_operations(
    prediction: str | None,
    expected_operations: list[str],
    custom_aliases: dict[str, list[str]] | None = None,
) -> list[OperationMatch]:
    normalized_prediction = normalize_operation_text(prediction)
    matches: list[OperationMatch] = []

    for operation in expected_operations:
        matched_alias = next(
            (
                alias
                for alias in aliases_for(operation, custom_aliases)
                if _alias_in_text(normalized_prediction, alias)
            ),
            None,
        )

        matches.append(
            OperationMatch(
                operation=operation,
                matched=matched_alias is not None,
                matched_alias=matched_alias,
            )
        )

    return matches


def operation_coverage(
    prediction: str | None,
    expected_operations: list[str],
    custom_aliases: dict[str, list[str]] | None = None,
) -> float:
    return operation_metrics(
        prediction,
        expected_operations,
        custom_aliases,
    ).recall


def operation_precision(
    prediction: str | None,
    expected_operations: list[str],
    custom_aliases: dict[str, list[str]] | None = None,
) -> float:
    return operation_metrics(
        prediction,
        expected_operations,
        custom_aliases,
    ).precision


def operation_recall(
    prediction: str | None,
    expected_operations: list[str],
    custom_aliases: dict[str, list[str]] | None = None,
) -> float:
    return operation_metrics(
        prediction,
        expected_operations,
        custom_aliases,
    ).recall


def operation_f1(
    prediction: str | None,
    expected_operations: list[str],
    custom_aliases: dict[str, list[str]] | None = None,
) -> float:
    return operation_metrics(
        prediction,
        expected_operations,
        custom_aliases,
    ).f1


def hallucinated_operation_rate(
    prediction: str | None,
    expected_operations: list[str],
    custom_aliases: dict[str, list[str]] | None = None,
) -> float:
    return operation_metrics(
        prediction,
        expected_operations,
        custom_aliases,
    ).hallucinated_rate


def workflow_order_score(
    prediction: str | None,
    expected_operations: list[str],
    custom_aliases: dict[str, list[str]] | None = None,
) -> float:
    if not prediction or len(expected_operations) < 2:
        return 0.0

    normalized_prediction = normalize_operation_text(prediction)
    positions: list[int | None] = []

    for operation in expected_operations:
        candidate_positions = [
            normalized_prediction.find(normalize_operation_text(alias))
            for alias in aliases_for(operation, custom_aliases)
            if _alias_in_text(normalized_prediction, alias)
        ]

        positions.append(
            min(candidate_positions) if candidate_positions else None
        )

    comparable_pairs = 0
    ordered_pairs = 0

    for left_index in range(len(positions) - 1):
        left = positions[left_index]

        for right_index in range(left_index + 1, len(positions)):
            right = positions[right_index]

            if left is None or right is None:
                continue

            comparable_pairs += 1
            ordered_pairs += int(left < right)

    return ordered_pairs / comparable_pairs if comparable_pairs else 0.0
