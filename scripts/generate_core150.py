from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import argparse
from datetime import date
import yaml

DATASETS = [
    ("landsat8", "Landsat 8", "usgs", "LANDSAT/LC08/C02/T1_L2", 30),
    ("sentinel2", "Sentinel-2 SR", "esa", "COPERNICUS/S2_SR_HARMONIZED", 10),
    ("modis_ndvi", "MODIS NDVI", "nasa", "MODIS/061/MOD13Q1", 250),
    ("gaul2", "GAUL Level 2", "fao", "FAO/GAUL/2015/level2", None),
    ("srtm", "SRTM DEM", "usgs", "USGS/SRTMGL1_003", 30),
]
CATEGORIES = ["discovery", "filtering", "visualization", "statistics", "code_generation", "spatial_reasoning", "temporal", "change_detection", "multimodal", "planning"]
DIFFICULTIES = ["easy", "medium", "hard"]
PROMPTS = {
    "discovery": "Identify the Google Earth Engine asset for {dataset}.",
    "filtering": "Describe how to filter {dataset} over Hanoi for 2024.",
    "visualization": "Generate GEE code to visualize {dataset} over Hanoi.",
    "statistics": "Generate a workflow to compute a regional statistic from {dataset} over Hanoi.",
    "code_generation": "Generate executable GEE JavaScript code using {asset}.",
    "spatial_reasoning": "Explain a spatial reasoning workflow using {dataset} and Hanoi districts.",
    "temporal": "Generate a temporal analysis workflow for {dataset} from 2020 to 2024.",
    "change_detection": "Generate a change-detection workflow using {dataset}.",
    "multimodal": "Describe how text and map inputs could guide analysis of {dataset}.",
    "planning": "Create a multi-step GIS analysis plan using {dataset}.",
}

def make_task(index):
    category = CATEGORIES[(index - 1) % len(CATEGORIES)]
    difficulty = DIFFICULTIES[((index - 1) // len(CATEGORIES)) % len(DIFFICULTIES)]
    dataset_id, name, provider, asset, resolution = DATASETS[(index - 1) % len(DATASETS)]
    is_code = category in {"visualization", "code_generation", "temporal", "change_detection"}
    output = {"output_type": "code" if is_code else "text", "required_keywords": [asset, "Hanoi"]}
    output["code" if is_code else "answer"] = f"// Ground-truth template must use {asset}" if is_code else asset
    return {
        "metadata": {
            "id": f"MMGIS-{index:04d}",
            "name": f"{category.replace('_', ' ').title()} {index:03d}",
            "version": "0.2.0-draft",
            "benchmark": "MMGIS-Bench-Core150-Draft",
            "split": "test",
            "category": category,
            "difficulty": difficulty,
            "author": "Nguyen Kim Son",
            "created": date.today().isoformat(),
            "description": "Automatically generated draft task; requires human audit.",
            "tags": [category, dataset_id, difficulty],
        },
        "datasets": [{"id": dataset_id, "name": name, "provider": provider, "asset": asset, "resolution": resolution}],
        "input": {"modality": "text", "platform": "gee", "dataset": asset, "prompt": PROMPTS[category].format(dataset=name, asset=asset)},
        "output": output,
        "evaluation": {
            "metrics": ["code_presence", "keyword_coverage"] if is_code else ["keyword_coverage"],
            "reasoning_level": "planning" if category == "planning" else "spatial" if category == "spatial_reasoning" else "temporal" if category in {"temporal", "change_detection"} else "analysis",
            "pass_score": 0.5,
        },
        "runtime": {"timeout": 120, "max_tokens": 4096, "temperature": 0.0},
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="tasks/core150")
    args = parser.parse_args()
    target = Path(args.output)
    target.mkdir(parents=True, exist_ok=True)
    for i in range(1, 151):
        (target / f"task{i:03d}.yaml").write_text(yaml.safe_dump(make_task(i), sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(f"Generated 150 draft tasks in {target}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
