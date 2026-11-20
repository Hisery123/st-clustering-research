"""E3d 48-config CPU AutoK: immutable-task batch launcher, not an estimator.

Default is a READ-ONLY plan. --run executes only missing tasks using the frozen
single-config script in the same Windows directory. Never overwrites outputs.
A sample-local failure skips remaining configurations of that sample and moves
on; failures on two different samples stop the batch (likely shared failure).
Audit is deferred to the end of the full phase, per user's execution-first rule.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
SCRIPT = BASE / "e3d_autok_single_config_v1.py"
SCRIPT_SHA256 = "24f500a953e73055d44bfbe3b68e2301f3aeab7e9046035fe31bc2ca81ed8da2"
PROTOCOL = "E3D_AUTOK_FIXED_CPU_V1"
SAMPLES = ("151507", "151508", "151509", "151510", "151669", "151670",
           "151671", "151672", "151673", "151674", "151675", "151676")
CONDITIONS = (
    ("cum_L0_L1", 10),
    ("cum_L0_L1_L2", 15),
    ("cum_L0_L1_L2_L3", 20),
    ("cum_L0_L1_L2_L3_L4", 25),
)
TASKS = tuple((sample, name, dim) for sample in SAMPLES for name, dim in CONDITIONS)
RESULTS = BASE / "results" / "e3d_autok_fixed_v1"
SESSIONS = BASE / "results" / "e3d_autok_batch_sessions_v1"
LOCK = SESSIONS / "_ACTIVE_BATCH.lock"
GLOBAL_ERROR_RE = re.compile(
    r"(FROZEN_E3C_SHA_MISMATCH|SOURCE_SHA_MISMATCH|UNEXPECTED_CELLCHARTER_VERSION|"
    r"UNEXPECTED_TORCHGMM_VERSION|No space left on device|ENOSPC|PermissionError|"
    r"OSError.*[Ww]rite|OUTPUT_EXISTS_NO_OVERWRITE|UNEXPECTED_RANDOM_SEED|"
    r"FEATURE_CONDITION_MISMATCH|INTERNAL_K_MISMATCH|BATCH_SOURCE_SHA_CHANGED)"
)


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def file_sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def require_frozen_script():
    if not SCRIPT.is_file():
        raise RuntimeError(f"BATCH_SOURCE_MISSING {SCRIPT}")
    actual = file_sha256(SCRIPT)
    if actual != SCRIPT_SHA256:
        raise RuntimeError(f"BATCH_SOURCE_SHA_MISMATCH actual={actual} expected={SCRIPT_SHA256}")


def read_json(path):
    with Path(path).open("r", encoding="utf-8") as stream:
        return json.load(stream)


def outcome(sample, condition, dim):
    """Lightweight execution safety check only; not a per-task scientific audit."""
    out = RESULTS / sample / condition
    if not out.exists():
        return "pending", None
    if not out.is_dir():
        return "blocked", "EXPECTED_DIRECTORY"
    manifest = out / "manifest.json"
    if not manifest.is_file():
        return "blocked", "EXISTING_OUTPUT_MISSING_MANIFEST"
    try:
        info = read_json(manifest)
    except (ValueError, OSError) as exc:
        return "blocked", f"INVALID_MANIFEST {exc}"
    if (info.get("sample") != sample or info.get("condition") != condition
            or info.get("feature_dim") != dim
            or info.get("protocol") != PROTOCOL
            or info.get("device") != "cpu"
            or info.get("K_candidates") != list(range(2, 11))
            or info.get("internal_K") != list(range(1, 12))
            or info.get("max_runs") != 5
            or info.get("seeds") != list(range(22911, 22916))
            or info.get("reference_labels_used_for_selection") is not False):
        return "blocked", "EXISTING_OUTPUT_PROTOCOL_MISMATCH"
    status = info.get("status")
    if status == "failed":
        return "preexisting_failed", str(info.get("error", "UNKNOWN_FAILURE"))[:280]
    if status != "completed":
        return "blocked", f"EXISTING_OUTPUT_STATUS_{status}"
    summary_path = out / "autok_summary.json"
    if not summary_path.is_file():
        return "blocked", "COMPLETED_OUTPUT_MISSING_SUMMARY"
    try:
        summary = read_json(summary_path)
    except (ValueError, OSError) as exc:
        return "blocked", f"INVALID_COMPLETED_SUMMARY {exc}"
    if (summary.get("status") != "completed" or
            summary.get("selected_k") != info.get("selected_k") or
            not isinstance(info.get("selected_k"), int) or
            not 2 <= info["selected_k"] <= 10):
        return "blocked", "COMPLETED_OUTPUT_STATUS_K_MISMATCH"
    for filename in ("predictions.csv", "all_k_run_labels.npz"):
        if not (out / filename).is_file():
            return "blocked", f"COMPLETED_OUTPUT_MISSING_{filename}"
    return "completed", info["selected_k"]


def build_plan():
    statuses = {}
    for sample, condition, dim in TASKS:
        status, value = outcome(sample, condition, dim)
        statuses[(sample, condition)] = (status, value)
    return statuses


def print_plan(plan):
    from collections import Counter
    counts = Counter(x[0] for x in plan.values())
    print("E3D_BATCH_PLAN", " ".join(f"{k}={counts[k]}" for k in
          ("completed", "pending", "preexisting_failed", "blocked")),
          "total=48 device=cpu K=2..10 runs_per_k=5", flush=True)
    for sample in SAMPLES:
        items = [f"{dim}D:{plan[(sample, name)][0]}" for name, dim in CONDITIONS]
        print("E3D_BATCH_SAMPLE", sample, " ".join(items), flush=True)
    return counts


def write_json_atomic(path, obj):
    p = Path(path)
    tmp = p.with_name(p.name + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(obj, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, p)


def run_all(plan):
    if any(s == "blocked" for s, _ in plan.values()):
        raise RuntimeError("BATCH_PREEXISTING_OUTPUT_BLOCKED: inspect plan first; nothing launched")
    require_frozen_script()
    SESSIONS.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(str(LOCK), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise RuntimeError(f"BATCH_ACTIVE_LOCK_EXISTS {LOCK}") from exc
    session = None
    session_dir = None
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(f"started_utc={utc_now()} pid={os.getpid()}\n")
        identity = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + f"_{os.getpid()}"
        session_dir = SESSIONS / identity
        session_dir.mkdir(parents=False, exist_ok=False)
        session = {
            "protocol": PROTOCOL,
            "batch_runner_version": "v1",
            "status": "running", "started_utc": utc_now(),
            "session_dir": str(session_dir), "single_config_source_sha256": SCRIPT_SHA256,
            "device": "cpu", "K_candidates": list(range(2, 11)),
            "max_runs": 5, "expected_total": 48,
            "tasks": [],
        }
        status_file = session_dir / "session_status.json"
        for sample, condition, dim in TASKS:
            old, value = plan[(sample, condition)]
            session["tasks"].append({
                "sample": sample, "condition": condition, "feature_dim": dim,
                "status": ("skipped_existing" if old == "completed" else
                           "skipped_preexisting_failed" if old == "preexisting_failed" else
                           "pending"),
                "existing_selected_k": value if old == "completed" else None,
                "failure": value if old == "preexisting_failed" else None,
            })
        write_json_atomic(status_file, session)
        print(f"E3D_BATCH_SESSION_START path={session_dir}", flush=True)
        last_failed_sample = None
        failed_sample = None
        stop_reason = None
        for i, task in enumerate(session["tasks"]):
            sample, condition, dim = task["sample"], task["condition"], task["feature_dim"]
            if task["status"] != "pending":
                print(f"E3D_BATCH_SKIP {sample} {dim}D reason={task['status']}", flush=True)
                continue
            if failed_sample == sample:
                task["status"] = "skipped_same_sample_after_failure"
                write_json_atomic(status_file, session)
                print(f"E3D_BATCH_SKIP {sample} {dim}D reason=earlier_sample_task_failure", flush=True)
                continue
            # Recheck for another process's work or modified source, without resetting it.
            require_frozen_script()
            actual, detail = outcome(sample, condition, dim)
            if actual != "pending":
                if actual == "completed":
                    task["status"] = "skipped_existing_during_batch"
                    task["existing_selected_k"] = detail
                    write_json_atomic(status_file, session)
                    continue
                if actual == "preexisting_failed":
                    task["status"] = "skipped_preexisting_failed"
                    task["failure"] = detail
                    write_json_atomic(status_file, session)
                    failed_sample = sample
                    continue
                task["status"] = "blocked"
                task["failure"] = detail
                stop_reason = f"OUTPUT_CHANGED_DURING_BATCH {sample} {condition} {detail}"
                write_json_atomic(status_file, session)
                break
            log = session_dir / f"task_{i+1:02d}_{sample}_{dim}D.log"
            task["status"] = "running"
            task["started_utc"] = utc_now()
            task["log"] = str(log)
            write_json_atomic(status_file, session)
            cmd = [sys.executable, str(SCRIPT), "--sample", sample,
                   "--condition", condition, "--run"]
            print(f"E3D_BATCH_START task={i+1}/48 sample={sample} dim={dim} log={log}", flush=True)
            start = time.perf_counter()
            try:
                with log.open("w", encoding="utf-8", errors="replace") as stream:
                    stream.write("# COMMAND: " + " ".join(cmd) + "\n")
                    stream.flush()
                    ret = subprocess.run(cmd, cwd=str(BASE), stdout=stream,
                                         stderr=subprocess.STDOUT, check=False).returncode
            except OSError as exc:
                ret = -99
                with log.open("a", encoding="utf-8", errors="replace") as stream:
                    stream.write(f"\nBATCH_PROCESS_SPAWN_FAILED: {exc!r}\n")
            duration = round(time.perf_counter() - start, 3)
            task["finished_utc"] = utc_now()
            task["elapsed_seconds"] = duration
            task["exit_code"] = ret
            actual, detail = outcome(sample, condition, dim)
            if ret == 0 and actual == "completed":
                task["status"] = "completed"
                task["selected_k"] = detail
                failed_sample = None
                last_failed_sample = None
                print(f"E3D_BATCH_PASS task={i+1}/48 sample={sample} dim={dim} "
                      f"selected_k={detail} seconds={duration}", flush=True)
            else:
                tail = ""
                try:
                    with log.open("r", encoding="utf-8", errors="replace") as stream:
                        tail = stream.read()[-2200:]
                except OSError:
                    pass
                task["status"] = "failed"
                task["failure"] = f"exit={ret} output_state={actual} detail={detail}"
                failed_sample = sample
                print(f"E3D_BATCH_TASK_FAILED task={i+1}/48 sample={sample} dim={dim} "
                      f"exit={ret} log={log}", flush=True)
                if GLOBAL_ERROR_RE.search(tail):
                    stop_reason = f"GLOBAL_ERROR_IN_LOG {sample} {condition}"
                elif last_failed_sample is not None and last_failed_sample != sample:
                    stop_reason = (f"TWO_SAMPLES_FAILED {last_failed_sample} {sample}; "
                                   "stop possible global failure")
                last_failed_sample = sample
            write_json_atomic(status_file, session)
            if stop_reason:
                break
        from collections import Counter
        counts = Counter(t["status"] for t in session["tasks"])
        pending = sum(t["status"] == "pending" for t in session["tasks"])
        bad = sum(t["status"] in ("failed", "blocked", "skipped_preexisting_failed",
                                   "skipped_same_sample_after_failure")
                  for t in session["tasks"])
        session["status"] = "halted" if stop_reason else ("partial" if bad or pending else "completed")
        session["stop_reason"] = stop_reason
        session["finished_utc"] = utc_now()
        session["counts"] = dict(counts)
        write_json_atomic(status_file, session)
        print(f"E3D_BATCH_FINAL status={session['status']} completed={counts['completed']} "
              f"existing={counts['skipped_existing']+counts['skipped_existing_during_batch']} "
              f"problem_tasks={bad} pending={pending} summary={status_file}", flush=True)
        return 0 if session["status"] == "completed" else 2
    except BaseException as exc:
        if session is not None and session_dir is not None:
            session["status"] = "halted_exception"
            session["stop_reason"] = repr(exc)
            session["traceback"] = traceback.format_exc()
            session["finished_utc"] = utc_now()
            try:
                write_json_atomic(session_dir / "session_status.json", session)
            except OSError:
                pass
        print(f"E3D_BATCH_HALTED_EXCEPTION {exc!r}", file=sys.stderr, flush=True)
        return 3
    finally:
        # Remove only own session lock; unexpected OS/process termination leaves it
        # behind as a fail-closed signal requiring operator review.
        try:
            LOCK.unlink()
        except FileNotFoundError:
            pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true", help="execute missing tasks (default: plan only)")
    args = parser.parse_args()
    if len(TASKS) != 48 or len(set(TASKS)) != 48:
        raise RuntimeError("BATCH_TASK_MATRIX_INVALID")
    require_frozen_script()
    plan = build_plan()
    counts = print_plan(plan)
    if counts["blocked"]:
        print("E3D_BATCH_BLOCKED_EXISTING_OUTPUT; no work performed", file=sys.stderr, flush=True)
        return 2
    if not args.run:
        print("E3D_BATCH_DRY_RUN_ONLY NO_TRAINING_NO_FILES_WRITTEN", flush=True)
        return 0
    return run_all(plan)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"E3D_BATCH_PREFLIGHT_FAILED error={exc!r}", file=sys.stderr, flush=True)
        sys.exit(1)
