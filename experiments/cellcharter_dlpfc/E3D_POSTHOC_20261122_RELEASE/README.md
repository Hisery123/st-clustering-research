# E3d 12 DLPFC slices × 4 K-blind CellCharter scales: posthoc ARI/NMI results

**Actual computed results, NOT pre-registered evaluation performed at E3d run time.** This new evaluation was run after the model stage was fully finished and the researcher had viewed other datasets' results. The original AutoK K selection remains completely **label-blind and frozen**; there were **zero refits and no hyperparameter changes**.

## Original-data evidence and independent arithmetic check

Input was the user's SHA-verifiable `e3d_posthoc_inputs_20261122.zip` (SHA256 `1f3e55c1acbf9162998a1a3e198c26284c8a63f7784ab8b28088220e2e148094`) containing 48 unchanged prediction CSVs, 12 spots/coords files, 12 original manual annotation CSVs, and a source-file SHA256 manifest (72 input CSVs). Every source file SHA passed. Predictions' SHA and frozen K stability argmax matched [the original E3d audit](../E3D_20261122_RELEASE/derived/all_48_autok_audit.csv). All 12 label file and spot order SHA values matched historical [E1/E2 full audit CSV](../E1E2_20261119_RELEASE/derived/all_1200_tasks.csv). Original reference masks were not changed. All 48 sklearn ARI and NMI values were independently reproduced using explicit contingency-table formulas (difference < 1e-10), 48/48 PASS.

**Original input ZIP is not included in this GitHub release; the 48 source predictions / raw reference labels remain on the user's Windows system or uploaded conversation, while their SHA256 values and derived scores can be checked here.** The source ZIP is not a novel source of labels, and the results cannot be rebuilt from these derived CSVs alone without retrieving it.

## Readable results

| Scale | Mean ARI, 12 slices | Mean NMI, 12 slices |
|---|---:|---:|
| 10D L0+L1 | 0.379285 | 0.503341 |
| 15D L0+L1+L2 | 0.386114 | 0.535941 |
| 20D L0+L1+L2+L3 | 0.431145 | 0.594212 |
| 25D L0+L1+L2+L3+L4 | 0.388976 | 0.543449 |

Mean values are arithmetic means across **12 nested slices**, NOT results from n=12 independent biological replicates. Only **3 independent donors** exist, four slices each; no p-values or naive slice-independent CIs are used. The 20D condition has the highest descriptive average in this data, but this does not imply a statistically superior or universally optimal scale. AutoK can select different K across scales and samples; effects mix representation and changed K. The original AutoK search hits its K2..10 boundary 10/48 times and those cases remain included.

## Derived data and code

- [48 exact posthoc scores](derived/all_48_posthoc_ari_nmi.csv) with selected K, mask sizes, provenance SHA and label categories.
- [48 per-slice paired contrasts](derived/all_48_paired_slice_effects.csv) for 15D−10D, 20D−15D, 25D−20D, 25D−15D (both metrics, negative values retained).
- [Four scale means and heterogeneity](derived/four_scale_descriptives.csv), [three-donor per-scale means](derived/three_donor_scale_summary.csv).
- [Posthoc full integrity report](derived/posthoc_audit_report.json), [reproducible posthoc metric program](e3d_posthoc_evaluate_v1.py).
- See [manifest](manifest.json) for full input source SHA and exact output file SHA.

**Next**: E3b spatial boundary sensitivity is separate and cannot be inferred from ARI/NMI. The frozen 1200-prediction E1/E2 strict/tolerant edge audit remains an independent task.
