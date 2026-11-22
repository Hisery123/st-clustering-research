# E3b full E1/E2 1200-prediction strict boundary and 1/2-hop tolerance analysis

**Status: completed and SHA-audited, 2026-11-22.** This is a **new, explicitly post-hoc evaluation**, based on 1,200 previously frozen E1/E2 prediction files, all of which passed user-Windows verification and an independent 1,200/1,200 SHA and barcode check from the uploaded 28,988,158-byte ZIP (see [manifest.json](manifest.json)). **No model was refitted, selected K was not modified, and no row was excluded.**

This is distinct from the [E3d 48-prediction K-blind boundary posthoc analysis](../E3B_E3D48_POSTHOC_20261122_RELEASE/). **E1/E2 uses reference-category-count-informed Oracle-K**, so its scores must never be described as K-blind performance.

## Reproducible files

- [All 3,600 task × tolerance-level metric rows](derived/all_3600_boundary_metric_rows.csv) — all 1,200 source predictions, for **strict 0-hop**, **1-hop**, **2-hop**; prediction/reference file SHA, TP, FP, FN, precision, recall, F1.
- [All 1,200 task-wise paired threshold rows](derived/all_1200_paired_strict_tolerance.csv) — strict and tolerant F1 values on identical prediction.
- [Nested slice and seed summaries, 360 rows](derived/slice_mean_360.csv).
- [Three-donor summaries, 90 rows](derived/donor_mean_90.csv). Each donor has four related sections.
- [Descriptive 12-slice macro means, 30 rows](derived/macro_mean_30.csv).
- [Source SHA256 ledger for ALL 1,200 original prediction CSVs](derived/source_prediction_sha256_1200.csv) — copied **byte-for-byte** from the uploaded Windows ZIP, including UTF-8 BOM and Windows line endings.
- [Full programmatic evaluation audit report](derived/posthoc_boundary_audit_report.json), [read-only evaluator](e3b_e1e2_1200_boundary_posthoc_v1.py), [plot script](e3b_e1e2_1200_plot_v1.py), and two editable SVGs: [all ten configs / three thresholds](derived/E3B_E1E2_1200_all_config_0_1_2hop.svg), [three donors / strict F1](derived/E3B_E1E2_1200_donor_strict_f1.svg).

## Twelve-section equal-weight descriptive F1

| Config | Strict 0-hop | 1-hop | 2-hop |
|---|---:|---:|---:|
| L0 (5D) | 0.1441 | 0.2621 | 0.2863 |
| L0+L1 (10D) | 0.1446 | 0.3369 | 0.4116 |
| L0–L2 (15D) | 0.1361 | 0.3559 | 0.4838 |
| L0–L3 (20D) | 0.1344 | 0.3614 | 0.5223 |
| L0–L4 (25D) | **0.1179** | 0.3457 | **0.5333** |
| fixed L0+L1+L3 | 0.1341 | 0.3544 | 0.4910 |
| fixed L0+L1+L4 (B15D) | 0.1309 | 0.3478 | 0.4856 |
| fixed L0+L2+L3 | 0.1310 | 0.3346 | 0.4682 |
| fixed L0+L2+L4 | 0.1237 | 0.3248 | 0.4700 |
| fixed L0+L3+L4 | 0.1297 | 0.3308 | 0.4619 |

All these means are **descriptive across 12 nested slices**, internally averaging 10 technical seeds per slice. They are not 1,200 independent biological replicates or a 12-donor significance test. Independent biological sample size is **n=3 donors**. No post-hoc p-values or selective best-seed tests performed.

The particularly important *negative/tradeoff result* is that L0–L4 produces the highest 2-hop tolerant mean (0.5333) but the **lowest strict F1 among these ten configurations** (0.1179). Thus spatial tolerance should not replace accurate boundary localization, and improving tolerance F1 does not show that exact reference layer boundaries are better detected.

## Exact boundary geometry and verification

- Valid graph: Visium hex six adjacency offsets (`(0,±2), (±1,±1)`) on `array_row,array_col`. Both endpoint spots need reference layer labels; no favorable trimming of difficult edges. Pixel distance distribution checked for every patient slice.
- Reference edge positive: its two annotation labels differ. Prediction positive: its two **original, unmodified** clustering IDs differ.
- Strict TP: intersection of both positive edge sets, no distance tolerance. One-hop and two-hop: line-graph distance between **valid edges** with maximum-cardinality **one-to-one bipartite matching**, disallowing counting one reference boundary multiple times. Precision, recall, TP/FP/FN for each threshold retained in full CSV.
- Historical independent strict TP cross-check: for seed 22911, full twelve-slice A15D total TP **2103**, B15D total TP **1999**, exactly equal to the old `chapter_04_results_integrated.tex` records. All 1,200 distinct prediction SHA and all twelve reference input SHA cross-checked.
- **Source original predictions are not part of this GitHub release**: the 28.99 MB user-uploaded ZIP `D:\paper\CellCharter_reproduction\results\e3b_e1e2_1200_export_20261122.zip` is retained on Windows. The full SHA manifest and all *derived* result rows are on GitHub. To recreate scores from predictions, supply this SHA-verified ZIP along with original E3d reference ZIP and [E3d posthoc provenance](../E3D_POSTHOC_20261122_RELEASE/).
- Users must distinguish this new post-hoc supplementary E3b result from the frozen pre-experiment protocol; thresholds do not define a pre-registered primary analysis.

## Files further pending elsewhere

E4 primary visualization SVG/CSV outputs were audited on Windows but their complete original source figure set has not yet been proven GitHub-archived. The publication novelty overlap audit with CellCharter original Supplement and revised manuscript Chapter 4 still need attention. This E3b release does not resolve those issues.
