# E3b spatial boundary tolerance: E3d K-blind 48-grid *partial* posthoc analysis

## 2026-11-22 补充结果完成后状态更新

在本文件最初撰写后，**E1/E2完整1200份Oracle-K冻结预测**也已使用相同图拓扑及一对一匹配法完成全量事后边界分析：1200个任务×严格0-hop/1-hop/2-hop＝3600项完整评价；全部源预测SHA校验PASS，独立历史A/B严格TP总数分别2103/1999完全吻合。GitHub完整结果见[ E3B_E1E2_1200_POSTHOC_20261122_RELEASE ](E3B_E1E2_1200_POSTHOC_20261122_RELEASE/)；前一阶段E3d48仅是**另一份K-blind补充评估**，不可把两者混为同一K选取设定。全部源28.99MB ZIP保留于Windows，仅derived完整指标和1200源文件SHA在GitHub；原文中的“尚未完成1200份”是历史状态。所有新增分析均为已见指标后的**post-hoc**，不是原实验预注册结果。


**This is an actual completed analysis, but it is explicitly a partial (48 frozen E3d K-blind predictions) E3b supplement. It does NOT cover the originally planned E1/E2 1200 prediction files.** The 48 predictions were generated and audited on Windows before this analysis. This new evaluation reused unchanged outputs, selected K and reference annotations; **0 model refits**.

## Boundary definition, an important geometry point

The spatial graph uses original Visium `array_row,array_col` positions with the six immediate offsets `(0,±2),(±1,±1)`. The alternative `(±2,0)` is longer (approximately √3× the nearest-neighbor physical distance), so using it as a true immediate neighbor would be incorrect. Only edges between two manually labeled spots are eligible. A reference boundary is an eligible edge between different reference layers; a predicted boundary is an eligible edge between different raw cluster IDs. No posthoc label alignment.

The **main spatial outcome** is strict **0-hop edge-F1**: TP is the exact intersection of predicted and reference boundary edges. Precision/recall/F1 all use original TP, FP, FN. All input sources, topology, reference masks, exact spot barcode order and prediction SHA were checked.

**Sensitivity analysis (strict F1 never substituted):** 1-hop tolerance permits matching two boundary edges that share a spot; 2-hop additionally permits endpoint-to-endpoint adjacency in the same hex graph. Both use a **maximum-cardinality one-to-one bipartite matching**, so one reference edge cannot be matched to multiple predicted edges. Matching yields TP/FP/FN anew at each hop threshold. All three thresholds 0/1/2 reported for all 48 grids, no posthoc choice of the most favorable threshold. Tolerant-F1 is not a measure of exact boundary localization.

## Descriptive 12-slice results, not donor-level inference

| E3d AutoK scale | Strict 0-hop F1 | 1-hop F1 | 2-hop F1 |
|---|---:|---:|---:|
| 10D | 0.159578 | 0.354529 | 0.447191 |
| 15D | 0.129871 | 0.310503 | 0.418746 |
| 20D | 0.133824 | 0.353747 | 0.502284 |
| 25D | 0.119033 | 0.306971 | 0.457723 |

The 20D scale has the highest descriptive 2-hop F1 but **not** the highest strict F1. Do not select a threshold based on the outcome, claim 20D is best on exact boundary localization, or infer any mechanism. DLPFC has 12 slices nested in 3 donors (n=3 biological), not n=12 or 48 independent samples. All selected K differ by sample/scale according to the frozen E3d AutoK pipeline; contrasts also involve K variation.

## Files

- [All 144 metric rows](derived/all_144_tolerance_metric_rows.csv): 48 E3d predictions × 3 hop tolerances; includes all counts, precision, recall, F1, original prediction SHA, candidate matching graph sizes.
- [48 gridwide strict/tolerant summary](derived/all_48_strict_and_tolerant_f1.csv), [12 macro rows](derived/twelve_slice_macro_descriptives.csv), [36 donor × scale × threshold rows](derived/donor_scale_tolerance_summary.csv).
- [Independent phase audit JSON](derived/posthoc_boundary_audit_report.json) and [repeatable evaluation Python source](e3b_e3d48_boundary_posthoc_v1.py). Files also listed with SHA256 in [manifest.json](manifest.json).
- Source predictions, positions and reference annotations remain in the user's original ZIP, not this release. Exact source ZIP SHA256: `1f3e55c1acbf9162998a1a3e198c26284c8a63f7784ab8b28088220e2e148094`.
- Initial posthoc scope declaration: [E3D_E3B_POSTHOC_COMPLETION_PLAN_20261122.md](../E3D_E3B_POSTHOC_COMPLETION_PLAN_20261122.md).

**Blocking step for full E3b:** source original predictions for all 12 slices × 10 E1/E2 conditions × 10 technical seeds (=1200 grids) must be individually SHA-aligned to [E1/E2 1200-task ledger](../E1E2_20261119_RELEASE/derived/all_1200_tasks.csv) before executing the same fixed boundary metrics and publishing the full 3600 metric rows. No source predictions have been fabricated or retroactively relabeled.
