"""One-time END-OF-PHASE audit of all 48 frozen E3d CPU AutoK tasks.

Read-only for ALL original experiment and batch-session directories.
Writes only NEW summary JSON and CSV inside a separate, unique audit directory.
No GMM fits, no label annotations, no metrics against human ground truth.
Run on user's Windows only after E3D_BATCH_FINAL status=completed.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results" / "e3d_autok_fixed_v1"
SESSION = BASE / "results" / "e3d_autok_batch_sessions_v1" / "20261120T061725Z_16624" / "session_status.json"
RUNNER = BASE / "e3d_autok_batch_runner_v1.py"
RUNNER_SHA256 = "c9fc65275638a1627a1c836198e8804ecfa866938377448e0de40346d9d01191"
FIT_SCRIPT = BASE / "e3d_autok_single_config_v1.py"
FIT_SCRIPT_SHA256 = "24f500a953e73055d44bfbe3b68e2301f3aeab7e9046035fe31bc2ca81ed8da2"
PROTOCOL = "E3D_AUTOK_FIXED_CPU_V1"
SAMPLES = ("151507", "151508", "151509", "151510", "151669", "151670",
           "151671", "151672", "151673", "151674", "151675", "151676")
CONDITIONS = (("cum_L0_L1", 10), ("cum_L0_L1_L2", 15),
              ("cum_L0_L1_L2_L3", 20), ("cum_L0_L1_L2_L3_L4", 25))
TASKS = [(sample, condition, dim)
         for sample in SAMPLES for condition, dim in CONDITIONS]
CANDIDATES = tuple(range(2, 11))
INTERNAL = tuple(range(1, 12))
RUNS = 5
EXPECTED_SEEDS = list(range(22911, 22916))


def require(test, message):
    if not test:
        raise ValueError(message)


def sha256_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_json(path):
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def verify_sha(path, expected, name):
    require(path.is_file(), name + "_FILE_MISSING")
    actual = sha256_file(path)
    require(isinstance(expected, str) and actual == expected,
            f"{name}_SHA_MISMATCH expected={expected} actual={actual}")
    return actual


def read_session():
    session = read_json(SESSION)
    require(session["status"] == "completed", "BATCH_SESSION_NOT_COMPLETE")
    require(session["expected_total"] == 48, "BATCH_EXPECTED_TOTAL_BAD")
    require(session["protocol"] == PROTOCOL, "BATCH_PROTOCOL_BAD")
    require(session["device"] == "cpu", "BATCH_DEVICE_BAD")
    require(session["K_candidates"] == list(CANDIDATES), "BATCH_K_BAD")
    require(session["max_runs"] == RUNS, "BATCH_RUNS_BAD")
    require(session["single_config_source_sha256"] == FIT_SCRIPT_SHA256,
            "BATCH_FIT_SCRIPT_SHA_BAD")
    entries = session["tasks"]
    require(len(entries) == 48, "BATCH_TASK_COUNT_BAD")
    statuses = Counter()
    for entry, (sample, condition, dim) in zip(entries, TASKS):
        require((entry["sample"], entry["condition"], entry["feature_dim"])
                == (sample, condition, dim), "BATCH_TASK_ORDER_OR_ID_BAD")
        require(entry["status"] in ("completed", "skipped_existing",
                                    "skipped_existing_during_batch"),
                f"BATCH_TASK_NOT_SUCCESSFUL {sample} {condition} {entry['status']}")
        statuses[entry["status"]] += 1
    require(statuses["completed"] == 46
            and statuses["skipped_existing"] + statuses["skipped_existing_during_batch"] == 2,
            f"BATCH_SUCCESS_COUNTS_BAD {dict(statuses)}")
    return session, statuses


def examine(sample, condition, dim, batch_entry):
    out = RESULTS / sample / condition
    require(out.is_dir(), "OUTPUT_DIRECTORY_MISSING")
    manifest = read_json(out / "manifest.json")
    summary = read_json(out / "autok_summary.json")
    require(manifest.get("status") == summary.get("status") == "completed",
            "TASK_NOT_COMPLETED")
    require(manifest.get("protocol") == PROTOCOL, "TASK_PROTOCOL_MISMATCH")
    require(manifest.get("sample") == sample
            and manifest.get("condition") == condition, "TASK_ID_MISMATCH")
    require(manifest.get("feature_dim") == dim, "FEATURE_DIM_MISMATCH")
    n = manifest["n_spots"]
    require(isinstance(n, int) and n > 100, "N_SPOTS_INVALID")
    require(manifest.get("device") == "cpu", "DEVICE_MISMATCH")
    require(manifest.get("K_candidates") == list(CANDIDATES), "K_GRID_MISMATCH")
    require(manifest.get("internal_K") == list(INTERNAL), "INTERNAL_K_MISMATCH")
    require(manifest.get("max_runs") == RUNS, "MAX_RUNS_MISMATCH")
    require(manifest.get("seeds") == EXPECTED_SEEDS, "SEED_POLICY_MISMATCH")
    require(manifest.get("stability_convergence_tol") == 0.0,
            "EARLY_STOP_POLICY_MISMATCH")
    require(manifest.get("reference_labels_used_for_selection") is False,
            "REFERENCE_LABELS_POLICY_MISMATCH")
    require(manifest.get("frozen_e3c_source_sha256")
            == "c3bbe996e8bf5f13775a193061fc4b654d9317170e0dca14b7792c429cd77cca",
            "UPSTREAM_CODE_SHA_MISMATCH")
    params = manifest.get("gmm", {})
    require(params.get("covariance_type") == "full"
            and params.get("init_strategy") == "kmeans"
            and params.get("convergence_tolerance") == 0.001
            and params.get("covariance_regularization") == 1e-6,
            "GMM_CONFIG_MISMATCH")
    trainer = params.get("trainer_params", {})
    require(trainer.get("accelerator") == "cpu"
            and trainer.get("devices") == 1
            and trainer.get("max_epochs") == 100,
            "TRAINER_CONFIG_MISMATCH")
    k_best = manifest.get("selected_k")
    require(isinstance(k_best, int) and k_best in CANDIDATES
            and summary.get("selected_k") == k_best, "BEST_K_MISMATCH")
    key = ("selected_k" if batch_entry["status"] == "completed"
           else "existing_selected_k")
    require(batch_entry.get(key) == k_best,
            "SESSION_MANIFEST_SELECTED_K_MISMATCH")
    require(summary.get("boundary_hit") is (k_best in (2, 10)),
            "BOUNDARY_FLAG_MISMATCH")

    predfile = out / "predictions.csv"
    labelsfile = out / "all_k_run_labels.npz"
    predsha = verify_sha(predfile, summary.get("prediction_sha256"),
                         "PREDICTIONS")
    require(predsha == manifest.get("prediction_sha256"),
            "PREDICTIONS_MANIFEST_SHA_MISMATCH")
    labelsha = verify_sha(labelsfile, summary.get("all_k_run_labels_sha256"),
                          "ALL_K_RUN_LABELS")
    require(labelsha == manifest.get("all_k_run_labels_sha256"),
            "LABELS_MANIFEST_SHA_MISMATCH")
    pred = pd.read_csv(predfile, dtype={"barcode": str})
    require(list(pred.columns) == ["barcode", "cluster"],
            "PREDICTION_COLUMNS_BAD")
    require(len(pred) == n and pred["barcode"].notna().all()
            and pred["barcode"].is_unique, "PREDICTION_SPOTS_OR_BARCODES_INVALID")
    ids = pd.to_numeric(pred["cluster"], errors="raise").to_numpy()
    require(np.isfinite(ids).all()
            and np.all(ids == np.floor(ids))
            and np.isin(ids, np.arange(k_best)).all(),
            "PREDICTION_CLUSTER_IDS_INVALID")

    with np.load(labelsfile, allow_pickle=False) as archive:
        require(set(archive.files) == {f"k_{k}" for k in INTERNAL},
                "ALL_K_KEYS_INVALID")
        for k in INTERNAL:
            values = archive[f"k_{k}"]
            require(values.shape == (RUNS, n),
                    f"ALL_K_ARRAY_SHAPE_MISMATCH k={k}")
            require(np.issubdtype(values.dtype, np.integer)
                    and np.isin(values, np.arange(k)).all(),
                    f"ALL_K_LABEL_RANGE_INVALID k={k}")
    actual_runs = summary.get("all_model_runs", {})
    require(set(actual_runs) == {str(k) for k in INTERNAL}
            and all(actual_runs[str(k)] == RUNS for k in INTERNAL),
            "PER_K_RUN_COUNTS_MISMATCH")
    stable = summary.get("stability_by_K", {})
    require(set(stable) == {str(k) for k in CANDIDATES},
            "STABILITY_K_KEYS_INVALID")
    means = {}
    for k in CANDIDATES:
        record = stable[str(k)]
        mean = float(record["mean"])
        scores = np.asarray(record["values"], dtype=np.float64)
        require(scores.ndim == 1 and scores.size > 0
                and np.isfinite(scores).all() and math.isfinite(mean),
                f"STABILITY_NONFINITE_OR_BAD_SHAPE k={k}")
        require(math.isclose(mean, float(np.mean(scores)),
                             rel_tol=1e-8, abs_tol=1e-8),
                f"STABILITY_MEAN_MISMATCH k={k}")
        means[k] = mean
    require(CANDIDATES[int(np.argmax([means[k] for k in CANDIDATES]))]
            == k_best, "AUTOK_K_NOT_STABILITY_ARGMAX")
    best_models = summary.get("best_models", {})
    require(set(best_models) == {str(k) for k in INTERNAL},
            "BEST_MODEL_KEYS_INVALID")
    converged = 0
    for k in INTERNAL:
        model = best_models[str(k)]
        require(isinstance(model.get("converged"), bool),
                "BEST_MODEL_CONVERGED_NOT_BOOL")
        converged += int(model["converged"])
        require(math.isfinite(float(model["nll"])),
                f"BEST_MODEL_NLL_INVALID k={k}")
        if model.get("num_iter") is not None:
            require(isinstance(model["num_iter"], int)
                    and model["num_iter"] >= 0, "BEST_MODEL_NUM_ITER_INVALID")
    duration = float(summary["fit_predict_seconds"])
    require(math.isfinite(duration) and duration >= 0,
            "FIT_DURATION_INVALID")

    result = {
        "sample": sample, "condition": condition, "dim": dim, "spots": n,
        "selected_k": k_best, "boundary_hit": k_best in (2, 10),
        "fit_seconds": duration, "best_models_converged_11": converged,
        "prediction_sha256": predsha, "all_k_run_labels_sha256": labelsha,
        "feature_sha256": manifest["feature_sha256"],
        "position_sha256": manifest["positions_sha256"],
        "source_sha256": manifest["source_sha256"],
        "barcode_order": pred["barcode"].tolist(),
    }
    result.update({f"stability_k{k}": means[k] for k in CANDIDATES})
    return result


def run_audit():
    require(len(TASKS) == 48 and len(set(TASKS)) == 48, "TASK_GRID_NOT_48")
    require(SCRIPT_CHECK_OK(), "UNEXPECTED_SCRIPT_INTEGRITY_FAILURE")
    session, counts = read_session()
    reports = []
    errors = []
    for i, (sample, cond, dim) in enumerate(TASKS):
        try:
            report = examine(sample, cond, dim, session["tasks"][i])
            reports.append(report)
            print(f"E3D_PHASE_AUDIT_PASS {i+1}/48 sample={sample} "
                  f"dim={dim}D selected_k={report['selected_k']}", flush=True)
        except Exception as exc:
            error = f"{sample}/{cond} {type(exc).__name__}: {exc}"
            errors.append(error)
            print(f"E3D_PHASE_AUDIT_FAILURE {error}", flush=True)

    # Frozen features should preserve identical spot order for all four scales
    # of any given slice; inspect this once after all 48 files are read.
    grouped = {}
    for row in reports:
        grouped.setdefault(row["sample"], []).append(row)
    for sample, group in grouped.items():
        if len(group) == 4:
            for row in group[1:]:
                if row["barcode_order"] != group[0]["barcode_order"]:
                    errors.append(f"{sample} CROSS_SCALE_BARCODE_ORDER_MISMATCH")
                if row["position_sha256"] != group[0]["position_sha256"]:
                    errors.append(f"{sample} CROSS_SCALE_POSITION_SHA_MISMATCH")

    serializable = [{k: v for k, v in row.items() if k != "barcode_order"}
                    for row in reports]
    k_counts = {str(k): sum(row["selected_k"] == k for row in reports)
                for k in CANDIDATES}
    summary = {
        "audit_name": "E3D_AUTOK_48_CONFIG_PHASE_FINAL_AUDIT_V1",
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "status": "passed" if len(reports) == 48 and not errors else "failed",
        "runner_report_status": session["status"],
        "runner_status_counts": dict(counts),
        "expected_configs": 48,
        "fully_audited_configs": len(reports),
        "planned_runs_per_config": 55,
        "verified_label_run_arrays_total": 55 * len(reports),
        "selected_k_counts": k_counts,
        "boundary_hits": sum(row["boundary_hit"] for row in reports),
        "best_models_converged_count": sum(
            row["best_models_converged_11"] for row in reports),
        "best_models_checked_count": 11 * len(reports),
        "fit_seconds_total": round(sum(row["fit_seconds"] for row in reports), 4),
        "errors": errors,
        "tasks": serializable,
        "source_sha256": {
            "frozen_fit_script": FIT_SCRIPT_SHA256,
            "batch_runner": RUNNER_SHA256,
            "batch_session_file": sha256_file(SESSION),
        },
        "limitations": [
            "This audit checks saved files and model summaries, not all-run convergence.",
            "No human layer labels were used and no ARI/NMI versus annotations was calculated.",
            "Twelve slices are nested in three donors; seeds/spots are not biological replicates.",
            "Raw experiment files remain only on the user's Windows machine unless uploaded.",
        ],
    }
    audit_root = BASE / "results" / "e3d_autok_phase_audit_v1"
    audit_dir = audit_root / (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") +
        "_" + str(os.getpid()))
    audit_dir.mkdir(parents=True, exist_ok=False)
    summary_path = audit_dir / "audit_report.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False),
                            encoding="utf-8")
    csv_path = audit_dir / "all_48_autok_audit.csv"
    if serializable:
        with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(serializable[0]))
            writer.writeheader()
            writer.writerows(serializable)
    print(f"E3D_PHASE_AUDIT_SUMMARY status={summary['status']} "
          f"verified={len(reports)}/48 errors={len(errors)} "
          f"label_fit_archives={summary['verified_label_run_arrays_total']}/2640 "
          f"boundary_hits={summary['boundary_hits']} "
          f"best_converged={summary['best_models_converged_count']}/"
          f"{summary['best_models_checked_count']}", flush=True)
    print(f"E3D_PHASE_AUDIT_K_COUNTS {k_counts}", flush=True)
    print(f"E3D_PHASE_AUDIT_REPORT path={summary_path}", flush=True)
    return 0 if summary["status"] == "passed" else 2


def SCRIPT_CHECK_OK():
    verify_sha(FIT_SCRIPT, FIT_SCRIPT_SHA256, "FROZEN_FIT_SOURCE")
    verify_sha(RUNNER, RUNNER_SHA256, "FROZEN_BATCH_RUNNER_SOURCE")
    return True


if __name__ == "__main__":
    try:
        sys.exit(run_audit())
    except Exception as exc:
        print(f"E3D_PHASE_AUDIT_ABORTED {type(exc).__name__}: {exc}",
              file=sys.stderr, flush=True)
        sys.exit(1)
