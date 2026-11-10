"""Exploratory CellCharter DLPFC 151507 hop ablation, one hop per invocation.

Requires the vetted local CellCharter v0.3.2 / TorchGMM 0.1.2 environment.
Reads ONLY saved, label-free latent/aggregated features and baseline manifest.
Does not read manual annotations or calculate ARI/NMI/Boundary F1.

Run one chosen hop at a time; no automatic 0-4 batch execution.
This script is a candidate, not yet executed in the user's Windows environment.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata as metadata
import json
import shutil
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

import anndata as ad
import cellcharter as cc
import numpy as np
import pandas as pd
import torch
from pytorch_lightning.overrides.distributed import IndexBatchSamplerWrapper

SOURCE_RUN = Path(
    r"D:\paper\CellCharter_reproduction\runs\151507_baseline_seed0_20261109_135812_583663"
)
OUTPUT_ROOT = Path(r"D:\paper\CellCharter_reproduction\runs")
K = 7
SEED = 0
MAX_EM_ITERATIONS = 100
EXPECTED_SHAPE = (4226, 25)


def digest_file(path: Path) -> str:
    checksum = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            checksum.update(block)
    return checksum.hexdigest()


def record_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


class Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, text: str):
        for stream in self.streams:
            stream.write(text)
            stream.flush()

    def flush(self):
        for stream in self.streams:
            stream.flush()


def load_and_validate():
    required = ["manifest.json", "latent.npz", "aggregated.npz", "predictions.csv"]
    for filename in required:
        if not (SOURCE_RUN / filename).is_file():
            raise FileNotFoundError(SOURCE_RUN / filename)

    original_manifest = json.loads((SOURCE_RUN / "manifest.json").read_text(encoding="utf-8"))
    if original_manifest.get("status") != "EXPLORATORY_FIT_CONVERGED":
        raise AssertionError("Source baseline does not report a converged fit")
    if original_manifest.get("manual_labels_read") is not False:
        raise AssertionError("Source baseline label access status is unexpected")

    with np.load(SOURCE_RUN / "latent.npz", allow_pickle=False) as loaded:
        latent = loaded["X_scVI"].copy()
        barcodes1 = loaded["barcodes"].copy()
    with np.load(SOURCE_RUN / "aggregated.npz", allow_pickle=False) as loaded:
        features = loaded["X_cellcharter"].copy()
        barcodes2 = loaded["barcodes"].copy()
    predictions = pd.read_csv(SOURCE_RUN / "predictions.csv", usecols=["barcode"])

    if features.shape != EXPECTED_SHAPE or latent.shape != (4226, 5):
        raise AssertionError(f"Unexpected shapes: latent={latent.shape}, aggregate={features.shape}")
    if not (np.isfinite(latent).all() and np.isfinite(features).all()):
        raise AssertionError("Latent or aggregate contains NaN/Inf")
    if not np.array_equal(latent, features[:, :5]):
        raise AssertionError("The first five aggregated features differ from latent")
    if len(np.unique(barcodes1)) != 4226:
        raise AssertionError("Duplicate barcodes")
    if not (np.array_equal(barcodes1, barcodes2)
            and np.array_equal(barcodes1, predictions["barcode"].to_numpy())):
        raise AssertionError("Barcodes / order mismatch")

    print("SOURCE_VALIDATION_PASS:", features.shape, flush=True)
    print("FIRST_5_COLUMNS_EXACT_MATCH: True", flush=True)
    print("NO_MANUAL_LABEL_FILES_READ: True", flush=True)
    return barcodes1, features


def fit_one_hop(hop: int, barcodes: np.ndarray, all_features: np.ndarray) -> Path:
    n_features = 5 * (hop + 1)
    X = np.ascontiguousarray(all_features[:, :n_features], dtype=np.float32)
    if X.shape != (4226, n_features) or not np.isfinite(X).all():
        raise AssertionError("Invalid feature slice")

    # A minimal AnnData is sufficient; the CellCharter estimator reads ONLY
    # adata.obsm['X_cellcharter'] during fit/predict, never the dummy adata.X.
    adata = ad.AnnData(X=np.zeros((4226, 1), dtype=np.float32))
    adata.obs_names = pd.Index(barcodes.astype(str))
    adata.obsm["X_cellcharter"] = X

    target = OUTPUT_ROOT / (
        "151507_hop_ablation_h" + str(hop) + "_seed0_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    )
    target.mkdir(parents=True, exist_ok=False)
    shutil.copy2(Path(__file__), target / "script_snapshot.py")

    manifest = {
        "status": "RUNNING",
        "stage": "setup",
        "experiment": "EXPLORATORY_HOP_ABLATION_NOT_INDEPENDENT_TEST",
        "sample": "151507",
        "hop": hop,
        "input_features": n_features,
        "n_spots": len(barcodes),
        "source_run": str(SOURCE_RUN),
        "source_aggregated_sha256": digest_file(SOURCE_RUN / "aggregated.npz"),
        "source_latent_sha256": digest_file(SOURCE_RUN / "latent.npz"),
        "source_predictions_sha256": digest_file(SOURCE_RUN / "predictions.csv"),
        "script_sha256": digest_file(Path(__file__)),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "manual_labels_read": False,
        "ARI_computed": False,
        "known_k_reference_count": True,
        "parameters": {
            "random_seed": SEED,
            "gmm_k": K,
            "gmm_covariance_type": "full",
            "gmm_init_strategy": "kmeans",
            "gmm_convergence_tolerance": 0.001,
            "gmm_covariance_regularization": 1e-6,
            "gmm_max_em_iterations": MAX_EM_ITERATIONS,
            "gmm_accelerator": "cpu",
            "input": "first 5*(hop+1) columns of saved CellCharter h4 features",
        },
        "versions": {k: metadata.version(k) for k in
                     ("cellcharter", "torchgmm", "torch", "pytorch-lightning", "anndata")},
        "shim": "IndexBatchSamplerWrapper._batch_sampler -> _sampler (runtime only)",
        "limits": [
            "One explored slice / one seed, not independent testing",
            "Feature dimensionality increases with hop number",
            "K=7 known from reference class count, but spot labels not loaded",
            "NLL values across different dimensions are not directly comparable",
        ],
    }
    record_json(target / "manifest.json", manifest)
    std_out, std_err = sys.stdout, sys.stderr
    with (target / "run.log").open("w", encoding="utf-8") as log:
        sys.stdout, sys.stderr = Tee(std_out, log), Tee(std_err, log)
        try:
            print("RUN_DIR:", target, flush=True)
            print("ABLATION_HOP:", hop, "FEATURE_SHAPE:", X.shape, flush=True)
            # Same compatibility shim and estimator defaults as the tested baseline.
            IndexBatchSamplerWrapper._batch_sampler = property(lambda self: self._sampler)
            torch.manual_seed(SEED)
            np.random.seed(SEED)
            model = cc.tl.Cluster(
                n_clusters=K,
                random_state=SEED,
                covariance_type="full",
                init_strategy="kmeans",
                convergence_tolerance=0.001,
                covariance_regularization=1e-6,
                trainer_params={
                    "accelerator": "cpu",
                    "devices": 1,
                    "max_epochs": MAX_EM_ITERATIONS,
                    "enable_progress_bar": False,
                },
            )
            start = time.perf_counter()
            manifest["stage"] = "gmm_training"
            record_json(target / "manifest.json", manifest)
            model.fit(adata)
            labels = np.asarray(model.predict(adata), dtype=int)
            if labels.shape != (4226,) or not np.isin(labels, np.arange(K)).all():
                raise AssertionError("Invalid GMM labels")
            pd.DataFrame({"barcode": barcodes, "cluster": labels}).to_csv(
                target / "predictions.csv", index=False
            )
            torch.save(model.model_.state_dict(), target / "gmm_weights.pt")
            groups, counts = np.unique(labels, return_counts=True)
            manifest.update({
                "status": "GMM_CONVERGED" if bool(model.converged_) else "GMM_NOT_CONVERGED",
                "stage": "done",
                "gmm_converged": bool(model.converged_),
                "gmm_iterations": int(model.num_iter_),
                "gmm_nll": float(model.nll_),
                "cluster_counts": {str(g): int(n) for g, n in zip(groups, counts)},
                "runtime_seconds": round(time.perf_counter() - start, 3),
            })
            print("GMM_ITERATIONS:", manifest["gmm_iterations"], flush=True)
            print("GMM_CONVERGED:", manifest["gmm_converged"], flush=True)
            print("GMM_NLL:", manifest["gmm_nll"], flush=True)
            print("CLUSTER_COUNTS:", manifest["cluster_counts"], flush=True)
            print("HOP_ABLATION_RESULT_SAVED:", manifest["status"], flush=True)
        except BaseException as err:
            manifest["status"] = "INTERRUPTED" if isinstance(err, KeyboardInterrupt) else "FAILED"
            manifest["exception"] = repr(err)
            traceback.print_exc()
            raise
        finally:
            manifest["finished_at"] = datetime.now().isoformat(timespec="seconds")
            record_json(target / "manifest.json", manifest)
            sys.stdout, sys.stderr = std_out, std_err
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description="Run label-free CellCharter 0-4 hop ablation, one hop at a time")
    parser.add_argument("--mode", choices=("preflight", "run"), default="preflight")
    parser.add_argument("--hop", type=int, choices=range(5), default=0)
    args = parser.parse_args()
    print("MODE:", args.mode, "HOP:", args.hop, flush=True)
    barcodes, X = load_and_validate()
    if args.mode == "preflight":
        for hop in range(5):
            portion = X[:, :5 * (hop + 1)]
            print("FEATURES_HOP_" + str(hop) + ":", portion.shape, flush=True)
        print("HOP_ABLATION_PREFLIGHT_PASS", flush=True)
        return
    target = fit_one_hop(args.hop, barcodes, X)
    print("HOP_ABLATION_FINISHED:", target, flush=True)


if __name__ == "__main__":
    main()
