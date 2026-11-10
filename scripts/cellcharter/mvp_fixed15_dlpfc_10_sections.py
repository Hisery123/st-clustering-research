"""Frozen 10-slice DLPFC equal-15D CellCharter block comparison.

Adapted from the verified 151508 fixed15 script. Default: read-only audit.
--fit explicitly performs paired CPU GMM clustering, saves predictions, then
reads reference labels to evaluate both predictions. No scVI training.
--all dispatches one fresh Python interpreter per section, stopping on errors.
The oracle K (5 or 7) comes from the frozen reference-class protocol, NOT from
a label-independent unsupervised selection.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

import anndata as ad
import cellcharter as cc
import numpy as np
import pandas as pd
import torch
from pytorch_lightning.overrides.distributed import IndexBatchSamplerWrapper
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

BASE = Path(r"D:\paper\CellCharter_reproduction")
DATA_ROOT = Path(r"D:\paper\ST_Benchmark_Planning\mvp\data")
SEED = 22911
# Frozen from the previous user-verified data + graph checks.
# sample: (total spots, undirected graph edges, annotated spots, oracle K)
SAMPLES = {
    "151509": (4789, 14086, 4788, 7),
    "151510": (4634, 13599, 4595, 7),
    "151669": (3661, 10597, 3636, 5),
    "151670": (3498, 10185, 3484, 5),
    "151671": (4110, 12026, 4093, 5),
    "151672": (4015, 11691, 3888, 5),
    "151673": (3639, 10562, 3611, 7),
    "151674": (3673, 10629, 3635, 7),
    "151675": (3592, 10381, 3566, 7),
    "151676": (3460, 10026, 3431, 7),
}
CONDITIONS = {
    "control_L0_L1_L2": (0, 1, 2),
    "candidate_L0_L1_L4": (0, 1, 4),
}


def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as reader:
        for block in iter(lambda: reader.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


def spatial_pairs(pos, expected_edges):
    rows = pos["array_row"].to_numpy(dtype=int)
    cols = pos["array_col"].to_numpy(dtype=int)
    lookup = {}
    for i, xy in enumerate(zip(rows.tolist(), cols.tolist())):
        if xy in lookup:
            raise ValueError("Duplicate Visium grid coordinate")
        lookup[xy] = i
    pairs = set()
    for i, (r, c) in enumerate(zip(rows.tolist(), cols.tolist())):
        for dr, dc in ((0, 2), (1, -1), (1, 1)):
            j = lookup.get((r + dr, c + dc))
            if j is not None:
                pairs.add((min(i, j), max(i, j)))
    ordered = np.asarray(sorted(pairs), dtype=np.int64).reshape(-1, 2)
    if len(ordered) != expected_edges:
        raise ValueError(f"Graph edges {len(ordered)} != frozen {expected_edges}")
    return ordered[:, 0], ordered[:, 1]


def measure(pred, truth, u, v):
    valid = pd.notna(truth)
    valid_edges = valid[u] & valid[v]
    i, j = u[valid_edges], v[valid_edges]
    true_edge = truth[i] != truth[j]
    pred_edge = pred[i] != pred[j]
    tp = int((true_edge & pred_edge).sum())
    fp = int((~true_edge & pred_edge).sum())
    fn = int((true_edge & ~pred_edge).sum())
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    l56 = (((truth[i] == "Layer 5") & (truth[j] == "Layer 6")) |
           ((truth[i] == "Layer 6") & (truth[j] == "Layer 5")))
    l56_n = int(l56.sum())
    l56_hit = int((l56 & pred_edge).sum())
    return {
        "ari": float(adjusted_rand_score(truth[valid], pred[valid])),
        "nmi": float(normalized_mutual_info_score(truth[valid], pred[valid])),
        "boundary_tp": tp, "boundary_fp": fp, "boundary_fn": fn,
        "boundary_precision": precision, "boundary_recall": recall,
        "boundary_f1": f1, "reference_boundary_edges": int(true_edge.sum()),
        "evaluated_spatial_edges": int(len(i)),
        "l5_l6_detected": l56_hit, "l5_l6_reference": l56_n,
        "l5_l6_recall": l56_hit / l56_n if l56_n else None,
    }


def run_sample(sid, do_fit):
    n, expected_edges, expected_annot, k = SAMPLES[sid]
    folder = DATA_ROOT / sid
    feature_dir = BASE / "results" / f"cellcharter_{sid}_scvi22911_features_batch_v1"
    out = BASE / "results" / f"mvp_fixed15_{sid}_gmm22911_batch_v1"
    pos_file = folder / "spots_aligned.csv"
    annot_file = folder / "manual_layer_annotations.csv"
    agg_file = feature_dir / "cellcharter_aggregated.npy"

    for path in (pos_file, annot_file, agg_file,
                 feature_dir / "status.json", feature_dir / "config.json",
                 feature_dir / "spot_order.csv"):
        if not path.is_file():
            raise FileNotFoundError(path)
    pos = pd.read_csv(pos_file, dtype={"barcode": str})
    order = pd.read_csv(feature_dir / "spot_order.csv", dtype={"barcode": str})
    if (len(pos) != n or len(order) != n or not pos["barcode"].is_unique or
            not np.array_equal(pos["barcode"].to_numpy(), order["barcode"].to_numpy())):
        raise ValueError(f"{sid}: barcode order mismatch")
    stat = json.loads((feature_dir / "status.json").read_text(encoding="utf-8"))
    cfg = json.loads((feature_dir / "config.json").read_text(encoding="utf-8"))
    source_sha = sha256_file(agg_file)
    if (stat.get("status") != "completed" or stat.get("sample") != sid or
            stat.get("aggregate_sha256") != source_sha or cfg.get("sample") != sid or
            cfg.get("aligned_csv_sha256") != sha256_file(pos_file)):
        raise ValueError(f"{sid}: feature cache status or hash mismatch")
    x = np.load(agg_file, allow_pickle=False)
    if x.shape != (n, 25) or not np.isfinite(x).all():
        raise ValueError(f"{sid}: invalid aggregate feature shape/values")
    i, j = spatial_pairs(pos, expected_edges)
    features = {}
    for name, blocks in CONDITIONS.items():
        columns = np.concatenate([np.arange(b*5, (b+1)*5) for b in blocks])
        part = np.ascontiguousarray(x[:, columns], dtype=np.float32)
        if part.shape != (n, 15) or not np.isfinite(part).all():
            raise ValueError(f"{sid}: invalid selected feature block {name}")
        features[name] = part

    if not do_fit:
        print("FIXED15_CHECK_PASS", sid, "spots", n, "K", k,
              "edges", len(i), "source_sha256", source_sha, flush=True)
        return

    if out.exists():
        raise FileExistsError(f"Refuse to overwrite output; preserve previous run: {out}")

    out.mkdir(parents=True, exist_ok=False)
    manifest = {
        "status": "running", "sample": sid, "oracle_k": k,
        "seed": SEED, "source_feature_file": str(agg_file),
        "source_feature_sha256": source_sha,
        "position_csv_sha256": sha256_file(pos_file),
        "reference_annotation_sha256": sha256_file(annot_file),
        "source_status_sha256": sha256_file(feature_dir / "status.json"),
        "source_config_sha256": sha256_file(feature_dir / "config.json"),
        "source_spot_order_sha256": sha256_file(feature_dir / "spot_order.csv"),
        "feature_dim": 15, "conditions": CONDITIONS,
        "cluster": {
            "covariance_type": "full", "init_strategy": "kmeans",
            "convergence_tolerance": 0.001,
            "covariance_regularization": 1e-6,
            "trainer_params": {"accelerator": "cpu", "devices": 1,
                               "max_epochs": 100, "enable_progress_bar": False}
        },
        "predeclared_annotated_spots": expected_annot,
        "manual_labels_used_for_fit": False,
        "source_annotation_provenance": "SEDR metadata layer_guess normalized to Layer 1..6, WM",
        "status_utc": datetime.now(timezone.utc).isoformat(),
    }

    def save_manifest():
        (out / "manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    save_manifest()
    try:
        IndexBatchSamplerWrapper._batch_sampler = property(lambda self: self._sampler)
        # Fit BOTH GMM models before opening the reference-annotation CSV.
        for name, data in features.items():
            print("GMM_START", sid, name, flush=True)
            np.random.seed(SEED)
            torch.manual_seed(SEED)
            adata = ad.AnnData(X=np.zeros((n, 1), dtype=np.float32))
            adata.obs_names = pd.Index(pos["barcode"].to_numpy())
            adata.obsm["X_cellcharter"] = data
            model = cc.tl.Cluster(
                n_clusters=k, random_state=SEED,
                covariance_type="full", init_strategy="kmeans",
                convergence_tolerance=0.001, covariance_regularization=1e-6,
                trainer_params={"accelerator": "cpu", "devices": 1,
                                "max_epochs": 100, "enable_progress_bar": False})
            start = time.perf_counter()
            model.fit(adata)
            clusters = np.asarray(model.predict(adata), dtype=int)
            if clusters.shape != (n,) or not np.isin(clusters, np.arange(k)).all():
                raise ValueError(f"{sid} {name}: invalid GMM predictions")
            pd.DataFrame({"barcode": pos["barcode"], "cluster": clusters}).to_csv(
                out / f"{name}_predictions.csv", index=False)
            manifest[name] = {
                "state": "predictions_saved",
                "elapsed_fit_predict_seconds": round(time.perf_counter()-start, 3),
                "feature_sha256": hashlib.sha256(data.tobytes()).hexdigest(),
                "cluster_sizes": np.bincount(clusters, minlength=k).tolist(),
            }
            save_manifest()
            print("GMM_COMPLETE", sid, name, manifest[name]["cluster_sizes"], flush=True)

        ann = pd.read_csv(annot_file, dtype={"spot_name": str})
        ann = ann.loc[ann["sample_name"].astype(str) == sid, ["spot_name", "layer"]]
        if (len(ann) != expected_annot or ann["spot_name"].duplicated().any()
                or ann["layer"].isna().any() or ann["layer"].nunique() != k
                or not ann["spot_name"].isin(pos["barcode"]).all()):
            raise ValueError(f"{sid}: reference label mismatch with frozen audit")
        truth = ann.set_index("spot_name")["layer"].reindex(pos["barcode"]).to_numpy()
        if pd.notna(truth).sum() != expected_annot:
            raise ValueError(f"{sid}: label alignment differs from source audit")
        report = {}
        for name in CONDITIONS:
            preds = pd.read_csv(out / f"{name}_predictions.csv", dtype={"barcode": str})
            if not np.array_equal(preds["barcode"].to_numpy(), pos["barcode"].to_numpy()):
                raise ValueError(f"{sid}: prediction barcode mismatch {name}")
            result = measure(preds["cluster"].to_numpy(dtype=int), truth, i, j)
            report[name] = result
            print("RESULT", sid, name, json.dumps(result), flush=True)
        report["difference_candidate_minus_control"] = {
            metric: report["candidate_L0_L1_L4"][metric] -
                    report["control_L0_L1_L2"][metric]
            for metric in ("ari", "nmi", "boundary_f1", "boundary_precision",
                           "boundary_recall", "boundary_fp", "boundary_tp", "boundary_fn")
        }
        (out / "results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        manifest["status"] = "completed"
        manifest["finished_utc"] = datetime.now(timezone.utc).isoformat()
        save_manifest()
        print("MVP_FIXED15_COMPLETE", sid, "RESULT_DIR", str(out), flush=True)
    except BaseException as err:
        manifest["status"] = "failed"
        manifest["error"] = repr(err)
        manifest["traceback"] = traceback.format_exc()
        save_manifest()
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--sample", choices=tuple(SAMPLES))
    group.add_argument("--all", action="store_true")
    parser.add_argument("--fit", action="store_true",
                        help="Fit both GMM models and save both predictions")
    args = parser.parse_args()
    if args.all:
        import subprocess
        import sys
        for sid in SAMPLES:
            command = [sys.executable, str(Path(__file__).resolve()), "--sample", sid]
            if args.fit:
                command.append("--fit")
            print("SECTION_LAUNCH", sid, "FIT" if args.fit else "CHECK_ONLY", flush=True)
            subprocess.run(command, check=True)
        print("DLPFC_10_FIXED15_" + ("FIT" if args.fit else "CHECK_ONLY") +
              "_COMPLETE 10/10", flush=True)
    else:
        run_sample(args.sample, args.fit)


if __name__ == "__main__":
    main()
