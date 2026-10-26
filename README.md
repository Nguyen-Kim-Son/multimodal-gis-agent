# MultiModal-GISAgent / MMGIS-Bench

[![Tests](https://github.com/Nguyen-Kim-Son/multimodal-gis-agent/actions/workflows/tests.yml/badge.svg)](https://github.com/Nguyen-Kim-Son/multimodal-gis-agent/actions/workflows/tests.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)

A reproducible benchmark and experiment toolkit for evaluating multimodal GIS agents, geospatial language models, spatial-reasoning workflows, and code-generating systems on Google Earth Engine–oriented tasks.

**Repository:** <https://github.com/Nguyen-Kim-Son/multimodal-gis-agent>  
**Archived revision release:** <https://doi.org/10.5281/zenodo.23654897> (v1.1.0)

This repository contains the benchmark code (the original S1 code artifact) together with the revision evidence archives **S2–S10** at the repository root. The revision archives document the additional analyses reported in the manuscript; they are not required for the basic benchmark smoke test.

## Research scope

The repository supports two complementary benchmark views:

1. **35 unique tasks** (`tasks/contextgeo_unique35`) — the primary statistical unit.
2. **150 task instances** (`tasks/contextgeo150`) — a robustness/sensitivity set containing 35 recurring prompt templates. These are not 150 independent questions and must not be treated as such.

The benchmark covers spatial query, spatial analysis, raster analysis, data integration, spatial reasoning, and three difficulty levels. Recorded outcomes include answer quality, pass/fail status, operation precision/recall/F1, workflow order, hallucinated-operation rate, latency, token use, failure rate, and API cost.

The revision evidence adds:

- a controlled LASR ablation (420 runs) and 11-setting weight-sensitivity analysis;
- the M025 visual-study archive (60 image-input responses);
- the legacy35 reanalysis;
- a full-raster Hanoi NDVI audit;
- a five-task execution-level equivalence pilot;
- an annotation-agreement analysis;
- a WorldCover/MODIS common-support comparison;
- a read-only GEE task-provenance record.

## Repository layout

```text
.
├── audit/                       # Task-quality auditing and review utilities
├── benchmark/                   # Runner, caching, and result records
├── configs/                     # Reproducible experiment configurations
├── contextgeo_import/           # Import/conversion logic and provenance
├── data/contextgeo/             # Source task specification and import manifest
├── docs/                        # Protocols, schemas, provenance and data sources
├── evaluation/                  # Automatic metrics and operation matching
├── experiments/                 # Multi-model matrix and aggregate reports
├── gee/                         # Optional Google Earth Engine execution
├── models/                      # Mock, OpenRouter, Ollama and compatible adapters
├── prompts/                     # Versioned system prompts
├── scripts/                     # CLI utilities
├── tasks/                       # YAML benchmark task sets
├── tests/                       # Unit and integration tests
├── S2_S3_LASR_Source_Data.zip   # LASR ablation and weight-sensitivity evidence
├── S4_M025_FINAL_EVIDENCE.zip   # M025 inputs, outputs, ratings and adjudication
├── S5_LEGACY35_REANALYSIS.zip   # Legacy35 reanalysis
├── S6_HANOI_NDVI_AUDIT.zip      # Hanoi NDVI summaries and raster audit
├── S7_E1_pilot_v1_1.zip         # Execution-level equivalence pilot
├── S8_GEE_task_provenance.json  # GEE task query record
├── S9_Annotation_Agreement.zip  # Annotation labels, vocabulary and kappa
├── S10_Landcover_Common_Support.zip
├── run_benchmark.py
├── pyproject.toml
├── requirements.txt
├── CITATION.cff
└── README.md
```

Generated outputs, reports, logs, caches, credentials and virtual environments are excluded from version control. The root-level `S2–S10` archives are intentionally tracked evidence, not generated outputs.

## Revision evidence map

| Archive | Contents | Analysis |
|---|---|---|
| `S2_S3_LASR_Source_Data.zip` | Task-level means, paired contrasts, 11 weight settings, summaries | Controlled LASR ablation and weight sensitivity |
| `S4_M025_FINAL_EVIDENCE.zip` | M025 inputs, raw outputs, ratings, adjudication history | One-intent visual study; MAP and GRAPHIC tracks analysed separately |
| `S5_LEGACY35_REANALYSIS.zip` | Legacy35 task means, paired comparisons, bootstrap outputs | Reanalysis of the 35-task benchmark |
| `S6_HANOI_NDVI_AUDIT.zip` | NDVI statistics, histogram, scene list, raster audit | Full-raster internal-consistency audit |
| `S7_E1_pilot_v1_1.zip` | Ten pilot records, generated code, hashes | Five-task execution-level equivalence pilot |
| `S8_GEE_task_provenance.json` | Read-only GEE task query | Task provenance; it does not by itself prove a task-to-TIFF chain |
| `S9_Annotation_Agreement.zip` | Per-task annotations, 22-operation vocabulary, adjudication, bootstrap CI | Pre-adjudication inter-annotator agreement |
| `S10_Landcover_Common_Support.zip` | Common-support matrix, crosswalk, summary table | Product-to-product agreement, not independent accuracy |

The archives contain their own README files. Read the relevant README before using a package, especially for field definitions and known limitations.

## Installation

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

Add only the credentials required by the backend you intend to use:

```dotenv
OPENROUTER_API_KEY=
OPENAI_API_KEY=
DEEPSEEK_API_KEY=
DASHSCOPE_API_KEY=
GEE_PROJECT=
```

Never commit `.env`, service-account JSON, API keys, or raw provider payloads.

## Validate the release

```bash
python -m pytest
python scripts/check_dataset.py tasks/contextgeo_unique35
python scripts/check_dataset.py tasks/contextgeo150
```

## Smoke test without paid APIs

```bash
python run_benchmark.py \
  --model mock \
  --tasks tasks/examples \
  --output outputs/mock_run

python scripts/build_report.py \
  outputs/mock_run/results.jsonl \
  --output reports/mock_run
```

## Primary 35-task experiment

The primary configuration is `configs/paper_unique35.yaml`. It uses 35 unique tasks, three repeats, disabled cache, and resumable execution.

```bash
python scripts/preflight_openrouter_models.py \
  --config configs/paper_unique35.yaml

python scripts/estimate_paper_cost.py \
  --config configs/paper_unique35.yaml \
  --budget 10

python scripts/run_experiment_matrix.py \
  --config configs/paper_unique35.yaml
```

Expected matrix path:

```text
outputs/experiments/mmgis_paper_unique35_paper_unique35_v1/matrix_results.jsonl
```

Build the standard and paper-oriented reports:

```bash
python scripts/build_experiment_report.py \
  outputs/experiments/mmgis_paper_unique35_paper_unique35_v1/matrix_results.jsonl \
  --output reports/paper_unique35

python scripts/build_paper_report.py \
  reports/paper_unique35/all_runs.csv \
  --output reports/paper_unique35/paper
```

## 150-instance robustness analysis

```bash
python scripts/run_experiment_matrix.py \
  --config configs/paper_full150_robustness.yaml
```

The 150 records reuse 35 prompt templates. Report them as a sensitivity analysis, not as 150 independent task formulations.

## Working with S2–S10

Extract the revision archives locally. Do not commit extracted files or generated outputs.

```bash
mkdir -p evidence

unzip -q S2_S3_LASR_Source_Data.zip      -d evidence/S2_S3
unzip -q S4_M025_FINAL_EVIDENCE.zip      -d evidence/S4
unzip -q S5_LEGACY35_REANALYSIS.zip      -d evidence/S5
unzip -q S6_HANOI_NDVI_AUDIT.zip         -d evidence/S6
unzip -q S7_E1_pilot_v1_1.zip            -d evidence/S7
unzip -q S9_Annotation_Agreement.zip     -d evidence/S9
unzip -q S10_Landcover_Common_Support.zip -d evidence/S10
mkdir -p evidence/S8
cp S8_GEE_task_provenance.json evidence/S8/
```

Then follow the README in each archive. The evidence packages are self-contained with respect to derived tables and scripts; the original GEE rasters and credentials are not redistributed.

## What the revision evidence shows

- **Primary benchmark:** 35 tasks × 5 backends × 3 runs = 525 responses. Gemma 4 26B A4B and Qwen3-Coder were closely matched (mean composite 0.562 vs 0.557); the difference was not statistically significant.
- **LASR ablation:** full LASR did not outperform single-scale, pooled-context or retrieval-only controls after Holm correction. The 11-setting weight analysis did not identify the prespecified weights as superior.
- **M025:** 60 image-input responses across separate MAP and GRAPHIC tracks. Nine MAP responses reached the output limit; tracks are reported separately and no cross-track composite is defined.
- **Execution pilot:** 10/10 candidate runs matched reference values within prespecified tolerances. This is feasibility evidence, not corpus-level equivalence.
- **Annotation agreement:** 770 binary pairs; Cohen's κ = 0.6911 (95% CI 0.627–0.748).
- **Hanoi NDVI:** 12,080,126 finite cells; mean 0.3581, median 0.3671, SD 0.2275. The audit establishes internal consistency of the supplied raster, not acquisition-to-TIFF provenance.
- **Land-cover:** 12,216,988 common-support pixels; overall agreement 0.395 and κ = 0.216. This is product-to-product agreement, not independent classification accuracy.
- **GEE provenance:** five COMPLETED HANOI/NDVI tasks. The record supports task retrieval but does not by itself establish a one-to-one task-to-file chain.

## Reproducibility rules

For a valid comparison, every model must use the same:

- task files and task ordering;
- prompt template;
- decoding settings;
- retry and timeout policy;
- evaluator and alias definitions;
- pass threshold;
- aggregation method.

Record API/provider failures separately; they are not model-quality failures. Archive raw responses and immutable configurations with any published result.

## Google Earth Engine data

Live workflows use Sentinel-2 surface reflectance, SRTM DEM, JRC Global Surface Water, GHSL population, ESA WorldCover, MODIS NDVI, FAO GAUL, Hansen forest change, and CHIRPS precipitation. NASA EONET is accessed through its public API.

Collection identifiers and access dates are documented in `docs/data_sources.md` and in the manuscript. Third-party source data are not redistributed; users retrieve them from the original providers under the applicable terms.

## Data and code availability

- Code: this repository, Apache License 2.0.
- Archived revision release: <https://doi.org/10.5281/zenodo.23654897>.
- Revision evidence: `S2–S10` at the repository root.
- GEE credentials, API keys, and the full Hanoi GeoTIFF are not included. The GeoTIFF checksum and derived audit tables are provided in `S6_HANOI_NDVI_AUDIT.zip`.

## Citation

Citation metadata are in [`CITATION.cff`](CITATION.cff). Cite the software release and the associated article. The archived v1.1.0 release has DOI `10.5281/zenodo.23654897
        
        `.

## License

The repository source code is released under the [Apache License 2.0](LICENSE). Third-party datasets, services, pretrained models, and imported benchmark materials remain subject to their respective licenses and terms. Check the README inside each S2–S10 archive for package-specific notes.

## Security

Do not commit `.env`, API keys, service-account JSON files, private datasets, virtual environments, or outputs containing sensitive prompts. See [`SECURITY.md`](SECURITY.md).

## Versioning

- `v1.0.0` is the original benchmark/code release.
- `v1.1.0` is the revision evidence release archived at Zenodo.
- Do not move or rewrite historical tags. Create a new tag for later changes.
