"""E5b frozen external nonspatial GMM and Leiden baselines (72 predictions).

Six patients x two methods x two K arms x three seeds = 72.
Adapted without method/parameter changes from the audited E5a baseline.
Uses E5b frozen per-patient scVI L0 5D, never DLPFC cached features.
NEVER opens reference_only labels or calculates ARI/NMI.
K-blind GMM: minimum BIC K=2..10. K-blind Leiden: resolution 1.0.
Oracle GMM: externally informed K. Oracle Leiden: nearest K from
16 frozen resolutions (tie smallest resolution). Strict separation.
Default makes no change. --run starts isolated new session, --resume SESSION
continues incomplete tasks without overwriting or restarting successful ones.
Not yet tested on user's Windows.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata as md
import json
import os
from pathlib import Path
import random
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np
import pandas as pd

ROOT = Path(r"D:\paper\CellCharter_reproduction\results\e5b_external_v1")
FEATURES = ROOT / "features_20261121T090400Z_28460"
PROTOCOL = "E5B_NONSPATIAL_GMM_LEIDEN_FROZEN_V1"
SAMPLES = ("1142243F", "1160920F", "CID4290",
           "CID4465", "CID44971", "CID4535")
SPOTS = (4784, 4895, 2426, 1211, 1160, 1125)
ORACLE_K = (5, 7, 3, 3, 6, 6)
SEEDS = (22911, 7449, 25842)
METHODS = ("GMM", "Leiden")
ARMS = ("k_blind", "oracle_k")
K_GRID = tuple(range(2, 11))
RESOLUTIONS = (0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.65,
               0.8, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0)

def demand(ok, message):
    if not ok:
        raise RuntimeError(message)

def now():
    return datetime.now(timezone.utc).isoformat()

def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as fd:
        for chunk in iter(lambda: fd.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()

def dump_json(path, obj):
    Path(path).write_text(
        json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False)+"\n",
        encoding="utf-8")

def feature_status():
    f = FEATURES / "batch_status.json"
    demand(f.is_file(), "E5B_FEATURE_BATCH_STATUS_MISSING")
    b = json.loads(f.read_text(encoding="utf-8"))
    demand(b.get("protocol") == "E5B_EXTERNAL_SCVI_FEATURES_FROZEN_V1"
           and b.get("status") == "completed"
           and len(b.get("completed", [])) == 6
           and [x["sample"] for x in b["completed"]] == list(SAMPLES),
           "E5B_FEATURE_BATCH_NOT_COMPLETED")
    return sha256(f)

def load_features(sample):
    idx = SAMPLES.index(sample)
    d = FEATURES / sample
    statefile = d / "status.json"
    demand(statefile.is_file(), "E5B_FEATURE_SAMPLE_STATUS_MISSING")
    record = json.loads(statefile.read_text(encoding="utf-8"))
    demand(record.get("status") == "completed" and
           record.get("sample") == sample and
           record.get("n_spots") == SPOTS[idx] and
           record.get("latent_shape") == [SPOTS[idx], 5] and
           record.get("aggregate_shape") == [SPOTS[idx], 25],
           "E5B_FEATURE_STATE_INVALID " + sample)
    paths = {
        "scvi_latent.npy": "scvi_latent_sha256",
        "cellcharter_aggregated.npy": "source_25d_sha256",
        "spot_order.csv": "spot_order_sha256",
    }
    for name, key in paths.items():
        demand((d / name).is_file() and
               sha256(d / name) == record.get(key),
               "E5B_FEATURE_SHA_INVALID " + sample + " " + name)
    latent = np.load(d / "scvi_latent.npy", allow_pickle=False)
    aggr = np.load(d / "cellcharter_aggregated.npy", allow_pickle=False,
                   mmap_mode="r")
    coords = pd.read_csv(d / "spot_order.csv", dtype={"barcode": str})
    demand(latent.shape == (SPOTS[idx], 5) and
           aggr.shape == (SPOTS[idx], 25) and
           len(coords) == SPOTS[idx] and
           coords["barcode"].is_unique and
           (coords["barcode"].notna()).all() and
           np.isfinite(latent).all() and
           np.array_equal(latent, np.asarray(aggr[:, :5], dtype=np.float32)),
           "E5B_L0_LATENT_OR_BARCODE_MISMATCH " + sample)
    return np.asarray(latent, dtype=np.float32), coords.barcode.to_numpy(), {
        "sample_status_sha256": sha256(statefile),
        "scvi_latent_sha256": record["scvi_latent_sha256"],
        "25d_sha256": record["source_25d_sha256"],
        "spot_order_sha256": record["spot_order_sha256"],
    }

def fit_gmm(z, seed, arm, oracle_k):
    from sklearn.mixture import GaussianMixture
    params = dict(covariance_type="full", tol=0.001, reg_covar=1e-6,
                  max_iter=100, n_init=1, init_params="kmeans",
                  random_state=seed)
    grid = K_GRID if arm == "k_blind" else (oracle_k,)
    trial = []
    selected_labels = {}
    for k in grid:
        start = time.perf_counter()
        model = GaussianMixture(n_components=k, **params)
        pred = model.fit_predict(z)
        bic = float(model.bic(z))
        demand(np.isfinite(bic), "E5B_GMM_BIC_NONFINITE")
        trial.append({
            "k": int(k), "bic": bic,
            "converged": bool(model.converged_),
            "n_iter": int(model.n_iter_),
            "fit_seconds": round(time.perf_counter()-start, 6),
        })
        selected_labels[k] = pred.astype(np.int64)
    k_selected = min(trial, key=lambda x: (x["bic"], x["k"]))["k"]
    return selected_labels[k_selected], {
        "selection": ("minimum_BIC" if arm == "k_blind"
                      else "reference_category_count_oracle"),
        "selected_k": k_selected,
        "actual_k": int(np.unique(selected_labels[k_selected]).size),
        "candidate_results": trial, "model_params": params,
    }

def fit_leiden(z, seed, arm, oracle_k):
    import anndata as ad
    import scanpy as sc
    dummy = ad.AnnData(X=np.zeros((len(z), 1), dtype=np.float32))
    dummy.obsm["X_scvi_l0"] = z
    sc.pp.neighbors(dummy, n_neighbors=15, n_pcs=None,
                    use_rep="X_scvi_l0", random_state=seed)
    grid = RESOLUTIONS if arm == "oracle_k" else (1.0,)
    trials = []
    for resolution in grid:
        start = time.perf_counter()
        sc.tl.leiden(dummy, resolution=resolution, key_added="_e5b_leiden",
                     random_state=seed, flavor="leidenalg",
                     n_iterations=-1, directed=False)
        raw = dummy.obs["_e5b_leiden"].astype(str).to_numpy()
        trials.append({
            "resolution": resolution,
            "actual_k": int(np.unique(raw).size),
            "fit_seconds": round(time.perf_counter()-start, 6),
            "labels": raw.copy(),
        })
    choice = (min(trials, key=lambda x:
                  (abs(x["actual_k"]-oracle_k), x["resolution"]))
              if arm == "oracle_k" else trials[0])
    raw = choice["labels"]
    unique = sorted(set(raw), key=lambda x: int(x))
    mapper = {lab: i for i, lab in enumerate(unique)}
    labels = np.array([mapper[x] for x in raw], dtype=np.int64)
    return labels, {
        "selection": ("nearest_known_K_on_frozen_resolution_grid"
                      if arm == "oracle_k" else
                      "fixed_resolution_without_reference_labels"),
        "selected_resolution": choice["resolution"],
        "actual_k": int(np.unique(labels).size),
        "candidate_results": [
            {k: v for k, v in row.items() if k != "labels"}
            for row in trials],
        "graph_n_neighbors": 15, "flavor": "leidenalg",
        "resolution_grid": list(grid),
    }

def tasks():
    return [(sample, method, arm, seed)
            for sample in SAMPLES for method in METHODS
            for arm in ARMS for seed in SEEDS]

def verify_done(path, target):
    manifest_file = path / "manifest.json"
    demand(manifest_file.is_file(), "E5B_EXISTING_MANIFEST_MISSING")
    rec = json.loads(manifest_file.read_text(encoding="utf-8"))
    demand(rec.get("status") == "completed" and
           rec.get("protocol") == PROTOCOL and
           tuple(rec.get("task", [])) == tuple(target),
           "E5B_EXISTING_TASK_NOT_COMPLETED")
    pred = path / "predictions.csv"
    demand(pred.is_file() and rec.get("prediction_sha256") == sha256(pred),
           "E5B_EXISTING_PREDICTION_SHA_BAD")
    return rec

def execute(session=None):
    batch_sha = feature_status()
    if session is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        session = ROOT / f"nonspatial_{stamp}_{os.getpid()}"
        demand(not session.exists(), "E5B_NONSPATIAL_SESSION_EXISTS")
        session.mkdir(parents=True, exist_ok=False)
        state = {
            "status": "running", "protocol": PROTOCOL,
            "feature_batch_sha256": batch_sha,
            "expected": 72, "completed": [],
            "failures": [], "started_utc": now(),
            "reference_labels_used": False, "metrics_computed": False,
            "methods": list(METHODS), "seeds": list(SEEDS),
            "regimes": list(ARMS), "kblind_gmm_candidates": list(K_GRID),
            "leiden_oracle_resolution_grid": list(RESOLUTIONS),
        }
    else:
        session = Path(session).resolve()
        sf = session / "batch_status.json"
        demand(sf.is_file(), "E5B_NONSPATIAL_RESUME_STATUS_MISSING")
        state = json.loads(sf.read_text(encoding="utf-8"))
        demand(state.get("protocol") == PROTOCOL and
               state.get("feature_batch_sha256") == batch_sha and
               state.get("status") == "halted" and
               state.get("expected") == 72,
               "E5B_NONSPATIAL_RESUME_NOT_ALLOWED")
        state["status"] = "running"
        state.setdefault("resume_utc", []).append(now())
    sf = session / "batch_status.json"
    dump_json(sf, state)
    completed = {tuple(x["task"]): x for x in state["completed"]}
    start = time.perf_counter()
    active_sample = None
    z = bc = provenance = None
    try:
        for sample, method, arm, seed in tasks():
            task = (sample, method, arm, seed)
            if task in completed:
                verify_done(Path(completed[task]["path"]), task)
                print(f"E5B_NONSPATIAL_REUSED task={task}", flush=True)
                continue
            if sample != active_sample:
                z, bc, provenance = load_features(sample)
                active_sample = sample
            folder = session / sample / method / arm / f"seed_{seed}"
            demand(not folder.exists(), "E5B_TASK_OUTPUT_EXISTS "+str(folder))
            folder.mkdir(parents=True, exist_ok=False)
            manifest = folder / "manifest.json"
            rec = {
                "status": "running", "protocol": PROTOCOL, "task": list(task),
                "sample": sample, "method": method, "arm": arm, "seed": seed,
                "n_spots": len(z), "input": provenance,
                "reference_labels_used": False,
                "oracle_k_is_label_count_informed": arm == "oracle_k",
                "started_utc": now(), "versions": {
                    pkg: md.version(pkg) for pkg in
                    ("numpy", "pandas", "scikit-learn", "scanpy", "anndata")},
            }
            dump_json(manifest, rec)
            t0 = time.perf_counter()
            print(f"E5B_NONSPATIAL_TASK_START "
                  f"num={len(completed)+1}/72 sample={sample} method={method} "
                  f"arm={arm} seed={seed}", flush=True)
            try:
                random.seed(seed)
                np.random.seed(seed)
                oracle_k = ORACLE_K[SAMPLES.index(sample)] if arm == "oracle_k" else None
                if method == "GMM":
                    labels, details = fit_gmm(z, seed, arm, oracle_k)
                else:
                    labels, details = fit_leiden(z, seed, arm, oracle_k)
                demand(labels.shape == (len(z),) and
                       np.issubdtype(labels.dtype, np.integer) and
                       len(np.unique(labels)) >= 1,
                       "E5B_NONSPATIAL_PREDICTION_SHAPE_BAD")
                pd.DataFrame({"barcode": bc, "cluster": labels}).to_csv(
                    folder / "predictions.csv", index=False)
                rec.update({
                    "status": "completed", "details": details,
                    "n_actual_k": int(np.unique(labels).size),
                    "prediction_sha256": sha256(folder / "predictions.csv"),
                    "wall_seconds": round(time.perf_counter()-t0, 6),
                    "completed_utc": now(),
                })
                dump_json(manifest, rec)
                verify_done(folder, task)
                state["completed"].append({
                    "task": list(task), "path": str(folder),
                    "manifest_sha256": sha256(manifest)})
                completed[task] = state["completed"][-1]
                dump_json(sf, state)
                print(f"E5B_NONSPATIAL_PASS completed={len(completed)}/72 "
                      f"sample={sample} method={method} arm={arm} "
                      f"seed={seed} actual_k={rec['n_actual_k']}",
                      flush=True)
            except BaseException as exc:
                rec.update({"status": "failed", "error": repr(exc),
                            "traceback": traceback.format_exc(),
                            "failed_utc": now()})
                dump_json(manifest, rec)
                raise
        demand(len(completed) == 72, "E5B_NONSPATIAL_TASK_COUNT_INCOMPLETE")
        state["status"] = "completed"
        state["completed_utc"] = now()
        state["wall_seconds_total"] = round(time.perf_counter()-start, 6)
        dump_json(sf, state)
        print(f"E5B_NONSPATIAL_FINAL status=completed completed=72/72 "
              f"failed=0 result={sf}", flush=True)
        print("NO_REFERENCE_LABELS_NO_ARI_NMI_NO_SCVI_RETRAIN", flush=True)
    except BaseException as exc:
        state["status"] = "halted"
        state["failures"].append({
            "error": repr(exc), "traceback": traceback.format_exc(),
            "when": now()})
        dump_json(sf, state)
        print(f"E5B_NONSPATIAL_HALTED completed={len(completed)}/72 "
              f"error={exc!r} result={sf}", flush=True)
        raise

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", action="store_true")
    p.add_argument("--resume", metavar="SESSION")
    args = p.parse_args()
    demand(not (args.run and args.resume), "E5B_NONSPATIAL_INVALID_ARGS")
    if args.run:
        execute()
    elif args.resume:
        execute(args.resume)
    else:
        print("E5B_NONSPATIAL_DRY_RUN patients=6 methods=GMM,Leiden "
              "arms=k_blind,oracle_k seeds=3 tasks=72 "
              "NO_FILES_WRITTEN_NO_TRAINING")

if __name__ == "__main__":
    try:
        main()
    except BaseException as exc:
        print(f"E5B_NONSPATIAL_FATAL {type(exc).__name__}: {exc}",
              file=sys.stderr, flush=True)
        sys.exit(1)
