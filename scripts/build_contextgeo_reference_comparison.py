from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from contextgeo_import import load_reference_results


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Place historical ContextGeo reference results beside a new "
            "MMGIS-Bench model summary. Results are labelled as protocol-mismatched."
        )
    )
    parser.add_argument(
        "--new-summary",
        default=None,
        help="Optional Release 0.6 model_summary.csv.",
    )
    parser.add_argument(
        "--output",
        default="reports/contextgeo_reference_comparison.csv",
    )
    args = parser.parse_args()

    reference = load_reference_results()
    rows = []

    contextgeo = reference["contextgeo"]
    rows.append(
        {
            "source": "historical_contextgeo_artifact",
            "method": "ContextGeo",
            "task_completion_rate": contextgeo.get("tcr"),
            "tokens": contextgeo.get("tokens"),
            "time": contextgeo.get("time"),
            "spatial_accuracy": contextgeo.get("saa"),
            "comparable_protocol": False,
        }
    )

    for method, values in reference["baselines"].items():
        rows.append(
            {
                "source": "historical_contextgeo_artifact",
                "method": method,
                "task_completion_rate": values.get("tcr"),
                "tokens": values.get("tokens"),
                "time": values.get("time"),
                "spatial_accuracy": values.get("saa"),
                "comparable_protocol": False,
            }
        )

    if args.new_summary:
        frame = pd.read_csv(args.new_summary)
        for _, row in frame.iterrows():
            rows.append(
                {
                    "source": "mmgis_release_0_6",
                    "method": row["model_key"],
                    "task_completion_rate": row.get("pass_rate"),
                    "tokens": row.get("mean_total_tokens"),
                    "time": row.get("mean_latency_seconds"),
                    "spatial_accuracy": None,
                    "comparable_protocol": True,
                }
            )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(output, index=False)

    note = output.with_suffix(".json")
    note.write_text(
        json.dumps(
            {
                "warning": reference["warning"],
                "output": str(output),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"[ OK ] comparison: {output}")
    print(f"[ OK ] warning note: {note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
