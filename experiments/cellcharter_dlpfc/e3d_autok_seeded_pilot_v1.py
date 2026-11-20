"""E3d independent CPU/GPU AutoK pilot (NOT final paper results).

Read-only by default. Explicit --run fits a single DLPFC slice on 15D
features, with an explicit deterministic seed before each GMM fit.
Never edits E1/E2, E3c, reference labels, or model dependencies.
Requires the frozen local E3c/E1 scripts already used on Windows.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import random
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
SAMPLE = "151509"  # pilot only; previously explored sample, NOT independent test
CONDITION = "cum_L0_L1_L2"
SEED = 22911
K_RANGE = (4, 10)  # v0.3.2 internally also fits K=3 and K=11
MAX_RUNS = 3        # timing/feasibility pilot only, NOT final E3d budget
EXPECTED_E3C_SHA256 = "c3bbe996e8bf5f13775a193061fc4b654d9317170e0dca14b7792c429cd77cca"
PROTOCOL = "E3D_AUTOK_SEEDED_CPU_GPU_PILOT_V1_NOT_PAPER_RESULT"


def demand(ok, reason):
    if not ok:
        raise RuntimeError(reason)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def import_script(path, alias):
    spec = importlib.util.spec_from_file_location(alias, path)
    demand(spec is not None and spec.loader is not None, f"IMPORT_ERROR {path}")
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def preflight_inputs():
    f = BASE / "e3c_k_sensitivity_single_task_v1.py"
    demand(f.is_file(), f"E3C_SOURCE_MISSING {f}")
    observed = sha256(f)
    demand(observed == EXPECTED_E3C_SHA256,
           f"FROZEN_E3C_SHA_MISMATCH expected={EXPECTED_E3C_SHA256} actual={observed}")
    e3 = import_script(f, "e3d_pilot_frozen_e3c")
    e1 = e3.source_check(BASE)  # frozen E1/E2 source SHA checks
    info = e1.preflight(SAMPLE, CONDITION, SEED)  # inspect inputs; labels NEVER used to choose K
    demand(info["feature_dim"] == 15 and info["n"] > 100,
           "FEATURE_OR_SPOT_GRID_MISMATCH")
    import numpy as np
    data = np.asarray(info["selected"], dtype=np.float32)
    demand(data.shape == (info["n"], 15), "SELECTED_FEATURE_SHAPE_MISMATCH")
    demand(np.isfinite(data).all(), "NONFINITE_FEATURES")
    return e1, info, data


def run_device(device, data, info, parent):
    import numpy as np
    import pandas as pd
    import anndata as ad
    import torch
    import cellcharter as cc
    from pytorch_lightning import seed_everything
    from pytorch_lightning.overrides.distributed import IndexBatchSamplerWrapper

    class ExplicitSeededGMM(cc.tl.GaussianMixture):
        def fit(self, x):
            # v0.3.2 stores random_state but does not apply it before TorchGMM fit.
            # Every AutoK restart is seeded from its own model's random_state.
            s = int(self.random_state)
            random.seed(s)
            np.random.seed(s)
            seed_everything(s, workers=True)
            return super().fit(x)

    # Existing frozen E3c compatibility shim. This affects only THIS process.
    IndexBatchSamplerWrapper._batch_sampler = property(lambda self: self._sampler)
    params = {
        "covariance_type": "full",
        "init_strategy": "kmeans",
        "convergence_tolerance": 0.001,
        "covariance_regularization": 1e-6,
        "random_state": SEED,
        "trainer_params": {
            "accelerator": device,
            "devices": 1,
            "max_epochs": 100,
            "enable_progress_bar": False,
        },
    }
    adata = ad.AnnData(X=np.zeros((len(data), 1), dtype=np.float32))
    adata.obs_names = pd.Index(info["positions"]["barcode"].astype(str).to_numpy())
    adata.obsm["X_cellcharter"] = data
    model = cc.tl.ClusterAutoK(
        n_clusters=K_RANGE, model_class=ExplicitSeededGMM,
        model_params=params, max_runs=MAX_RUNS,
        convergence_tol=0.0,  # no early stop in this 3-restart pilot
    )
    start = time.perf_counter()
    print(f"E3D_PILOT_DEVICE_START device={device} range={K_RANGE} "
          f"max_runs={MAX_RUNS} seed={SEED}", flush=True)
    model.fit(adata, use_rep="X_cellcharter")
    chosen = int(model.best_k)
    assert K_RANGE[0] <= chosen <= K_RANGE[1]
    pred = np.asarray(model.predict(adata, use_rep="X_cellcharter")).astype(int)
    demand(pred.shape == (len(data),), "PREDICTION_SHAPE_BAD")
    demand(((pred >= 0) & (pred < chosen)).all(), "PREDICTION_K_BAD")
    p = parent / f"{device}_predictions.csv"
    pd.DataFrame({"barcode": adata.obs_names, "cluster": pred}).to_csv(p, index=False)
    stability = np.asarray(model.stability, dtype=float)
    demand(stability.shape[0] == K_RANGE[1] - K_RANGE[0] + 1,
           f"STABILITY_SHAPE_BAD {stability.shape}")
    demand(np.isfinite(stability).all(), "NONFINITE_STABILITY")
    elapsed = time.perf_counter() - start
    entry = {
        "device": device,
        "chosen_k": chosen,
        "outer_candidates": list(range(K_RANGE[0], K_RANGE[1] + 1)),
        "internally_fitted_k": list(model.n_clusters),
        "actual_runs": {str(k): len(v) for k, v in model.labels.items()},
        "stability_mean_by_candidate": dict(zip(
            (str(k) for k in range(K_RANGE[0], K_RANGE[1]+1)),
            np.mean(stability, axis=1).tolist())),
        "wall_seconds": round(elapsed, 3),
        "predictions_sha256": sha256(p),
        "prediction_file": str(p),
    }
    print(f"E3D_PILOT_DEVICE_PASS device={device} chosen_k={chosen} "
          f"wall_seconds={elapsed:.2f} predictions_sha256={entry['predictions_sha256']}", flush=True)
    return entry


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run", action="store_true",
                    help="Opt-in: run exploratory AutoK CPU/GPU fits")
    args = ap.parse_args()
    e1, info, data = preflight_inputs()
    import torch
    import cellcharter as cc
    import importlib.metadata as md
    demand(md.version("cellcharter") == "0.3.2", "CELLCHARTER_VERSION_NOT_FROZEN")
    demand(md.version("torchgmm") == "0.1.2", "TORCHGMM_VERSION_NOT_FROZEN")
    cuda = bool(torch.cuda.is_available())
    print(f"E3D_PILOT_PREFLIGHT_PASS sample={SAMPLE} condition={CONDITION} "
          f"n={info['n']} dim=15 cuda={cuda} original_feature_sha256={info['feature_sha256']}",
          flush=True)
    if not args.run:
        print("DRY_RUN_ONLY NO_TRAINING_NO_FILES_WRITTEN", flush=True)
        return 0
    demand(cuda, "GPU_UNAVAILABLE_NO_TRAINING")
    root = e1.RESULT_ROOT / "e3d_autok_seeded_pilot_v1"
    # Write outside all original E1/E2/E3c directories. Never overwrite pilot dirs.
    session = root / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                      + f"_{os.getpid()}")
    demand(not session.exists(), f"PILOT_OUTPUT_EXISTS {session}")
    session.mkdir(parents=True, exist_ok=False)
    result = {
        "protocol": PROTOCOL, "sample": SAMPLE, "condition": CONDITION,
        "feature_sha256": info["feature_sha256"],
        "cuda": cuda, "seed_policy": "explicit_before_each_GMM_fit",
        "references_used_for_K_selection": False,
        "K_candidate_bounds": list(K_RANGE), "max_runs": MAX_RUNS,
        "status": "running", "devices": {},
    }
    output = session / "summary.json"
    try:
        for device in ("cpu", "gpu"):
            try:
                result["devices"][device] = run_device(device, data, info, session)
            except BaseException as exc:
                result["devices"][device] = {"status": "failed", "error": repr(exc)}
                result["status"] = "failed"
                result["traceback"] = traceback.format_exc()
                raise
            finally:
                output.write_text(json.dumps(result, indent=2), encoding="utf-8")
        result["status"] = "completed"
        output.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"E3D_PILOT_COMPLETE CPU_GPU success summary={output}", flush=True)
        return 0
    except BaseException as exc:
        print(f"E3D_PILOT_HALTED error={exc!r} summary={output}", flush=True)
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"E3D_PILOT_PREFLIGHT_ABORTED error={e!r}", file=sys.stderr, flush=True)
        sys.exit(1)
