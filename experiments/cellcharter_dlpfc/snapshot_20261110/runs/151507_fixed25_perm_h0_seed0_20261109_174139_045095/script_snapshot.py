"""CellCharter exploratory *fixed-width* spatial-identity permutation control.

DLPFC 151507, single section/seed. Not a scientific result until run on
researcher's Windows machine. Built to contrast the previously completed
variable-width 0..4-hop *prefix* experiment with a fixed 25-feature control.

Every condition contains the SAME five 5-dimensional blocks as the CellCharter
h4 aggregate. Blocks 1..h are correctly aligned to their spots; blocks
h+1..4 are *separately* permuted across spots with a fixed, shared set of
no-fixed-point permutations. This preserves each block's exact marginal
rows/values and fixes feature count at 25, but breaks spot-neighborhood
correspondence in unused blocks. It is a placebo/permutation intervention,
NOT a clean estimate of pure hop-depth effect: it also changes cross-block
correlation and injects mismatched spatial information.

Preflight only checks saved features; run fits exactly ONE GMM without reading
labels or fitting scVI. Results are stored in new, non-overwriting folders.
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

import numpy as np
import pandas as pd

SOURCE_RUN = Path(r"D:\paper\CellCharter_reproduction\runs\151507_baseline_seed0_20261109_135812_583663")
OUTPUT_ROOT = Path(r"D:\paper\CellCharter_reproduction\runs")
K = 7
SEED = 0
PERMUTATION_SEED = 20261109
MAX_EM_ITERATIONS = 100
EXPECTED_SHAPE = (4226, 25)


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def array_sha256(array: np.ndarray) -> str:
    c = np.ascontiguousarray(array)
    return hashlib.sha256(c.tobytes()).hexdigest()


def record_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


class Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, message: str) -> None:
        for stream in self.streams:
            stream.write(message)
            stream.flush()

    def flush(self) -> None:
        for stream in self.streams:
            stream.flush()


def load_and_validate() -> tuple[np.ndarray, np.ndarray, dict]:
    required = ("manifest.json", "latent.npz", "aggregated.npz", "predictions.csv")
    for item in required:
        if not (SOURCE_RUN / item).is_file():
            raise FileNotFoundError(SOURCE_RUN / item)

    manifest = json.loads((SOURCE_RUN / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "EXPLORATORY_FIT_CONVERGED", "Unexpected source run"
    assert manifest["manual_labels_read"] is False, "Source manifest indicates label access"

    with np.load(SOURCE_RUN / "latent.npz", allow_pickle=False) as f:
        latent = f["X_scVI"].copy()
        bc_latent = f["barcodes"].copy()
    with np.load(SOURCE_RUN / "aggregated.npz", allow_pickle=False) as f:
        aggregate = f["X_cellcharter"].copy()
        bc_aggregate = f["barcodes"].copy()
    original_barcodes = pd.read_csv(
        SOURCE_RUN / "predictions.csv", usecols=["barcode"]
    )["barcode"].to_numpy()

    assert latent.shape == (4226, 5) and aggregate.shape == EXPECTED_SHAPE
    assert np.isfinite(latent).all() and np.isfinite(aggregate).all()
    assert np.array_equal(latent, aggregate[:, :5]), "scVI block differs"
    assert len(np.unique(bc_latent)) == 4226, "Duplicate barcode"
    assert np.array_equal(bc_latent, bc_aggregate)
    assert np.array_equal(bc_latent, original_barcodes)

    print("SOURCE_VALIDATION_PASS:", aggregate.shape, flush=True)
    print("FIRST_5_COLUMNS_EXACT_MATCH: True", flush=True)
    print("NO_MANUAL_LABEL_FILES_READ: True", flush=True)
    return bc_latent, np.asarray(aggregate, dtype=np.float32), manifest


def create_derangements(n: int) -> dict[int, np.ndarray]:
    """Create one fixed derangement per 5D neighbor block; shared across hops."""
    rng = np.random.default_rng(PERMUTATION_SEED)
    indices = np.arange(n, dtype=np.int64)
    out: dict[int, np.ndarray] = {}
    for block in range(1, 5):
        for _ in range(1000):
            perm = rng.permutation(n)
            if np.all(perm != indices):
                out[block] = perm
                break
        else:
            raise RuntimeError(f"Could not create a derangement for block {block}")
    return out


def build_features(hop: int, original: np.ndarray,
                   permutations: dict[int, np.ndarray]) -> np.ndarray:
    if hop not in range(5):
        raise ValueError("hop must be 0..4")
    X = original.copy()
    for block in range(hop + 1, 5):
        c = slice(5 * block, 5 * (block + 1))
        X[:, c] = original[permutations[block], c]
    assert X.shape == EXPECTED_SHAPE
    assert np.isfinite(X).all()
    assert np.array_equal(X[:, :5], original[:, :5])
    for block in range(1, 5):
        c = slice(5 * block, 5 * (block + 1))
        # Preserves each block's set of row vectors and each column's distribution.
        if block <= hop:
            assert np.array_equal(X[:, c], original[:, c])
        else:
            assert np.array_equal(X[:, c], original[permutations[block], c])
    return np.ascontiguousarray(X, dtype=np.float32)


def preflight(original: np.ndarray, perms: dict[int, np.ndarray]) -> None:
    assert len(perms) == 4
    index = np.arange(original.shape[0], dtype=np.int64)
    for block in range(1, 5):
        p = perms[block]
        assert p.shape == (4226,) and np.unique(p).size == 4226
        assert (p != index).all()
        print(f"PERM_BLOCK_{block}_SHA256:", array_sha256(p)[:16], flush=True)

    for hop in range(5):
        x = build_features(hop, original, perms)
        assert np.array_equal(x, build_features(hop, original, create_derangements(len(x))))
        if hop == 4:
            assert np.array_equal(x, original), "Full h4 control must equal original data"
        if hop > 0:
            # The newly activated block is exactly the true, unpermuted block.
            lower = build_features(hop - 1, original, perms)
            start, stop = 5 * hop, 5 * (hop + 1)
            assert np.array_equal(x[:, start:stop], original[:, start:stop])
            assert np.array_equal(lower[:, start:stop],
                                  original[perms[hop], start:stop])
        print(f"CONTROL_HOP_{hop}: shape={x.shape} aligned_blocks={hop} "
              f"permuted_blocks={4-hop} feature_sha256={array_sha256(x)[:16]}",
              flush=True)
    print("FIXED25_PERMUTATION_PREFLIGHT_PASS", flush=True)


def run_one(hop: int, barcodes: np.ndarray, original: np.ndarray,
            perms: dict[int, np.ndarray]) -> Path:
    # Heavy imports live here; preflight does not use TorchGMM or GPU.
    import anndata as ad
    import cellcharter as cc
    import torch
    from pytorch_lightning.overrides.distributed import IndexBatchSamplerWrapper

    X = build_features(hop, original, perms)
    target = OUTPUT_ROOT / (
        f"151507_fixed25_perm_h{hop}_seed{SEED}_"
        + datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    )
    target.mkdir(parents=True, exist_ok=False)
    shutil.copy2(Path(__file__), target / "script_snapshot.py")

    manifest = {
        "status": "RUNNING",
        "stage": "setup",
        "experiment": "EXPLORATORY_FIXED25_PERMUTATION_CONTROL_NOT_INDEPENDENT_TEST",
        "sample": "151507",
        "hop": int(hop),
        "feature_dim": 25,
        "aligned_neighborhood_blocks": int(hop),
        "permuted_neighborhood_blocks": list(range(hop + 1, 5)),
        "source_run": str(SOURCE_RUN),
        "source_aggregated_sha256": file_sha256(SOURCE_RUN / "aggregated.npz"),
        "source_latent_sha256": file_sha256(SOURCE_RUN / "latent.npz"),
        "source_predictions_sha256": file_sha256(SOURCE_RUN / "predictions.csv"),
        "script_sha256": file_sha256(Path(__file__)),
        "feature_matrix_sha256": array_sha256(X),
        "permutation_index_sha256": {str(b): array_sha256(perms[b]) for b in range(1, 5)},
        "permutation_seed": PERMUTATION_SEED,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "manual_labels_read": False,
        "ARI_computed": False,
        "parameters": {
            "seed": SEED,
            "K": K,
            "covariance_type": "full",
            "init_strategy": "kmeans",
            "convergence_tolerance": 0.001,
            "covariance_regularization": 1e-6,
            "max_em_iterations": MAX_EM_ITERATIONS,
            "accelerator": "cpu",
            "permutation": "independent full-row derangement of each unused hop block",
        },
        "limitations": [
            "This is a matched-25D shuffled-neighborhood placebo, NOT a clean hop-depth estimate",
            "Changes both spot-to-neighborhood alignment and cross-block covariance",
            "Single explored DLPFC 151507 section, single seed, not independent testing",
            "K=7 known from reference class count; spot label values never accessed",
            "GMM initialization may produce run-specific results, even at fixed seed",
        ],
        "versions": {
            name: metadata.version(name) for name in
            ("cellcharter", "torchgmm", "torch", "pytorch-lightning", "anndata")
        },
        "shim": "IndexBatchSamplerWrapper._batch_sampler -> _sampler (runtime only)",
    }
    record_json(target / "manifest.json", manifest)
    std_out, std_err = sys.stdout, sys.stderr
    with (target / "run.log").open("w", encoding="utf-8") as log:
        sys.stdout, sys.stderr = Tee(std_out, log), Tee(std_err, log)
        try:
            np.savez_compressed(target / "permutation_indices.npz",
                                **{f"block_{b}": p for b, p in perms.items()})
            print("RUN_DIR:", target, flush=True)
            print("FIXED_DIMENSION:", X.shape, flush=True)
            print("CONTROL_HOP:", hop, "TRUE_BLOCKS:", hop,
                  "SHUFFLED_BLOCKS:", 4 - hop, flush=True)
            print("PERMUTATION_SEED:", PERMUTATION_SEED, flush=True)
            # Same TorchGMM+PL compatibility shim as successfully tested old ablation.
            IndexBatchSamplerWrapper._batch_sampler = property(lambda self: self._sampler)
            torch.manual_seed(SEED)
            np.random.seed(SEED)
            adata = ad.AnnData(X=np.zeros((4226, 1), dtype=np.float32))
            adata.obs_names = pd.Index(barcodes.astype(str))
            adata.obsm["X_cellcharter"] = X
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
            manifest["stage"] = "gmm_training"
            record_json(target / "manifest.json", manifest)
            start = time.perf_counter()
            model.fit(adata)
            labels = np.asarray(model.predict(adata), dtype=int)
            assert labels.shape == (4226,) and np.isin(labels, np.arange(K)).all()
            pd.DataFrame({"barcode": barcodes, "cluster": labels}).to_csv(
                target / "predictions.csv", index=False)
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
            print("CLUSTER_COUNTS:", manifest["cluster_counts"], flush=True)
            print("FIXED25_CONTROL_RESULT_SAVED:", manifest["status"], flush=True)
        except BaseException as error:
            manifest["status"] = (
                "INTERRUPTED" if isinstance(error, KeyboardInterrupt) else "FAILED")
            manifest["exception"] = repr(error)
            traceback.print_exc()
            raise
        finally:
            manifest["finished_at"] = datetime.now().isoformat(timespec="seconds")
            record_json(target / "manifest.json", manifest)
            sys.stdout, sys.stderr = std_out, std_err
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description="CellCharter fixed-25D shuffled-neighborhood control")
    parser.add_argument("--mode", choices=("preflight", "run"), default="preflight")
    parser.add_argument("--hop", type=int, choices=range(5), default=0)
    args = parser.parse_args()
    print("MODE:", args.mode, "HOP:", args.hop, flush=True)
    barcodes, original, _ = load_and_validate()
    perms = create_derangements(len(barcodes))
    preflight(original, perms)
    if args.mode == "preflight":
        return
    run_path = run_one(args.hop, barcodes, original, perms)
    print("FIXED25_CONTROL_FINISHED:", run_path, flush=True)


if __name__ == "__main__":
    main()
