from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

from tasks.schema import Task
from tasks.validator import validate_task


DATASET_DEFINITIONS: dict[str, list[dict[str, Any]]] = {
    "osm": [
        {
            "id": "osm",
            "name": "OpenStreetMap",
            "provider": "osm",
            "asset": "osm",
            "citation": "OpenStreetMap contributors",
        }
    ],
    "census": [
        {
            "id": "census",
            "name": "United States Census / ACS",
            "provider": "us_census",
            "asset": "census",
            "citation": "United States Census Bureau",
        }
    ],
    "sentinel2": [
        {
            "id": "sentinel2",
            "name": "Sentinel-2 imagery",
            "provider": "esa",
            "asset": "sentinel2",
            "resolution": 10,
            "citation": "European Space Agency Copernicus programme",
        }
    ],
    "multi": [
        {
            "id": "multi",
            "name": "ContextGeo multi-source bundle",
            "provider": "multi_source",
            "asset": "multi",
            "citation": "OSM + US Census/ACS + Sentinel-2",
        },
        {
            "id": "osm",
            "name": "OpenStreetMap",
            "provider": "osm",
            "asset": "osm",
        },
        {
            "id": "census",
            "name": "United States Census / ACS",
            "provider": "us_census",
            "asset": "census",
        },
        {
            "id": "sentinel2",
            "name": "Sentinel-2 imagery",
            "provider": "esa",
            "asset": "sentinel2",
            "resolution": 10,
        },
    ],
}


def _canonical_id(source_id: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9]+", "-", source_id).strip("-")
    return f"CONTEXTGEO-{normalized.upper()}"


def _reasoning_level(task_type: str) -> str:
    return {
        "spatial_query": "retrieval",
        "spatial_analysis": "spatial",
        "raster_analysis": "analysis",
        "data_integration": "planning",
        "spatial_reasoning": "multi_step",
    }.get(task_type, "analysis")


def _system_prompt(expected_operations: list[str]) -> str:
    # The expected operations are intentionally NOT exposed to the model.
    # They remain evaluator-only ground truth.
    del expected_operations

    return (
        "You are evaluating a geospatial analysis task. "
        "Return a concrete and reproducible workflow with clear ordered steps, "
        "assumptions, intermediate outputs, and validation checks. "
        "Do not fabricate final numeric values when the source data have not "
        "actually been executed."
    )


def convert_contextgeo_task(
    source_task: dict[str, Any],
    *,
    created: str = "2026-08-02",
) -> dict[str, Any]:
    source_id = str(source_task["task_id"])
    question = str(source_task["question"])
    dataset_key = str(source_task["dataset"])
    task_type = str(source_task["type"])
    difficulty = str(source_task["difficulty"])
    expected_operations = [
        str(item)
        for item in source_task["expected_operations"]
    ]

    payload: dict[str, Any] = {
        "metadata": {
            "id": _canonical_id(source_id),
            "name": question,
            "version": "1.0.0",
            "benchmark": "MMGIS-Bench-ContextGeo150",
            "split": "test",
            "category": task_type,
            "difficulty": difficulty,
            "author": "Nguyen Kim Son",
            "created": created,
            "description": (
                "Manually designed ContextGeo task imported from "
                "data/tasks_150.json. Ground truth is operation-level."
            ),
            "tags": [
                "contextgeo",
                source_id,
                dataset_key,
                task_type,
                difficulty,
            ],
        },
        "datasets": DATASET_DEFINITIONS[dataset_key],
        "input": {
            "modality": "text",
            "platform": "general_gis",
            "dataset": dataset_key,
            "prompt": question,
            "system_prompt": _system_prompt(expected_operations),
        },
        "output": {
            "output_type": "workflow",
            "expected_operations": expected_operations,
            "structured_output": {
                "source_task_id": source_id,
                "source_dataset": dataset_key,
                "source_type": task_type,
                "expected_operations": expected_operations,
            },
            "reference_notes": (
                "The attached ContextGeo source defines expected GIS operations, "
                "not a universal exact numeric answer. Evaluation therefore uses "
                "operation coverage and workflow ordering."
            ),
        },
        "evaluation": {
            "metrics": [
                "operation_precision",
                "operation_recall",
                "operation_f1",
                "workflow_order",
                "hallucinated_operation_rate",
            ],
            "reasoning_level": _reasoning_level(task_type),
            "pass_score": 0.6,
            "weight": 1.0,
        },
        "runtime": {
            "timeout": 300,
            "internet": True,
            "gpu": False,
            "api_required": True,
            "memory_gb": 4.0,
            "max_tokens": 4096,
            "temperature": 0.0,
            "retries": 1,
            "cache": False,
        },
    }

    # Validate during conversion so no invalid task is written.
    validate_task(payload, source=source_id)
    return payload


def import_contextgeo_tasks(
    source_json: str | Path,
    output_dir: str | Path,
) -> list[Task]:
    source_path = Path(source_json)
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)

    source_tasks = json.loads(
        source_path.read_text(encoding="utf-8")
    )

    if not isinstance(source_tasks, list):
        raise ValueError("ContextGeo task source must be a JSON list.")

    for old_file in target.glob("*.yaml"):
        old_file.unlink()

    converted: list[Task] = []

    for index, source_task in enumerate(source_tasks, start=1):
        payload = convert_contextgeo_task(source_task)
        task = Task.model_validate(payload)
        converted.append(task)

        path = target / f"task{index:03d}.yaml"
        path.write_text(
            yaml.safe_dump(
                payload,
                sort_keys=False,
                allow_unicode=True,
            ),
            encoding="utf-8",
        )

    return converted
