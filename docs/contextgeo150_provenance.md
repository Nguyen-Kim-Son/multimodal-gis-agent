# ContextGeo150 provenance and ground truth

Version 1.0.0 imports the attached `ContextGeo-main/data/tasks_150.json` without replacing its task wording or taxonomy.

## Source-supported structure

The source contains 150 tasks with:

- 50 easy tasks
- 60 medium tasks
- 40 hard tasks

Task types:

- 50 `spatial_query`
- 40 `spatial_analysis`
- 20 `raster_analysis`
- 20 `data_integration`
- 20 `spatial_reasoning`

Datasets:

- 45 OSM tasks
- 45 Census tasks
- 20 Sentinel-2 tasks
- 40 multi-source tasks

The source ground truth is `expected_operations`. It does **not** provide a universal exact numeric result for every question. Version 1.0.0 therefore evaluates operation coverage and workflow ordering. It does not silently invent numeric answers.

## Leakage prevention

Expected operations are stored only under `output.expected_operations` and are never inserted into the model prompt or system prompt.

## Historical results

The attached project also contains historical result artifacts for ContextGeo and three baselines. Version 1.0.0 preserves those files under `data/contextgeo/reference_results/`.

They are labelled reference-only because their model, prompt, data, runtime, and scoring protocol may differ from new MMGIS-Bench runs.


## Question-pattern duplication

The attached source contains 150 task instances but 35 unique question strings. Each unique question is repeated across multiple source task IDs, with a maximum repetition of five. Version 1.0.0 preserves all 150 instances for provenance and reports this explicitly in `reports/contextgeo_ground_truth_audit.json`.

The generated `tasks/contextgeo_pilot` set removes duplicate question strings so a pilot run does not spend API quota on identical prompts.
