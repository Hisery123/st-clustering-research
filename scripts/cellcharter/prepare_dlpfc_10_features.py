"""Prepare scVI-5D and CellCharter-25D features for 10 frozen DLPFC sections.

Adapted directly from this repository's 151507 baseline preprocessing/graph
protocol. Does not perform GMM, score labels, or choose feature combinations.
This is an extension, NOT a pristine blind test. Default read-only; use --train\nexplicitly to fit. --all isolates sections in separate Python processes.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
import traceback
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import scanpy as sc
import squidpy as sq
import scvi
import cellcharter as cc
import torch

DATA_ROOT = Path(r"D:\paper\ST_Benchmark_Planning\mvp\data")
RESULTS_ROOT = Path(r"D:\paper\CellCharter_reproduction\results")
SAMPLES = {
    "151509": 4789, "151510": 4634,
    "151669": 3661, "151670": 3498, "151671": 4110, "151672": 4015,
    "151673": 3639, "151674": 3673, "151675": 3592, "151676": 3460,
}
SEED = 22911
N_GENES = 33538


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as reader:
        for chunk in iter(lambda: reader.read(1024*1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_section(sample: str, train: bool):
    if sample not in SAMPLES:
        raise ValueError(f"Unrecognized section: {sample}")
    DATA = DATA_ROOT / sample
    OUT = RESULTS_ROOT / f"cellcharter_{sample}_scvi22911_features_batch_v1"
    N_SPOTS = SAMPLES[sample]

    h5 = DATA / "filtered_feature_bc_matrix.h5"
    pos_path = DATA / "spots_aligned.csv"
    for path in (h5, pos_path):
        if not path.is_file():
            raise FileNotFoundError(path)

    adata = sc.read_10x_h5(str(h5))
    pos = pd.read_csv(pos_path, dtype={"barcode": str})
    if adata.shape != (N_SPOTS, N_GENES):
        raise ValueError(f"Unexpected expression shape: {adata.shape}")
    if len(pos) != N_SPOTS or not pos["barcode"].is_unique:
        raise ValueError("Invalid aligned coordinate table")
    if not np.array_equal(adata.obs_names.to_numpy(), pos["barcode"].to_numpy()):
        raise ValueError("Barcode order mismatch")
    if not pos["in_tissue"].eq(1).all():
        raise ValueError("Unexpected non-tissue spot")
    if pos[["array_row", "array_col"]].isna().any().any():
        raise ValueError("Missing spatial coordinates")

    r = pos["array_row"].to_numpy(dtype=int)
    c = pos["array_col"].to_numpy(dtype=int)
    adata.obsm["spatial"] = np.column_stack((c.astype(float), np.sqrt(3.)*r))
    sq.gr.spatial_neighbors(adata, coord_type="grid", n_neighs=6, n_rings=1)
    graph = adata.obsp["spatial_connectivities"].tocsr()
    ii, jj = graph.nonzero()
    dr = np.abs(r[ii] - r[jj])
    dc = np.abs(c[ii] - c[jj])
    ok = ((dr == 0) & (dc == 2)) | ((dr == 1) & (dc == 1))
    if graph.shape != (N_SPOTS, N_SPOTS) or graph.nnz == 0 or not ok.all():
        raise ValueError("Spatial graph geometric audit failed")
    if (graph != graph.T).nnz or np.diff(graph.indptr).max() > 6:
        raise ValueError("Invalid undirected six-neighbor spatial graph")
    print(f"{sample}_GRAPH_CHECK_PASS", "spots", N_SPOTS, "edges", graph.nnz//2, flush=True)

    if not train:
        print(f"{sample}_CHECK_ONLY_COMPLETE; NO_TRAINING; NO_FILES_WRITTEN", flush=True)
        return
    if OUT.exists():
        # Resume the batch safely: reuse only a fully completed, hash-matched cache.
        status_file = OUT / "status.json"
        config_file = OUT / "config.json"
        if status_file.is_file() and config_file.is_file():
            prior = json.loads(status_file.read_text(encoding="utf-8"))
            cfg = json.loads(config_file.read_text(encoding="utf-8"))
            cache = OUT / "cellcharter_aggregated.npy"
            if (prior.get("status") == "completed"
                    and prior.get("sample") == sample
                    and cfg.get("raw_h5_sha256") == sha256_file(h5)
                    and cfg.get("aligned_csv_sha256") == sha256_file(pos_path)
                    and cache.is_file()
                    and prior.get("aggregate_sha256") == sha256_file(cache)):
                print(f"{sample}_FEATURE_CACHE_REUSED", flush=True)
                return
        raise FileExistsError(f"Prior directory not safely reusable; preserve it: {OUT}")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA not available: will not silently alter 151507 protocol")
    # Explicitly initialize CUDA *before* creating output directory or training.
    # This is a controlled response to the v1 reset_peak_memory_stats failure.
    # It does not establish why v1 failed; keep v1 failure for provenance.
    torch.cuda.init()
    cuda_probe = torch.zeros(1, device="cuda:0")
    torch.cuda.synchronize(0)
    del cuda_probe
    print(f"{sample}_CUDA_READY", torch.cuda.get_device_name(0), flush=True)
    OUT.mkdir(parents=True, exist_ok=False)
    status = OUT / "status.json"
    config = {
        "status": "running", "sample": sample,
        "purpose": "produce frozen scVI 5D and CellCharter 4-hop 25D features only",
        "cross_section_status": "extension within previously known benchmark; not a blind test",
        "source_protocol": "scripts/cellcharter/cellcharter_151507_baseline_v032.py",
        "seed": SEED, "hvg": 5000, "hvg_flavor": "seurat_v3", "scvi_latent": 5,
        "scvi_max_epochs": 400, "early_stopping": True, "optimizer": "AdamW",
        "reduce_lr_on_plateau": True, "neighborhood_layers": 4,
        "raw_h5_sha256": sha256_file(h5),
        "aligned_csv_sha256": sha256_file(pos_path),
        "python": platform.python_version(),
        "packages": {x: importlib.metadata.version(x) for x in [
            "cellcharter", "torch", "scvi-tools", "squidpy", "scanpy", "anndata",
            "numpy", "scikit-learn"]},
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    (OUT / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
    status.write_text(json.dumps({"status": "running"}), encoding="utf-8")
    try:
        adata.var_names_make_unique()
        sc.pp.filter_genes(adata, min_counts=3)
        sc.pp.filter_cells(adata, min_counts=3)
        if adata.n_obs != N_SPOTS:
            raise ValueError(f"Filtering changed row alignment: {adata.n_obs}")
        adata.layers["counts"] = adata.X.copy()
        sc.pp.normalize_total(adata, target_sum=1e6)
        sc.pp.log1p(adata)
        sc.pp.highly_variable_genes(adata, n_top_genes=5000, subset=True,
                                   layer="counts", flavor="seurat_v3")
        if adata.shape != (N_SPOTS, 5000):
            raise ValueError(f"Unexpected filtered shape {adata.shape}")
        print(f"{sample}_PREPROCESS_PASS", adata.shape, flush=True)

        np.random.seed(SEED)
        scvi.settings.seed = SEED
        scvi.model.SCVI.setup_anndata(adata, layer="counts")
        model = scvi.model.SCVI(adata, n_latent=5)
        # Memory tracking is diagnostic; failure must not change the actual model protocol.
        try:
            torch.cuda.reset_peak_memory_stats(0)
            peak_memory_tracking = True
        except RuntimeError as exc:
            print("CUDA_MEMORY_STATS_WARNING", repr(exc), flush=True)
            peak_memory_tracking = False
        print(f"{sample}_SCVI_TRAIN_START", flush=True)
        model.train(max_epochs=400, use_gpu=True, early_stopping=True,
                    plan_kwargs={"optimizer": "AdamW", "reduce_lr_on_plateau": True})
        if model.trainer.strategy.root_device.type != "cuda":
            raise RuntimeError("SCVI training did not use CUDA")
        print(f"{sample}_SCVI_TRAIN_FINISHED", flush=True)
        latent = np.asarray(model.get_latent_representation(adata), dtype=np.float32)
        if latent.shape != (N_SPOTS, 5) or not np.isfinite(latent).all():
            raise ValueError(f"Invalid latent {latent.shape}")

        adata.obsm["X_scVI"] = latent
        cc.gr.aggregate_neighbors(adata, n_layers=4, use_rep="X_scVI")
        agg = np.asarray(adata.obsm["X_cellcharter"], dtype=np.float32)
        if agg.shape != (N_SPOTS, 25) or not np.isfinite(agg).all():
            raise ValueError(f"Invalid aggregate {agg.shape}")
        # Store barcode order to allow safe downstream cross-condition comparisons.
        np.save(OUT / "scvi_latent.npy", latent)
        np.save(OUT / "cellcharter_aggregated.npy", agg)
        pd.DataFrame({"barcode": adata.obs_names.to_numpy(),
                      "array_row": r, "array_col": c}).to_csv(OUT / "spot_order.csv", index=False)
        model.save(str(OUT / "scvi_model"), overwrite=False, save_anndata=False)
        result = {
            "status": "completed", "sample": sample,
            "n_spots": N_SPOTS, "latent_shape": list(latent.shape),
            "aggregate_shape": list(agg.shape), "edges_undirected": int(graph.nnz//2),
            "latent_sha256": sha256_file(OUT / "scvi_latent.npy"),
            "aggregate_sha256": sha256_file(OUT / "cellcharter_aggregated.npy"),
            "peak_cuda_mib": (round(torch.cuda.max_memory_allocated(0)/1048576, 2)
                              if peak_memory_tracking else None),
            "finished_utc": datetime.now(timezone.utc).isoformat()
        }
        status.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"{sample}_FEATURE_CACHE_COMPLETE", json.dumps(result, ensure_ascii=False), flush=True)
    except BaseException as exc:
        status.write_text(json.dumps({
            "status": "failed", "error": repr(exc), "traceback": traceback.format_exc(),
            "finished_utc": datetime.now(timezone.utc).isoformat()
        }, indent=2), encoding="utf-8")
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    choices = parser.add_mutually_exclusive_group(required=True)
    choices.add_argument("--sample", choices=list(SAMPLES))
    choices.add_argument("--all", action="store_true",
                         help="Run 10 independent child processes, stop on first failure")
    parser.add_argument("--train", action="store_true",
                        help="Explicitly allow GPU scVI training and new output writes")
    args = parser.parse_args()
    if args.all:
        import subprocess
        import sys
        for sid in SAMPLES:
            cmd = [sys.executable, str(Path(__file__).resolve()), "--sample", sid]
            if args.train:
                cmd.append("--train")
            print("SECTION_LAUNCH", sid, "TRAIN" if args.train else "CHECK_ONLY", flush=True)
            subprocess.run(cmd, check=True)
        print("DLPFC_10_FEATURE_" + ("TRAIN" if args.train else "CHECK_ONLY") +
              "_COMPLETE 10/10", flush=True)
    else:
        run_section(args.sample, train=args.train)


if __name__ == "__main__":
    main()
