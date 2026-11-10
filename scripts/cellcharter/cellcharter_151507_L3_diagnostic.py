"""L3-only CellCharter diagnostic (151507, seed22911).

Uses the already trained scVI latent. Never retrains scVI or overwrites results.
Same geometry / clustering as cellcharter_151507_baseline_v032.py.
This script is newly prepared AFTER the L0/L1/L2/L4 experiments.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
import traceback

import numpy as np
import pandas as pd
import scanpy as sc
import squidpy as sq
import cellcharter as cc
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score
from pytorch_lightning.overrides.distributed import IndexBatchSamplerWrapper


DATA = Path(r"D:\paper\ST_Benchmark_Planning\mvp\data\151507")
RESULTS = Path(r"D:\paper\CellCharter_reproduction\results")
BASELINE = RESULTS / "cellcharter_v032_151507_seed22911_oracleK7"
OUT = RESULTS / "cellcharter_v032_151507_seed22911_L3_diagnostic"
SEED = 22911


def boundary_metrics(pred, truth, graph, valid):
    upper = (graph + graph.T).tocsr()
    upper.data[:] = 1
    upper.setdiag(0)
    upper.eliminate_zeros()
    import scipy.sparse as sp
    i, j = sp.triu(upper, k=1).nonzero()
    keep = valid[i] & valid[j]
    i, j = i[keep], j[keep]
    y = truth.to_numpy()
    actual = y[i] != y[j]
    estimated = pred[i] != pred[j]
    tp = int(np.count_nonzero(actual & estimated))
    fp = int(np.count_nonzero(~actual & estimated))
    fn = int(np.count_nonzero(actual & ~estimated))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    pair = ((y[i] == "Layer 5") & (y[j] == "Layer 6")) | ((y[i] == "Layer 6") & (y[j] == "Layer 5"))
    pair_count = int(np.count_nonzero(pair))
    pair_found = int(np.count_nonzero(pair & estimated))
    if int(actual.sum()) != 950 or pair_count != 145:
        raise ValueError(f"Unexpected reference boundary counts: {actual.sum()}, L5/L6={pair_count}")
    return dict(
        boundary_reference_edges=int(actual.sum()), boundary_tp=tp, boundary_fp=fp,
        boundary_fn=fn, boundary_precision=precision, boundary_recall=recall,
        boundary_f1=f1, l5_l6_reference_edges=pair_count,
        l5_l6_detected_edges=pair_found,
        l5_l6_boundary_recall=pair_found / pair_count,
        eligible_undirected_edges=len(i),
    )


def main():
    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite L3 directory: {OUT}")
    for file in (DATA / "filtered_feature_bc_matrix.h5", DATA / "spots_aligned.csv",
                 DATA / "manual_layer_annotations.csv", BASELINE / "scvi_latent.npy"):
        if not file.is_file():
            raise FileNotFoundError(file)
    np.random.seed(SEED)
    print("L3_INPUT_START", flush=True)
    adata = sc.read_10x_h5(str(DATA / "filtered_feature_bc_matrix.h5"))
    positions = pd.read_csv(DATA / "spots_aligned.csv")
    if adata.shape != (4226, 33538) or len(positions) != 4226:
        raise ValueError(f"Unexpected input shape {adata.shape}, positions={len(positions)}")
    if not np.array_equal(adata.obs_names.to_numpy(), positions["barcode"].to_numpy()):
        raise ValueError("Barcode/row alignment mismatch")
    r = positions["array_row"].to_numpy(dtype=int)
    c = positions["array_col"].to_numpy(dtype=int)
    adata.obsm["spatial"] = np.column_stack((c.astype(float), np.sqrt(3.) * r))
    sq.gr.spatial_neighbors(adata, coord_type="grid", n_neighs=6, n_rings=1)
    graph = adata.obsp["spatial_connectivities"].tocsr()
    gi, gj = graph.nonzero()
    dr, dc = np.abs(r[gi] - r[gj]), np.abs(c[gi] - c[gj])
    geom_ok = ((dr == 0) & (dc == 2)) | ((dr == 1) & (dc == 1))
    if graph.nnz != 24770 or (graph != graph.T).nnz or not geom_ok.all():
        raise ValueError("Reconstructed spatial graph failed baseline audit")
    z = np.load(BASELINE / "scvi_latent.npy", allow_pickle=False)
    if z.shape != (4226, 5) or not np.isfinite(z).all():
        raise ValueError(f"Latent invalid: {z.shape}")
    adata.obsm["X_scVI"] = z.astype(np.float32, copy=False)
    cc.gr.aggregate_neighbors(adata, n_layers=3, use_rep="X_scVI")
    aggregate = np.asarray(adata.obsm["X_cellcharter"])
    if aggregate.shape != (4226, 20) or not np.isfinite(aggregate).all():
        raise ValueError(f"Aggregate invalid: {aggregate.shape}")
    print("L3_AGGREGATION_PASS", aggregate.shape, flush=True)

    OUT.mkdir(parents=True, exist_ok=False)
    config = dict(method="CellCharter", version="0.3.2", sample="151507",
                  seed=SEED, n_layers=3, feature_dim=20, n_clusters=7,
                  k_selection="oracle/manual label count", embedding="reuse baseline scvi_latent.npy",
                  graph="reconstructed Visium six-neighbor hex grid",
                  gmm="CellCharter TorchGMM CPU; Lightning compatibility shim",
                  script="scripts/cellcharter/cellcharter_151507_L3_diagnostic.py",
                  note="Newly written script; not historical L0/L1/L2 execution code")
    (OUT / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    try:
        IndexBatchSamplerWrapper._batch_sampler = property(lambda self: self._sampler)
        model = cc.tl.Cluster(n_clusters=7, random_state=SEED,
                              trainer_params={"accelerator": "cpu", "devices": 1,
                                              "enable_progress_bar": False})
        print("L3_GMM_START", flush=True)
        model.fit(adata)
        pred = np.asarray(model.predict(adata)).astype(int)
        if pred.shape != (4226,) or len(np.unique(pred)) != 7:
            raise ValueError("Unexpected predicted clusters")
        pd.DataFrame(dict(sample_name="151507", barcode=adata.obs_names.to_numpy(),
                          cluster=pred, array_row=r, array_col=c)).to_csv(
                              OUT / "predictions.csv", index=False)
        manual = pd.read_csv(DATA / "manual_layer_annotations.csv")
        manual = manual.loc[manual["sample_name"].astype(str) == "151507",
                            ["spot_name", "layer"]]
        if manual["spot_name"].duplicated().any():
            raise ValueError("Repeated barcodes within 151507 annotations")
        truth = manual.set_index("spot_name")["layer"].reindex(adata.obs_names)
        valid = truth.notna().to_numpy()
        if valid.sum() != 4221:
            raise ValueError(f"Expected 4221 labeled spots, found {valid.sum()}")
        results = dict(status="completed", sample="151507", seed=SEED,
                       condition="L3_neighborhood_aggregation_diagnostic", n_layers=3,
                       feature_dim=20, n_clusters=7, n_evaluated=int(valid.sum()),
                       cluster_sizes=np.bincount(pred).tolist(),
                       ari=float(adjusted_rand_score(truth.to_numpy()[valid], pred[valid])),
                       nmi=float(normalized_mutual_info_score(truth.to_numpy()[valid], pred[valid])),
                       **boundary_metrics(pred, truth, graph, valid),
                       end_utc=datetime.now(timezone.utc).isoformat())
        (OUT / "metrics.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
        (OUT / "status.json").write_text(json.dumps({"status": "completed"}, indent=2), encoding="utf-8")
        print("L3_DIAGNOSTIC_COMPLETE", json.dumps(results, ensure_ascii=False), flush=True)
        print("RESULT_DIR", OUT, flush=True)
    except BaseException as exc:
        (OUT / "status.json").write_text(
            json.dumps(dict(status="failed", error=repr(exc), traceback=traceback.format_exc()),
                       indent=2), encoding="utf-8")
        raise


if __name__ == "__main__":
    main()
