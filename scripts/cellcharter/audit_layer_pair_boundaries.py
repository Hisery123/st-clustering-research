"""Read-only boundary-pair recall audit for DLPFC section 151671 / 151676.

Uses all original adjacent Visium (array_row,array_col) neighbor pairs.
Counts undirected adjacent pairs exactly once; reference-labeled endpoints only.
A predicted boundary is detected when the TWO raw cluster IDs differ within A (or B).
No cluster-to-layer majority vote is used. No model fitting or writes.
This audits layer-pair RECALL only; FP are not assigned to any reference boundary pair.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

DATA_ROOT = Path(r"D:\paper\ST_Benchmark_Planning\mvp\data")
RESULT_ROOT = Path(r"D:\paper\CellCharter_reproduction\results")
SAMPLES = ("151671", "151676")


def load_sample(sid: str) -> pd.DataFrame:
    datadir = DATA_ROOT / sid
    resultdir = RESULT_ROOT / f"mvp_fixed15_{sid}_gmm22911_batch_v1"
    pos = pd.read_csv(datadir / "spots_aligned.csv", dtype={"barcode": str})
    annot = pd.read_csv(datadir / "manual_layer_annotations.csv",
                        dtype={"spot_name": str, "layer": str})
    a = pd.read_csv(resultdir / "control_L0_L1_L2_predictions.csv", dtype={"barcode": str})
    b = pd.read_csv(resultdir / "candidate_L0_L1_L4_predictions.csv", dtype={"barcode": str})
    if not pos["barcode"].is_unique or not annot["spot_name"].is_unique:
        raise ValueError(f"{sid}: duplicate barcode or reference annotation")
    for name, table in (("A", a), ("B", b)):
        if not table["barcode"].is_unique or set(table["barcode"]) != set(pos["barcode"]):
            raise ValueError(f"{sid}: {name} prediction barcode mismatch")
    if not set(annot["spot_name"]).issubset(set(pos["barcode"])):
        raise ValueError(f"{sid}: unknown reference annotation barcode")
    aligned = pos.merge(annot[["spot_name", "layer"]],
                        left_on="barcode", right_on="spot_name",
                        how="left", validate="one_to_one")
    aligned = aligned.merge(a[["barcode", "cluster"]].rename(columns={"cluster":"A"}),
                            on="barcode", validate="one_to_one")
    aligned = aligned.merge(b[["barcode", "cluster"]].rename(columns={"cluster":"B"}),
                            on="barcode", validate="one_to_one")
    if len(aligned) != len(pos) or aligned[["A", "B", "array_row", "array_col"]].isna().any().any():
        raise ValueError(f"{sid}: failed to join predictions or coordinates")
    return aligned


def audit(sid: str) -> None:
    df = load_sample(sid)
    rows = df.array_row.to_numpy(dtype=int)
    cols = df.array_col.to_numpy(dtype=int)
    lookup = {}
    for i, xy in enumerate(zip(rows.tolist(), cols.tolist())):
        if xy in lookup:
            raise ValueError(f"{sid}: duplicated array coordinate")
        lookup[xy] = i

    # Identical direction set to frozen evaluation: each undirected edge once.
    pairs = set()
    for i, (row, col) in enumerate(zip(rows.tolist(), cols.tolist())):
        for dr, dc in ((0, 2), (1, -1), (1, 1)):
            j = lookup.get((row + dr, col + dc))
            if j is not None:
                pairs.add((min(i, j), max(i, j)))
    pair_ids = np.asarray(sorted(pairs), dtype=int).reshape(-1, 2)
    ref = df.layer.to_numpy()
    a = df.A.to_numpy()
    b = df.B.to_numpy()
    totals = defaultdict(lambda: [0, 0, 0])
    eval_edges = 0
    all_ref_tp_a = all_ref_tp_b = all_ref_edges = 0

    for i, j in pair_ids:
        if pd.isna(ref[i]) or pd.isna(ref[j]):
            continue
        eval_edges += 1
        if ref[i] == ref[j]:
            continue
        key = tuple(sorted((str(ref[i]), str(ref[j]))))
        totals[key][0] += 1
        detect_a = (a[i] != a[j])
        detect_b = (b[i] != b[j])
        totals[key][1] += int(detect_a)
        totals[key][2] += int(detect_b)
        all_ref_edges += 1
        all_ref_tp_a += int(detect_a)
        all_ref_tp_b += int(detect_b)

    print(f"SECTION {sid} spots={len(df)} spatial_edges={len(pair_ids)} evaluated_edges={eval_edges}")
    print("layer_pair,reference_boundary_edges,A_detected,B_detected,A_recall,B_recall,delta_recall")
    for key in sorted(totals):
        total, tp_a, tp_b = totals[key]
        print(f"{key[0]} | {key[1]},{total},{tp_a},{tp_b},"
              f"{tp_a/total:.6f},{tp_b/total:.6f},{(tp_b-tp_a)/total:+.6f}")
    print(f"TOTAL_REFERENCE_BOUNDARIES {all_ref_edges} TP_A {all_ref_tp_a} TP_B {all_ref_tp_b}")
    print(f"LAYER_PAIR_AUDIT_COMPLETE {sid}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", choices=SAMPLES, required=True)
    args = parser.parse_args()
    audit(args.sample)


if __name__ == "__main__":
    main()
