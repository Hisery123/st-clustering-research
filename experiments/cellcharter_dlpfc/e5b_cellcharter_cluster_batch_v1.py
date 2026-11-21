"""E5b frozen CellCharter external clustering: 6 patients x 6 scales x 2 K arms x 3 seeds.

36 unlabeled AutoK runs (K2..10, internally K1..11, five explicitly seeded
fits per K) and 216 separate frozen-parameter CPU CellCharter GMM predictions.
Input is the FINISHED Windows feature batch; NO scVI training; NO reference
labels, ARI or NMI are read or computed in this file. Oracle-K constants are
the prospectively frozen label-count-informed comparator ONLY.

Default is read-only. --run explicitly launches all 36 configuration tasks.
Parent stops at first child failure. --resume SESSION requires explicit action
after diagnosing the failure, preserves all previous attempts and completed
tasks, and never modifies their predictions. Untested on user's Windows.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata as md
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone

ROOT = Path(r"D:\paper\CellCharter_reproduction\results\e5b_external_v1")
FEATURES = ROOT / "features_20261121T090400Z_28460"
PROTOCOL = "E5B_CELLCHARTER_FROZEN_CLUSTER_BATCH_V1"
SAMPLES = ("1142243F", "1160920F", "CID4290",
           "CID4465", "CID44971", "CID4535")
N_SPOTS = (4784, 4895, 2426, 1211, 1160, 1125)
# Only for the explicitly label-count-informed oracle comparator, NEVER AutoK.
ORACLE_K = (5, 7, 3, 3, 6, 6)
CONFIGS = {
    "L0_5D": (0,),
    "L0L1_10D": (0, 1),
    "A_L0L1L2_15D": (0, 1, 2),
    "L0L1L2L3_20D": (0, 1, 2, 3),
    "L0L1L2L3L4_25D": (0, 1, 2, 3, 4),
    "B_L0L1L4_15D": (0, 1, 4),
}
SEEDS = (22911, 7449, 25842)
AUTOK_SEEDS = tuple(range(22911, 22916))
ARMS = ("k_blind", "oracle_k")
K_BOUNDS = (2, 10)
GMM_PARAMS = {
    "covariance_type": "full",
    "init_strategy": "kmeans",
    "convergence_tolerance": 0.001,
    "covariance_regularization": 1e-6,
    "trainer_params": {
        "accelerator": "cpu", "devices": 1, "max_epochs": 100,
        "enable_progress_bar": False,
    },
}

def demand(ok, message):
    if not ok:
        raise RuntimeError(message)

def now():
    return datetime.now(timezone.utc).isoformat()

def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as fd:
        for data in iter(lambda: fd.read(1024*1024), b""):
            h.update(data)
    return h.hexdigest()

def sha_of_bytes(data):
    return hashlib.sha256(data).hexdigest()

def dump(path, value):
    Path(path).write_text(
        json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)+"\n",
        encoding="utf-8")

def load_feature_batch():
    bfile = FEATURES / "batch_status.json"
    demand(bfile.is_file(), "FEATURE_BATCH_STATUS_MISSING " + str(bfile))
    batch = json.loads(bfile.read_text(encoding="utf-8"))
    demand(batch.get("protocol") == "E5B_EXTERNAL_SCVI_FEATURES_FROZEN_V1" and
           batch.get("status") == "completed" and
           batch.get("expected_count") == 6 and
           len(batch.get("completed", [])) == 6 and
           not batch.get("failed"),
           "E5B_FEATURE_BATCH_NOT_SIX_COMPLETE")
    for i, rec in enumerate(batch["completed"]):
        demand(rec.get("sample") == SAMPLES[i],
               "E5B_FEATURE_BATCH_ORDER_CHANGED")
    return sha256(bfile)

def load_source(sample):
    import numpy as np
    import pandas as pd
    idx = SAMPLES.index(sample)
    d = FEATURES / sample
    statefile = d / "status.json"
    demand(statefile.is_file(), "E5B_FEATURE_SAMPLE_STATUS_MISSING " + sample)
    state = json.loads(statefile.read_text(encoding="utf-8"))
    demand(state.get("status") == "completed" and
           state.get("sample") == sample and
           state.get("n_spots") == N_SPOTS[idx] and
           state.get("aggregate_shape") == [N_SPOTS[idx], 25] and
           state.get("latent_shape") == [N_SPOTS[idx], 5] and
           state.get("reference_labels_read") is False,
           "E5B_FEATURE_SAMPLE_NOT_FROZEN " + sample)
    pairs = [
        ("cellcharter_aggregated.npy", "source_25d_sha256"),
        ("scvi_latent.npy", "scvi_latent_sha256"),
        ("spot_order.csv", "spot_order_sha256"),
    ]
    for name, key in pairs:
        path = d / name
        demand(path.is_file() and sha256(path) == state.get(key),
               f"E5B_FEATURE_SHA_MISMATCH {sample} {name}")
    x25 = np.load(d / "cellcharter_aggregated.npy", allow_pickle=False)
    latent = np.load(d / "scvi_latent.npy", allow_pickle=False, mmap_mode="r")
    coords = pd.read_csv(d / "spot_order.csv", dtype={"barcode": str})
    demand(x25.shape == (N_SPOTS[idx], 25) and
           latent.shape == (N_SPOTS[idx], 5) and
           len(coords) == N_SPOTS[idx] and
           coords["barcode"].is_unique and
           np.isfinite(x25).all(),
           "E5B_FEATURE_VALUES_OR_SPOTS_INVALID " + sample)
    # Correctness must not depend on any label file.
    return x25, coords["barcode"].to_numpy(), {
        "feature_status_sha256": sha256(statefile),
        "aggregate_sha256": state["source_25d_sha256"],
        "latent_sha256": state["scvi_latent_sha256"],
        "spot_order_sha256": state["spot_order_sha256"],
    }

def get_blocks(x25, blocks):
    import numpy as np
    columns = [j for block in blocks for j in range(block*5, block*5+5)]
    z = np.asarray(x25[:, columns], dtype=np.float32)
    demand(z.ndim == 2 and z.shape[1] == 5*len(blocks) and
           np.isfinite(z).all(), "SELECTED_FEATURE_VALUES_INVALID")
    return np.ascontiguousarray(z)

def check_versions():
    demand(md.version("cellcharter") == "0.3.2",
           "CELLCHARTER_VERSION_NOT_FROZEN")
    demand(md.version("torchgmm") == "0.1.2",
           "TORCHGMM_VERSION_NOT_FROZEN")

def expected_tasks():
    return [(s, c) for s in SAMPLES for c in CONFIGS]

def verify_attempt(out, sample, condition):
    import pandas as pd
    f = out / "manifest.json"
    demand(f.is_file(), f"E5B_CLUSTER_MANIFEST_MISSING {out}")
    m = json.loads(f.read_text(encoding="utf-8"))
    demand(m.get("status") == "completed" and
           m.get("protocol") == PROTOCOL and
           m.get("sample") == sample and
           m.get("condition") == condition and
           m.get("expected_predictions") == 6,
           "E5B_CLUSTER_CONFIG_NOT_COMPLETE " + str(out))
    pred = m.get("predictions", [])
    demand(len(pred) == 6 and
           [(x.get("arm"), x.get("seed")) for x in pred] ==
           [(a, s) for a in ARMS for s in SEEDS],
           "E5B_CLUSTER_PREDICTION_TASKS_MISMATCH " + str(out))
    for item in pred:
        path = out / item["file"]
        demand(path.is_file() and sha256(path) == item.get("sha256"),
               "E5B_CLUSTER_PREDICTION_SHA_CHANGED " + str(path))
    for name in ("autok_summary.json", "all_k_run_labels.npz"):
        digest = m.get("autok_sha256", {}).get(name)
        demand(digest and sha256(out / name) == digest,
               "E5B_AUTOK_FILE_SHA_CHANGED " + str(out / name))
    return m

def run_config(sample, condition, session):
    import anndata as ad
    import numpy as np
    import pandas as pd
    import torch
    import cellcharter as cc
    from pytorch_lightning import seed_everything
    from pytorch_lightning.overrides.distributed import IndexBatchSamplerWrapper

    check_versions()
    feature_batch_sha = load_feature_batch()
    x25, barcodes, source = load_source(sample)
    blocks = CONFIGS[condition]
    z = get_blocks(x25, blocks)
    index = SAMPLES.index(sample)

    task_root = session / sample / condition
    task_root.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out = task_root / f"attempt_{stamp}_{os.getpid()}"
    demand(not out.exists(), "E5B_CLUSTER_ATTEMPT_EXISTS_NO_OVERWRITE")
    out.mkdir(parents=False, exist_ok=False)
    manifest_file = out / "manifest.json"
    manifest = {
        "status": "running", "protocol": PROTOCOL,
        "sample": sample, "condition": condition, "blocks": list(blocks),
        "feature_dim": int(z.shape[1]), "n_spots": int(z.shape[0]),
        "feature_batch_status_sha256": feature_batch_sha,
        "source": source, "selected_feature_sha256": sha_of_bytes(z.tobytes()),
        "autok": {
            "K_candidates": list(range(2, 11)),
            "internal_K": list(range(1, 12)),
            "max_runs": 5, "convergence_tol": 0.0,
            "seeds": list(AUTOK_SEEDS),
            "device": "cpu",
            "gmm": GMM_PARAMS,
        },
        "arms": list(ARMS), "prediction_seeds": list(SEEDS),
        "oracle_k_is_label_count_informed": True,
        "blind_arm_never_reads_reference_label": True,
        "expected_predictions": 6,
        "predictions": [],
        "versions": {pkg: md.version(pkg) for pkg in
                     ("cellcharter", "torchgmm", "torch", "numpy",
                      "pytorch-lightning", "anndata", "pandas")},
        "started_utc": now(),
    }
    dump(manifest_file, manifest)
    start = time.perf_counter()
    try:
        IndexBatchSamplerWrapper._batch_sampler = property(
            lambda self: self._sampler)
        adata = ad.AnnData(X=np.zeros((len(z), 1), dtype=np.float32))
        adata.obs_names = pd.Index(barcodes.astype(str))
        adata.obsm["X_cellcharter"] = z

        # The same seeded subclass used in frozen DLPFC E3d avoids the
        # confirmed CellCharter 0.3.2 random_state issue during AutoK.
        class SeededGMM(cc.tl.GaussianMixture):
            def fit(self, X):
                seed = int(self.random_state)
                demand(seed in AUTOK_SEEDS,
                       f"UNEXPECTED_AUTOK_RANDOM_SEED {seed}")
                random.seed(seed)
                np.random.seed(seed)
                seed_everything(seed, workers=True)
                return super().fit(X)

        params = dict(GMM_PARAMS)
        params["random_state"] = AUTOK_SEEDS[0]
        print(f"E5B_CC_AUTOK_START sample={sample} condition={condition} "
              f"spots={len(z)} dim={z.shape[1]} K=2..10 runs=5", flush=True)
        autok = cc.tl.ClusterAutoK(
            n_clusters=K_BOUNDS, max_runs=5, convergence_tol=0.0,
            model_class=SeededGMM, model_params=params)
        auto_start = time.perf_counter()
        autok.fit(adata, use_rep="X_cellcharter")
        k_blind = int(autok.best_k)
        demand(2 <= k_blind <= 10 and list(autok.n_clusters) ==
               list(range(1, 12)), "E5B_AUTOK_K_RANGE_MISMATCH")
        for k in range(1, 12):
            demand(len(autok.labels[k]) == 5,
                   f"E5B_AUTOK_FIVE_RUNS_MISSING k={k}")
        stability = np.asarray(autok.stability, dtype=float)
        demand(stability.ndim == 2 and stability.shape[0] == 9 and
               np.isfinite(stability).all(),
               "E5B_AUTOK_STABILITY_INVALID")
        means = np.mean(stability, axis=1)
        demand(k_blind == 2 + int(np.argmax(means)),
               "E5B_AUTOK_BEST_K_NOT_STABILITY_MAX")
        labels = {}
        for k in range(1, 12):
            raw = np.stack(
                [np.asarray(x, dtype=np.int16) for x in autok.labels[k]])
            demand(raw.shape == (5, len(z)) and
                   np.isin(raw, np.arange(k)).all(),
                   f"E5B_AUTOK_LABELS_INVALID k={k}")
            labels[f"k_{k}"] = raw
        np.savez_compressed(out / "all_k_run_labels.npz", **labels)
        summary = {
            "selected_k": k_blind,
            "boundary_hit": k_blind in K_BOUNDS,
            "selection": "unlabeled_stability_argmax_first_max",
            "candidate_K": list(range(2, 11)),
            "internal_K": list(range(1, 12)),
            "runs_per_internal_K": 5,
            "stability_by_k": {
                str(k): {
                    "mean": float(means[k-2]),
                    "values": stability[k-2].tolist()
                } for k in range(2, 11)
            },
            "autok_seconds": round(time.perf_counter()-auto_start, 6),
            "source_feature_sha256": manifest["selected_feature_sha256"],
        }
        dump(out / "autok_summary.json", summary)
        manifest["autok_selected_k"] = k_blind
        manifest["autok_sha256"] = {
            x: sha256(out / x) for x in
            ("autok_summary.json", "all_k_run_labels.npz")}
        dump(manifest_file, manifest)
        print(f"E5B_CC_AUTOK_PASS sample={sample} condition={condition} "
              f"selected_k={k_blind} seconds={summary['autok_seconds']}",
              flush=True)
        del autok

        for arm in ARMS:
            # Oracle comparator explicitly receives the previously frozen
            # true label-category count; this value is NOT used by AutoK.
            target_k = k_blind if arm == "k_blind" else ORACLE_K[index]
            for seed in SEEDS:
                random.seed(seed)
                np.random.seed(seed)
                torch.manual_seed(seed)
                seed_everything(seed, workers=True)
                cluster = cc.tl.Cluster(
                    n_clusters=target_k, random_state=seed,
                    **GMM_PARAMS)
                begin = time.perf_counter()
                cluster.fit(adata)
                predicted = np.asarray(cluster.predict(adata), dtype=np.int64)
                elapsed = time.perf_counter()-begin
                demand(predicted.shape == (len(z),) and
                       np.isin(predicted, np.arange(target_k)).all(),
                       f"E5B_CC_PREDICTION_INVALID {arm} {seed}")
                filename = f"predictions_{arm}_seed{seed}.csv"
                pd.DataFrame({
                    "barcode": barcodes.astype(str),
                    "cluster": predicted,
                }).to_csv(out / filename, index=False)
                record = {
                    "arm": arm, "seed": int(seed),
                    "chosen_k": int(target_k),
                    "actual_k": int(np.unique(predicted).size),
                    "cluster_sizes": np.bincount(
                        predicted, minlength=target_k).tolist(),
                    "file": filename, "sha256": sha256(out / filename),
                    "fit_predict_seconds": round(elapsed, 6),
                    "selection": ("AutoK_unlabeled_stability" if arm == "k_blind"
                                  else "oracle_reference_category_count"),
                }
                manifest["predictions"].append(record)
                dump(manifest_file, manifest)
                print(f"E5B_CC_PREDICTION_PASS sample={sample} "
                      f"condition={condition} arm={arm} seed={seed} "
                      f"k={target_k} actual_k={record['actual_k']}", flush=True)
                del cluster
        demand(len(manifest["predictions"]) == 6,
               "E5B_CC_SIX_PREDICTIONS_MISSING")
        manifest["status"] = "completed"
        manifest["finished_utc"] = now()
        manifest["total_seconds"] = round(time.perf_counter()-start, 6)
        dump(manifest_file, manifest)
        print(f"E5B_CC_CONFIG_PASS sample={sample} condition={condition} "
              f"predictions=6 autok_k={k_blind} "
              f"seconds={manifest['total_seconds']} result={out}", flush=True)
    except BaseException as exc:
        manifest.update({
            "status": "failed", "error": repr(exc),
            "traceback": traceback.format_exc(),
            "failed_utc": now(),
        })
        dump(manifest_file, manifest)
        print(f"E5B_CC_CONFIG_FAILED sample={sample} condition={condition} "
              f"error={exc!r} result={out}", flush=True)
        raise

def execute_batch(session=None):
    feature_batch_sha = load_feature_batch()
    check_versions()
    if session is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        session = ROOT / f"cellcharter_cluster_{stamp}_{os.getpid()}"
        demand(not session.exists(), "E5B_CC_BATCH_OUTPUT_EXISTS")
        session.mkdir(parents=True, exist_ok=False)
        manifest = {
            "status": "running", "protocol": PROTOCOL,
            "feature_batch_dir": str(FEATURES),
            "feature_batch_status_sha256": feature_batch_sha,
            "expected_configs": 36, "expected_predictions": 216,
            "completed_configs": [], "failures": [],
            "started_utc": now(),
            "reference_labels_read": False, "metrics_computed": False,
        }
    else:
        session = Path(session).resolve()
        mf = session / "batch_status.json"
        demand(mf.is_file(), "E5B_CC_RESUME_SESSION_STATUS_MISSING")
        manifest = json.loads(mf.read_text(encoding="utf-8"))
        demand(manifest.get("protocol") == PROTOCOL and
               manifest.get("feature_batch_status_sha256") ==
               feature_batch_sha and
               manifest.get("expected_configs") == 36 and
               manifest.get("expected_predictions") == 216 and
               manifest.get("status") in ("halted", "running"),
               "E5B_CC_RESUME_NOT_ALLOWED")
        manifest["status"] = "running"
        manifest.setdefault("resumed_utc", []).append(now())

    status_file = session / "batch_status.json"
    dump(status_file, manifest)
    done = {(x["sample"], x["condition"]): x for x in
            manifest["completed_configs"]}
    try:
        for sample, condition in expected_tasks():
            task = (sample, condition)
            if task in done:
                verify_attempt(Path(done[task]["attempt"]), sample, condition)
                print(f"E5B_CC_REUSED_VERIFIED sample={sample} "
                      f"condition={condition}", flush=True)
                continue
            print(f"E5B_CC_CONFIG_START sample={sample} "
                  f"condition={condition}", flush=True)
            ret = subprocess.run(
                [sys.executable, str(Path(__file__).resolve()),
                 "--child-sample", sample, "--child-condition", condition,
                 "--session", str(session)],
                check=False)
            demand(ret.returncode == 0,
                   f"E5B_CC_CHILD_FAILED sample={sample} "
                   f"condition={condition} exit_code={ret.returncode}")
            root = session / sample / condition
            attempts = sorted(p for p in root.glob("attempt_*") if p.is_dir())
            candidates = []
            for p in attempts:
                try:
                    m = json.loads((p / "manifest.json").read_text(
                        encoding="utf-8"))
                    if m.get("status") == "completed":
                        candidates.append(p)
                except (OSError, ValueError, KeyError):
                    continue
            demand(len(candidates) == 1,
                   "E5B_CC_COMPLETED_ATTEMPT_AMBIGUITY " + str(root))
            attempt = candidates[0]
            verify_attempt(attempt, sample, condition)
            manifest["completed_configs"].append({
                "sample": sample, "condition": condition,
                "attempt": str(attempt),
                "manifest_sha256": sha256(attempt / "manifest.json"),
                "predictions": 6,
            })
            done[task] = manifest["completed_configs"][-1]
            dump(status_file, manifest)
            print(f"E5B_CC_PROGRESS configs={len(done)}/36 "
                  f"predictions={len(done)*6}/216", flush=True)
        demand(len(done) == 36, "E5B_CC_CONFIG_COUNT_MISMATCH")
        manifest["status"] = "completed"
        manifest["finished_utc"] = now()
        dump(status_file, manifest)
        print(f"E5B_CC_FINAL status=completed configs=36/36 "
              f"predictions=216/216 failed=0 result={status_file}", flush=True)
        print("NO_REFERENCE_LABELS_NO_ARI_NMI_NO_SCVI_RETRAIN", flush=True)
    except BaseException as exc:
        manifest["status"] = "halted"
        manifest["failures"].append({
            "error": repr(exc), "traceback": traceback.format_exc(),
            "time_utc": now()})
        dump(status_file, manifest)
        print(f"E5B_CC_HALTED configs={len(done)}/36 "
              f"error={exc!r} result={status_file}", flush=True)
        raise

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", action="store_true",
                   help="Explicitly fit all 36 configurations and 216 GMM predictions")
    p.add_argument("--resume", metavar="SESSION",
                   help="Explicitly continue a halted session without overwrites")
    p.add_argument("--child-sample", choices=SAMPLES)
    p.add_argument("--child-condition", choices=tuple(CONFIGS))
    p.add_argument("--session")
    args = p.parse_args()
    if args.child_sample or args.child_condition:
        demand(args.child_sample and args.child_condition and args.session and
               not args.run and not args.resume,
               "E5B_CC_INVALID_CHILD_ARGUMENTS")
        run_config(args.child_sample, args.child_condition, Path(args.session))
    elif args.run:
        demand(not args.resume and not args.session,
               "E5B_CC_INVALID_RUN_ARGUMENTS")
        execute_batch()
    elif args.resume:
        demand(not args.run and not args.session,
               "E5B_CC_INVALID_RESUME_ARGUMENTS")
        execute_batch(session=args.resume)
    else:
        print("E5B_CC_DRY_RUN tasks=36 AutoK=36 "
              "GMM_predictions=216; no output and no fitting")
        print("Use --run to start the frozen batch.")

if __name__ == "__main__":
    try:
        main()
    except BaseException as exc:
        print(f"E5B_CC_FATAL {type(exc).__name__}: {exc}",
              file=sys.stderr, flush=True)
        sys.exit(1)
