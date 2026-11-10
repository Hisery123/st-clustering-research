"""CellCharter v0.3.2 / DLPFC single-section exploratory baseline.

This is a *planned* full-training pipeline, not a validated full-training result.
Use --mode preflight first. The run mode NEVER reads manual layer labels or computes ARI.
The sample (151507/151508) has already been explored; it is not an untouched test.

Requires the specifically vetted local environment with the TorchGMM/PL 1.9 shim.
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
import scanpy as sc
import scvi
import squidpy as sq
import cellcharter as cc
import torch
from scipy import sparse
from pytorch_lightning.overrides.distributed import IndexBatchSamplerWrapper

DATA_ROOT = Path(r"D:\paper\ST_Benchmark_Planning\mvp\data")
RUN_ROOT = Path(r"D:\paper\CellCharter_reproduction\runs")
SAMPLES = {"151507": (4226, 12385), "151508": (4384, 12849)}
OFFSETS = ((0, 2), (0, -2), (1, 1), (1, -1), (-1, 1), (-1, -1))

# Predetermined for a known-K DLPFC baseline (K is not learned from labels here).
CONFIG = {
    "min_gene_counts": 3,
    "min_spot_counts": 3,
    "hvg": 5000,
    "hvg_flavor": "seurat_v3",
    "norm_target": 1_000_000,
    "scvi_latent": 5,
    "scvi_epochs_cap": 400,
    "scvi_batch_size": 128,
    "scvi_train_size": 0.9,
    "scvi_early_stopping": True,
    "scvi_optimizer": "AdamW",
    "scvi_reduce_lr_on_plateau": True,
    "nhood_layers": 4,
    "spatial_grid_n_neighs": 6,
    "gmm_k": 7,
    "gmm_em_iterations_cap": 100,
    "gmm_covariance_type": "full",
    "gmm_accelerator": "cpu",
    "random_seed": 0,
}


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


class Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, s):
        for stream in self.streams:
            stream.write(s)
            stream.flush()

    def flush(self):
        for stream in self.streams:
            stream.flush()


def graph_check(graph, positions):
    arr = positions[["array_row", "array_col"]].to_numpy(dtype=int)
    lut = {tuple(pair): i for i, pair in enumerate(arr)}
    if len(lut) != len(arr):
        raise AssertionError("Duplicate 10x Visium array positions")
    rows, cols = [], []
    for i, (r, c) in enumerate(arr):
        for dr, dc in OFFSETS:
            j = lut.get((r + dr, c + dc))
            if j is not None:
                rows.append(i)
                cols.append(j)
    expected = sparse.csr_matrix((np.ones(len(rows), dtype=np.float32), (rows, cols)), shape=graph.shape)
    if (graph != expected).nnz:
        raise AssertionError("Spatial graph differs from exact Visium hex lattice")
    if (graph != graph.T).nnz:
        raise AssertionError("Graph is not symmetric")
    return expected.nnz // 2


def preprocess(section: str):
    src = DATA_ROOT / section
    h5 = src / "filtered_feature_bc_matrix.h5"
    positions_file = src / "tissue_positions_list.csv"
    if not h5.is_file() or not positions_file.is_file():
        raise FileNotFoundError(f"Missing mandatory inputs in {src}")

    adata = sc.read_10x_h5(str(h5))
    adata.var["gene_symbol_original"] = adata.var_names.to_numpy()
    if adata.var["gene_ids"].isna().any() or adata.var["gene_ids"].duplicated().any():
        raise AssertionError("Missing or duplicate Ensembl gene IDs")
    adata.var_names = adata.var["gene_ids"].astype(str).to_numpy()
    if adata.n_obs != SAMPLES[section][0]:
        raise AssertionError("Unexpected initial spot count")

    sc.pp.filter_genes(adata, min_counts=CONFIG["min_gene_counts"])
    sc.pp.filter_cells(adata, min_counts=CONFIG["min_spot_counts"])
    adata.layers["counts"] = adata.X.copy()
    sc.pp.normalize_total(adata, target_sum=CONFIG["norm_target"])
    sc.pp.log1p(adata)
    sc.pp.highly_variable_genes(
        adata, n_top_genes=CONFIG["hvg"], flavor=CONFIG["hvg_flavor"],
        layer="counts", subset=True,
    )
    if (adata.n_obs, adata.n_vars) != (SAMPLES[section][0], CONFIG["hvg"]):
        raise AssertionError("Unexpected preprocessing shape")
    print("PREPROCESS_PASS:", adata.shape, flush=True)

    pos = pd.read_csv(
        positions_file, header=None,
        names=["barcode", "in_tissue", "array_row", "array_col", "pxl_row", "pxl_col"],
    ).set_index("barcode").reindex(adata.obs_names)
    if pos.isna().any().any() or not (pos["in_tissue"] == 1).all():
        raise AssertionError("Missing tissue positions or incorrect tissue mask")

    adata.obsm["spatial"] = pos[["pxl_row", "pxl_col"]].to_numpy(dtype=np.float64)
    sq.gr.spatial_neighbors(adata, coord_type="grid", n_neighs=6, n_rings=1)
    graph = adata.obsp["spatial_connectivities"].tocsr()
    edges = graph_check(graph, pos)
    if edges != SAMPLES[section][1]:
        raise AssertionError("Unexpected edge count")
    print("GRAPH_PASS:", edges, flush=True)
    return adata, {h5.name: file_sha256(h5), positions_file.name: file_sha256(positions_file)}


def experiment(section: str, run_dir: Path, manifest: dict) -> None:
    start = time.perf_counter()
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable: refusing silent CPU scVI fallback")
    torch.cuda.reset_peak_memory_stats()
    scvi.settings.seed = CONFIG["random_seed"]
    manifest["gpu"] = torch.cuda.get_device_name(0)
    adata, hashes = preprocess(section)
    manifest["input_sha256"] = hashes
    manifest["stage"] = "scvi_training"
    write_json(run_dir / "manifest.json", manifest)

    scvi.model.SCVI.setup_anndata(adata, layer="counts")
    vae = scvi.model.SCVI(adata, n_latent=CONFIG["scvi_latent"])
    print("SCVI_FULL_TRAIN_START", flush=True)
    vae.train(
        max_epochs=CONFIG["scvi_epochs_cap"],
        use_gpu=True,
        train_size=CONFIG["scvi_train_size"],
        batch_size=CONFIG["scvi_batch_size"],
        early_stopping=CONFIG["scvi_early_stopping"],
        plan_kwargs={"optimizer": CONFIG["scvi_optimizer"],
                     "reduce_lr_on_plateau": CONFIG["scvi_reduce_lr_on_plateau"]},
        enable_progress_bar=True,
        enable_model_summary=False,
        logger=False,
    )
    if not bool(vae.is_trained_):
        raise AssertionError("scVI model reports not trained")
    z = vae.get_latent_representation(adata).astype(np.float32)
    if z.shape != (adata.n_obs, 5) or not np.isfinite(z).all():
        raise AssertionError("scVI latent is invalid")
    adata.obsm["X_scVI"] = z
    np.savez_compressed(run_dir / "latent.npz", barcodes=np.asarray(adata.obs_names, dtype="U"), X_scVI=z)
    vae.save(str(run_dir / "scvi_model"), overwrite=False, save_anndata=False)
    manifest["scvi_cuda_peak_allocated_mib"] = round(torch.cuda.max_memory_allocated() / 2**20, 2)
    try:
        for key, frame in vae.history.items():
            if hasattr(frame, "to_csv"):
                frame.to_csv(run_dir / ("scvi_history_" + str(key) + ".csv"))
        manifest["scvi_history_keys"] = sorted(str(k) for k in vae.history.keys())
    except Exception as e:
        manifest["history_export_warning"] = repr(e)
    print("SCVI_TRAIN_AND_SAVE_PASS:", z.shape, flush=True)
    manifest["stage"] = "aggregating"
    write_json(run_dir / "manifest.json", manifest)

    cc.gr.aggregate_neighbors(adata, n_layers=CONFIG["nhood_layers"], use_rep="X_scVI")
    features = np.asarray(adata.obsm["X_cellcharter"])
    if features.shape != (adata.n_obs, 25) or not np.isfinite(features).all():
        raise AssertionError("CellCharter aggregated representation invalid")
    np.savez_compressed(run_dir / "aggregated.npz", barcodes=np.asarray(adata.obs_names, dtype="U"), X_cellcharter=features)
    print("AGGREGATION_PASS:", features.shape, flush=True)
    manifest["stage"] = "gmm_training"
    write_json(run_dir / "manifest.json", manifest)

    # Runtime shim only for tested environment: TorchGMM 0.1.2 / PyTorch-Lightning 1.9.5.
    IndexBatchSamplerWrapper._batch_sampler = property(lambda self: self._sampler)
    gmm = cc.tl.Cluster(
        n_clusters=CONFIG["gmm_k"], random_state=CONFIG["random_seed"],
        covariance_type=CONFIG["gmm_covariance_type"],
        trainer_params={"accelerator": CONFIG["gmm_accelerator"], "devices": 1,
                        "max_epochs": CONFIG["gmm_em_iterations_cap"],
                        "enable_progress_bar": False},
    )
    gmm.fit(adata)
    labels = np.asarray(gmm.predict(adata)).astype(int)
    if len(labels) != adata.n_obs or not np.isin(labels, range(7)).all():
        raise AssertionError("GMM output invalid")
    pd.DataFrame({"barcode": adata.obs_names.to_numpy(), "cluster": labels}).to_csv(run_dir / "predictions.csv", index=False)
    torch.save(gmm.model_.state_dict(), run_dir / "gmm_weights.pt")
    values, counts = np.unique(labels, return_counts=True)
    manifest.update({
        "gmm_iterations": int(gmm.num_iter_),
        "gmm_converged": bool(gmm.converged_),
        "gmm_nll": float(gmm.nll_),
        "cluster_counts": {str(k): int(v) for k, v in zip(values, counts)},
        "runtime_seconds": round(time.perf_counter() - start, 2),
        "stage": "done",
    })
    manifest["status"] = "EXPLORATORY_FIT_CONVERGED" if gmm.converged_ else "EXPLORATORY_FIT_NONCONVERGED"
    print("GMM_STATUS:", manifest["gmm_iterations"], "CONVERGED:", manifest["gmm_converged"], flush=True)
    print("GMM_NLL:", manifest["gmm_nll"], flush=True)
    print("CLUSTER_COUNTS:", manifest["cluster_counts"], flush=True)
    print("BASELINE_RUN_RECORDED:", manifest["status"], flush=True)


def main():
    parser = argparse.ArgumentParser(description="DLPFC CellCharter full-training exploratory baseline (no manual labels, no ARI)")
    parser.add_argument("--section", choices=sorted(SAMPLES), required=True)
    parser.add_argument("--mode", choices=("preflight", "run"), default="preflight")
    args = parser.parse_args()
    print("MODE:", args.mode, "SECTION:", args.section, flush=True)
    if args.mode == "preflight":
        adata, _ = preprocess(args.section)
        print("PREFLIGHT_PASS:", adata.shape, flush=True)
        return

    run_dir = RUN_ROOT / (args.section + "_baseline_seed0_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f"))
    run_dir.mkdir(parents=True, exist_ok=False)
    shutil.copy2(Path(__file__), run_dir / "script_snapshot.py")
    manifest = {
        "status": "RUNNING", "stage": "setup", "mode": "EXPLORATORY_BASELINE_NOT_INDEPENDENT_TEST",
        "sample": args.section, "created_at": datetime.now().isoformat(timespec="seconds"),
        "manual_labels_read": False, "ARI_computed": False,
        "known_k_reference_count": True,
        "note": "K=7 uses reference category count, but reference spot labels are never loaded. This is known-K, not unsupervised-K-selection.",
        "parameters": CONFIG,
        "script_sha256": file_sha256(Path(__file__)),
        "versions": {name: metadata.version(name) for name in (
            "cellcharter", "torchgmm", "scvi-tools", "scanpy", "squidpy", "torch", "pytorch-lightning", "scikit-misc")},
        "shim": "IndexBatchSamplerWrapper._batch_sampler -> _sampler (runtime-only)",
    }
    write_json(run_dir / "manifest.json", manifest)
    stdout, stderr = sys.stdout, sys.stderr
    with (run_dir / "run.log").open("w", encoding="utf-8") as log:
        sys.stdout, sys.stderr = Tee(stdout, log), Tee(stderr, log)
        try:
            print("RUN_DIR:", run_dir, flush=True)
            experiment(args.section, run_dir, manifest)
        except BaseException as exc:
            manifest["status"] = "INTERRUPTED" if isinstance(exc, KeyboardInterrupt) else "FAILED"
            traceback.print_exc()
            raise
        finally:
            manifest["finished_at"] = datetime.now().isoformat(timespec="seconds")
            write_json(run_dir / "manifest.json", manifest)
            sys.stdout, sys.stderr = stdout, stderr


if __name__ == "__main__":
    main()
