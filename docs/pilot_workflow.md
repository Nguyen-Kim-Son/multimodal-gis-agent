# Pilot and task-audit workflow

The 150 automatically generated tasks are scaffolding, not publication-ready ground truth.

## 1. Generate and validate the draft set

```powershell
python scripts/generate_core150.py --output tasks/core150
python scripts/check_dataset.py tasks/core150
```

## 2. Create a balanced 20-task pilot

```powershell
python scripts/create_pilot.py tasks/core150 --output tasks/pilot20 --per-category 2
```

## 3. Run automatic audit checks

```powershell
python scripts/audit_tasks.py tasks/pilot20 --output reports/task_audit
```

The audit creates:

- `audit.json`: machine-readable errors and warnings
- `review_sheet.csv`: manual-review worksheet

## 4. Manually review

Open `reports/task_audit/review_sheet.csv`. For every task:

- verify the dataset asset
- rewrite generic prompts
- replace template ground truth with a defensible answer or executable script
- verify metric suitability
- set `review_status` to `approved` only after review
- add reviewer and notes

## 5. Promote approved tasks

```powershell
python scripts/select_reviewed_tasks.py tasks/pilot20 --review-sheet reports/task_audit/review_sheet.csv --output tasks/reviewed_pilot
```

## 6. Run model experiments

Start with the mock adapter, then a local/free model, then paid models:

```powershell
python run_benchmark.py --model mock --tasks tasks/reviewed_pilot --output outputs/mock_reviewed
python run_benchmark.py --model ollama --model-name qwen2.5-coder:7b --tasks tasks/reviewed_pilot --output outputs/qwen_reviewed
```

Do not run the full 150-task paid experiment until the pilot has been reviewed and the evaluation logic has been inspected.
