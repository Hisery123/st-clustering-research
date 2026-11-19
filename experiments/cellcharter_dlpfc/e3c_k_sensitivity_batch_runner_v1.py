"""Audit and safely run a bounded CellCharter DLPFC E3c frozen K-grid batch.

DEFAULT (without --run) IS READ-ONLY: independently audit all 4 conditions x
5 K values x 10 seeds for the requested sample(s), and print an inventory.
It creates no directories and does not fit any model.

Explicit --run permits at most --max-new NEW fits, defaulting to ONE. Before
fitting anything, it audits ALL requested cells and stops on any discrepancy.
Each fit is a fresh child Python process of the frozen one-task runner. It
never overwrites, deletes or auto-retries results; first error stops the batch.
The user runs this manually on their own Windows PC.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
import time
import traceback
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
SINGLE = BASE / 'e3c_k_sensitivity_single_task_v1.py'
EXPECTED_SINGLE_SHA256 = 'c3bbe996e8bf5f13775a193061fc4b654d9317170e0dca14b7792c429cd77cca'
BATCH_PROTOCOL = 'E3C_K_GRID_SAFE_BATCH_V1'
MAX_NEW_ALLOWED = 160  # Four feature conditions x four non-Oracle K values x ten seeds, per sample.


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for data in iter(lambda: f.read(1024 * 1024), b''):
            h.update(data)
    return h.hexdigest()


def utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def demand(ok: bool, message: str):
    if not ok:
        raise RuntimeError(message)


def load_frozen():
    demand(SINGLE.is_file(), f'SINGLE_TASK_MISSING {SINGLE}')
    actual = sha256(SINGLE)
    demand(actual == EXPECTED_SINGLE_SHA256,
           f'SINGLE_TASK_SHA256_MISMATCH actual={actual} expected={EXPECTED_SINGLE_SHA256}')
    import importlib.util
    spec = importlib.util.spec_from_file_location('e3c_frozen_single_batch_v1', SINGLE)
    demand(spec is not None and spec.loader is not None, f'IMPORT_FAILED {SINGLE}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    e1 = module.source_check(BASE)  # Verifies all three E1/E2 SHA256 hashes.
    demand(len(module.SAMPLES) == 12 and len(module.SEEDS) == 10 and
           len(module.CONDITIONS) == 4 and tuple(module.KS) == (5, 6, 7, 8, 9),
           'FROZEN_GRID_MISMATCH')
    return module, e1


def inventory(module, e1, samples: tuple[str, ...]):
    """Fail closed: every K grid cell must be either fully audited or absent."""
    rows = []
    # Import once to avoid repeated module loading for the 480 reused E1/E2 cells.
    e1v2 = module.import_script(BASE / 'e1e2_safe_batch_runner_v2.py', 'e3c_batch_frozen_e1_auditor')
    expected_sample_total = len(module.CONDITIONS) * len(module.SEEDS) * len(module.KS)
    for sid in samples:
        counts = {'REUSED_AUDITED': 0, 'EXISTING_AUDITED': 0, 'NEW_TASK': 0}
        for seed in module.SEEDS:
            for cond in module.CONDITIONS:
                info = e1.preflight(sid, cond, seed)
                demand(info['blocks'] == module.CONDITIONS[cond],
                       f'FEATURE_BLOCKS_MISMATCH {sid}/{cond}/{seed}')
                for k in module.KS:
                    out = module.destination(e1, sid, cond, k, seed)
                    cell = {'sample': sid, 'condition': cond, 'feature_dim': info['feature_dim'],
                            'k': int(k), 'gmm_seed': int(seed),
                            'oracle_k': int(info['k'])}
                    if k == info['k']:
                        demand(not out.exists(),
                               f'ORACLE_K_DUPLICATE_E3_OUTPUT_STOP {out}')
                        old = (e1.RESULT_ROOT / 'e1e2_multiscale_gmm_v1' /
                               sid / cond / f'seed_{seed}')
                        res = e1v2.check(cond, info, e1, old, info['legacy'])
                        demand(res['status'] in ('NEW_AUDITED', 'LEGACY_AUDITED'),
                               f'ORACLE_E1E2_AUDIT_FAILED sample={sid} condition={cond} '
                               f'k={k} seed={seed} result={res}')
                        cell.update(status='REUSED_AUDITED', origin=res['status'],
                                    ari=res['ari'], nmi=res['nmi'], output=str(old))
                    elif out.exists():
                        ari, nmi = module.audit_existing(e1, info, k, out)
                        cell.update(status='EXISTING_AUDITED', origin='E3C',
                                    ari=ari, nmi=nmi, output=str(out))
                    else:
                        cell.update(status='NEW_TASK', origin='NOT_RUN',
                                    ari=None, nmi=None, output=str(out))
                    counts[cell['status']] += 1
                    rows.append(cell)
            print(f'PREFLIGHT_SEED_OK sample={sid} seed={seed} ',
                  f'checked={len(module.CONDITIONS)*len(module.KS)}', flush=True)
        demand(sum(counts.values()) == expected_sample_total,
               f'SAMPLE_GRID_COUNT_MISMATCH {sid} {counts}')
        demand(counts['REUSED_AUDITED'] == len(module.CONDITIONS) * len(module.SEEDS),
               f'ORACLE_REUSE_COUNT_MISMATCH {sid}: {counts}')
        print(f'PREFLIGHT_SAMPLE_OK sample={sid} verified_reused={counts["REUSED_AUDITED"]} '
              f'verified_existing={counts["EXISTING_AUDITED"]} '
              f'pending_new={counts["NEW_TASK"]} total={sum(counts.values())}', flush=True)
    demand(len(rows) == expected_sample_total * len(samples), 'GRID_TOTAL_MISMATCH')
    return rows


@contextmanager
def exclusive_lock(lockfile: Path):
    """Windows nonblocking byte lock; released by OS on crash/exit."""
    lockfile.parent.mkdir(parents=True, exist_ok=True)
    with lockfile.open('a+b') as stream:
        stream.seek(0, os.SEEK_END)
        if stream.tell() == 0:
            stream.write(b'0')
            stream.flush()
        stream.seek(0)
        if os.name == 'nt':
            import msvcrt
            try:
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError as exc:
                raise RuntimeError('E3C_ANOTHER_BATCH_ACTIVE') from exc
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
                raise RuntimeError('E3C_ANOTHER_BATCH_ACTIVE') from exc
            try:
                yield
            finally:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


@contextmanager
def inhibit_idle_sleep():
    """Windows system-sleep inhibit, only for explicit training, not dry-run."""
    if os.name != 'nt':
        yield
        return
    import ctypes
    flags = 0x80000000 | 0x00000001  # ES_CONTINUOUS | ES_SYSTEM_REQUIRED
    set_state = ctypes.windll.kernel32.SetThreadExecutionState
    demand(set_state(flags) != 0, 'WINDOWS_INHIBIT_IDLE_SLEEP_FAILED')
    try:
        yield
    finally:
        set_state(0x80000000)


def write_json(path: Path, data):
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    temp.replace(path)


def run_bounded(module, e1, rows, samples, max_new: int, timeout_seconds: int):
    todo = [r for r in rows if r['status'] == 'NEW_TASK']
    if not todo:
        print('ALL_REQUESTED_GRID_AUDITED NO_TRAINING_NO_FILES_WRITTEN', flush=True)
        return 0
    if max_new > len(todo):
        print(f'REQUEST_CAP_GREATER_THAN_PENDING pending={len(todo)} '
              f'cap={max_new}: only pending tasks can run', flush=True)
    todo = todo[:max_new]
    root = e1.RESULT_ROOT / 'e3c_k_sensitivity_batch_sessions_v1'
    lock = root / '.exclusive_batch.lock'
    # Exclusive lock applies to a batch session. Do not concurrently run
    # separate single-task fits/manual copies during the same session.
    with exclusive_lock(lock):
        session = root / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') +
                          '_' + uuid.uuid4().hex[:10])
        session.mkdir(parents=True, exist_ok=False)
        log = session / 'session.log'
        csvfile = session / 'preflight_inventory.csv'
        fields = ['sample', 'condition', 'feature_dim', 'k', 'gmm_seed',
                  'oracle_k', 'status', 'origin', 'ari', 'nmi', 'output']
        with csvfile.open('w', newline='', encoding='utf-8') as stream:
            w = csv.DictWriter(stream, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
        state = {
            'protocol': BATCH_PROTOCOL, 'status': 'running', 'started_utc': utc(),
            'samples': list(samples), 'requested_max_new': max_new,
            'timeout_seconds_per_task': timeout_seconds,
            'single_task_sha256': EXPECTED_SINGLE_SHA256,
            'cells_total': len(rows),
            'reused_audited': sum(x['status'] == 'REUSED_AUDITED' for x in rows),
            'previously_completed_audited': sum(x['status'] == 'EXISTING_AUDITED' for x in rows),
            'pending_new_before_batch': sum(x['status'] == 'NEW_TASK' for x in rows),
            'started_new': 0, 'completed_new_and_audited': 0,
            'completed_tasks': [],
            'warning': 'Seeds and slices are NOT independent biological replicates.',
        }
        summary = session / 'session_status.json'
        write_json(summary, state)
        print(f'E3C_SESSION_START {session} starting_new={len(todo)}', flush=True)
        with log.open('w', encoding='utf-8', buffering=1) as sink:
            def say(msg):
                line = f'[{utc()}] {msg}'
                print(line, flush=True)
                sink.write(line + '\n')

            try:
                with inhibit_idle_sleep():
                    for i, item in enumerate(todo, 1):
                        sid, cond, k, seed = (item['sample'], item['condition'],
                                            item['k'], item['gmm_seed'])
                        out = module.destination(e1, sid, cond, k, seed)
                        demand(not out.exists(), f'OUTPUT_APPEARED_AFTER_PREFLIGHT {out}')
                        state['started_new'] += 1
                        write_json(summary, state)
                        cmd = [sys.executable, str(SINGLE), '--sample', sid,
                               '--condition', cond, '--k', str(k),
                               '--seed', str(seed), '--fit']
                        say(f'RUN_START {i}/{len(todo)} sample={sid} condition={cond} k={k} seed={seed}')
                        started = time.perf_counter()
                        try:
                            result = subprocess.run(cmd, stdout=subprocess.PIPE,
                                                    stderr=subprocess.STDOUT, text=True,
                                                    encoding='utf-8', errors='replace',
                                                    timeout=timeout_seconds, check=False)
                            response = result.stdout
                            returncode = result.returncode
                        except subprocess.TimeoutExpired as exc:
                            response = (exc.stdout or b'')
                            if isinstance(response, bytes):
                                response = response.decode('utf-8', 'replace')
                            raise RuntimeError(f'SINGLE_TASK_TIMEOUT_STOP after={timeout_seconds}s '
                                               f'sample={sid} condition={cond} k={k} seed={seed} '
                                               f'partial_log={response[-1200:]}') from exc
                        elapsed = time.perf_counter() - started
                        tasklog = session / f'task_{i:03d}_{sid}_{cond}_k{k}_seed{seed}.log'
                        tasklog.write_text(response, encoding='utf-8')
                        sink.write(f'[CHILD_TASK {i}]\n' + response + '\n')
                        demand(returncode == 0, f'CHILD_FAILED_STOP returncode={returncode} '
                               f'log={tasklog}')
                        demand('E3C_TASK_COMPLETE ' in response,
                               f'CHILD_MISSING_COMPLETE_MARKER {tasklog}')
                        # Recheck using the original immutable input and current output.
                        info = e1.preflight(sid, cond, seed)
                        ari, nmi = module.audit_existing(e1, info, k, out)
                        state['completed_new_and_audited'] += 1
                        state['completed_tasks'].append({
                            'sample': sid, 'condition': cond, 'k': k, 'seed': seed,
                            'ari': ari, 'nmi': nmi, 'child_wall_seconds': round(elapsed, 3),
                            'result_dir': str(out), 'log': str(tasklog),
                        })
                        write_json(summary, state)
                        say(f'RUN_AUDIT_PASS {i}/{len(todo)} sample={sid} '
                            f'condition={cond} k={k} seed={seed} '
                            f'ARI={ari:.6f} NMI={nmi:.6f} wall_seconds={elapsed:.2f}')
                state['status'] = 'completed'
                state['finished_utc'] = utc()
                write_json(summary, state)
                say(f'E3C_BATCH_COMPLETE new_audited={state["completed_new_and_audited"]} '
                    f'summary={summary}')
                return 0
            except BaseException as exc:
                state['status'] = 'failed'
                state['error'] = repr(exc)
                state['traceback'] = traceback.format_exc()
                state['finished_utc'] = utc()
                write_json(summary, state)
                say(f'E3C_BATCH_HALTED {exc!r} summary={summary}')
                return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sample', required=True,
                        help='One frozen DLPFC sample ID, or ALL for all 12 sections')
    parser.add_argument('--run', action='store_true',
                        help='Only this explicit option can start GMM fitting')
    parser.add_argument('--max-new', type=int, default=1,
                        help='At most this many new fits in one run (default 1; maximum 160)')
    parser.add_argument('--task-timeout-sec', type=int, default=600,
                        help='Seconds before a stuck task causes STOP (default 600)')
    args = parser.parse_args()
    demand(1 <= args.max_new <= MAX_NEW_ALLOWED,
           f'MAX_NEW_OUT_OF_RANGE {args.max_new}; limit=1..{MAX_NEW_ALLOWED}')
    demand(60 <= args.task_timeout_sec <= 3600,
           'TASK_TIMEOUT_OUT_OF_RANGE allowed=60..3600')
    module, e1 = load_frozen()
    if args.sample == 'ALL':
        samples = module.SAMPLES
    else:
        demand(args.sample in module.SAMPLES, f'UNKNOWN_SAMPLE {args.sample}')
        samples = (args.sample,)
    total = len(samples) * len(module.CONDITIONS) * len(module.KS) * len(module.SEEDS)
    print(f'E3C_GRID_PREFLIGHT_START samples={len(samples)} cells={total} '
          f'mode={"RUN_AFTER_PREFLIGHT" if args.run else "READ_ONLY"}', flush=True)
    rows = inventory(module, e1, samples)
    counts = {k: sum(row['status'] == k for row in rows)
              for k in ('REUSED_AUDITED','EXISTING_AUDITED','NEW_TASK')}
    print(f'E3C_GRID_PREFLIGHT_PASS total={len(rows)} '
          f'REUSED_AUDITED={counts["REUSED_AUDITED"]} '
          f'EXISTING_AUDITED={counts["EXISTING_AUDITED"]} '
          f'NEW_TASK={counts["NEW_TASK"]}', flush=True)
    if not args.run:
        print('DRY_RUN_ONLY NO_TRAINING_NO_FILES_WRITTEN', flush=True)
        return 0
    return run_bounded(module, e1, rows, samples, args.max_new, args.task_timeout_sec)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as err:
        print(f'E3C_PREFLIGHT_ABORTED {err!r}', file=sys.stderr, flush=True)
        sys.exit(1)
