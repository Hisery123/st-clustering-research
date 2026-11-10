"""Recover L3 evaluation from saved predictions only; no model fit.

The original L3 run completed aggregation/GMM/predictions then raised on an
incorrect L5/L6 label spelling. This script preserves the original failed
status.json and writes a separate recovered metric artifact.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
import numpy as np
import pandas as pd
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

ROOT = Path(r"D:\paper\CellCharter_reproduction\results\cellcharter_v032_151507_seed22911_L3_diagnostic")
DATA = Path(r"D:\paper\ST_Benchmark_Planning\mvp\data\151507")
OUTPUT = ROOT / "metrics_recovered.json"

if OUTPUT.exists():
    raise FileExistsError(f"Recovery already exists; refusing overwrite: {OUTPUT}")
p = pd.read_csv(ROOT / "predictions.csv", dtype={"barcode": str})
pos = pd.read_csv(DATA / "spots_aligned.csv", dtype={"barcode": str})
manual = pd.read_csv(DATA / "manual_layer_annotations.csv", dtype={"spot_name": str})
manual = manual.loc[manual["sample_name"].astype(str) == "151507", ["spot_name", "layer"]]
assert len(p) == len(pos) == 4226
assert p["barcode"].is_unique and pos["barcode"].is_unique
assert p["barcode"].equals(pos["barcode"]), "Prediction and original coordinate order must match"
assert np.array_equal(p["array_row"].to_numpy(), pos["array_row"].to_numpy())
assert np.array_equal(p["array_col"].to_numpy(), pos["array_col"].to_numpy())
assert not manual["spot_name"].duplicated().any()
y = manual.set_index("spot_name")["layer"].reindex(p["barcode"])
mask = y.notna().to_numpy()
assert mask.sum() == 4221, f"Labeled count differs: {mask.sum()}"
pred = p["cluster"].to_numpy()
assert len(np.unique(pred)) == 7
r = pos["array_row"].to_numpy(dtype=int)
c = pos["array_col"].to_numpy(dtype=int)
coord_to_i = {(int(rr), int(cc)): i for i, (rr, cc) in enumerate(zip(r,c))}
assert len(coord_to_i) == 4226
edges = []
for i, (rr, cc) in enumerate(zip(r, c)):
    for dr, dc in ((0, 2), (0, -2), (1, 1), (1, -1), (-1, 1), (-1, -1)):
        j = coord_to_i.get((int(rr + dr), int(cc + dc)))
        if j is not None and i < j:
            edges.append((i,j))
assert len(edges) == 12385, f"Unexpected edges {len(edges)}"
i, j = np.asarray(edges, dtype=int).T
keep = mask[i] & mask[j]
i, j = i[keep], j[keep]
yy = y.to_numpy()
reference = yy[i] != yy[j]
estimated = pred[i] != pred[j]
tp = int(np.count_nonzero(reference & estimated))
fp = int(np.count_nonzero(~reference & estimated))
fn = int(np.count_nonzero(reference & ~estimated))
assert int(reference.sum()) == 950, f"Unexpected real boundaries: {reference.sum()}"
pair = ((yy[i] == "Layer 5") & (yy[j] == "Layer 6")) | ((yy[i] == "Layer 6") & (yy[j] == "Layer 5"))
pair_n = int(pair.sum())
assert pair_n == 145, f"Unexpected L5/L6 boundaries: {pair_n}"
pair_detected = int(np.count_nonzero(pair & estimated))
precision = tp / (tp + fp) if tp + fp else 0.
recall = tp / (tp + fn) if tp + fn else 0.
f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.
result = dict(status="recovered_from_saved_predictions", sample="151507",
              seed=22911, n_layers=3, feature_dim=20, n_clusters_oracle=7,
              n_spots_total=len(p), n_evaluated=int(mask.sum()),
              source_prediction=str(ROOT / "predictions.csv"),
              recovery_reason="Original L3 script compared 'L5'/'L6' rather than 'Layer 5'/'Layer 6'",
              original_status_preserved=True,
              ari=float(adjusted_rand_score(yy[mask], pred[mask])),
              nmi=float(normalized_mutual_info_score(yy[mask], pred[mask])),
              reference_boundaries=int(reference.sum()),
              boundary_tp=tp, boundary_fp=fp, boundary_fn=fn,
              boundary_precision=precision, boundary_recall=recall, boundary_f1=f1,
              l5_l6_reference_edges=pair_n, l5_l6_detected_edges=pair_detected,
              l5_l6_boundary_recall=pair_detected/pair_n,
              evaluated_undirected_edges=int(len(i)),
              recovered_utc=datetime.now(timezone.utc).isoformat())
OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
print("L3_RECOVERY_COMPLETE", json.dumps(result, ensure_ascii=False), flush=True)
print("METRICS_FILE", OUTPUT, flush=True)
