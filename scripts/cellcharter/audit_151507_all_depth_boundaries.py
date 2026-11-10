"""Post-hoc boundary audit of saved CellCharter L0-L4 predictions, no fitting.

Outputs all layer-pair reference boundary recalls and same-layer fragmentation.
Exploratory single-section, single-seed, oracle K=7; edges are NOT independent replicates.
New script created after the experiments, not their original execution script.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import numpy as np
import pandas as pd

DATA = Path(r"D:\paper\ST_Benchmark_Planning\mvp\data\151507")
ROOT = Path(r"D:\paper\CellCharter_reproduction\results")
OUT = ROOT / "cellcharter_v032_151507_seed22911_all_depth_boundary_audit_v1"
DIRS = {h: ROOT / (f"cellcharter_v032_151507_seed22911_L{h}_diagnostic" if h < 4 else "cellcharter_v032_151507_seed22911_oracleK7") for h in range(5)}
LAYERS = ["Layer 1", "Layer 2", "Layer 3", "Layer 4", "Layer 5", "Layer 6", "WM"]


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for buf in iter(lambda: f.read(1024 * 1024), b""):
            h.update(buf)
    return h.hexdigest()


def main():
    if OUT.exists():
        raise FileExistsError(f"Output exists; refusing to overwrite: {OUT}")
    pos_file = DATA / "spots_aligned.csv"
    label_file = DATA / "manual_layer_annotations.csv"
    pos = pd.read_csv(pos_file, dtype={"barcode": str})
    labels = pd.read_csv(label_file, dtype={"spot_name": str})
    if len(pos) != 4226 or not pos["barcode"].is_unique:
        raise ValueError("Positions must have 4226 distinct barcodes")
    if "sample_name" not in labels.columns or not {"spot_name", "layer"}.issubset(labels.columns):
        raise ValueError("Annotation schema unexpected")
    labels = labels.loc[labels["sample_name"].astype(str) == "151507", ["spot_name", "layer"]]
    if labels["spot_name"].duplicated().any():
        raise ValueError("Repeated barcodes within sample annotation")
    truth = labels.set_index("spot_name")["layer"].reindex(pos["barcode"])
    valid = truth.notna().to_numpy()
    if int(valid.sum()) != 4221:
        raise ValueError(f"Unexpected labeled spots: {valid.sum()}")
    y = truth.to_numpy()
    if set(y[valid]) != set(LAYERS):
        raise ValueError(f"Unknown layer labels: {set(y[valid])}")
    r = pos["array_row"].to_numpy(dtype=int)
    c = pos["array_col"].to_numpy(dtype=int)
    lookup = {(int(a), int(b)): k for k, (a, b) in enumerate(zip(r, c))}
    if len(lookup) != len(pos):
        raise ValueError("Duplicate grid coordinates")
    edges = []
    for a, (rr, cc) in enumerate(zip(r, c)):
        for dr, dc in ((0, 2), (0, -2), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            b = lookup.get((int(rr + dr), int(cc + dc)))
            if b is not None and a < b:
                edges.append((a, b))
    if len(edges) != 12385:
        raise ValueError(f"Graph edges mismatch: {len(edges)}")
    i, j = np.asarray(edges, dtype=int).T
    keep = valid[i] & valid[j]
    i, j = i[keep], j[keep]
    if len(i) != 12381:
        raise ValueError(f"Evaluable edges mismatch: {len(i)}")
    actual = y[i] != y[j]
    if int(actual.sum()) != 950:
        raise ValueError(f"Reference boundary count mismatch: {actual.sum()}")

    details, overall, provenance = [], [], {}
    for h, folder in DIRS.items():
        file = folder / "predictions.csv"
        if not file.is_file():
            raise FileNotFoundError(file)
        p = pd.read_csv(file, dtype={"barcode": str})
        if not {"barcode", "cluster"}.issubset(p.columns):
            raise ValueError(f"L{h}: missing barcode or cluster columns; got {p.columns.tolist()}")
        if len(p) != 4226 or not p["barcode"].is_unique:
            raise ValueError(f"L{h}: invalid row count or repeated barcodes")
        if set(p["barcode"]) != set(pos["barcode"]):
            raise ValueError(f"L{h}: barcode sets differ from positions")
        if "sample_name" in p.columns and not (p["sample_name"].astype(str) == "151507").all():
            raise ValueError(f"L{h}: wrong sample_name")
        if {"array_row", "array_col"}.issubset(p.columns):
            aligned = p.set_index("barcode").reindex(pos["barcode"])
            if not (np.array_equal(aligned["array_row"].to_numpy(), r) and np.array_equal(aligned["array_col"].to_numpy(), c)):
                raise ValueError(f"L{h}: prediction coordinates inconsistent")
        x = p.set_index("barcode")["cluster"].reindex(pos["barcode"]).to_numpy()
        if pd.isna(x).any() or len(np.unique(x)) != 7:
            raise ValueError(f"L{h}: missing or unexpected number of clusters")
        predicted = x[i] != x[j]
        tp = int(np.count_nonzero(actual & predicted))
        fp = int(np.count_nonzero(~actual & predicted))
        fn = int(np.count_nonzero(actual & ~predicted))
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        overall.append(dict(depth=h, total_reference_boundaries=950, tp=tp, fp=fp, fn=fn,
                            precision=precision, recall=recall, f1=f1,
                            predicted_boundary_edges=int(predicted.sum()),
                            spatial_neighbor_agreement=float(1 - predicted.mean())))
        for a_idx, left in enumerate(LAYERS):
            inner = (y[i] == left) & (y[j] == left)
            n_inner = int(inner.sum())
            details.append(dict(depth=h, kind="within_layer", layer_a=left, layer_b=left,
                                reference_edges=n_inner, detected_edges=int((inner & predicted).sum()),
                                rate=float(predicted[inner].mean()) if n_inner else float("nan")))
            for right in LAYERS[a_idx+1:]:
                between = ((y[i] == left) & (y[j] == right)) | ((y[i] == right) & (y[j] == left))
                n = int(between.sum())
                if n:
                    details.append(dict(depth=h, kind="between_layers", layer_a=left,
                                        layer_b=right, reference_edges=n,
                                        detected_edges=int((between & predicted).sum()),
                                        rate=float(predicted[between].mean())))
        provenance[f"L{h}"] = dict(predictions_path=str(file), predictions_sha256=digest(file),
                                  column_names=p.columns.tolist(), row_count=len(p))
        print(f"L{h}_AUDIT_PASS TP={tp} FP={fp} FN={fn} F1={f1:.6f}", flush=True)
    boundary_df = pd.DataFrame(details)
    # Check the historically reported L5/L6 reference count without selecting based on performance.
    pair = boundary_df.loc[(boundary_df.kind == "between_layers") &
                           (boundary_df.layer_a == "Layer 5") &
                           (boundary_df.layer_b == "Layer 6")]
    if len(pair) != 5 or not (pair.reference_edges == 145).all():
        raise ValueError("L5/L6 reference edge count mismatch")
    # The recovered L3 result is a critical agreement check, not an optimization criterion.
    l3 = overall[3]
    if (l3["tp"], l3["fp"], l3["fn"]) != (194, 1708, 756):
        raise ValueError(f"L3 does not reproduce previously recovered boundary metrics: {l3}")
    OUT.mkdir(parents=True, exist_ok=False)
    pd.DataFrame(overall).to_csv(OUT / "overall_boundaries.csv", index=False)
    boundary_df.to_csv(OUT / "layer_pair_boundaries.csv", index=False)
    meta = dict(status="completed", study="exploratory single DLPFC 151507 section, seed22911, oracle K7",
                scope="post-hoc assessment only; no models fit", evaluated_spots=4221,
                evaluated_undirected_edges=12381, reference_boundary_edges=950,
                layer_pair_rate="fraction of reference between-layer edges predicted as different clusters",
                within_layer_rate="fraction of reference same-layer edges predicted as different clusters (false split)",
                edge_dependency_warning="Spatial edges and spots are not independent biological replicates",
                dimensions_by_depth={f"L{k}":5*(k+1) for k in range(5)},
                annotation_sha256=digest(label_file), positions_sha256=digest(pos_file),
                inputs=provenance, completed_utc=datetime.now(timezone.utc).isoformat())
    (OUT / "provenance.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print("ALL_DEPTH_BOUNDARY_AUDIT_COMPLETE", flush=True)
    print("RESULT_DIR", OUT, flush=True)


if __name__ == "__main__":
    main()
