"""151508 cross-section extension: locked, equal-dimensional feature-block comparison.

Two 15D conditions from the SAME saved 25D aggregated representation:
  control:   L0 + L1 + L2
  candidate: L0 + L1 + L4
Independent GMM initialization with identical seed and explicit same parameters.
This is an extension to a previously examined section, NOT a pristine independent blind test.
The script does NOT retrain scVI or edit any existing experiment directory.
"""
from __future__ import annotations

import hashlib
import json
import time
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
DATA = Path(r"D:\paper\ST_Benchmark_Planning\mvp\data\151508")
SOURCE_DIR = BASE / "results" / "cellcharter_151508_scvi22911_features_v2"
SOURCE = SOURCE_DIR / "cellcharter_aggregated.npy"
POSITIONS = DATA / "spots_aligned.csv"
MANUAL = DATA / "manual_layer_annotations.csv"
OUT = BASE / "results" / "mvp_fixed15_block_swap_151508_gmm22911_v1"
SEED = 22911
K = 7
EXPECTED_SOURCE_FILE_SHA256 = "094f702ba7fae32fc69c6c8026acb5765bd7bcd39b2802fbe8091b26baba60ee"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def spatial_pairs(positions: pd.DataFrame):
    r = positions["array_row"].to_numpy(dtype=int)
    c = positions["array_col"].to_numpy(dtype=int)
    index = {}
    for i, rc in enumerate(zip(r.tolist(), c.tolist())):
        if rc in index:
            raise ValueError("Duplicate spatial grid coordinate")
        index[rc] = i
    pairs = []
    for i, (ri, ci) in enumerate(zip(r, c)):
        for dr, dc in ((0, 2), (1, -1), (1, 1)):
            j = index.get((ri + dr, ci + dc))
            if j is not None:
                pairs.append((min(i, j), max(i, j)))
    pairs = np.asarray(sorted(set(pairs)), dtype=np.int64)
    if pairs.shape != (12849, 2):
        raise ValueError(f"Expected 12849 undirected grid edges, got {pairs.shape}")
    return pairs[:, 0], pairs[:, 1]


def metrics(pred: np.ndarray, truth: np.ndarray, i: np.ndarray, j: np.ndarray) -> dict:
    valid = pd.notna(truth)
    if valid.sum() != 4381:
        raise ValueError(f"Expected 4381 annotated spots; found {valid.sum()}")
    good = valid[i] & valid[j]
    u, v = i[good], j[good]
    y_boundary = truth[u] != truth[v]
    pred_boundary = pred[u] != pred[v]
    tp = int((y_boundary & pred_boundary).sum())
    fp = int((~y_boundary & pred_boundary).sum())
    fn = int((y_boundary & ~pred_boundary).sum())
    precision = tp / (tp + fp) if tp + fp else 0.
    recall = tp / (tp + fn) if tp + fn else 0.
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.
    l56 = (((truth[u] == "Layer 5") & (truth[v] == "Layer 6")) |
           ((truth[u] == "Layer 6") & (truth[v] == "Layer 5")))
    return {
        "ari": float(adjusted_rand_score(truth[valid], pred[valid])),
        "nmi": float(normalized_mutual_info_score(truth[valid], pred[valid])),
        "boundary_tp": tp, "boundary_fp": fp, "boundary_fn": fn,
        "boundary_precision": precision, "boundary_recall": recall,
        "boundary_f1": f1,
        "l5_l6_detected": int((l56 & pred_boundary).sum()),
        "l5_l6_reference": int(l56.sum()),
        "l5_l6_recall": float((l56 & pred_boundary).sum() / l56.sum()) if l56.sum() else None,
        "reference_boundary_edges": int(y_boundary.sum()),
        "evaluated_spatial_edges": int(len(u)),
    }


def main():
    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite existing experiment: {OUT}")
    for p in (SOURCE, POSITIONS, MANUAL):
        if not p.is_file():
            raise FileNotFoundError(p)
    source_sha = sha256_file(SOURCE)
    if source_sha != EXPECTED_SOURCE_FILE_SHA256:
        raise ValueError(f"Source file SHA256 differs from read-only preflight: {source_sha}")
    x = np.load(SOURCE, allow_pickle=False)
    if x.shape != (4384, 25) or not np.isfinite(x).all():
        raise ValueError(f"Unexpected aggregated input shape/values: {x.shape}")
    positions = pd.read_csv(POSITIONS, dtype={"barcode": str})
    if len(positions) != 4384 or positions["barcode"].duplicated().any():
        raise ValueError("Invalid spot positions")
    # Check saved row order against the manifest generated WITH this 151508 feature cache.
    spot_order = pd.read_csv(SOURCE_DIR / "spot_order.csv", dtype={"barcode": str})
    if len(spot_order) != 4384 or not np.array_equal(
            spot_order["barcode"].to_numpy(), positions["barcode"].to_numpy()):
        raise ValueError("Feature row/barcode order mismatch against source spot_order.csv")
    source_status = json.loads((SOURCE_DIR / "status.json").read_text(encoding="utf-8"))
    if source_status.get("status") != "completed" or source_status.get("aggregate_sha256") != source_sha:
        raise ValueError("151508 feature cache status/SHA256 mismatch")
    i, j = spatial_pairs(positions)
    conditions = {
        "control_L0_L1_L2": [0, 1, 2],
        "candidate_L0_L1_L4": [0, 1, 4],
    }
    features = {}
    for name, blocks in conditions.items():
        idx = np.concatenate([np.arange(b * 5, (b + 1) * 5) for b in blocks])
        z = np.ascontiguousarray(x[:, idx], dtype=np.float32)
        if z.shape != (4384, 15) or not np.isfinite(z).all():
            raise ValueError(f"Invalid {name} feature matrix")
        features[name] = z

    OUT.mkdir(parents=True, exist_ok=False)
    manifest = {
        "status": "running", "purpose": "locked cross-section equal-dimensional scale-block comparison",
        "sample": "151508", "split": "previously explored section; extension validation, NOT untouched independent blind test", "oracle_k": K,
        "seed": SEED, "source": str(SOURCE), "source_file_sha256": source_sha,
        "source_shape": list(x.shape), "feature_dim": 15,
        "conditions": conditions,
        "cluster": {"covariance_type": "full", "init_strategy": "kmeans",
                    "convergence_tolerance": 0.001, "covariance_regularization": 1e-6,
                    "trainer_params": {"accelerator": "cpu", "devices": 1,
                                       "max_epochs": 100, "enable_progress_bar": False}},
        "scvi_retrained": False, "manual_labels_used_for_fit": False,
        "comparison_frozen_before_this_section_fit": True,
        "started_utc": datetime.now(timezone.utc).isoformat()
    }

    def write_manifest():
        (OUT / "manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    write_manifest()
    try:
        IndexBatchSamplerWrapper._batch_sampler = property(lambda self: self._sampler)
        # All model fits occur before manual labels are read.
        for name, blocks in conditions.items():
            print("GMM_START", name, flush=True)
            np.random.seed(SEED)
            torch.manual_seed(SEED)
            d = ad.AnnData(X=np.zeros((4384, 1), dtype=np.float32))
            d.obs_names = pd.Index(positions["barcode"].to_numpy())
            d.obsm["X_cellcharter"] = features[name]
            model = cc.tl.Cluster(
                n_clusters=K, random_state=SEED,
                covariance_type="full", init_strategy="kmeans",
                convergence_tolerance=0.001, covariance_regularization=1e-6,
                trainer_params={"accelerator": "cpu", "devices": 1,
                                "max_epochs": 100, "enable_progress_bar": False})
            start = time.perf_counter()
            model.fit(d)
            labels = np.asarray(model.predict(d), dtype=int)
            if labels.shape != (4384,) or not np.isin(labels, np.arange(K)).all():
                raise ValueError(f"Invalid cluster labels for {name}")
            output = pd.DataFrame({"barcode": d.obs_names.to_numpy(), "cluster": labels})
            output.to_csv(OUT / f"{name}_predictions.csv", index=False)
            manifest[name] = {
                "stage": "predictions_saved",
                "elapsed_fit_and_predict_seconds": round(time.perf_counter()-start, 3),
                "feature_sha256": hashlib.sha256(features[name].tobytes()).hexdigest(),
                "cluster_sizes": np.bincount(labels, minlength=K).tolist()}
            write_manifest()
            print("GMM_COMPLETE", name, "CLUSTERS", manifest[name]["cluster_sizes"],
                  flush=True)

        annot = pd.read_csv(MANUAL)
        annot = annot.loc[annot["sample_name"].astype(str) == "151508", ["spot_name", "layer"]]
        if annot["spot_name"].duplicated().any():
            raise ValueError("Duplicate reference barcode")
        truth = annot.set_index("spot_name")["layer"].reindex(positions["barcode"]).to_numpy()
        report = {}
        for name in conditions:
            pred = pd.read_csv(OUT / f"{name}_predictions.csv")["cluster"].to_numpy(dtype=int)
            report[name] = metrics(pred, truth, i, j)
            print("RESULT", name, json.dumps(report[name]), flush=True)
        manifest["status"] = "completed"
        manifest["finished_utc"] = datetime.now(timezone.utc).isoformat()
        write_manifest()
        (OUT / "results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        print("MVP_FIXED15_COMPLETE", "RESULT_DIR", str(OUT), flush=True)
    except BaseException as exc:
        manifest["status"] = "failed"
        manifest["error"] = repr(exc)
        write_manifest()
        raise


if __name__ == "__main__":
    main()
