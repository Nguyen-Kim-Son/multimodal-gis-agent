# MMGIS-Bench paper experiment protocol

## Recommended main model set

The main comparison uses five complementary models:

1. `openai/gpt-oss-20b:free` — free open-weight baseline.
2. `google/gemma-4-26b-a4b-it:free` — efficient free instruction baseline.
3. `openai/gpt-5-mini` — compact proprietary general/reasoning baseline.
4. `google/gemini-2.5-flash` — reasoning-focused high-throughput baseline.
5. `qwen/qwen3-coder` — code and tool-use baseline.

`anthropic/claude-sonnet-4` is optional because it is substantially more expensive. Run it once on the unique-35 set if the remaining balance is sufficient.

## Scientific design

### Main experiment

- Dataset: `tasks/contextgeo_unique35`
- Models: five-model main set
- Repeats: 3
- Temperature: 0
- Cache: disabled
- Resume: enabled
- Unit of analysis: unique question
- Report: mean, pass rate, 95% bootstrap confidence interval, latency, tokens, and cost

### Robustness experiment

- Dataset: `tasks/contextgeo150`
- Models: GPT-5 Mini, Gemini 2.5 Flash, and Qwen3 Coder
- Repeats: 1
- Purpose: test whether conclusions remain similar when all source records are retained
- Limitation: the 150 records contain only 35 unique question patterns and are not independent observations

## Execution order

```powershell
python scripts/preflight_openrouter_models.py `
  --config configs/paper_unique35.yaml

python scripts/estimate_paper_cost.py `
  --config configs/paper_unique35.yaml `
  --budget 9.91

python scripts/run_experiment_matrix.py `
  --config configs/paper_unique35.yaml
```

Build the standard report:

```powershell
python scripts/build_experiment_report.py `
  outputs/experiments/mmgis_paper_unique35_paper_unique35_v1/matrix_results.jsonl `
  --output reports/paper_unique35
```

Build the paper-ready report:

```powershell
python scripts/build_paper_report.py `
  reports/paper_unique35/all_runs.csv `
  --output reports/paper_unique35/paper
```

## Before running

- Verify every enabled model has at least one OpenRouter endpoint.
- Save the preflight CSV.
- Save the cost estimate.
- Record the UTC start date.
- Do not alter the tasks, aliases, prompts, temperature, or evaluator between models.
- Do not count API failures as model-quality failures.
- Preserve raw `results.jsonl` files.

## Optional Claude run

```powershell
python scripts/preflight_openrouter_models.py `
  --config configs/paper_claude_unique35.yaml

python scripts/estimate_paper_cost.py `
  --config configs/paper_claude_unique35.yaml `
  --budget 9.91

python scripts/run_experiment_matrix.py `
  --config configs/paper_claude_unique35.yaml
```

Merge the Claude records with the main matrix only after verifying that task IDs, prompts, evaluator version, and temperature match.
