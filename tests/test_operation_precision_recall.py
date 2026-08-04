from evaluation.operations import operation_metrics


def test_operation_precision_recall_and_f1():
    prediction = (
        "Load OpenStreetMap data, buffer hospitals, "
        "calculate distance, and run regression."
    )

    metrics = operation_metrics(
        prediction,
        ["load_osm", "buffer", "spatial_join", "calculate_distance"],
    )

    assert metrics.true_positive == {
        "load_osm",
        "buffer",
        "calculate_distance",
    }
    assert "regression" in metrics.false_positive
    assert "spatial_join" in metrics.false_negative
    assert metrics.precision == 0.75
    assert metrics.recall == 0.75
    assert metrics.f1 == 0.75
