# MMGIS-Bench v1.2.0

Reproduction package for the PLOS ONE revision of “MultiModal-GISAgent: workflow synthesis, scale-conditioned reasoning, and evidence-aware visual interpretation” (PONE-D-26-39341).

## Contents

| Item | Contents |
|---|---|
| `S1_Code_v1.2.0.zip` | Revision code: benchmark, LASR prompt-policy variants, weight-sensitivity runner, evaluator, configs |
| `S2_LASR_Ablation_v1.2.0.zip` | 35 tasks × 4 conditions = 140 task-condition rows; three paired contrasts |
| `S3_LASR_Weight_Sensitivity_v1.2.0.zip` | 35 tasks × 11 settings = 385 task-level records; 10 paired comparisons |
| `S4_M025_FINAL_EVIDENCE.zip` | M025 inputs, outputs, ratings and adjudication history |
| `S5_LEGACY35_REANALYSIS.zip` | Legacy35 reanalysis |
| `S6_HANOI_NDVI_AUDIT.zip` | Hanoi NDVI summaries, histogram and manifest |
| `S7_E1_pilot_v1_1.zip` | Execution-level equivalence pilot |
| `S8_GEE_task_provenance.json` | Read-only GEE task provenance |
| `S9_Annotation_Agreement.zip` | Annotation labels, vocabulary and bootstrap CI |
| `S10_Landcover_Common_Support.zip` | WorldCover/MODIS common-support comparison |

## Key results documented

- Primary benchmark: 35 tasks × 5 backends × 3 runs = 525 responses.
- LASR ablation: Full 0.568, single-scale 0.559, pooled-context 0.596, retrieval-only 0.558; all Holm p = 1.000.
- Weight sensitivity: reference 0.547 (95% CI 0.451–0.638); grid 0.515–0.587; 0/10 Holm-significant.
- Annotation agreement: 770 pairs; Cohen's κ = 0.6911 (95% CI 0.627–0.748).
- Hanoi NDVI: 12,080,126 finite cells; mean 0.3581, median 0.3671, SD 0.2275.
- Land-cover: 12,216,988 common-support pixels; agreement 0.395; κ = 0.216.

## Important implementation boundary

The LASR code implements the scale partition as a prompt-level policy. The six compatibility terms in the manuscript define the intended semantics; they are not separately calibrated numeric predictors in the released ablation. The ablation and weight-sensitivity experiments are separate cohorts: the former averages three repeats per task, whereas each weight setting is run once per task.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q
```

## Citation and DOI

Concept DOI (all versions): https://doi.org/10.5281/zenodo.23654896  
The version DOI for this release is assigned by Zenodo on publication. Cite the version DOI in the manuscript after publication.

## License

Apache License 2.0; see `LICENSE`. Third-party datasets and services retain their own terms.
