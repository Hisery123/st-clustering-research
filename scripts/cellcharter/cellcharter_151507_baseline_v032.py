"""CellCharter v0.3.2 DLPFC 151507 single-section baseline.

Adapted from CSOgroup/cellcharter_analyses/src/benchmarking/CellCharter/individual.py.
Important differences: raw 10x H5 + verified hex-grid reconstruction instead of
published preprocessed .h5ad; v0.3.2 TorchGMM instead of v0.2.0 PyCave;
explicit CPU-only GMM compatibility shim for Lightning 1.9.5.

Evaluation protocol: oracle K=7 is from the paper's manual annotation count.
No manually annotated label is accessed until AFTER all training and predictions.
151507 is a development section, NOT an independent held-out test.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
from pathlib import Path
import platform
import traceback


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true", help="Read/check raw inputs and exit without creating results/training")
    args = parser.parse_args()

    import numpy as np
    import pandas as pd
    import scanpy as sc
    import squidpy as sq
    import scvi
    import cellcharter as cc
    import torch
    from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score
    from pytorch_lightning.overrides.distributed import IndexBatchSamplerWrapper

    data_dir = Path(r"D:\paper\ST_Benchmark_Planning\mvp\data\151507")
    output_dir = Path(r"D:\paper\CellCharter_reproduction\results\cellcharter_v032_151507_seed22911_oracleK7")
    raw_h5 = data_dir / "filtered_feature_bc_matrix.h5"
    aligned_path = data_dir / "spots_aligned.csv"
    manual_path = data_dir / "manual_layer_annotations.csv"
    seed = 22911  # first seed from np.random.default_rng(12345).integers(0,32768,size=10)

    for p in (raw_h5, aligned_path, manual_path):
        if not p.is_file():
            raise FileNotFoundError(p)

    print("READING_INPUT", flush=True)
    adata = sc.read_10x_h5(str(raw_h5))
    positions = pd.read_csv(aligned_path)
    assert adata.shape == (4226, 33538), f"Unexpected raw shape: {adata.shape}"
    assert len(positions) == adata.n_obs
    assert positions["barcode"].is_unique
    assert np.array_equal(adata.obs_names.to_numpy(), positions["barcode"].to_numpy())
    assert (positions["in_tissue"] == 1).all(), "Unexpected non-tissue spot"
    assert positions[["array_row", "array_col"]].notna().all().all()

    r = positions["array_row"].to_numpy(dtype=int)
    c = positions["array_col"].to_numpy(dtype=int)
    adata.obsm["spatial"] = np.column_stack((c.astype(float), np.sqrt(3.0)*r))
    sq.gr.spatial_neighbors(adata, coord_type="grid", n_neighs=6, n_rings=1)
    graph = adata.obsp["spatial_connectivities"].tocsr()
    row_ix, col_ix = graph.nonzero()
    dr = np.abs(r[row_ix] - r[col_ix]); dc = np.abs(c[row_ix] - c[col_ix])
    correct_geom = ((dr == 0) & (dc == 2)) | ((dr == 1) & (dc == 1))
    assert graph.shape == (4226, 4226)
    assert graph.nnz > 0 and correct_geom.all() and (graph != graph.T).nnz == 0
    assert np.diff(graph.indptr).max() <= 6
    print(f"GRAPH_PASS edges={graph.nnz}", flush=True)

    # Use this only as a consistency check. Do not load the annotation layer for model selection.
    if args.check_only:
        print("INPUT_AND_GRAPH_CHECK_PASS; NO_TRAINING; NO_FILES_WRITTEN", flush=True)
        return

    if output_dir.exists():
        raise FileExistsError(f"Refusing to overwrite a previous experiment: {output_dir}")
    output_dir.mkdir(parents=True)
    status_path = output_dir / "status.json"
    config_path = output_dir / "config.json"

    config = {
        "method": "CellCharter", "version": "0.3.2", "sample": "151507",
        "protocol": "single-section development baseline; oracle K=7 (label-count supplied)",
        "source": "https://github.com/CSOgroup/cellcharter_analyses/blob/main/src/benchmarking/CellCharter/individual.py",
        "differences_from_paper": [
            "raw 10x H5 and geometric graph reconstruction instead of author's preprocessed h5ad",
            "CellCharter 0.3.2 uses TorchGMM rather than original 0.2.0 PyCave",
            "temporary Lightning<2.0 TorchGMM DataLoader compatibility shim",
            "one of ten official seeded repeats (first seed only)",
        ],
        "hvg": 5000, "hvg_flavor": "seurat_v3", "scvi_latent": 5,
        "neighbors": 4, "n_clusters": 7, "k_selection": "oracle from manual label count (author protocol)",
        "seed": seed, "scvi_max_epochs": 400, "scvi_early_stopping": True,
        "scvi_optimizer": "AdamW", "scvi_reduce_lr_on_plateau": True,
        "gmm_compute": "cpu", "device": str(torch.cuda.get_device_name(0)) if torch.cuda.is_available() else "none",
        "packages": {k: importlib.metadata.version(k) for k in (
            "cellcharter", "torchgmm", "torch", "scvi-tools", "squidpy",
            "scanpy", "anndata", "pytorch-lightning", "numpy", "scikit-learn")},
        "python": platform.python_version(), "raw_data_path": str(raw_h5),
        "result_directory": str(output_dir),
    }
    config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
    status_path.write_text(json.dumps({"status": "running", "start_utc": datetime.now(timezone.utc).isoformat()}), encoding="utf-8")
    try:
        print("PREPROCESS_START", flush=True)
        adata.var_names_make_unique()
        sc.pp.filter_genes(adata, min_counts=3)
        sc.pp.filter_cells(adata, min_counts=3)
        assert adata.n_obs == 4226, "Filtered spot count changed; revisit label/coordinate correspondence"
        adata.layers["counts"] = adata.X.copy()
        sc.pp.normalize_total(adata, target_sum=1e6)
        sc.pp.log1p(adata)
        sc.pp.highly_variable_genes(
            adata, n_top_genes=5000, subset=True,
            layer="counts", flavor="seurat_v3")
        assert adata.shape == (4226, 5000)
        print("PREPROCESS_PASS", adata.shape, flush=True)

        np.random.seed(seed)
        scvi.settings.seed = seed
        scvi.model.SCVI.setup_anndata(adata, layer="counts")
        model = scvi.model.SCVI(adata, n_latent=5)
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA not available; abort rather than silently changing protocol")
        torch.cuda.reset_peak_memory_stats(0)
        print("FULL_SCVI_TRAIN_START", flush=True)
        model.train(
            max_epochs=400, use_gpu=True, early_stopping=True,
            plan_kwargs={"optimizer": "AdamW", "reduce_lr_on_plateau": True})
        assert model.trainer.strategy.root_device.type == "cuda"
        print("FULL_SCVI_TRAIN_FINISHED", flush=True)
        z = model.get_latent_representation(adata).astype(np.float32)
        assert z.shape == (4226, 5) and np.isfinite(z).all()
        adata.obsm["X_scVI"] = z
        np.save(output_dir / "scvi_latent.npy", z)
        model.save(str(output_dir / "scvi_model"), overwrite=False, save_anndata=False)

        cc.gr.aggregate_neighbors(adata, n_layers=4, use_rep="X_scVI")
        aggr = adata.obsm["X_cellcharter"]
        assert aggr.shape == (4226, 25) and np.isfinite(aggr).all()
        np.save(output_dir / "cellcharter_aggregated.npy", aggr)
        print("AGGREGATION_PASS", aggr.shape, flush=True)

        # Only the shim below is needed for the known Lightning-1.9/TorchGMM-0.1.2 issue.
        IndexBatchSamplerWrapper._batch_sampler = property(lambda self: self._sampler)
        cluster_model = cc.tl.Cluster(
            n_clusters=7, random_state=seed,
            trainer_params={"accelerator": "cpu", "devices": 1, "enable_progress_bar": False})
        cluster_model.fit(adata)
        pred = np.asarray(cluster_model.predict(adata)).astype(int)
        assert pred.shape == (4226,) and len(np.unique(pred)) == 7
        print("GMM_PREDICTION_PASS", np.unique(pred, return_counts=True)[1].tolist(), flush=True)
        pd.DataFrame({
            "sample_name": "151507", "barcode": adata.obs_names.to_numpy(),
            "cluster": pred, "array_row": r, "array_col": c,
        }).to_csv(output_dir / "predictions.csv", index=False)

        # Manual labels are read ONLY after model fitting and predicting.
        manual = pd.read_csv(manual_path)
        manual = manual.loc[manual["sample_name"].astype(str) == "151507", ["spot_name", "layer"]]
        assert not manual["spot_name"].duplicated().any()
        truth = manual.set_index("spot_name")["layer"].reindex(adata.obs_names)
        assert truth.notna().sum() == 4221
        mask = truth.notna().to_numpy()
        ari = adjusted_rand_score(truth.to_numpy()[mask], pred[mask])
        nmi = normalized_mutual_info_score(truth.to_numpy()[mask], pred[mask])
        result = {
            "status": "completed", "sample": "151507", "seed": seed,
            "n_spots_total": 4226, "n_spots_evaluated": int(mask.sum()),
            "n_clusters_oracle": 7, "k_selection": "manual annotation count; NOT label-free selection",
            "ari": float(ari), "nmi": float(nmi),
            "peak_torch_cuda_allocated_mib": round(torch.cuda.max_memory_allocated(0)/1048576, 2),
            "end_utc": datetime.now(timezone.utc).isoformat(),
        }
        (output_dir / "metrics.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        status_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        print("BASELINE_COMPLETE", f"ARI={ari:.6f}", f"NMI={nmi:.6f}", flush=True)
        print("RESULT_DIR", output_dir, flush=True)
    except BaseException as exc:
        failure = {"status": "failed", "error": repr(exc), "traceback": traceback.format_exc(),
                   "end_utc": datetime.now(timezone.utc).isoformat()}
        status_path.write_text(json.dumps(failure, indent=2, ensure_ascii=False), encoding="utf-8")
        raise


if __name__ == "__main__":
    main()
