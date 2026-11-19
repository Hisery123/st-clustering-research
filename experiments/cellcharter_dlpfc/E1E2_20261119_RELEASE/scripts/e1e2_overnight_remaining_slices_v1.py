"""Safe, sequential, resumable overnight orchestrator for the FROZEN DLPFC E1/E2 GMM matrix.

User-controlled Windows execution. No background execution by ChatGPT.

Target: exactly the eight unfinished sections 151669-151676, in frozen order;
         10 frozen GMM seeds and 10 frozen conditions per section.

Default: preflight only (reads existing model results, does NOT train).
Explicit --run: preflight ALL 80 section/seed groups BEFORE any training;
then run missing tasks one section/seed group at a time via the already
validated V2 safe batch runner; after each section, independently re-audit
all 100 tasks and export V2 multiseed statistics. Stop on first error.

All original inputs, prior predictions, and legacy results remain unchanged;
failed or incomplete tasks are NOT silently retried or overwritten.

Usage:
  python e1e2_overnight_remaining_slices_v1.py --run
"""
from __future__ import annotations

import argparse
import csv
import ctypes
import hashlib
import json
import os
import re
import subprocess
import sys
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
PYTHON = Path(sys.executable).resolve()
RUNNER = BASE / "e1e2_safe_batch_runner_v2.py"
STATS = BASE / "e1e2_aggregate_multiseed_v2.py"
TASK = BASE / "e1e2_multiscale_gmm_task.py"

# All eight remaining FROZEN sections. The first four sections 151507-151510
# were separately completed and are deliberately outside the run list.
SECTIONS = ("151669", "151670", "151671", "151672",
            "151673", "151674", "151675", "151676")
SEEDS = (22911, 7449, 25842, 10379, 6690,
         26128, 21059, 22159, 32389, 12815)
CONDITIONS = ("cum_L0", "cum_L0_L1", "cum_L0_L1_L2",
              "cum_L0_L1_L2_L3", "cum_L0_L1_L2_L3_L4",
              "fixed_L0_L1_L3", "fixed_L0_L1_L4", "fixed_L0_L2_L3",
              "fixed_L0_L2_L4", "fixed_L0_L3_L4")
ORACLE_K = {"151669": 5, "151670": 5, "151671": 5, "151672": 5,
            "151673": 7, "151674": 7, "151675": 7, "151676": 7}

# The exact, previously examined and independently audited source files.
# A different local script is a STOP, not permission to silently change the
# frozen analysis configuration during hundreds of overnight model fits.
EXPECTED_SHA256 = {
    "e1e2_multiscale_gmm_task.py": "d447dd2cc812616d3589c40f0fd586df3e78d89aec032ad4a82bb433465b958a",
    "e1e2_safe_batch_runner_v2.py": "22ae7b4cd5b8b652f493168fb7b037eb886a466ab1bdba0c734aec912b2f37e4",
    "e1e2_aggregate_multiseed_v2.py": "e8ef524c1cab24834c2160e1c06df1da94234c9c9ce72457b9d1d07defc9fce5",
}

PLAN_RE = re.compile(
    r"^PLAN_OK sample=(\d+) seed=(\d+) verified=(\d+) missing=(\d+) max_new=(\d+)$",
    re.MULTILINE,
)
CHECK_RE = re.compile(r"^CHECK (\w+) (MISSING|NEW_AUDITED|LEGACY_AUDITED)(?:\s|$)")
SUMMARY_RE = re.compile(
    r"^SUMMARY_COMPLETE sample=(\d+) verified=(\d+) conditions=(\d+) paired_rows=(\d+)$",
    re.MULTILINE,
)


def utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def assert_frozen_scripts() -> dict[str, str]:
    actual = {}
    for filename, expected in EXPECTED_SHA256.items():
        path = BASE / filename
        if not path.is_file():
            raise RuntimeError(f"REQUIRED_SCRIPT_NOT_FOUND: {path}")
        found = sha256(path)
        actual[filename] = found
        if found != expected:
            raise RuntimeError(
                f"CODE_SHA256_MISMATCH: {path}; actual={found}; frozen={expected}; "
                "DO_NOT_REPLACE_OR_EDIT_FILES_TO_BYPASS_CHECK"
            )
    if set(SECTIONS) != set(ORACLE_K) or len(SECTIONS) != 8 or len(SEEDS) != 10 or len(CONDITIONS) != 10:
        raise RuntimeError("FROZEN_PROTOCOL_OR_TARGET_LIST_MISMATCH")
    return actual


@contextmanager
def exclusive_process_lock(lock_path: Path):
    """Prevent simultaneous orchestrators; OS lock is freed on crash/exit."""
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+b") as stream:
        stream.seek(0, os.SEEK_END)
        if stream.tell() == 0:
            stream.write(b"0")
            stream.flush()
        stream.seek(0)
        if os.name == "nt":
            import msvcrt
            try:
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError as exc:
                raise RuntimeError("ANOTHER_OVERNIGHT_RUN_ALREADY_ACTIVE") from exc
            try:
                yield
            finally:
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            try:
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                raise RuntimeError("ANOTHER_OVERNIGHT_RUN_ALREADY_ACTIVE") from exc
            try:
                yield
            finally:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


@contextmanager
def keep_system_awake():
    """Windows: inhibit idle system sleep during the run; doesn't override lid-close."""
    if os.name != "nt":
        yield
        return
    kernel = ctypes.windll.kernel32
    # ES_CONTINUOUS | ES_SYSTEM_REQUIRED; screen is allowed to turn off.
    flag = 0x80000000 | 0x00000001
    value = kernel.SetThreadExecutionState(flag)
    if not value:
        raise RuntimeError("WINDOWS_SLEEP_INHIBIT_FAILED: keep computer awake manually")
    try:
        yield
    finally:
        kernel.SetThreadExecutionState(0x80000000)


class Session:
    def __init__(self, output_root: Path, is_run: bool, script_hashes: dict[str, str]):
        self.dest = output_root / (
            datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:10]
        )
        self.dest.mkdir(parents=True, exist_ok=False)
        self.logpath = self.dest / "session.log"
        self.stream = self.logpath.open("w", encoding="utf-8", buffering=1)
        self.state = {
            "status": "running", "mode": "RUN" if is_run else "PREFLIGHT_ONLY",
            "started_utc": utc(), "sections": list(SECTIONS), "seeds": list(SEEDS),
            "conditions": list(CONDITIONS), "oracle_k": ORACLE_K,
            "script_sha256": script_hashes, "python": str(PYTHON),
            "preflight": {}, "completed_seed_groups": [], "completed_summaries": {},
            "new_tasks_confirmed_by_runner": 0,
            "note": "GMM random seeds are NOT independent biological replicates.",
        }
        self.save()

    def tell(self, s: str):
        line = f"[{utc()}] {s}"
        print(line, flush=True)
        self.stream.write(line + "\n")

    def save(self):
        path = self.dest / "session_status.json"
        tmp = self.dest / "session_status.tmp"
        tmp.write_text(json.dumps(self.state, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(path)

    def child(self, args: list[str], tag: str, echo_runs: bool = False) -> str:
        self.tell(f"COMMAND_START {tag}: {' '.join(args)}")
        records = []
        p = subprocess.Popen(
            [str(PYTHON), *args], cwd=str(BASE),
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            encoding="utf-8", errors="replace", text=True, bufsize=1,
        )
        assert p.stdout is not None
        try:
            for line in p.stdout:
                line = line.rstrip("\r\n")
                records.append(line)
                self.stream.write(f"[{tag}] {line}\n")
                if echo_runs and (line.startswith("RUN_START ") or
                                  line.startswith("BATCH_HALTED ") or
                                  line.startswith("BATCH_RUN_COMPLETE ")):
                    print(line, flush=True)
            code = p.wait()
        except BaseException:
            # Do not silently leave an orchestrator running on interruption.
            # On Windows, its spawned GMM child may survive if interrupted;
            # we therefore stop and require manual examination, never retry.
            if p.poll() is None:
                p.terminate()
            raise
        output = "\n".join(records)
        if code != 0:
            excerpt = "\n".join(records[-25:])
            self.tell(f"COMMAND_FAILED {tag} exitcode={code}; last_output:\n{excerpt}")
            raise RuntimeError(f"CHILD_COMMAND_FAILED {tag} exitcode={code}; LOG={self.logpath}")
        self.tell(f"COMMAND_OK {tag}")
        return output

    def close(self):
        self.stream.close()


def parse_preflight(output: str, sid: str, seed: int) -> tuple[int, int]:
    plans = PLAN_RE.findall(output)
    if len(plans) != 1:
        raise RuntimeError(f"PREFLIGHT_MISSING_OR_DUPLICATE_PLAN sample={sid} seed={seed}")
    sample, raw_seed, verified, missing, max_new = plans[0]
    if sample != sid or int(raw_seed) != seed or int(verified) + int(missing) != 10:
        raise RuntimeError(f"PREFLIGHT_COUNTS_MISMATCH sample={sid} seed={seed} plan={plans[0]}")
    checks = [CHECK_RE.match(line) for line in output.splitlines()]
    found = [m.group(1, 2) for m in checks if m]
    if len(found) != len(CONDITIONS) or [name for name, _ in found] != list(CONDITIONS):
        raise RuntimeError(f"PREFLIGHT_CONDITION_SET_MISMATCH sample={sid} seed={seed}")
    if sum(status != "MISSING" for _, status in found) != int(verified):
        raise RuntimeError(f"PREFLIGHT_CHECK_COUNT_MISMATCH sample={sid} seed={seed}")
    # The historical two 15D assets for seed22911 are a mandatory part of
    # the audit; absence or silent recomputation is not allowed.
    if seed == SEEDS[0]:
        statuses = dict(found)
        if statuses["cum_L0_L1_L2"] != "LEGACY_AUDITED" or \
                statuses["fixed_L0_L1_L4"] != "LEGACY_AUDITED":
            raise RuntimeError(f"EXPECTED_LEGACY_NOT_AUDITED sample={sid}")
    if "DRY_RUN_ONLY NO_TRAINING_NO_FILES_WRITTEN" not in output:
        raise RuntimeError(f"PREFLIGHT_WAS_NOT_READ_ONLY sample={sid} seed={seed}")
    return int(verified), int(missing)


def check_runner_success(output: str, sid: str, seed: int, initially_missing: int) -> int:
    # Re-running is safe: already completed models cause ALL_TASKS_AUDITED.
    # If 1-10 tasks were absent, this runner fits up to 10 at a time.
    markers = [line for line in output.splitlines() if
               line.startswith("BATCH_RUN_COMPLETE ") or
               line.startswith("ALL_TASKS_AUDITED ")]
    if len(markers) != 1:
        raise RuntimeError(f"RUNNER_SUCCESS_MARKER_MISSING_OR_DUPLICATE sample={sid} seed={seed}")
    if markers[0].startswith("ALL_TASKS_AUDITED"):
        if initially_missing != 0:
            raise RuntimeError(f"INCONSISTENT_MISSING_TASK_COUNT sample={sid} seed={seed}")
        return 0
    m = re.search(r"\bnew_tasks=(\d+)\b", markers[0])
    if not m or int(m.group(1)) != initially_missing:
        raise RuntimeError(f"BATCH_RUN_COUNT_MISMATCH sample={sid} seed={seed} "
                           f"expected={initially_missing} marker={markers[0]}")
    passes = [line for line in output.splitlines() if line.startswith("RUN_AUDIT_PASS ")]
    if len(passes) != initially_missing:
        raise RuntimeError(f"BATCH_AUDIT_COUNT_MISMATCH sample={sid} seed={seed} "
                           f"expected={initially_missing} actual={len(passes)}")
    return initially_missing


def check_summary(output: str, sid: str) -> str:
    matches = SUMMARY_RE.findall(output)
    if len(matches) != 1 or matches[0] != (sid, "100", "10", "50"):
        raise RuntimeError(f"SUMMARY_INVALID sample={sid} found={matches}")
    if f"ALL_MATRIX_AUDIT_PASS sample={sid} tasks=100 seeds=10 conditions=10" not in output:
        raise RuntimeError(f"INDEPENDENT_MATRIX_AUDIT_MISSING sample={sid}")
    if "NO_MODEL_TRAINING_OR_ORIGINAL_FILES_CHANGED" not in output:
        raise RuntimeError(f"NO_ORIGINAL_FILE_MODIFICATION_MARKER_MISSING sample={sid}")
    dirs = [line.removeprefix("OUTPUT_DIR ") for line in output.splitlines()
            if line.startswith("OUTPUT_DIR ")]
    if len(dirs) != 1:
        raise RuntimeError(f"SUMMARY_OUTPUT_PATH_MISSING sample={sid}")
    directory = Path(dirs[0])
    expected_root = BASE / "results" / "e1e2_multiseed_statistics_v2" / sid
    if directory.parent != expected_root:
        raise RuntimeError(f"SUMMARY_OUTPUT_PATH_UNEXPECTED sample={sid}: {directory}")
    provenance_path = directory / "provenance.json"
    if not provenance_path.is_file():
        raise RuntimeError(f"SUMMARY_PROVENANCE_MISSING sample={sid}")
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    if not (provenance.get("status") == "completed" and
            provenance.get("sample") == sid and
            provenance.get("n_verified_cells") == 100 and
            provenance.get("seeds_in_frozen_order") == list(SEEDS) and
            list(provenance.get("conditions_in_frozen_order", {})) == list(CONDITIONS) and
            provenance.get("not_biological_replicates") is True and
            provenance.get("no_gmm_fit_or_scvi_training_performed") is True):
        raise RuntimeError(f"SUMMARY_PROVENANCE_INVALID sample={sid}")
    expected = {
        "all_100_verified_tasks.csv": 100,
        "condition_mean_sd_10seeds.csv": 10,
        "paired_equal15d_by_seed.csv": 50,
        "paired_equal15d_summary.csv": 5,
    }
    for filename, expected_rows in expected.items():
        p = directory / filename
        if not p.is_file():
            raise RuntimeError(f"SUMMARY_OUTPUT_MISSING sample={sid} file={filename}")
        if provenance.get("outputs_sha256", {}).get(filename) != sha256(p):
            raise RuntimeError(f"SUMMARY_OUTPUT_SHA_MISMATCH sample={sid} file={filename}")
        with p.open("r", newline="", encoding="utf-8-sig") as stream:
            entries = list(csv.DictReader(stream))
        if len(entries) != expected_rows or any(row.get("sample") != sid for row in entries):
            raise RuntimeError(f"SUMMARY_OUTPUT_ROWS_INVALID sample={sid} file={filename}")
        if filename == "all_100_verified_tasks.csv":
            keys = [(row.get("gmm_seed"), row.get("condition")) for row in entries]
            expect_keys = {(str(seed), cond) for seed in SEEDS for cond in CONDITIONS}
            if (len(set(keys)) != len(keys) or set(keys) != expect_keys or
                    any(int(row.get("oracle_k", -1)) != ORACLE_K[sid] for row in entries)):
                raise RuntimeError(f"SUMMARY_MATRIX_KEYS_OR_K_INVALID sample={sid}")
    return str(directory)


def preflight_all(session: Session) -> dict[tuple[str, int], int]:
    missing_by_key = {}
    total_existing = 0
    total_missing = 0
    session.tell("PREFLIGHT_ALL_BEGIN all eight frozen sections x ten seeds; NO_TRAINING")
    for sid in SECTIONS:
        for seed in SEEDS:
            label = f"PREFLIGHT {sid} seed={seed} K={ORACLE_K[sid]}"
            output = session.child([str(RUNNER), "--sample", sid, "--seed", str(seed)], label)
            verified, missing = parse_preflight(output, sid, seed)
            missing_by_key[(sid, seed)] = missing
            total_existing += verified
            total_missing += missing
            session.state["preflight"][f"{sid}:{seed}"] = {
                "verified": verified, "missing": missing,
            }
            session.save()
            session.tell(f"PREFLIGHT_PASS sample={sid} seed={seed} verified={verified} missing={missing}")
    if total_existing + total_missing != len(SECTIONS) * len(SEEDS) * len(CONDITIONS):
        raise RuntimeError("PREFLIGHT_TOTAL_NOT_800")
    session.tell(f"PREFLIGHT_ALL_PASS sections=8 cells=800 verified={total_existing} missing={total_missing}")
    session.state["preflight_passed_utc"] = utc()
    session.save()
    return missing_by_key


def run_remaining(session: Session, preflight_missing: dict[tuple[str, int], int]):
    total_trained = 0
    for index, sid in enumerate(SECTIONS, 1):
        session.tell(f"SECTION_BEGIN {sid} ({index}/{len(SECTIONS)}) K={ORACLE_K[sid]}")
        for seed in SEEDS:
            label = f"RUN {sid} seed={seed}"
            output = session.child(
                [str(RUNNER), "--sample", sid, "--seed", str(seed),
                 "--run", "--max-new", "10"], label, echo_runs=True,
            )
            count = check_runner_success(output, sid, seed, preflight_missing[(sid, seed)])
            total_trained += count
            session.state["new_tasks_confirmed_by_runner"] = total_trained
            session.state["completed_seed_groups"].append({
                "sample": sid, "seed": seed, "audited_new_tasks": count,
                "finished_utc": utc(),
            })
            session.save()
            session.tell(f"SEED_COMPLETE sample={sid} seed={seed} new={count} "
                         f"groups={len(session.state['completed_seed_groups'])}/80")
        # The V2 summarizer checks *all* 100 result files and recalculates
        # ARI/NMI before it creates its separate, unique statistics directory.
        session.tell(f"SECTION_FULL_AUDIT_AND_SUMMARY_BEGIN sample={sid}")
        output = session.child([str(STATS), "--sample", sid], f"SUMMARY {sid}")
        dest = check_summary(output, sid)
        session.state["completed_summaries"][sid] = dest
        session.save()
        session.tell(f"SECTION_COMPLETE sample={sid} verified=100/100 summary={dest}")
    session.tell(f"OVERNIGHT_ALL_COMPLETE sections=8 audited_cells=800 "
                 f"new_tasks={total_trained} summaries=8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true",
                        help="Explicitly run missing tasks (after the whole-matrix preflight)")
    args = parser.parse_args()
    try:
        hashes = assert_frozen_scripts()
        output_root = BASE / "results" / "e1e2_overnight_v1"
        with exclusive_process_lock(output_root / "overnight.lock"):
            session = Session(output_root, args.run, hashes)
            try:
                session.tell(f"SESSION_DIR {session.dest}")
                session.tell(f"MODE {'RUN' if args.run else 'PREFLIGHT_ONLY'}; sections={list(SECTIONS)}")
                with keep_system_awake():
                    planned = preflight_all(session)
                    if args.run:
                        session.tell("ALL_EIGHT_SECTIONS_PREFLIGHT_PASSED_START_SEQUENTIAL_TRAINING")
                        run_remaining(session, planned)
                        session.state["status"] = "completed"
                    else:
                        session.tell("DRY_RUN_COMPLETE_NO_GMM_TRAINING")
                        session.state["status"] = "preflight_completed"
                session.state["finished_utc"] = utc()
                session.save()
                session.tell(f"SESSION_LOG {session.logpath}")
                return 0
            except BaseException as exc:
                session.state["status"] = "halted"
                session.state["error"] = repr(exc)
                session.state["stopped_utc"] = utc()
                session.save()
                session.tell(f"OVERNIGHT_HALTED {type(exc).__name__}: {exc}")
                session.tell(f"SESSION_LOG {session.logpath}")
                return 1
            finally:
                session.close()
    except Exception as exc:
        print(f"OVERNIGHT_PRESTART_STOP {type(exc).__name__}: {exc}", file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
