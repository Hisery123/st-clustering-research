"""E3d prospectively fixed unlabeled AutoK: ONE sample x ONE scale per --run.

DEFAULT IS READ-ONLY. Formal CPU main protocol: K 2..10, internally 1..11,
max_runs=5 with explicit seeds 22911..22915, no early stability stopping.
No reference layer labels are read for K selection or fitting.
The user runs on Windows. Do not touch E1/E2/E3c/pilot outputs.
This script has not been tested on the user's Windows environment yet.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import importlib.metadata as md
import json
import os
import random
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
EXPECTED_E3C_SHA256 = "c3bbe996e8bf5f13775a193061fc4b654d9317170e0dca14b7792c429cd77cca"
SAMPLES = ("151507", "151508", "151509", "151510", "151669", "151670",
           "151671", "151672", "151673", "151674", "151675", "151676")
CONDITIONS = {
    "cum_L0_L1": (0, 1),
    "cum_L0_L1_L2": (0, 1, 2),
    "cum_L0_L1_L2_L3": (0, 1, 2, 3),
    "cum_L0_L1_L2_L3_L4": (0, 1, 2, 3, 4),
}
BASE_SEED = 22911
K_BOUNDS = (2, 10)
MAX_RUNS = 5
PROTOCOL = "E3D_AUTOK_FIXED_CPU_V1"


def demand(ok, msg):
    if not ok:
        raise RuntimeError(msg)


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as fd:
        for block in iter(lambda: fd.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def import_module(path, alias):
    spec = importlib.util.spec_from_file_location(alias, path)
    demand(spec and spec.loader, f"IMPORT_FAILED {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def now():
    return datetime.now(timezone.utc).isoformat()


def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def preflight(sample, condition):
    import numpy as np
    e3c_path = BASE / "e3c_k_sensitivity_single_task_v1.py"
    demand(e3c_path.is_file(), f"FROZEN_E3C_SOURCE_MISSING {e3c_path}")
    demand(sha256(e3c_path) == EXPECTED_E3C_SHA256,
           f"FROZEN_E3C_SHA_MISMATCH {sha256(e3c_path)}")
    e3 = import_module(e3c_path, "e3d_fixed_e3c")
    e1 = e3.source_check(BASE)
    demand(sample in e3.SAMPLES and sample in SAMPLES, "UNKNOWN_SAMPLE")
    demand(condition in e3.CONDITIONS and condition in CONDITIONS, "UNKNOWN_CONDITION")
    demand(e3.CONDITIONS[condition] == CONDITIONS[condition], "FEATURE_CONDITION_MISMATCH")
    info = e1.preflight(sample, condition, BASE_SEED)
    data = np.asarray(info["selected"], dtype=np.float32)
    expected_dim = 5 * len(CONDITIONS[condition])
    demand(info["feature_dim"] == expected_dim, "EXPECTED_FEATURE_DIM_MISMATCH")
    demand(data.shape == (info["n"], expected_dim), "FEATURE_SHAPE_MISMATCH")
    demand(np.isfinite(data).all(), "NONFINITE_DATA")
    return e1, e3, info, data


def run_one(sample, condition, e1, info, data):
    import numpy as np
    import pandas as pd
    import anndata as ad
    import cellcharter as cc
    from pytorch_lightning import seed_everything
    from pytorch_lightning.overrides.distributed import IndexBatchSamplerWrapper

    class SeededGMM(cc.tl.GaussianMixture):
        def fit(self, X):
            seed = int(self.random_state)
            demand(BASE_SEED <= seed < BASE_SEED + MAX_RUNS,
                   f"UNEXPECTED_RANDOM_SEED {seed}")
            random.seed(seed)
            np.random.seed(seed)
            seed_everything(seed, workers=True)
            return super().fit(X)

    IndexBatchSamplerWrapper._batch_sampler = property(lambda self: self._sampler)

    out = e1.RESULT_ROOT / "e3d_autok_fixed_v1" / sample / condition
    demand(not out.exists(), f"OUTPUT_EXISTS_NO_OVERWRITE {out}")
    out.mkdir(parents=True, exist_ok=False)
    manifest = {
        "status": "running", "protocol": PROTOCOL, "started_utc": now(),
        "sample": sample, "condition": condition, "n_spots": int(len(data)),
        "feature_dim": int(data.shape[1]),
        "source_sha256": info["source_sha256"],
        "feature_sha256": info["feature_sha256"],
        "positions_sha256": info["position_sha256"],
        "frozen_e3c_source_sha256": EXPECTED_E3C_SHA256,
        "device": "cpu", "K_candidates": list(range(K_BOUNDS[0], K_BOUNDS[1]+1)),
        "internal_K": list(range(K_BOUNDS[0]-1, K_BOUNDS[1]+2)),
        "max_runs": MAX_RUNS, "stability_convergence_tol": 0.0,
        "seed_policy": "explicit_before_every_gmm_fit",
        "seeds": list(range(BASE_SEED, BASE_SEED+MAX_RUNS)),
        "reference_labels_used_for_selection": False,
        "gmm": {
            "covariance_type": "full", "init_strategy": "kmeans",
            "convergence_tolerance": 0.001,
            "covariance_regularization": 1e-6,
            "trainer_params": {
                "accelerator": "cpu", "devices": 1,
                "max_epochs": 100, "enable_progress_bar": False,
            },
        },
        "versions": {n: md.version(n) for n in
                     ("cellcharter", "torchgmm", "torch", "pytorch-lightning", "numpy")},
    }
    mf = out / "manifest.json"
    write_json(mf, manifest)
    try:
        adata = ad.AnnData(X=np.zeros((len(data), 1), dtype=np.float32))
        adata.obs_names = pd.Index(info["positions"]["barcode"].astype(str).to_numpy())
        adata.obsm["X_cellcharter"] = data
        model_params = dict(manifest["gmm"])
        model_params["random_state"] = BASE_SEED
        model = cc.tl.ClusterAutoK(
            n_clusters=K_BOUNDS, max_runs=MAX_RUNS, convergence_tol=0.0,
            model_class=SeededGMM, model_params=model_params,
        )
        start = time.perf_counter()
        print(f"E3D_FIXED_FIT_START sample={sample} condition={condition} "
              f"K={K_BOUNDS} internal_K=1..11 runs={MAX_RUNS} cpu_only=True", flush=True)
        model.fit(adata, use_rep="X_cellcharter")
        best_k = int(model.best_k)
        demand(K_BOUNDS[0] <= best_k <= K_BOUNDS[1], "INVALID_AUTO_K")
        demand(list(model.n_clusters) == manifest["internal_K"], "INTERNAL_K_MISMATCH")
        for k in manifest["internal_K"]:
            demand(len(model.labels[k]) == MAX_RUNS,
                   f"REPETITION_COUNT_MISMATCH k={k}")
        stability = np.asarray(model.stability, dtype=float)
        demand(stability.ndim == 2 and stability.shape[0] == len(manifest["K_candidates"]),
               f"STABILITY_SHAPE_MISMATCH {stability.shape}")
        demand(np.isfinite(stability).all(), "NONFINITE_STABILITY")
        predicted = np.asarray(model.predict(adata, use_rep="X_cellcharter"), dtype=int)
        demand(predicted.shape == (len(data),), "PREDICTION_SHAPE_MISMATCH")
        demand(np.isin(predicted, np.arange(best_k)).all(), "INVALID_PREDICTION_CLASSES")
        file_pred = out / "predictions.csv"
        pd.DataFrame({"barcode": adata.obs_names, "cluster": predicted}).to_csv(
            file_pred, index=False)
        label_files = {}
        raw_labels = {}
        for k in manifest["internal_K"]:
            labels = np.stack([np.asarray(x, dtype=np.int16) for x in model.labels[k]])
            demand(labels.shape == (MAX_RUNS, len(data)), f"BAD_LABEL_SHAPE k={k}")
            demand(np.isin(labels, np.arange(k)).all(), f"INVALID_LABEL k={k}")
            raw_labels[f"k_{k}"] = labels
        label_archive = out / "all_k_run_labels.npz"
        np.savez_compressed(label_archive, **raw_labels)
        stability_means = np.mean(stability, axis=1)
        # Exact expected first-max tie policy from CellCharter implementation.
        demand(int(manifest["K_candidates"][int(np.argmax(stability_means))]) == best_k,
               "AUTOK_STABILITY_ARGMAX_MISMATCH")
        per_k = {str(k): {
            "mean": float(stability_means[i]),
            "values": stability[i].tolist(),
        } for i, k in enumerate(manifest["K_candidates"])}
        summary = {
            "status": "completed", "selected_k": best_k,
            "boundary_hit": best_k in K_BOUNDS,
            "stability_by_K": per_k,
            "all_model_runs": {str(k): len(model.labels[k]) for k in manifest["internal_K"]},
            "best_models": {str(k): {
                "converged": bool(getattr(model.best_models[k], "converged_", False)),
                "num_iter": (None if getattr(model.best_models[k], "num_iter_", None) is None
                             else int(model.best_models[k].num_iter_)),
                "nll": float(getattr(model.best_models[k], "nll_", float("nan"))),
            } for k in manifest["internal_K"]},
            "fit_predict_seconds": round(time.perf_counter()-start, 6),
            "prediction_sha256": sha256(file_pred),
            "all_k_run_labels_sha256": sha256(label_archive),
        }
        demand(all(np.isfinite(v["nll"]) for v in summary["best_models"].values()),
               "NONFINITE_BEST_MODEL_NLL")
        write_json(out / "autok_summary.json", summary)
        manifest["status"] = "completed"
        manifest["selected_k"] = best_k
        manifest["fit_predict_seconds"] = summary["fit_predict_seconds"]
        manifest["prediction_sha256"] = summary["prediction_sha256"]
        manifest["all_k_run_labels_sha256"] = summary["all_k_run_labels_sha256"]
        manifest["finished_utc"] = now()
        write_json(mf, manifest)
        print(f"E3D_FIXED_TASK_COMPLETE sample={sample} condition={condition} "
              f"selected_k={best_k} seconds={summary['fit_predict_seconds']:.2f} "
              f"output={out}", flush=True)
        return 0
    except BaseException as exc:
        manifest["status"] = "failed"
        manifest["error"] = repr(exc)
        manifest["traceback"] = traceback.format_exc()
        manifest["finished_utc"] = now()
        write_json(mf, manifest)
        print(f"E3D_FIXED_TASK_FAILED {exc!r} output={out}", flush=True)
        return 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", choices=SAMPLES, default="151509")
    parser.add_argument("--condition", choices=list(CONDITIONS), default="cum_L0_L1_L2")
    parser.add_argument("--run", action="store_true", help="fit exactly 1 sample x 1 scale")
    args = parser.parse_args()
    import torch
    demand(md.version("cellcharter") == "0.3.2", "UNEXPECTED_CELLCHARTER_VERSION")
    demand(md.version("torchgmm") == "0.1.2", "UNEXPECTED_TORCHGMM_VERSION")
    e1, _, info, data = preflight(args.sample, args.condition)
    print(f"E3D_FIXED_PREFLIGHT_PASS sample={args.sample} condition={args.condition} "
          f"spots={len(data)} dim={data.shape[1]} cuda={torch.cuda.is_available()} "
          f"feature_sha256={info['feature_sha256']}", flush=True)
    if not args.run:
        print("DRY_RUN_ONLY NO_TRAINING_NO_FILES_WRITTEN", flush=True)
        return 0
    return run_one(args.sample, args.condition, e1, info, data)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BaseException as e:
        print(f"E3D_FIXED_PREFLIGHT_ABORTED error={e!r}", file=sys.stderr, flush=True)
        sys.exit(1)
