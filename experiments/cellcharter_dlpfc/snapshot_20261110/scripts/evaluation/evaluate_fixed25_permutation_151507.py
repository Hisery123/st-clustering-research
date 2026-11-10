"""Post-hoc, label-based descriptive evaluation of frozen CellCharter fixed-25 permutation controls.
No training; refuse overwrite; exact sample and graph consistency checks.
"""
from pathlib import Path
import hashlib
import json

import numpy as np
import pandas as pd
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

root = Path(r"D:\paper\CellCharter_reproduction")
runs = root / "runs"
data = Path(r"D:\paper\ST_Benchmark_Planning\mvp\data\151507")
source = runs / "151507_baseline_seed0_20261109_135812_583663"
previous = runs / "151507_hop_ablation_evaluation_seed0" / "evaluation_provenance.json"
out = runs / "151507_fixed25_permutation_evaluation_seed0_20261109"

folders = [
    "151507_fixed25_perm_h0_seed0_20261109_174433_394836",
    "151507_fixed25_perm_h1_seed0_20261109_174648_424396",
    "151507_fixed25_perm_h2_seed0_20261109_174920_860393",
    "151507_fixed25_perm_h3_seed0_20261109_174937_316711",
    "151507_fixed25_perm_h4_seed0_20261109_174954_951592",
]

def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

assert not out.exists(), f"Output already exists; refusing overwrite: {out}"
ref = json.loads(previous.read_text(encoding="utf-8-sig"))
ann_path = data / "manual_layer_annotations.csv"
pos_path = data / "tissue_positions_list.csv"
assert digest(ann_path) == ref["manual_annotations_sha256"], "Manual annotation SHA256 mismatch"
assert digest(pos_path) == ref["tissue_positions_sha256"], "Tissue position SHA256 mismatch"

with np.load(source / "aggregated.npz", allow_pickle=False) as z:
    bc = z["barcodes"].astype(str)
    assert z["X_cellcharter"].shape == (4226, 25)
assert len(bc) == 4226 and len(set(bc)) == 4226

ann = pd.read_csv(ann_path, dtype={"sample_name": str, "spot_name": str})
ann = ann.loc[ann["sample_name"] == "151507", ["spot_name", "layer"]]
assert ann["spot_name"].is_unique, "Duplicate annotations for sample 151507"
truth = pd.Series(bc).map(ann.set_index("spot_name")["layer"]).to_numpy()
labeled = pd.notna(truth)
assert int(labeled.sum()) == ref["labeled_spots"] == 4221
assert len(pd.unique(truth[labeled])) == 7

# 10x Visium hex grid: array_row, array_col; each undirected edge listed once.
pos = pd.read_csv(pos_path, header=None, names=[
    "barcode", "in_tissue", "array_row", "array_col", "pxl_row", "pxl_col"
], dtype={"barcode": str})
assert pos["barcode"].is_unique
pos = pos.set_index("barcode").loc[bc]
assert (pd.to_numeric(pos["in_tissue"]) == 1).all(), "A predicted barcode is not in tissue"
coords = list(zip(pos["array_row"].astype(int), pos["array_col"].astype(int)))
assert len(set(coords)) == len(bc), "Duplicate spatial grid coordinate"
lookup = {c: i for i, c in enumerate(coords)}
edges = []
for i, (r, c) in enumerate(coords):
    for dr, dc in ((0, 2), (1, 1), (1, -1)):
        j = lookup.get((r + dr, c + dc))
        if j is not None:
            edges.append((i, j))
e = np.asarray(edges, dtype=np.int64)
assert e.shape == (12385, 2), f"Spatial edge count mismatch: {e.shape}"
e = e[labeled[e[:, 0]] & labeled[e[:, 1]]]
assert len(e) == ref["evaluated_spatial_edges"] == 12381
is_ref_boundary = truth[e[:, 0]] != truth[e[:, 1]]
ref_count = int(is_ref_boundary.sum())
assert ref_count == ref["reference_boundary_edges"] == 950
print("EVALUATION_SOURCE_PASS: labeled=4221 edges=12381 reference_boundaries=950", flush=True)

records = []
files = []
for hop, name in enumerate(folders):
    folder = runs / name
    manifest_path = folder / "manifest.json"
    prediction_path = folder / "predictions.csv"
    m = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    assert m["status"] == "GMM_CONVERGED" and m["gmm_converged"] is True
    assert m["hop"] == hop and m["feature_dim"] == 25
    assert m["manual_labels_read"] is False and m["ARI_computed"] is False
    p = pd.read_csv(prediction_path, dtype={"barcode": str})
    assert len(p) == 4226 and p["barcode"].is_unique
    assert np.array_equal(p["barcode"].to_numpy(), bc), f"Hop {hop} barcode mismatch"
    predicted = p["cluster"].to_numpy(dtype=np.int64)
    assert set(predicted) == set(range(7))
    ari = adjusted_rand_score(truth[labeled], predicted[labeled])
    nmi = normalized_mutual_info_score(truth[labeled], predicted[labeled], average_method="arithmetic")
    is_pred_boundary = predicted[e[:, 0]] != predicted[e[:, 1]]
    tp = int(np.count_nonzero(is_ref_boundary & is_pred_boundary))
    detected = int(is_pred_boundary.sum())
    precision = tp / detected if detected else 0.0
    recall = tp / ref_count
    f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0
    row = {
        "hop": hop, "features": 25, "ARI": ari, "NMI": nmi,
        "boundary_precision": precision, "boundary_recall": recall,
        "boundary_f1": f1,
        "spatial_neighbor_agreement": 1 - detected / len(e),
        "predicted_boundary_edges": detected, "true_positive_boundary_edges": tp,
    }
    records.append(row)
    files.append({
        "hop": hop, "run_dir": str(folder), "manifest_sha256": digest(manifest_path),
        "predictions_sha256": digest(prediction_path),
        "feature_matrix_sha256": m["feature_matrix_sha256"],
    })
    print(f"FIXED25_HOP_{hop}_EVALUATED", flush=True)

result = pd.DataFrame.from_records(records)
provenance = {
    "evaluation_type": "EXPLORATORY_POSTHOC_NOT_INDEPENDENT_TEST",
    "design": "FIXED25_PERMUTATION_NEGATIVE_CONTROL",
    "section": "151507", "seed": 0,
    "sample_unit": "single_DLPFC_section",
    "nmi_average_method": "arithmetic",
    "manual_labels_used_for_training": False,
    "reference_class_count_used_to_set_K": True,
    "labeled_spots": int(labeled.sum()),
    "evaluated_spatial_edges": int(len(e)),
    "reference_boundary_edges": ref_count,
    "manual_annotations_sha256": digest(ann_path),
    "tissue_positions_sha256": digest(pos_path),
    "previous_evaluation_provenance_sha256": digest(previous),
    "runs": files,
    "limitations": [
        "Single explored section and one random seed; not an independent test",
        "Permuting unused hop blocks also alters between-feature correlations",
        "Separate 4-hop run was not identical: cross-run partition ARI=0.713871",
        "K=7 uses known reference class count; no inferential significance",
    ],
}
out.mkdir(parents=True, exist_ok=False)
result.to_csv(out / "fixed25_permutation_metrics.csv", index=False, float_format="%.17g")
(out / "evaluation_provenance.json").write_text(
    json.dumps(provenance, indent=2, ensure_ascii=False), encoding="utf-8"
)
print("\n===== FIXED25 PERMUTATION METRICS =====")
print(result.to_string(index=False, float_format=lambda x: f"{x:.6f}"))
print("EVALUATION_SAVED:", out)
print("FIXED25_ALL_FIVE_EVALUATION_PASS")
