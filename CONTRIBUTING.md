# Contributing

Contributions are welcome through GitHub issues and pull requests.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest
```

## Pull requests

1. Do not commit API keys, `.env`, generated outputs, caches, or virtual environments.
2. Add or update tests for behavioral changes.
3. Validate modified task sets with `scripts/check_dataset.py`.
4. Preserve task provenance and avoid changing ground truth solely to improve model scores.
5. Document changes that affect reported benchmark results.

## Reporting benchmark results

Use identical task files, prompts, decoding settings, metric code, and retry policies for all compared models. Infrastructure failures must be reported separately from model-quality failures.
