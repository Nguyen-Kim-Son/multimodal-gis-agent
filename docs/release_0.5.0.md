# Release 0.5.0

Release 0.5.0 hardens the experimental workflow for long-running and repeatable benchmark studies.

## Improvements

- report generation no longer requires Jinja2
- `--latest` automatically finds the newest experiment result
- benchmark runner resumes from existing JSONL results
- experiment matrices resume by model, repeat, and task
- stable `run_id` can be configured for long experiments
- structured logging to console and log files
- difficulty-level comparison report
- clearer file-not-found and empty-result errors

## Build the latest experiment report

```powershell
python scripts/build_experiment_report.py `
  --latest `
  --experiments-root outputs/experiments `
  --output reports/pilot_baseline_comparison
```

## Resume a long experiment

Set a stable run ID:

```yaml
experiment:
  run_id: reviewed_pilot_v1
  resume: true
```

Run the same command again after interruption. Completed model/repeat/task combinations are skipped.

## Start from scratch

Either change `run_id`, remove the existing run directory, or set:

```yaml
experiment:
  resume: false
```

For one-model runs, pass `--no-resume` to `run_benchmark.py`.
