"""Frozen E5a non-spatial control baseline: GMM and Leiden on original scVI L0 5D.

Single batch 12 DLPFC slices x 2 methods x 2 K regimes x 3 seeds = 144
successful tasks expected. K-blind never accesses annotations before finishing all
fittings of each task; only subsequent ARI/NMI evaluation opens reference labels.
No training of scVI or CellCharter, no modification of any earlier results.

Usage: python e5a_nonspatial_baselines_batch_v1.py [--run]
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata as md
import json
import os
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
SAMPLES = ("151507", "151508", "151509", "151510", "151669", "151670",
           "151671", "151672", "151673", "151674", "151675", "151676")
SEEDS = (22911, 7449, 25842)
METHODS = ("GMM", "Leiden")
K_ARMS = ("oracle_k", "k_blind")
K_LIST = tuple(range(2, 11))
RESOLUTIONS = (0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.65,
               0.8, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0)
ORACLE_K = {sample: (5 if sample in {"151669", "151670", "151671", "151672"}
                     else 7) for sample in SAMPLES}
SPOTS_N = (4226,4384,4789,4634,3661,3498,4110,4015,3639,3673,3592,3460)
EXTRA_SOURCE_SHA = {"151507":"15b1fd58d092277f81fa2a1513bb2fbf865eea71b1b7450a9a2f710c941a8f54", "151508":"094f702ba7fae32fc69c6c8026acb5765bd7bcd39b2802fbe8091b26baba60ee"}
EXPECTED_N = dict(zip(SAMPLES, SPOTS_N))
EXPECTED_LABELED = dict(zip(SAMPLES, (4221,4381,4788,4595,3636,3484,
                                          4093,3888,3611,3635,3566,3431)))
PROTOCOL = "E5A_NONSPATIAL_4BASELINE_PLAN_V1"


def ensure(cond, message):
    if not cond:
        raise ValueError(message)


def stamp():
    return datetime.now(timezone.utc).isoformat()


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


def dump_json(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2,
                                    allow_nan=False) + "\n", encoding="utf-8")


def source_path(sample):
    if sample == "151507":
        return RESULT_ROOT / "cellcharter_v032_151507_seed22911_oracleK7", "predictions.csv"
    if sample == "151508":
        return RESULT_ROOT / "cellcharter_151508_scvi22911_features_v2", "spot_order.csv"
    return RESULT_ROOT / f"cellcharter_{sample}_scvi22911_features_batch_v1", "spot_order.csv"


def get_features(sample):
    source, order_file = source_path(sample)
    feature_path = source / "cellcharter_aggregated.npy"
    status_path = source / "status.json"
    order_path = source / order_file
    coords_path = DATA_ROOT / sample / "spots_aligned.csv"
    for item in (feature_path, status_path, order_path, coords_path):
        ensure(item.is_file(), "FROZEN_FEATURE_INPUT_MISSING " + str(item))
    status = json.loads(status_path.read_text(encoding="utf-8"))
    ensure(status.get("status") == "completed", "FROZEN_SOURCE_NOT_COMPLETE")
    if sample in EXTRA_SOURCE_SHA:
        ensure(sha256(feature_path) == EXTRA_SOURCE_SHA[sample], "FROZEN_SOURCE_SHA_CHANGED")
    else:
        ensure(status.get("sample") == sample, "FROZEN_SOURCE_SAMPLE_BAD")
        ensure(status.get("aggregate_sha256") == sha256(feature_path),
               "FROZEN_SOURCE_SHA_CHANGED")
    spots = pd.read_csv(coords_path, dtype={"barcode": str})
    order = pd.read_csv(order_path, dtype={"barcode": str})
    ensure("barcode" in spots.columns and "barcode" in order.columns,
           "FROZEN_BARCODES_COLUMN_MISSING")
    ensure(len(spots) == EXPECTED_N[sample] == len(order),
           "FROZEN_SOURCE_SPOT_COUNT_CHANGED")
    ensure(spots.barcode.is_unique and order.barcode.is_unique, "DUPLICATE_BARCODES")
    ensure(np.array_equal(spots.barcode.to_numpy(), order.barcode.to_numpy()),
           "FROZEN_BARCODES_ORDER_MISMATCH")
    z25 = np.load(feature_path, allow_pickle=False, mmap_mode="r")
    ensure(z25.shape == (len(spots), 25) and z25.dtype == np.float32,
           "FROZEN_FEATURE_MATRIX_SHAPE_BAD")
    z = np.array(z25[:, :5], copy=True, dtype=np.float32)
    ensure(np.isfinite(z).all(), "FROZEN_FEATURES_NONFINITE")
    return z, spots.barcode.to_numpy(), {
        "source_25d_path": str(feature_path),
        "source_25d_sha256": sha256(feature_path),
        "source_spot_order_sha256": sha256(order_path),
        "source_spots_sha256": sha256(coords_path),
        "scvi_5d_sha256": hashlib.sha256(z.tobytes()).hexdigest(),
        "source_sample_status_sha256": sha256(status_path),
    }


def gmm_fit(z, seed, regime, oracle_k):
    from sklearn.mixture import GaussianMixture
    kwargs = {"covariance_type": "full", "tol": 0.001, "reg_covar": 1e-6,
              "max_iter": 100, "n_init": 1, "init_params": "kmeans",
              "random_state": seed}
    grid = K_LIST if regime == "k_blind" else (oracle_k,)
    candidates = []
    labels_by_k = {}
    for k in grid:
        begin = time.perf_counter()
        model = GaussianMixture(n_components=k, **kwargs)
        partition = model.fit_predict(z)
        bic = float(model.bic(z))
        ensure(np.isfinite(bic), "GMM_BIC_NONFINITE")
        candidates.append({"k": k, "bic": bic, "converged": bool(model.converged_),
                           "n_iter": int(model.n_iter_),
                           "fit_seconds": round(time.perf_counter()-begin, 4)})
        labels_by_k[k] = partition.astype(int)
    selected_k = min(candidates, key=lambda c: (c["bic"], c["k"]))["k"]
    return labels_by_k[selected_k], {"selected_k": selected_k,
                                     "selection": "minimum_BIC" if regime=="k_blind"
                                                  else "reference_category_count_oracle",
                                     "candidate_results": candidates,
                                     "actual_k": int(np.unique(labels_by_k[selected_k]).size),
                                     "model_params": kwargs}


def leiden_fit(z, seed, regime, oracle_k):
    import anndata as ad
    import scanpy as sc
    # Only 5D nonspatial scVI; zero gene expression and no spatial input.
    adata = ad.AnnData(X=np.zeros((len(z), 1), dtype=np.float32))
    adata.obsm["X_scvi_l0"] = z
    sc.pp.neighbors(adata, n_neighbors=15, n_pcs=None,
                    use_rep="X_scvi_l0", random_state=seed)
    grid = RESOLUTIONS if regime == "oracle_k" else (1.0,)
    trials = []
    for resolution in grid:
        begin = time.perf_counter()
        sc.tl.leiden(adata, resolution=resolution, key_added="_e5a_leiden",
                     random_state=seed, flavor="leidenalg", n_iterations=-1,
                     directed=False)
        labels = adata.obs["_e5a_leiden"].astype(str).to_numpy()
        n_clusters = int(np.unique(labels).size)
        trials.append({"resolution": resolution, "actual_k": n_clusters,
                       "fit_seconds": round(time.perf_counter()-begin, 4),
                       "labels": labels.copy()})
    if regime == "oracle_k":
        picked = min(trials, key=lambda x: (abs(x["actual_k"]-oracle_k), x["resolution"]))
    else:
        picked = trials[0]
    labels = picked["labels"]
    unique = sorted(set(labels), key=lambda x: int(x))
    mapper = {key:i for i,key in enumerate(unique)}
    numeric = np.asarray([mapper[x] for x in labels], dtype=int)
    reports = [{k:v for k,v in t.items() if k!="labels"} for t in trials]
    return numeric, {"selected_resolution": picked["resolution"],
                     "actual_k": int(np.unique(numeric).size),
                     "selection": "nearest_known_K_on_frozen_resolution_grid"
                     if regime == "oracle_k" else "fixed_resolution_without_reference_labels",
                     "candidate_results": reports,
                     "graph_n_neighbors": 15, "flavor": "leidenalg"}


def evaluate_after_fit(sample, barcodes, labels):
    from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score
    file = DATA_ROOT / sample / "manual_layer_annotations.csv"
    ensure(file.is_file(), "REFERENCE_LABEL_FILE_MISSING")
    ann = pd.read_csv(file, dtype={"sample_name":str, "spot_name":str, "layer":str})
    subset = ann.loc[ann["sample_name"]==sample, ["spot_name", "layer"]]
    ensure(subset.spot_name.is_unique and subset.layer.notna().all(),
           "REFERENCE_DUPLICATES_OR_NA")
    truth = subset.set_index("spot_name").reindex(barcodes)["layer"]
    valid = truth.notna().to_numpy()
    ensure(int(valid.sum()) == EXPECTED_LABELED[sample], "REFERENCE_MASK_CHANGED")
    ensure(truth[valid].nunique() == ORACLE_K[sample], "REFERENCE_K_CHANGED")
    ensure(len(labels) == len(barcodes), "PREDICTION_LENGTH_BAD")
    return {"ari":float(adjusted_rand_score(truth[valid], labels[valid])),
            "nmi":float(normalized_mutual_info_score(truth[valid], labels[valid])),
            "n_labeled":int(valid.sum()), "n_unlabeled":int((~valid).sum()),
            "reference_path":str(file), "reference_sha256":sha256(file)}


def execute():
    import sklearn
    import scanpy as sc
    import anndata as ad
    ensure(len(SAMPLES) == 12 and len(K_ARMS) == 2 and len(SEEDS) == 3,
           "FROZEN_TASK_GRID_BAD")
    phase_dir = RESULT_ROOT / "e5a_baselines_v1"
    session_name = "nonspatial_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + str(os.getpid())
    session = phase_dir / session_name
    ensure(not session.exists(), "E5A_SESSION_ALREADY_EXISTS")
    session.mkdir(parents=True, exist_ok=False)
    status_file = session / "batch_status.json"
    completed, failures = 0, []
    status = {
        "protocol":PROTOCOL, "status":"running", "started_utc":stamp(),
        "sample_list": SAMPLES, "seed_list": SEEDS, "methods": METHODS,
        "regimes": K_ARMS, "expected_tasks":144,
        "reference_label_policy":"only_postfit_evaluation",
        "leiden_resolution_grid":RESOLUTIONS, "gmm_blind_grid":K_LIST,
        "oracle_k":ORACLE_K, "tasks":[],
        "environment": {"python":sys.version, "sklearn":sklearn.__version__,
                        "scanpy":sc.__version__, "anndata":ad.__version__},
    }
    dump_json(status_file,status)
    task_num = 0
    for sample in SAMPLES:
        source_error = None
        try:
            z, barcodes, provenance = get_features(sample)
        except Exception as exc:
            z, barcodes, provenance = None, None, None
            source_error = repr(exc)
        for method in METHODS:
            for regime in K_ARMS:
                for seed in SEEDS:
                    task_num += 1
                    folder = session / sample / method / regime / f"seed_{seed}"
                    folder.mkdir(parents=True, exist_ok=False)
                    label_path = folder / "predictions.csv"
                    manifest_file = folder / "manifest.json"
                    begin = time.perf_counter()
                    rec = {"sample": sample, "method": method, "regime": regime,
                           "seed": seed, "oracle_k_prior": ORACLE_K[sample],
                           "start_utc":stamp(), "status":"running"}
                    dump_json(manifest_file, rec)
                    print(f"E5A_NONSPATIAL_START {task_num}/144 sample={sample} "
                          f"method={method} regime={regime} seed={seed}",flush=True)
                    try:
                        ensure(source_error is None,
                               "SOURCE_LOAD_FAILED " + str(source_error))
                        random.seed(seed); np.random.seed(seed)
                        if method == "GMM":
                            labels, details = gmm_fit(z,seed,regime,ORACLE_K[sample])
                        else:
                            labels, details = leiden_fit(z,seed,regime,ORACLE_K[sample])
                        ensure(labels.shape == (len(barcodes),) and
                               np.issubdtype(labels.dtype,np.integer),
                               "PREDICTION_SHAPE_OR_TYPE_BAD")
                        pd.DataFrame({"barcode":barcodes,
                                      "cluster":labels}).to_csv(label_path,index=False)
                        predsha = sha256(label_path)
                        # IMPORTANT: reference layer labels are not read above this line.
                        metrics = evaluate_after_fit(sample,barcodes,labels)
                        rec.update({
                            "status":"completed", "n_spots":len(z),
                            "selected_or_actual_k":int(np.unique(labels).size),
                            "prediction_file":str(label_path),
                            "prediction_sha256":predsha,
                            "details":details,"metrics":metrics,
                            "input":provenance,
                            "wall_seconds":round(time.perf_counter()-begin,6),
                            "finish_utc":stamp(),
                        })
                        completed += 1
                        print(f"E5A_NONSPATIAL_PASS {task_num}/144 "
                              f"sample={sample} method={method} regime={regime} "
                              f"seed={seed} actual_k={rec['selected_or_actual_k']} "
                              f"seconds={rec['wall_seconds']}",flush=True)
                    except Exception as exc:
                        rec.update({"status":"failed", "error":repr(exc),
                                    "traceback":traceback.format_exc(),
                                    "wall_seconds":round(time.perf_counter()-begin,6),
                                    "finish_utc":stamp()})
                        failures.append({"sample":sample, "method":method,
                                         "regime":regime,"seed":seed,
                                         "error":repr(exc)})
                        print(f"E5A_NONSPATIAL_FAIL {task_num}/144 "
                              f"sample={sample} method={method} regime={regime} "
                              f"seed={seed} error={exc!r}",flush=True)
                    dump_json(manifest_file,rec)
                    status["tasks"].append({"sample":sample,"method":method,
                                            "regime":regime,"seed":seed,
                                            "status":rec["status"],
                                            "manifest":str(manifest_file)})
                    status["completed"] = completed
                    status["failed"] = len(failures)
                    dump_json(status_file,status)
        del z
    status["status"] = "completed" if completed==144 and not failures else "partial"
    status["finish_utc"] = stamp()
    status["failures"] = failures
    dump_json(status_file,status)
    print(f"E5A_NONSPATIAL_FINAL status={status['status']} "
          f"completed={completed}/144 failed={len(failures)} "
          f"summary={status_file}",flush=True)
    return 0 if status["status"]=="completed" else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run",action="store_true",
                        help="Execute all 12x2x2x3 tasks, preserving originals")
    args = parser.parse_args()
    if not args.run:
        print("E5A_NONSPATIAL_PLAN samples=12 methods=GMM,Leiden "
              "regimes=oracle_k,k_blind seeds=3 tasks=144")
        print("E5A_NONSPATIAL_DRY_RUN_ONLY NO_TRAINING_NO_FILES_WRITTEN")
        return 0
    return execute()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"E5A_NONSPATIAL_FATAL {type(exc).__name__}: {exc}",
              file=sys.stderr,flush=True)
        sys.exit(1)