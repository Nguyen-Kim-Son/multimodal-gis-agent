from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any

import requests
import yaml
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def endpoint_url(base_url: str, model_id: str) -> str:
    author, slug = model_id.split("/", 1)
    return f"{base_url.rstrip('/')}/models/{author}/{slug}/endpoints"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check OpenRouter model existence and endpoint availability."
    )
    parser.add_argument(
        "--config",
        default="configs/paper_unique35.yaml",
    )
    parser.add_argument(
        "--output",
        default="reports/openrouter_preflight.csv",
    )
    args = parser.parse_args()

    load_dotenv(PROJECT_ROOT / ".env")
    key = os.getenv("OPENROUTER_API_KEY")

    if not key:
        raise SystemExit("OPENROUTER_API_KEY is missing from .env")

    config = yaml.safe_load(
        (PROJECT_ROOT / args.config).read_text(encoding="utf-8")
    )
    headers = {"Authorization": f"Bearer {key}"}
    rows: list[dict[str, Any]] = []

    for model_key, model in config["models"].items():
        if not model.get("enabled", True):
            continue

        model_id = str(model["model"])
        base_url = str(
            model.get("base_url", "https://openrouter.ai/api/v1")
        )

        try:
            response = requests.get(
                endpoint_url(base_url, model_id),
                headers=headers,
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()["data"]
            endpoints = data.get("endpoints") or []

            rows.append(
                {
                    "model_key": model_key,
                    "model": model_id,
                    "exists": True,
                    "endpoint_count": len(endpoints),
                    "available": len(endpoints) > 0,
                    "providers": "; ".join(
                        str(endpoint.get("provider_name") or endpoint.get("name"))
                        for endpoint in endpoints
                    ),
                    "error": "",
                }
            )
        except Exception as exc:
            rows.append(
                {
                    "model_key": model_key,
                    "model": model_id,
                    "exists": False,
                    "endpoint_count": 0,
                    "available": False,
                    "providers": "",
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )

    import pandas as pd

    output = PROJECT_ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(rows)
    frame.to_csv(output, index=False)
    print(frame.to_string(index=False))
    print(f"Saved: {output}")

    return int((~frame["available"]).any()) if not frame.empty else 1


if __name__ == "__main__":
    raise SystemExit(main())
