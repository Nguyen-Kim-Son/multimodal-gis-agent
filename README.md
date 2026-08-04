# MultiModal-GISAgent / MMGIS-Bench v1.0.0

[![Tests](https://github.com/Nguyen-Kim-Son/multimodal-gis-agent/actions/workflows/tests.yml/badge.svg)](https://github.com/Nguyen-Kim-Son/multimodal-gis-agent/actions/workflows/tests.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](pyproject.toml)

A reproducible benchmark and experiment toolkit for evaluating multimodal GIS agents, geospatial language models, spatial reasoning workflows, and code-generating systems on Google Earth Engine–oriented tasks.

Repository: **https://github.com/Nguyen-Kim-Son/multimodal-gis-agent**

## Research scope

The repository supports two complementary forms of evaluation:

1. **A 35-question primary benchmark** (`tasks/contextgeo_unique35`) containing unique geospatial task formulations.
2. **A 150-instance robustness benchmark** (`tasks/contextgeo150`) preserving the source task instances and their difficulty/category structure.

The benchmark covers:

- spatial query;
- spatial analysis;
- raster analysis;
- data integration;
- spatial reasoning;
- easy, medium, and hard task levels.

The framework records answer quality, pass/fail status, operation precision and recall, operation F1, workflow order, hallucinated-operation rate, latency, token usage, failure rate, and API cost.

## Repository structure

```text
.
├── audit/                  # Task-quality auditing and review utilities
├── benchmark/              # Runner, caching, and result records
├── configs/                # Reproducible experiment configurations
├── contextgeo_import/      # Import/conversion logic and provenance
├── data/contextgeo/        # Source task specification and import manifest
├── docs/                   # Protocol, schema, provenance, and data sources
├── evaluation/             # Automatic metrics and operation matching
├── experiments/            # Multi-model matrix and aggregate reports
├── gee/                    # Optional Google Earth Engine code execution
├── models/                 # Mock, OpenRouter, Ollama, and compatible adapters
├── prompts/                # Versioned system prompts
├── scripts/                # CLI utilities
├── tasks/                  # YAML benchmark task sets
├── tests/                  # Unit and integration tests
├── run_benchmark.py        # Single-model benchmark CLI
├── pyproject.toml
└── requirements.txt
```

Generated outputs, reports, logs, caches, API keys, and virtual environments are deliberately excluded from version control.

## Installation

### Windows PowerShell

```powershell
git clone https://github.com/Nguyen-Kim-Son/multimodal-gis-agent.git
cd multimodal-gis-agent

python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

Copy-Item .env.example .env
```

### Linux/macOS

```bash
git clone https://github.com/Nguyen-Kim-Son/multimodal-gis-agent.git
cd multimodal-gis-agent

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

cp .env.example .env
```

Add only the credentials needed for the selected backend. Never commit `.env`.

```dotenv
OPENROUTER_API_KEY=
OPENAI_API_KEY=
DEEPSEEK_API_KEY=
DASHSCOPE_API_KEY=
GEE_PROJECT=
```

## Validate the release

```powershell
python -m pytest
python scripts/check_dataset.py tasks/contextgeo_unique35
python scripts/check_dataset.py tasks/contextgeo150
```

The release was packaged after the complete test suite passed.

## Local smoke test without paid APIs

```powershell
python run_benchmark.py `
  --model mock `
  --tasks tasks/examples `
  --output outputs/mock_run

python scripts/build_report.py `
  outputs/mock_run/results.jsonl `
  --output reports/mock_run
```

## Main paper experiment

The primary configuration is:

```text
configs/paper_unique35.yaml
```

It uses 35 unique tasks, three repeats, disabled cache, and resumable execution. Before running a paid or free OpenRouter experiment, check live endpoint availability and estimate cost:

```powershell
python scripts/preflight_openrouter_models.py `
  --config configs/paper_unique35.yaml

python scripts/estimate_paper_cost.py `
  --config configs/paper_unique35.yaml `
  --budget 10
```

Run the matrix:

```powershell
python scripts/run_experiment_matrix.py `
  --config configs/paper_unique35.yaml
```

The expected matrix path is:

```text
outputs/experiments/mmgis_paper_unique35_paper_unique35_v1/matrix_results.jsonl
```

Build the standard experiment report:

```powershell
python scripts/build_experiment_report.py `
  outputs/experiments/mmgis_paper_unique35_paper_unique35_v1/matrix_results.jsonl `
  --output reports/paper_unique35
```

Build paper-oriented tables:

```powershell
python scripts/build_paper_report.py `
  reports/paper_unique35/all_runs.csv `
  --output reports/paper_unique35/paper
```

## Full 150-instance robustness experiment

The 150 task records contain 35 unique question patterns. They are retained as a robustness/sensitivity set and should not be treated as 150 fully independent question formulations.

```powershell
python scripts/run_experiment_matrix.py `
  --config configs/paper_full150_robustness.yaml
```

See [`docs/contextgeo150_provenance.md`](docs/contextgeo150_provenance.md) before interpreting these results.

## Google Earth Engine data

Live workflows use real Google Earth Engine collections for Sentinel-2, SRTM, JRC surface water, GHSL population, ESA WorldCover, MODIS NDVI, FAO GAUL, Hansen forest change, and CHIRPS precipitation. NASA EONET is accessed through its public API rather than through GEE.

The exact identifiers, fixed study regions, access date, and author project metadata are documented in [`docs/data_sources.md`](docs/data_sources.md).

Third-party source data are not redistributed in this repository. Users retrieve them from the original providers under the applicable terms and licenses.

## Reproducibility rules

For a valid comparison, every model must use the same:

- task files and task ordering;
- prompt template;
- decoding settings;
- retry and timeout policy;
- evaluator and alias definitions;
- pass threshold;
- aggregation method.

API/provider failures are recorded separately and must not be interpreted as model-quality failures. Raw responses and immutable experiment configurations should be archived with any published result.

## Benchmark provenance

The source task specification is preserved in `data/contextgeo/tasks_150.json`. The importer retains the original wording, taxonomy, and operation-level ground truth. It does not invent missing numeric answers. Details are provided in [`docs/contextgeo150_provenance.md`](docs/contextgeo150_provenance.md).

## Citation

Citation metadata are provided in [`CITATION.cff`](CITATION.cff). After the associated paper and archival DOI are available, update this file and create a tagged GitHub release without rewriting the historical tag.

## License

The project source code is released under the [Apache License 2.0](LICENSE). Third-party datasets, services, pretrained models, and imported benchmark materials remain subject to their respective licenses and terms.

## Security

Do not commit `.env`, API keys, service-account JSON files, private datasets, virtual environments, outputs containing sensitive prompts, or provider response payloads. See [`SECURITY.md`](SECURITY.md).
