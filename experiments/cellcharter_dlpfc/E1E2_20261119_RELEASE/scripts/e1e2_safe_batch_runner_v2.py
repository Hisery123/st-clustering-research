"""Safely plan or run a bounded batch of E1/E2 CellCharter GMM tasks.

By default, READ ONLY: inventory and independently audit ALL existing results
for ONE sample and ONE pre-registered seed. No GMM fitting and no files written.

Training requires explicit --run. Default --max-new=1 means only ONE new
training task may start per invocation; a larger bounded cap is optional.

Each task is run in a fresh Python subprocess using the established
`e1e2_multiscale_gmm_task.py` script; this runner never deletes, overwrites,
or silently retries a task, and stops on the first failure.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

SCRIPT = Path(__file__).resolve().parent / "e1e2_multiscale_gmm_task.py"


def load_task():
    if not SCRIPT.is_file():
        raise FileNotFoundError(f"Original single-task runner not found: {SCRIPT}")
    spec = importlib.util.spec_from_file_location("e1e2_task", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import original task script: {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def check(cond: str, info: dict, task, existing: Path, legacy: Path | None) -> dict:
    """Independent read-only audit; raising aborts the whole batch."""
    if legacy is not None and legacy.is_file() and existing.exists():
        raise RuntimeError(f"BOTH_LEGACY_AND_NEW_EXIST: {cond}; manual reconciliation required")
    if legacy is not None and legacy.is_file():
        mfile = legacy.parent / "manifest.json"
        rfile = legacy.parent / "results.json"
        if not mfile.is_file() or not rfile.is_file():
            raise RuntimeError(f"INCOMPLETE_LEGACY: {cond}: {legacy.parent}")
        m = json.loads(mfile.read_text(encoding="utf-8"))
        results = json.loads(rfile.read_text(encoding="utf-8"))
        name = legacy.name.removesuffix("_predictions.csv")
        # Legacy 151507/151508 files use source_file_sha256; the historical
        # ten-section batch script uses source_feature_sha256. The payload is
        # equivalent (SHA256 of the same 25D aggregated .npy). Check EVERY
        # populated spelling, not just one, so conflicts still block reuse.
        source_hashes = [m[key] for key in ("source_file_sha256", "source_feature_sha256")
                         if key in m]
        source_hash_ok = bool(source_hashes) and all(
            h == info["source_sha256"] for h in source_hashes)
        # Extra provenance hashes are available in the ten-section records.
        # If present, verify them instead of silently accepting bad files.
        positions_hash_ok = ("position_csv_sha256" not in m or
                             m["position_csv_sha256"] == info["position_sha256"])
        labels_hash_ok = ("reference_annotation_sha256" not in m or
                          m["reference_annotation_sha256"] == info["labels_sha256"])
        if not (m.get("status") == "completed" and m.get("seed") == info["seed"]
                and m.get("sample") == info["sid"]
                and m.get("oracle_k") == info["k"]
                and m.get("feature_dim") == info["feature_dim"]
                and source_hash_ok and positions_hash_ok and labels_hash_ok
                and m.get("conditions", {}).get(name) == list(info["blocks"])
                and m.get(name, {}).get("feature_sha256") == info["feature_sha256"]):
            raise RuntimeError(f"LEGACY_MANIFEST_MISMATCH: {cond}")
        if name not in results:
            raise RuntimeError(f"LEGACY_METRICS_MISSING: {cond}")
        record, pfile, status = results[name], legacy, "LEGACY_AUDITED"
    elif existing.exists():
        files = [existing / n for n in ("manifest.json", "metrics.json", "predictions.csv")]
        if not all(p.is_file() for p in files):
            raise RuntimeError(f"INCOMPLETE_NEW_OUTPUT: {cond}: {existing}")
        m = json.loads(files[0].read_text(encoding="utf-8"))
        record = json.loads(files[1].read_text(encoding="utf-8"))
        pfile = files[2]
        if not (m.get("status") == "completed"
                and m.get("protocol") == "E1E2_MULTISCALE_GMM_TASK_V1"
                and m.get("sample") == info["sid"]
                and m.get("gmm_seed") == info["seed"]
                and m.get("oracle_k") == info["k"]
                and m.get("feature_dim") == info["feature_dim"]
                and m.get("feature_blocks") == list(info["blocks"])
                and m.get("source_sha256") == info["source_sha256"]
                and m.get("feature_sha256") == info["feature_sha256"]
                and m.get("positions_sha256") == info["position_sha256"]
                and m.get("reference_sha256") == info["labels_sha256"]
                and m.get("prediction_sha256") == sha256_file(pfile)):
            raise RuntimeError(f"NEW_OUTPUT_MANIFEST_OR_SHA_MISMATCH: {cond}")
        if record.get("n_evaluated") != info["n_labeled_expected"]:
            raise RuntimeError(f"NEW_N_EVALUATED_MISMATCH: {cond}")
        status = "NEW_AUDITED"
    else:
        if legacy is not None and not legacy.is_file():
            # A legacy source is expected for this seed/condition. Failure to
            # locate it is a BLOCKER, not permission to recompute silently.
            raise RuntimeError(f"EXPECTED_LEGACY_MISSING: {cond}: {legacy}")
        return {"condition": cond, "status": "MISSING", "dimension": info["feature_dim"]}

    pred = pd.read_csv(pfile, dtype={"barcode": str})
    pos = info["positions"]
    if not (len(pred) == len(pos) == info["n"]
            and pred["barcode"].is_unique
            and np.array_equal(pred["barcode"].to_numpy(), pos["barcode"].to_numpy())
            and pred["cluster"].isin(range(info["k"])).all()):
        raise RuntimeError(f"PREDICTIONS_SHAPE_OR_BARCODES_INVALID: {cond}")
    labels = pd.read_csv(info["label_path"], dtype={"sample_name": str, "spot_name": str})
    labels = labels.loc[labels["sample_name"] == info["sid"]]
    if labels["spot_name"].duplicated().any():
        raise RuntimeError(f"DUPLICATE_REFERENCE_BARCODE: {cond}")
    truth = labels.set_index("spot_name")["layer"].reindex(pred["barcode"])
    valid = truth.notna().to_numpy()
    if int(valid.sum()) != info["n_labeled_expected"]:
        raise RuntimeError(f"INVALID_REFERENCE_COUNT: {cond}")
    cluster = pred["cluster"].to_numpy()
    ari = adjusted_rand_score(truth.to_numpy()[valid], cluster[valid])
    nmi = normalized_mutual_info_score(truth.to_numpy()[valid], cluster[valid])
    if abs(ari - record["ari"]) >= 1e-10 or abs(nmi - record["nmi"]) >= 1e-10:
        raise RuntimeError(f"METRICS_RECOMPUTATION_MISMATCH: {cond}")
    return {"condition": cond, "status": status, "dimension": info["feature_dim"],
            "ari": float(ari), "nmi": float(nmi)}


def save_json(path: Path, content: dict) -> None:
    path.write_text(json.dumps(content, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    task = load_task()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", choices=task.SAMPLES, required=True)
    parser.add_argument("--seed", type=int, choices=task.SEEDS, required=True)
    parser.add_argument("--run", action="store_true", help="Explicitly permit training of missing tasks")
    parser.add_argument("--max-new", type=int, default=1, help="Cap NEW GMM training runs (default: 1)")
    args = parser.parse_args()
    if not (1 <= args.max_new <= len(task.CONDITIONS)):
        parser.error("--max-new must be between 1 and number of configurations")

    # Full read-only inventory/audit BEFORE creating any output or fitting.
    inventory = []
    for cond in task.CONDITIONS:
        info = task.preflight(args.sample, cond, args.seed)
        dest = task.RESULT_ROOT / "e1e2_multiscale_gmm_v1" / args.sample / cond / f"seed_{args.seed}"
        row = check(cond, info, task, dest, info["legacy"])
        inventory.append(row)
        print(f"CHECK {cond} {row['status']} "+
              (f"ARI={row['ari']:.6f} NMI={row['nmi']:.6f}" if "ari" in row else ""), flush=True)

    missing = [row["condition"] for row in inventory if row["status"] == "MISSING"]
    print(f"PLAN_OK sample={args.sample} seed={args.seed} "
          f"verified={len(inventory) - len(missing)} missing={len(missing)} "
          f"max_new={args.max_new}", flush=True)
    if not args.run:
        print("DRY_RUN_ONLY NO_TRAINING_NO_FILES_WRITTEN", flush=True)
        return 0
    if not missing:
        print("ALL_TASKS_AUDITED NO_TRAINING_NO_FILES_WRITTEN", flush=True)
        return 0

    # Unique report directory. Never overwrite a previous batch report.
    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    reportdir = (task.RESULT_ROOT / "e1e2_batch_reports_v1" / args.sample /
                 f"seed_{args.seed}" / f"{now}_{uuid.uuid4().hex[:10]}")
    reportdir.mkdir(parents=True, exist_ok=False)
    report = {"status": "running", "sample": args.sample, "seed": args.seed,
              "protocol": "E1E2_SAFE_BATCH_V1", "max_new": args.max_new,
              "started_utc": datetime.now(timezone.utc).isoformat(),
              "initial_inventory": inventory, "tasks": []}
    summary = reportdir / "summary.json"
    save_json(summary, report)
    launched = 0
    try:
        for cond in missing[:args.max_new]:
            dest = (task.RESULT_ROOT / "e1e2_multiscale_gmm_v1" / args.sample /
                    cond / f"seed_{args.seed}")
            if dest.exists():
                raise RuntimeError(f"OUTPUT_APPEARED_BEFORE_FIT_STOP: {dest}")
            cmd = [sys.executable, str(SCRIPT), "--sample", args.sample,
                   "--condition", cond, "--seed", str(args.seed), "--fit"]
            print(f"RUN_START {args.sample} {cond} seed={args.seed}", flush=True)
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    text=True, encoding="utf-8", errors="replace", check=False)
            launched += 1
            logfile = reportdir / f"{launched:02d}_{cond}.log"
            logfile.write_text(result.stdout, encoding="utf-8")
            attempt = {"condition": cond, "returncode": result.returncode,
                       "log": str(logfile), "output": str(dest)}
            report["tasks"].append(attempt)
            save_json(summary, report)
            if result.returncode != 0:
                print(result.stdout[-1600:], flush=True)
                raise RuntimeError(f"FIT_FAILED_STOP: {cond} exit={result.returncode}")
            # Verify the saved artifacts before starting another GMM.
            info = task.preflight(args.sample, cond, args.seed)
            audited = check(cond, info, task, dest, info["legacy"])
            if audited["status"] != "NEW_AUDITED":
                raise RuntimeError(f"POST_FIT_AUDIT_NOT_NEW: {cond}")
            attempt["audit"] = audited
            save_json(summary, report)
            print(f"RUN_AUDIT_PASS {cond} ARI={audited['ari']:.6f} "
                  f"NMI={audited['nmi']:.6f}", flush=True)
        report["status"] = "completed"
        report["finished_utc"] = datetime.now(timezone.utc).isoformat()
        save_json(summary, report)
        print(f"BATCH_RUN_COMPLETE new_tasks={launched} report={summary}", flush=True)
        return 0
    except BaseException as err:
        report["status"] = "failed"
        report["error"] = repr(err)
        report["finished_utc"] = datetime.now(timezone.utc).isoformat()
        save_json(summary, report)
        print(f"BATCH_HALTED {err} report={summary}", file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
