"""CellCharter v0.3.2 / DLPFC single-slice smoke test (NOT a performance result).

Run only after manually reviewing inputs and environment.
The script does not read or use any manual layer annotations.
Output: a new timestamped subdirectory under D:\\paper\\CellCharter_reproduction\\runs.
"""

import argparse
import hashlib
import importlib.metadata as md
import json
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
EXPECTED = {"151507": (4226, 12385), "151508": (4384, 12849)}
HEX_OFFSETS = ((0, 2), (0, -2), (1, 1), (1, -1), (-1, 1), (-1, -1))


class Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, msg):
        for stream in self.streams:
            stream.write(msg)
            stream.flush()

    def flush(self):
        for stream in self.streams:
            stream.flush()


def file_sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_manifest(path, manifest):
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def verify_hex_graph(graph, pos):
    xy = pos[["array_row", "array_col"]].to_numpy(dtype=int)
    lookup = {tuple(rc): i for i, rc in enumerate(xy)}
    if len(lookup) != len(xy):
        raise ValueError("Duplicate Visium array positions")
    rows, cols = [], []
    for i, (r, c) in enumerate(xy):
        for dr, dc in HEX_OFFSETS:
            j = lookup.get((r + dr, c + dc))
            if j is not None:
                rows.append(i)
                cols.append(j)
    theory = sparse.csr_matrix(
        (np.ones(len(rows), dtype=np.float32), (rows, cols)),
        shape=graph.shape,
    )
    if (graph != theory).nnz:
        raise AssertionError("Pixel-based graph does not match theoretical hex graph")
    return theory.nnz // 2


def run(section, run_dir, manifest):
    start = time.perf_counter()
    folder = DATA_ROOT / section
    h5 = folder / "filtered_feature_bc_matrix.h5"
    positions_file = folder / "tissue_positions_list.csv"
    if not h5.is_file() or not positions_file.is_file():
        raise FileNotFoundError("Missing H5 or tissue_positions_list.csv in " + str(folder))
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable; refusing silent CPU fallback for scVI")

    manifest["input_sha256"] = {
        "filtered_feature_bc_matrix.h5": file_sha256(h5),
        "tissue_positions_list.csv": file_sha256(positions_file),
    }
    scvi.settings.seed = 0
    manifest["cuda_device"] = torch.cuda.get_device_name(0)
    torch.cuda.reset_peak_memory_stats()

    adata = sc.read_10x_h5(str(h5))
    adata.var["gene_symbol_original"] = adata.var_names.to_numpy()
    if adata.var["gene_ids"].duplicated().any():
        raise ValueError("Non-unique gene_ids")
    adata.var_names = adata.var["gene_ids"].astype(str).to_numpy()
    if adata.n_obs != EXPECTED[section][0]:
        raise AssertionError("Unexpected number of raw spots")

    sc.pp.filter_genes(adata, min_counts=3)
    sc.pp.filter_cells(adata, min_counts=3)
    adata.layers["counts"] = adata.X.copy()
    sc.pp.normalize_total(adata, target_sum=1e6)
    sc.pp.log1p(adata)
    sc.pp.highly_variable_genes(
        adata, n_top_genes=5000, flavor="seurat_v3", layer="counts", subset=True
    )
    if adata.n_obs != EXPECTED[section][0] or adata.n_vars != 5000:
        raise AssertionError("Unexpected post-HVG dimensions")
    manifest["preprocessing_shape"] = [int(adata.n_obs), int(adata.n_vars)]
    print("PREPROCESS_PASS:", adata.shape, flush=True)

    scvi.model.SCVI.setup_anndata(adata, layer="counts")
    vae = scvi.model.SCVI(adata, n_latent=5)
    vae.train(
        max_epochs=2, use_gpu=True, batch_size=128,
        early_stopping=False, enable_progress_bar=False,
        enable_model_summary=False, logger=False,
    )
    z = vae.get_latent_representation(adata).astype(np.float32)
    if z.shape != (adata.n_obs, 5) or not np.isfinite(z).all():
        raise AssertionError("Invalid scVI features")
    manifest["scvi_cuda_peak_allocated_mib"] = round(torch.cuda.max_memory_allocated() / 2**20, 2)
    adata.obsm["X_scVI"] = z
    np.savez_compressed(run_dir / "latent.npz", barcodes=np.asarray(adata.obs_names, dtype="U"), X_scVI=z)
    print("SCVI_PASS:", z.shape, flush=True)

    pos = pd.read_csv(
        positions_file, header=None,
        names=["barcode", "in_tissue", "array_row", "array_col", "pxl_row", "pxl_col"],
    ).set_index("barcode").reindex(adata.obs_names)
    if pos.isna().any().any() or not (pos["in_tissue"] == 1).all():
        raise AssertionError("Incomplete spot positions / tissue mask")
    adata.obsm["spatial"] = pos[["pxl_row", "pxl_col"]].to_numpy(dtype=np.float64)
    sq.gr.spatial_neighbors(adata, coord_type="grid", n_neighs=6, n_rings=1)
    graph = adata.obsp["spatial_connectivities"].tocsr()
    edges = verify_hex_graph(graph, pos)
    if edges != EXPECTED[section][1]:
        raise AssertionError("Unexpected number of hex-graph edges")
    manifest["spatial_undirected_edges"] = int(edges)
    print("GRAPH_PASS:", edges, flush=True)

    cc.gr.aggregate_neighbors(adata, n_layers=4, use_rep="X_scVI")
    features = np.asarray(adata.obsm["X_cellcharter"])
    if features.shape != (adata.n_obs, 25) or not np.isfinite(features).all():
        raise AssertionError("Invalid aggregated features")
    np.savez_compressed(run_dir / "aggregated.npz", barcodes=np.asarray(adata.obs_names, dtype="U"), X_cellcharter=features)
    print("AGGREGATION_PASS:", features.shape, flush=True)

    # Runtime-only compatibility fix for TorchGMM v0.1.2 + Lightning v1.9.5.
    # Do not modify third-party package files.
    IndexBatchSamplerWrapper._batch_sampler = property(lambda self: self._sampler)
    model = cc.tl.Cluster(
        n_clusters=7, random_state=0,
        trainer_params={
            "accelerator": "cpu", "devices": 1,
            "max_epochs": 20, "enable_progress_bar": False,
        },
    )
    model.fit(adata)
    labels = np.asarray(model.predict(adata)).astype(int)
    values, counts = np.unique(labels, return_counts=True)
    if len(labels) != adata.n_obs or not np.isin(labels, np.arange(7)).all():
        raise AssertionError("Invalid predicted cluster codes")
    pd.DataFrame({"barcode": adata.obs_names.to_numpy(), "cluster": labels}).to_csv(
        run_dir / "predictions.csv", index=False
    )
    torch.save(model.model_.state_dict(), run_dir / "gmm_weights.pt")
    # Save without embedded AnnData; raw inputs remain in their original files.
    vae.save(str(run_dir / "scvi_model"), overwrite=False, save_anndata=False)

    manifest["gmm_converged"] = bool(model.converged_)
    manifest["gmm_num_iter"] = int(model.num_iter_)
    manifest["cluster_counts"] = {str(k): int(v) for k, v in zip(values, counts)}
    manifest["runtime_seconds"] = round(time.perf_counter() - start, 2)
    print("GMM_ITERATIONS:", model.num_iter_, "CONVERGED:", model.converged_, flush=True)
    print("CLUSTER_COUNTS:", manifest["cluster_counts"], flush=True)
    print("SMOKE_PASS_SAVED_WITH_SHIM", flush=True)


def main():
    parser = argparse.ArgumentParser(description="DLPFC CellCharter smoke test only; no ARI")
    parser.add_argument("--section", choices=sorted(EXPECTED), default="151507")
    args = parser.parse_args()
    RUN_ROOT.mkdir(parents=True, exist_ok=True)
    run_dir = RUN_ROOT / (args.section + "_smoke_seed0_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f"))
    run_dir.mkdir(parents=False, exist_ok=False)
    manifest = {
        "status": "RUNNING", "mode": "SMOKE_NOT_PUBLICATION_METRIC",
        "section": args.section, "created_at": datetime.now().isoformat(timespec="seconds"),
        "random_seed": 0, "manual_labels_read": False, "ARI_computed": False,
        "python_version": sys.version.split()[0], "torch_cuda_version": torch.version.cuda,
        "parameters": {"gene_min_counts": 3, "spot_min_counts": 3, "hvg": 5000,
                       "hvg_flavor": "seurat_v3", "norm_target": 1000000,
                       "scvi_n_latent": 5, "scvi_max_epochs": 2,
                       "scvi_batch_size": 128, "nhood_layers": 4,
                       "spatial_grid_neighbors": 6, "gmm_k": 7,
                       "gmm_max_em_iterations": 20, "gmm_accelerator": "cpu"},
        "package_versions": {
            name: md.version(name) for name in
            ("cellcharter", "torchgmm", "scvi-tools", "scanpy", "squidpy", "torch", "pytorch-lightning")
        },
        "shim": "IndexBatchSamplerWrapper._batch_sampler -> _sampler (runtime only)",
    }
    manifest_file = run_dir / "manifest.json"
    write_manifest(manifest_file, manifest)
    original_out, original_err = sys.stdout, sys.stderr
    with (run_dir / "run.log").open("w", encoding="utf-8") as logfile:
        sys.stdout, sys.stderr = Tee(original_out, logfile), Tee(original_err, logfile)
        try:
            print("RUN_DIR:", run_dir, flush=True)
            run(args.section, run_dir, manifest)
            manifest["status"] = "SMOKE_PASS"
        except Exception:
            manifest["status"] = "FAILED"
            traceback.print_exc()
            raise
        finally:
            manifest["finished_at"] = datetime.now().isoformat(timespec="seconds")
            write_manifest(manifest_file, manifest)
            sys.stdout, sys.stderr = original_out, original_err


if __name__ == "__main__":
    main()
