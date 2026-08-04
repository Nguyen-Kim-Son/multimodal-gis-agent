# Release 0.4.0

This release completes the baseline-experiment layer.

## Added

- generic OpenAI-compatible API adapter
- model factory
- YAML experiment matrix
- repeated runs
- timestamped experiment manifests
- task-level aggregation
- 95% confidence intervals
- model/category comparison CSV reports
- LaTeX model-comparison table

## Remaining research work

The software pipeline is complete enough to run experiments, but the scientific benchmark is not complete until:

- all tasks are manually reviewed
- ground-truth code is executed and verified
- multimodal assets are supplied for multimodal tasks
- baseline model versions are frozen
- evaluation metrics are validated against human judgments
