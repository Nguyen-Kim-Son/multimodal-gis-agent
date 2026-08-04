# Release 0.6.0

Release 0.6 integrates the attached ContextGeo 150-task benchmark into the reproducible MMGIS-Bench runner.

## Added

- exact preservation of the 150 source questions
- original difficulty, dataset, type, and expected-operation metadata
- operation-level ground truth
- operation alias ontology
- `operation_coverage` metric
- `workflow_order` metric
- no ground-truth leakage into prompts
- 150 validated YAML tasks in `tasks/contextgeo150`
- 10-task stratified pilot in `tasks/contextgeo_pilot`
- source import and audit scripts
- historical baseline artifacts retained as reference-only
- OpenRouter pilot and full-150 experiment configurations

## Validate the imported benchmark

```powershell
python scripts/check_dataset.py tasks/contextgeo150
python scripts/audit_contextgeo_ground_truth.py tasks/contextgeo150
```

## Rebuild from the attached source JSON

```powershell
python scripts/import_contextgeo150.py `
  --source data/contextgeo/tasks_150.json `
  --output tasks/contextgeo150
```

## Run a free OpenRouter pilot

Ensure `.env` contains `OPENROUTER_API_KEY`, then:

```powershell
python scripts/run_experiment_matrix.py `
  --config configs/contextgeo_openrouter_pilot.yaml
```

Build the report:

```powershell
python scripts/build_experiment_report.py `
  --latest `
  --experiments-root outputs/experiments `
  --output reports/contextgeo_openrouter_pilot
```

## Full 150-task run

Edit `configs/contextgeo_full150.yaml` to enable the desired model, then run:

```powershell
python scripts/run_experiment_matrix.py `
  --config configs/contextgeo_full150.yaml
```

Start with one repeat because free API quotas may be limited. Resume is enabled.


## Source limitation disclosed

Although the source has 150 task records, it contains 35 unique question patterns repeated across task IDs. The full imported set preserves those records exactly; the pilot selection deduplicates prompts.
