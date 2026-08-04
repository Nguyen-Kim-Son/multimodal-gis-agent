from evaluation.operations import (
    operation_coverage,
    workflow_order_score,
)


def test_operation_coverage_with_aliases():
    prediction = (
        "Load OpenStreetMap data, filter restaurants, "
        "then count the selected features."
    )

    score = operation_coverage(
        prediction,
        ["load_osm", "filter", "count"],
    )

    assert score == 1.0


def test_workflow_order():
    prediction = (
        "Load Census data, calculate population density, "
        "sort districts, and filter the highest-density areas."
    )

    score = workflow_order_score(
        prediction,
        [
            "load_census",
            "calculate_density",
            "sort",
            "filter",
        ],
    )

    assert score == 1.0
