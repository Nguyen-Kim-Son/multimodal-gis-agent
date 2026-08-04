from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_reference_results(
    root: str | Path = "data/contextgeo/reference_results",
) -> dict[str, Any]:
    root = Path(root)

    contextgeo_path = root / "contextgeo/experiment_results.json"
    baselines_path = root / "baselines/experiment_results.json"

    return {
        "contextgeo": json.loads(
            contextgeo_path.read_text(encoding="utf-8")
        ),
        "baselines": json.loads(
            baselines_path.read_text(encoding="utf-8")
        ),
        "warning": (
            "These are historical reference artifacts from the attached "
            "ContextGeo project. They are not directly comparable with new "
            "MMGIS-Bench runs unless models, prompts, data, runtime, and "
            "evaluation protocols are matched."
        ),
    }
