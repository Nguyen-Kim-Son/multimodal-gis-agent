from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class ExperimentConfigError(ValueError):
    pass


def load_experiment_config(
    path: str | Path,
) -> dict[str, Any]:
    config_path = Path(path)

    if not config_path.is_file():
        raise FileNotFoundError(config_path)

    raw = yaml.safe_load(
        config_path.read_text(encoding="utf-8")
    )

    if not isinstance(raw, dict):
        raise ExperimentConfigError(
            "Experiment configuration must be a mapping."
        )

    if "experiment" not in raw:
        raise ExperimentConfigError(
            "Missing experiment section."
        )

    if "models" not in raw or not isinstance(raw["models"], dict):
        raise ExperimentConfigError(
            "Missing models mapping."
        )

    return raw
