"""One-task-at-a-time DLPFC GMM multiscale experiment (E1/E2).

Safety: defaults to read-only check, --fit explicitly creates one new output dir.
The user runs each task manually on Windows. No scVI retraining.
Use previously validated 25D CellCharter caches and barcode-ordered labels.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata as metadata
import json
import random
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path(r"D:\paper\CellCharter_reproduction")
DATA_ROOT = Path(r"D:\paper\ST_Benchmark_Planning\mvp\data")
RESULT_ROOT = BASE / "results"
SEEDS = (22911, 7449, 25842, 10379, 6690, 26128, 21059, 22159, 32389, 12815)
SAMPLES = {
    "151507": (4226, 4221, 7),
    "151508": (4384, 4381, 7),
    "151509": (4789, 4788, 7),
    "151510": (4634, 4595, 7),
    "151669": (3661, 3636, 5),
    "151670": (3498, 3484, 5),
    "151671": (4110, 4093, 5),
    "151672": (4015, 3888, 5),
    "151673": (3639, 3611, 7),
    "151674": (3673, 3635, 7),
    "151675": (3592, 3566, 7),
    "151676": (3460, 3431, 7),
}
CONDITIONS = {
    "cum_L0": (0,),
    "cum_L0_L1": (0, 1),
    "cum_L0_L1_L2": (0, 1, 2),
    "cum_L0_L1_L2_L3": (0, 1, 2, 3),
    "cum_L0_L1_L2_L3_L4": (0, 1, 2, 3, 4),
    "fixed_L0_L1_L3": (0, 1, 3),
    "fixed_L0_L1_L4": (0, 1, 4),
    "fixed_L0_L2_L3": (0, 2, 3),
    "fixed_L0_L2_L4": (0, 2, 4),
    "fixed_L0_L3_L4": (0, 3, 4),
}
EXTRA_SOURCE_HASH = {
    "151507": "15b1fd58d092277f81fa2a1513bb2fbf865eea71b1b7450a9a2f710c941a8f54",
    "151508": "094f702ba7fae32fc69c6c8026acb5765bd7bcd39b2802fbe8091b26baba60ee",
}


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1048576), b""):
            digest.update(chunk)
    return digest.hexdigest()


def get_source(sid: str):
    if sid == "151507":
        return RESULT_ROOT / "cellcharter_v032_151507_seed22911_oracleK7", "predictions.csv"
    if sid == "151508":
        return RESULT_ROOT / "cellcharter_151508_scvi22911_features_v2", "spot_order.csv"
    return RESULT_ROOT / f"cellcharter_{sid}_scvi22911_features_batch_v1", "spot_order.csv"


def get_legacy_result(sid: str, condition: str, seed: int) -> Path | None:
    if seed != 22911:
        return None
    name = {"cum_L0_L1_L2": "control_L0_L1_L2", "fixed_L0_L1_L4": "candidate_L0_L1_L4"}.get(condition)
    if name is None:
        return None
    if sid == "151507":
        dirname = "mvp_fixed15_block_swap_151507_seed22911_v1"
    elif sid == "151508":
        dirname = "mvp_fixed15_block_swap_151508_gmm22911_v1"
    else:
        dirname = f"mvp_fixed15_{sid}_gmm22911_batch_v1"
    return RESULT_ROOT / dirname / f"{name}_predictions.csv"


def preflight(sid: str, condition: str, seed: int):
    n, n_labeled, k = SAMPLES[sid]
    source_dir, order_name = get_source(sid)
    feature_path = source_dir / "cellcharter_aggregated.npy"
    pos_path = DATA_ROOT / sid / "spots_aligned.csv"
    label_path = DATA_ROOT / sid / "manual_layer_annotations.csv"
    order_path = source_dir / order_name
    status_path = source_dir / "status.json"

    for p in (feature_path, pos_path, label_path, order_path, status_path):
        if not p.is_file():
            raise FileNotFoundError(p)
    source_hash = file_sha256(feature_path)
    status = json.loads(status_path.read_text(encoding="utf-8"))
    assert status.get("status") == "completed", (sid, "source incomplete")
    if sid in EXTRA_SOURCE_HASH:
        assert source_hash == EXTRA_SOURCE_HASH[sid], (sid, "source hash mismatch")
    else:
        assert status.get("sample") == sid
        assert source_hash == status.get("aggregate_sha256"), (sid, "source hash mismatch")
        config = json.loads((source_dir / "config.json").read_text(encoding="utf-8"))
        assert config.get("aligned_csv_sha256") == file_sha256(pos_path)
    pos = pd.read_csv(pos_path, dtype={"barcode": str})
    order = pd.read_csv(order_path, dtype={"barcode": str})
    assert len(pos) == n and pos["barcode"].is_unique
    assert len(order) == n and order["barcode"].is_unique
    assert np.array_equal(pos["barcode"].to_numpy(), order["barcode"].to_numpy())
    x = np.load(feature_path, allow_pickle=False, mmap_mode="r")
    assert x.shape == (n, 25) and x.dtype == np.float32 and bool(np.isfinite(x).all())
    blocks = CONDITIONS[condition]
    cols = np.concatenate([np.arange(i * 5, (i + 1) * 5) for i in blocks])
    z = np.ascontiguousarray(x[:, cols], dtype=np.float32)
    assert z.shape == (n, 5 * len(blocks))
    feature_hash = hashlib.sha256(z.tobytes()).hexdigest()
    legacy = get_legacy_result(sid, condition, seed)
    return {
        "sid": sid, "seed": seed, "k": k, "n": n, "n_labeled_expected": n_labeled,
        "condition": condition, "blocks": blocks, "feature_dim": z.shape[1],
        "source_path": str(feature_path), "source_sha256": source_hash,
        "position_sha256": file_sha256(pos_path),
        "labels_sha256": file_sha256(label_path),
        "feature_sha256": feature_hash,
        "positions": pos, "selected": z, "label_path": label_path,
        "legacy": legacy,
    }


def run_fit(info, out: Path):
    import anndata as ad
    import cellcharter as cc
    import torch
    from pytorch_lightning.overrides.distributed import IndexBatchSamplerWrapper
    from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

    if out.exists():
        raise FileExistsError(f"Existing output preserved: {out}")

    env_versions = {}
    for pkg in ("cellcharter", "torchgmm", "torch", "numpy", "scikit-learn", "pytorch-lightning", "anndata"):
        try:
            env_versions[pkg] = metadata.version(pkg)
        except metadata.PackageNotFoundError:
            env_versions[pkg] = "NOT_RECORDED"

    manifest = {
        "status": "running", "protocol": "E1E2_MULTISCALE_GMM_TASK_V1",
        "sample": info["sid"], "gmm_seed": info["seed"],
        "oracle_k": info["k"], "feature_blocks": list(info["blocks"]),
        "feature_dim": info["feature_dim"],
        "source_file": info["source_path"], "source_sha256": info["source_sha256"],
        "positions_sha256": info["position_sha256"], "reference_sha256": info["labels_sha256"],
        "feature_sha256": info["feature_sha256"],
        "manual_labels_used_for_fit": False,
        "cluster": {"covariance_type": "full", "init_strategy": "kmeans",
                    "convergence_tolerance": 0.001, "covariance_regularization": 1e-6,
                    "trainer_params": {"accelerator": "cpu", "devices": 1,
                                       "max_epochs": 100, "enable_progress_bar": False}},
        "versions": env_versions, "python": sys.version,
        "started_utc": datetime.now(timezone.utc).isoformat(),
    }
    out.mkdir(parents=True, exist_ok=False)

    def save():
        (out / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    save()
    try:
        random.seed(info["seed"])
        np.random.seed(info["seed"])
        torch.manual_seed(info["seed"])
        IndexBatchSamplerWrapper._batch_sampler = property(lambda self: self._sampler)
        adata = ad.AnnData(X=np.zeros((info["n"], 1), dtype=np.float32))
        adata.obs_names = pd.Index(info["positions"]["barcode"].to_numpy())
        adata.obsm["X_cellcharter"] = info["selected"]
        model = cc.tl.Cluster(
            n_clusters=info["k"], random_state=info["seed"],
            covariance_type="full", init_strategy="kmeans",
            convergence_tolerance=0.001, covariance_regularization=1e-6,
            trainer_params={"accelerator": "cpu", "devices": 1,
                            "max_epochs": 100, "enable_progress_bar": False},
        )
        start = time.perf_counter()
        model.fit(adata)
        clusters = np.asarray(model.predict(adata), dtype=np.int64)
        fit_secs = time.perf_counter() - start
        assert clusters.shape == (info["n"],)
        assert bool(np.isin(clusters, np.arange(info["k"])).all())
        prediction_path = out / "predictions.csv"
        pd.DataFrame({"barcode": adata.obs_names.to_numpy(), "cluster": clusters}).to_csv(prediction_path, index=False)
        manifest["prediction_sha256"] = file_sha256(prediction_path)
        manifest["fit_predict_seconds"] = round(fit_secs, 6)
        manifest["cluster_sizes"] = np.bincount(clusters, minlength=info["k"]).tolist()
        save()

        # Labels are opened ONLY AFTER model fitting and prediction is saved.
        manual = pd.read_csv(info["label_path"], dtype={"sample_name": str, "spot_name": str})
        manual = manual.loc[manual["sample_name"] == info["sid"], ["spot_name", "layer"]]
        if (len(manual) != info["n_labeled_expected"] or manual["spot_name"].duplicated().any()
                or manual["layer"].isna().any() or manual["layer"].nunique() != info["k"]):
            raise ValueError("Reference-label manifest mismatch")
        if not manual["spot_name"].isin(info["positions"]["barcode"]).all():
            raise ValueError("Reference barcode outside current sample")
        truth = manual.set_index("spot_name")["layer"].reindex(info["positions"]["barcode"])
        valid = truth.notna().to_numpy()
        assert valid.sum() == info["n_labeled_expected"]
        metrics = {
            "ari": float(adjusted_rand_score(truth.to_numpy()[valid], clusters[valid])),
            "nmi": float(normalized_mutual_info_score(truth.to_numpy()[valid], clusters[valid])),
            "n_evaluated": int(valid.sum()),
            "oracle_k_used": True,
        }
        (out / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
        manifest["metrics"] = metrics
        manifest["status"] = "completed"
        manifest["finished_utc"] = datetime.now(timezone.utc).isoformat()
        save()
        print("E1E2_TASK_COMPLETE", info["sid"], info["condition"], "seed", info["seed"],
              "ARI", round(metrics["ari"], 6), "NMI", round(metrics["nmi"], 6),
              "fit_seconds", round(fit_secs, 3), flush=True)
        print("RESULT_DIR", out, flush=True)
    except BaseException as exc:
        manifest["status"] = "failed"
        manifest["error"] = repr(exc)
        manifest["traceback"] = traceback.format_exc()
        manifest["finished_utc"] = datetime.now(timezone.utc).isoformat()
        save()
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", choices=SAMPLES, required=True)
    parser.add_argument("--condition", choices=CONDITIONS, required=True)
    parser.add_argument("--seed", type=int, choices=SEEDS, required=True)
    parser.add_argument("--fit", action="store_true", help="Fit exactly ONE GMM task; otherwise check only")
    args = parser.parse_args()
    print("FROZEN_SEEDS", list(SEEDS), flush=True)
    info = preflight(args.sample, args.condition, args.seed)
    out = RESULT_ROOT / "e1e2_multiscale_gmm_v1" / args.sample / args.condition / f"seed_{args.seed}"
    legacy = info["legacy"]
    if legacy is not None and legacy.is_file():
        print("LEGACY_RESULT_EXISTS", legacy, flush=True)
        print("Do not rerun matching existing baseline; reuse only after audit.", flush=True)
        return
    if out.exists():
        raise FileExistsError(f"Output already exists and will NOT be overwritten: {out}")
    if not args.fit:
        print("E1E2_PREFLIGHT_PASS", args.sample, args.condition, args.seed,
              "shape", (info["n"], info["feature_dim"]), "K", info["k"],
              "feature_sha256", info["feature_sha256"], flush=True)
        print("NO_TRAINING_NO_FILES_WRITTEN", flush=True)
        return
    run_fit(info, out)


if __name__ == "__main__":
    main()
