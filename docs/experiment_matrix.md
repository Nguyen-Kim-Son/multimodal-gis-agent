# Multi-model experiment matrix

Release 0.4.0 adds repeated, configuration-driven experiments for fair baseline comparison.

## Configure models

Edit `configs/experiment_matrix.yaml`.

Enable only models for which the runtime and credentials are available:

```yaml
models:
  qwen_ollama:
    enabled: true
    provider: ollama
    model: qwen2.5-coder:7b
```

API keys belong in `.env`, never in YAML or Git:

```text
OPENROUTER_API_KEY=...
DEEPSEEK_API_KEY=...
DASHSCOPE_API_KEY=...
```

## Run the matrix

```powershell
python scripts/run_experiment_matrix.py --config configs/experiment_matrix.yaml
```

The command prints the timestamped experiment directory. It contains:

- `manifest.json`
- model/repeat-specific `results.jsonl`
- combined `matrix_results.jsonl`

## Build comparison reports

```powershell
python scripts/build_experiment_report.py `
  outputs/experiments/pilot_baseline_comparison_<TIMESTAMP>/matrix_results.jsonl `
  --output reports/pilot_baseline_comparison
```

Generated outputs:

- `all_runs.csv`
- `task_aggregates.csv`
- `model_summary.csv`
- `category_summary.csv`
- `summary.json`
- `model_comparison.tex`

## Recommended publication protocol

1. Freeze and archive the reviewed task set.
2. Record the exact model identifiers and access dates.
3. Use the same task order, system prompt, temperature, token limit, and timeout.
4. Run at least three repeats for nondeterministic hosted models.
5. Report failures rather than silently retrying until success.
6. Report task-level, category-level, and overall results.
7. Separate execution-based scores from text-similarity scores.
8. Preserve raw JSONL outputs for reproducibility.
