"""E5b Wu 2021 frozen six-patient scVI-5D + CellCharter-25D feature batch.

Only --run fits models; default prints guidance and changes no files.
Use staged counts+barcodes+positions, NEVER read reference_only/Classification.
Separate child process for each sample, fail-closed, no implicit retraining/retry.
No GMM/Leiden/BANKSY/BayesSpace predictions, no ARI/NMI in this phase.
Built from frozen E5b protocol and working DLPFC feature preparation precedent.
Not yet tested on user's Windows system.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(r"D:\paper\CellCharter_reproduction")
STAGE = BASE / "results" / "e5b_external_v1" / "input_stage_20261121T083911Z_14272"
ROOT = BASE / "results" / "e5b_external_v1"
SAMPLES = ("1142243F", "1160920F", "CID4290",
           "CID4465", "CID44971", "CID4535")
SPOTS = (4784, 4895, 2426, 1211, 1160, 1125)
GENES = (28402, 28402, 19237, 19237, 19237, 19237)
SEED = 22911
PROTOCOL = "E5B_EXTERNAL_SCVI_FEATURES_FROZEN_V1"

def demand(condition, message):
    if not condition:
        raise RuntimeError(message)

def now():
    return datetime.now(timezone.utc).isoformat()

def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as fd:
        for data in iter(lambda: fd.read(1024 * 1024), b""):
            h.update(data)
    return h.hexdigest()

def write_json(path, obj):
    Path(path).write_text(
        json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8")

def read_stage():
    status_file = STAGE / "batch_status.json"
    demand(status_file.is_file(), "E5B_STAGE_STATUS_MISSING")
    status = json.loads(status_file.read_text(encoding="utf-8"))
    demand(status.get("status") == "completed", "E5B_STAGE_NOT_COMPLETED")
    demand(status.get("no_training") is True and
           status.get("no_metric_computation") is True,
           "E5B_STAGE_SOURCE_NOT_LABEL_BLIND")
    demand(status.get("total_model_spots") == 15601 and
           status.get("total_eval_spots") == 15324,
           "E5B_STAGE_TOTAL_MISMATCH")
    rows = status.get("samples", [])
    demand([x.get("sample") for x in rows] == list(SAMPLES),
           "E5B_STAGE_SAMPLE_ORDER_MISMATCH")
    for x, n, genes in zip(rows, SPOTS, GENES):
        demand(x.get("model_spots") == n and
               x.get("matrix_shape_gene_spot", [None])[0] == genes,
               "E5B_STAGE_SHAPE_MISMATCH " + x["sample"])
    return status

def check_input_sha(source, stage_entry):
    files = ("matrix.mtx", "barcodes.tsv", "features.tsv", "model_spots.csv")
    for name in files:
        path = source / name
        demand(path.is_file(), "E5B_STAGE_FILE_MISSING " + str(path))
        expected = stage_entry["input_files_sha256"].get(name)
        demand(expected and sha256(path) == expected,
               "E5B_STAGE_INPUT_SHA_MISMATCH " + str(path))

def fit_sample(sample, session):
    import numpy as np
    import pandas as pd
    import anndata as ad
    import scanpy as sc
    import squidpy as sq
    import scvi
    import cellcharter as cc
    import torch
    from scipy import sparse
    from scipy.io import mmread

    stage = read_stage()
    expected_index = SAMPLES.index(sample)
    info = stage["samples"][expected_index]
    source = STAGE / "inputs" / sample
    check_input_sha(source, info)
    spots_expected = SPOTS[expected_index]
    genes_expected = GENES[expected_index]
    out = session / sample
    demand(not out.exists(), "E5B_SAMPLE_RESULT_EXISTS_NO_OVERWRITE " + str(out))

    if not torch.cuda.is_available():
        raise RuntimeError("E5B_GPU_NOT_AVAILABLE_DO_NOT_FALLBACK")
    torch.cuda.init()
    torch.empty(1, device="cuda:0")
    torch.cuda.synchronize(0)

    # MatrixMarket is genes x barcodes, AnnData requires barcodes x genes.
    positions = pd.read_csv(source / "model_spots.csv",
                            dtype={"barcode": str})
    barcodes = pd.read_csv(source / "barcodes.tsv",
                           sep="\t", header=None, dtype=str)[0].astype(str).tolist()
    feats = pd.read_csv(source / "features.tsv",
                        sep="\t", header=None, dtype=str)
    demand(feats.shape[0] == genes_expected and feats.shape[1] in (2, 3),
           "E5B_FEATURES_TABLE_BAD " + sample)
    x = mmread(str(source / "matrix.mtx"))
    demand(sparse.issparse(x) and x.shape ==
           (genes_expected, len(barcodes)),
           "E5B_MATRIX_SHAPE_BAD " + sample)
    x = x.T.tocsr().astype(np.float32)
    demand(x.shape[0] == len(barcodes) and
           len(barcodes) >= spots_expected and x.data.size > 0 and
           np.isfinite(x.data).all() and (x.data >= 0).all(),
           "E5B_SPARSE_COUNTS_BAD " + sample)
    demand(len(set(barcodes)) == len(barcodes) and
           positions.barcode.is_unique and len(positions) == spots_expected and
           set(positions.barcode) <= set(barcodes),
           "E5B_SPOT_BARCODE_MISMATCH " + sample)
    index = pd.Index(barcodes).get_indexer(positions.barcode)
    demand((index >= 0).all(), "E5B_POSITION_INDEX_MISSING " + sample)
    x = x[index].copy()
    demand(x.shape == (spots_expected, genes_expected),
           "E5B_MODEL_SPOT_SHAPE_CHANGED")
    demand(np.all(x.getnnz(axis=1) > 0), "E5B_EMPTY_MODEL_SPOT")

    gene_symbols = feats.iloc[:, 1].fillna("").astype(str)
    demand((gene_symbols.str.strip() != "").all(),
           "E5B_GENE_SYMBOL_MISSING")
    adata = ad.AnnData(X=x)
    adata.obs_names = pd.Index(positions["barcode"].tolist(), dtype=str)
    adata.var_names = pd.Index(gene_symbols.tolist(), dtype=str)
    adata.var["gene_ids"] = feats.iloc[:, 0].astype(str).values
    adata.var_names_make_unique()

    r_float = positions["array_row"].to_numpy(dtype=float)
    c_float = positions["array_col"].to_numpy(dtype=float)
    demand(np.isfinite(r_float).all() and np.isfinite(c_float).all() and
           np.all(r_float == r_float.astype(np.int64)) and
           np.all(c_float == c_float.astype(np.int64)),
           "E5B_GRID_COORDINATES_NONINTEGRAL " + sample)
    row = r_float.astype(np.int64)
    col = c_float.astype(np.int64)
    adata.obsm["spatial"] = np.column_stack(
        (col.astype(float), np.sqrt(3.0) * row.astype(float)))
    sq.gr.spatial_neighbors(adata, coord_type="grid",
                            n_neighs=6, n_rings=1)
    graph = adata.obsp["spatial_connectivities"].tocsr()
    ii, jj = graph.nonzero()
    dr = np.abs(row[ii] - row[jj])
    dc = np.abs(col[ii] - col[jj])
    expected_geometry = ((dr == 0) & (dc == 2)) | ((dr == 1) & (dc == 1))
    demand(graph.shape == (spots_expected, spots_expected) and
           graph.nnz > 0 and expected_geometry.all() and
           (graph != graph.T).nnz == 0 and
           np.diff(graph.indptr).max() <= 6,
           "E5B_HEX_NEIGHBOR_GRAPH_BAD " + sample)
    print(f"E5B_GRAPH_PASS sample={sample} "
          f"spots={spots_expected} edges={graph.nnz//2}", flush=True)

    # Preserve the DLPFC adapted protocol, including its exact preprocessing.
    sc.pp.filter_genes(adata, min_counts=3)
    sc.pp.filter_cells(adata, min_counts=3)
    demand(adata.n_obs == spots_expected,
           "E5B_CELL_FILTER_CHANGED_FROZEN_MODEL_SPOTS " + sample)
    demand(adata.n_vars >= 5000, "E5B_INSUFFICIENT_GENES " + sample)
    adata.layers["counts"] = adata.X.copy()
    sc.pp.normalize_total(adata, target_sum=1e6)
    sc.pp.log1p(adata)
    sc.pp.highly_variable_genes(adata, n_top_genes=5000, subset=True,
                                 layer="counts", flavor="seurat_v3")
    demand(adata.shape == (spots_expected, 5000),
           "E5B_HVG_COUNT_CHANGED " + sample)
    print(f"E5B_PREPROCESS_PASS sample={sample} "
          f"spots={adata.n_obs} hvg={adata.n_vars}", flush=True)

    out.mkdir(parents=True, exist_ok=False)
    status_path = out / "status.json"
    cfg = {
        "protocol": PROTOCOL, "sample": sample,
        "source_stage": str(STAGE),
        "source_stage_status_sha256": sha256(STAGE / "batch_status.json"),
        "source_sha256": dict(info["input_files_sha256"]),
        "n_spots": spots_expected, "n_genes_raw": genes_expected,
        "expected_hvg": 5000, "latent_dims": 5, "layers": 4,
        "scvi": {"seed": SEED, "max_epochs": 400, "early_stopping": True,
                 "optimizer": "AdamW", "reduce_lr_on_plateau": True,
                 "use_gpu": True},
        "graph": {"coord_type": "grid", "n_neighs": 6, "n_rings": 1,
                  "edges_undirected": int(graph.nnz//2)},
        "versions": {name: importlib.metadata.version(name) for name in
                     ("cellcharter", "scvi-tools", "scanpy", "squidpy",
                      "anndata", "torch", "numpy", "scipy")},
        "python": platform.python_version(),
        "started_utc": now(), "reference_labels_read": False,
        "no_metric_computation": True,
    }
    write_json(out / "config.json", cfg)
    write_json(status_path, {"status": "running", "sample": sample})
    start = time.perf_counter()
    try:
        np.random.seed(SEED)
        scvi.settings.seed = SEED
        scvi.model.SCVI.setup_anndata(adata, layer="counts")
        model = scvi.model.SCVI(adata, n_latent=5)
        try:
            torch.cuda.reset_peak_memory_stats(0)
            mem_tracking = True
        except RuntimeError as exc:
            print(f"E5B_CUDA_MEMORY_STATS_WARNING sample={sample} error={exc!r}",
                  flush=True)
            mem_tracking = False
        print(f"E5B_SCVI_TRAIN_START sample={sample} seed={SEED} "
              f"gpu={torch.cuda.get_device_name(0)}", flush=True)
        model.train(max_epochs=400, use_gpu=True, early_stopping=True,
                    plan_kwargs={"optimizer": "AdamW",
                                 "reduce_lr_on_plateau": True})
        demand(model.trainer.strategy.root_device.type == "cuda",
               "E5B_SCVI_NOT_TRAINED_ON_GPU " + sample)
        z = np.asarray(model.get_latent_representation(adata), dtype=np.float32)
        demand(z.shape == (spots_expected, 5) and np.isfinite(z).all(),
               "E5B_SCVI_LATENT_BAD " + sample)
        adata.obsm["X_scVI"] = z
        cc.gr.aggregate_neighbors(adata, n_layers=4, use_rep="X_scVI")
        z25 = np.asarray(adata.obsm["X_cellcharter"], dtype=np.float32)
        demand(z25.shape == (spots_expected, 25) and np.isfinite(z25).all(),
               "E5B_AGGREGATE_25D_BAD " + sample)

        np.save(out / "scvi_latent.npy", z, allow_pickle=False)
        np.save(out / "cellcharter_aggregated.npy", z25, allow_pickle=False)
        positions.to_csv(out / "spot_order.csv", index=False)
        model.save(str(out / "scvi_model"), overwrite=False,
                   save_anndata=False)
        result = {
            "status": "completed", "sample": sample,
            "n_spots": spots_expected, "n_hvg": 5000,
            "latent_shape": list(z.shape), "aggregate_shape": list(z25.shape),
            "source_stage": str(STAGE), "elapsed_seconds": round(
                time.perf_counter() - start, 3),
            "edges_undirected": int(graph.nnz//2),
            "gpu_peak_allocated_mib": (
                round(torch.cuda.max_memory_allocated(0) / 1048576, 2)
                if mem_tracking else None),
            "source_25d_sha256": sha256(out / "cellcharter_aggregated.npy"),
            "scvi_latent_sha256": sha256(out / "scvi_latent.npy"),
            "spot_order_sha256": sha256(out / "spot_order.csv"),
            "completed_utc": now(), "reference_labels_read": False,
            "no_ari_or_nmi": True,
        }
        write_json(status_path, result)
        print(f"E5B_FEATURE_SAMPLE_PASS sample={sample} "
              f"spots={spots_expected} latent=5D aggregated=25D "
              f"seconds={result['elapsed_seconds']}", flush=True)
    except BaseException as exc:
        write_json(status_path, {
            "status": "failed", "sample": sample, "error": repr(exc),
            "traceback": traceback.format_exc(),
            "failed_utc": now(),
        })
        raise

def execute_batch():
    stage = read_stage()
    import torch
    demand(torch.cuda.is_available(), "E5B_GPU_NOT_AVAILABLE_DO_NOT_RUN")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    session = ROOT / f"features_{stamp}_{os.getpid()}"
    demand(not session.exists(), "E5B_BATCH_ALREADY_EXISTS")
    session.mkdir(parents=True, exist_ok=False)
    status_file = session / "batch_status.json"
    batch = {
        "protocol": PROTOCOL, "status": "running",
        "stage": str(STAGE), "stage_status_sha256":
            sha256(STAGE / "batch_status.json"),
        "expected_samples": list(SAMPLES),
        "expected_count": len(SAMPLES), "completed": [],
        "failed": [], "started_utc": now(),
        "method": "scVI5D_CellCharter25D_features_only",
    }
    write_json(status_file, batch)
    try:
        for sample in SAMPLES:
            print(f"E5B_FEATURE_SAMPLE_START sample={sample}", flush=True)
            ret = subprocess.run(
                [sys.executable, str(Path(__file__).resolve()),
                 "--sample", sample, "--session", str(session)],
                check=False,
            )
            demand(ret.returncode == 0,
                   f"E5B_CHILD_FAILURE sample={sample} exit={ret.returncode}")
            report_file = session / sample / "status.json"
            demand(report_file.is_file(), "E5B_FEATURE_SAMPLE_STATUS_MISSING")
            record = json.loads(report_file.read_text(encoding="utf-8"))
            demand(record.get("status") == "completed" and
                   record.get("sample") == sample,
                   "E5B_FEATURE_SAMPLE_NOT_COMPLETED")
            for key, filename in [
                ("scvi_latent_sha256", "scvi_latent.npy"),
                ("source_25d_sha256", "cellcharter_aggregated.npy"),
                ("spot_order_sha256", "spot_order.csv"),
            ]:
                demand(sha256(session / sample / filename) == record[key],
                       "E5B_FEATURE_SHA_MISMATCH " + sample)
            batch["completed"].append({
                "sample": sample, "status_path": str(report_file),
                "latent_sha256": record["scvi_latent_sha256"],
                "aggregate_sha256": record["source_25d_sha256"],
            })
            write_json(status_file, batch)
            print(f"E5B_FEATURE_PROGRESS completed={len(batch['completed'])}/6",
                  flush=True)
        batch["status"] = "completed"
        batch["completed_utc"] = now()
        write_json(status_file, batch)
        print(f"E5B_FEATURE_FINAL status=completed completed=6/6 "
              f"failed=0 result={status_file}", flush=True)
        print("NO_GMM_NO_ARI_NMI", flush=True)
    except BaseException as exc:
        batch["status"] = "failed"
        batch["failed"].append({"error": repr(exc),
                                "traceback": traceback.format_exc()})
        batch["failed_utc"] = now()
        write_json(status_file, batch)
        print(f"E5B_FEATURE_HALTED completed={len(batch['completed'])}/6 "
              f"error={exc!r} result={status_file}", flush=True)
        raise

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--sample", choices=SAMPLES)
    parser.add_argument("--session")
    args = parser.parse_args()
    if args.sample:
        demand(args.session and not args.run, "E5B_INVALID_CHILD_ARGS")
        fit_sample(args.sample, Path(args.session))
    elif args.run:
        demand(not args.session, "E5B_INVALID_PARENT_ARGS")
        execute_batch()
    else:
        print("E5B_FEATURE_NO_ACTION: pass --run to fit six patient-specific "
              "scVI models in isolated child processes")

if __name__ == "__main__":
    main()
