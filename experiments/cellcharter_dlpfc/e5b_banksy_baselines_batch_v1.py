"""E5b six-patient BANKSY frozen mature baseline; 36 predictions.

This is the same adapted official BANKSY Python core as E5a:
initialize_banksy -> generate_banksy_matrix -> pca_umap (PC20 only)
-> run_Leiden_partition (16 frozen resolutions, 50 neighbors).
All 16 resolution partitions per technical seed; K-blind is fixed 1.0,
Oracle is nearest actual K on frozen grid, tie smaller resolution.
No reference_only/Classification reading and no ARI/NMI until whole E5b done.
Input: exact barcode-aligned in-tissue staged matrix, 2000 HVGs, native
BANKSY normalize1e4/log1p, pixel coordinates x/y. Six independent patients.
--run starts six independent sample child processes, each six predictions.
--resume explicitly continues completed-safe sample batch, no overwrites.
This file has NOT yet been validated on the user's Windows computer.
"""
from __future__ import annotations

import argparse
import contextlib
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

import numpy as np
import pandas as pd

BASE = Path(r"D:\paper\CellCharter_reproduction")
ROOT = BASE / "results" / "e5b_external_v1"
STAGE = ROOT / "input_stage_20261121T083911Z_14272"
BANKSY_LIB = BASE / "third_party" / "e5a_banksy_libs"
PROTOCOL = "E5B_BANKSY_FROZEN_SIX_PATIENTS_V1"
SAMPLES = ("1142243F", "1160920F", "CID4290",
           "CID4465", "CID44971", "CID4535")
SPOTS = (4784, 4895, 2426, 1211, 1160, 1125)
GENES = (28402, 28402, 19237, 19237, 19237, 19237)
ORACLE_K = (5, 7, 3, 3, 6, 6)
SEEDS = (22911, 7449, 25842)
RESOLUTIONS = (0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.65,
               0.8, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0)
BLIND_RESOLUTION = 1.0
EMBED_SEED = 22911

def require(ok, msg):
    if not ok:
        raise RuntimeError(msg)

def now():
    return datetime.now(timezone.utc).isoformat()

def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as fd:
        for block in iter(lambda: fd.read(1048576), b""):
            h.update(block)
    return h.hexdigest()

def write_json(path, obj):
    Path(path).write_text(
        json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8")

def version(name):
    try:
        return md.version(name)
    except md.PackageNotFoundError:
        return "not_recorded"

def stage_status():
    f = STAGE / "batch_status.json"
    require(f.is_file(), "E5B_BANKSY_STAGE_STATUS_MISSING")
    data = json.loads(f.read_text(encoding="utf-8"))
    require(data.get("status") == "completed" and
            data.get("total_model_spots") == 15601 and
            [x["sample"] for x in data.get("samples", [])] == list(SAMPLES),
            "E5B_BANKSY_STAGE_NOT_COMPLETED")
    return sha256(f), data

def sample_input(sample, entry):
    from scipy import sparse
    from scipy.io import mmread
    import scanpy as sc
    import anndata as ad

    sid = SAMPLES.index(sample)
    folder = STAGE / "inputs" / sample
    required = ("model_spots.csv", "barcodes.tsv",
                "features.tsv", "matrix.mtx")
    for name in required:
        f = folder / name
        require(f.is_file(), "E5B_BANKSY_SOURCE_MISSING " + str(f))
        require(sha256(f) == entry["input_files_sha256"][name],
                "E5B_BANKSY_SOURCE_SHA_MISMATCH " + str(f))

    spots = pd.read_csv(folder / "model_spots.csv",
                        dtype={"barcode": str}, keep_default_na=False)
    bc = pd.read_csv(folder / "barcodes.tsv", sep="\t", header=None,
                     dtype=str, keep_default_na=False).iloc[:, 0].tolist()
    ft = pd.read_csv(folder / "features.tsv", sep="\t", header=None,
                     dtype=str, keep_default_na=False)
    require(len(spots) == SPOTS[sid] and spots.barcode.is_unique and
            len(ft) == GENES[sid] and ft.shape[1] in (2, 3) and
            len(set(bc)) == len(bc),
            "E5B_BANKSY_SOURCE_ROW_COUNT_OR_COLUMNS_BAD " + sample)
    cols = ("pxl_col_in_fullres", "pxl_row_in_fullres")
    require(all(c in spots.columns for c in cols),
            "E5B_BANKSY_SPATIAL_PIXEL_COLUMNS_MISSING")
    xy = spots[list(cols)].to_numpy(dtype=np.float64)
    require(xy.shape == (SPOTS[sid], 2) and np.isfinite(xy).all(),
            "E5B_BANKSY_XY_INVALID " + sample)

    matrix = mmread(str(folder / "matrix.mtx"))
    require(sparse.issparse(matrix) and
            matrix.shape == (GENES[sid], len(bc)),
            "E5B_BANKSY_COUNTS_SHAPE_MISMATCH")
    indices = pd.Index(bc).get_indexer(spots.barcode)
    require((indices >= 0).all(), "E5B_BANKSY_BARCODE_NOT_MATCHED")
    counts = matrix.tocsc()[:, indices].T.tocsr().astype(np.float32)
    del matrix
    require(counts.shape == (SPOTS[sid], GENES[sid]) and
            np.isfinite(counts.data).all() and (counts.data >= 0).all(),
            "E5B_BANKSY_COUNTS_VALUES_BAD")
    require(np.all(np.asarray(counts.sum(axis=1)).ravel() > 0),
            "E5B_BANKSY_ZERO_UMI_SPOT_BLOCKS_LOGNORM")

    obs = pd.DataFrame(index=pd.Index(spots.barcode, name="barcode"))
    obs["x"] = xy[:, 0]
    obs["y"] = xy[:, 1]
    var = pd.DataFrame(index=pd.Index(ft.iloc[:, 1].tolist(),
                                      name="gene_symbol"))
    adata = ad.AnnData(X=counts, obs=obs, var=var)
    adata.var_names_make_unique()
    adata.obsm["coord_xy"] = xy
    # Preserve audited adapted E5a BANKSY native preprocessing.
    sc.pp.normalize_total(adata, target_sum=10000)
    sc.pp.log1p(adata)
    sc.pp.highly_variable_genes(adata, flavor="seurat",
                                n_top_genes=2000, subset=False)
    mask = adata.var["highly_variable"].to_numpy()
    require(int(mask.sum()) == 2000,
            "E5B_BANKSY_EXPECTED_HVG_2000")
    adata = adata[:, mask].copy()
    require(adata.n_obs == SPOTS[sid] and adata.n_vars == 2000 and
            (np.isfinite(adata.X.data).all() if sparse.issparse(adata.X)
             else np.isfinite(adata.X).all()),
            "E5B_BANKSY_HVG_VALUES_OR_SPOTS_BAD")
    provenance = {
        "matrix_sha256": entry["input_files_sha256"]["matrix.mtx"],
        "feature_sha256": entry["input_files_sha256"]["features.tsv"],
        "barcodes_sha256": entry["input_files_sha256"]["barcodes.tsv"],
        "model_spots_sha256": entry["input_files_sha256"]["model_spots.csv"],
        "n_spots": int(adata.n_obs),
        "n_hvg": int(adata.n_vars),
        "hvg_names_sha256": hashlib.sha256(
            "\n".join(adata.var_names).encode("utf-8")).hexdigest(),
        "spatial_xy_source": list(cols),
        "expression_preprocessing":
            "normalize_total(1e4),log1p,HVG(seurat,2000)",
    }
    return adata, spots.barcode.to_numpy(), provenance

def make_embedding(adata):
    from banksy.initialize_banksy import initialize_banksy
    from banksy.embed_banksy import generate_banksy_matrix
    from banksy_utils.umap_pca import pca_umap

    random.seed(EMBED_SEED)
    np.random.seed(EMBED_SEED)
    banksy = initialize_banksy(
        adata, ("x", "y", "coord_xy"), num_neighbours=15,
        nbr_weight_decay="scaled_gaussian", max_m=1,
        plt_edge_hist=False, plt_nbr_weights=False,
        plt_agf_angles=False, plt_theta=False)
    banksy, _ = generate_banksy_matrix(
        adata, banksy, lambda_list=[0.2], max_m=1,
        variance_balance=False, plot_std=False,
        save_matrix=False, verbose=False)
    pca_umap(banksy, pca_dims=[20], add_umap=False,
             plt_remaining_var=False)
    reduced = banksy["scaled_gaussian"][0.2]["adata"].obsm["reduced_pc_20"]
    require(reduced.shape == (adata.n_obs, 20) and
            np.isfinite(reduced).all(), "E5B_BANKSY_20PC_NONFINITE")
    return banksy, np.asarray(reduced, dtype=np.float32)

def fit_seed(banksy, seed, n):
    from banksy.cluster_methods import run_Leiden_partition
    random.seed(seed)
    np.random.seed(seed)
    results, _ = run_Leiden_partition(
        banksy_dict=banksy,
        resolutions=list(RESOLUTIONS),
        num_nn=50, num_iterations=-1, partition_seed=seed,
        match_labels=False, annotations=None, max_labels=None,
        verbose=False)
    require(len(results) == len(RESOLUTIONS),
            "E5B_BANKSY_16_RESOLUTION_RESULTS_MISSING")
    candidates = []
    partitions = {}
    for j, res in enumerate(RESOLUTIONS):
        mask = np.isclose(results["resolution"].to_numpy(dtype=float),
                          res, atol=1e-12, rtol=0)
        require(int(mask.sum()) == 1,
                "E5B_BANKSY_RESOLUTION_RESULT_MISSING " + str(res))
        row = results.loc[mask].iloc[0]
        labels = np.asarray(row["labels"].dense, dtype=np.int64)
        require(labels.shape == (n,) and (labels >= 0).all(),
                "E5B_BANKSY_PARTITION_INVALID")
        actual = int(np.unique(labels).size)
        require(actual == int(row["num_labels"]),
                "E5B_BANKSY_REPORTED_K_MISMATCH")
        candidates.append({
            "resolution": res, "actual_k": actual,
            "archive_key": f"r_{j:02d}",
        })
        partitions[res] = labels.copy()
    return candidates, partitions

def validate_sample_attempt(attempt, sample):
    mfile = attempt / "manifest.json"
    require(mfile.is_file(), "E5B_BANKSY_MANIFEST_MISSING")
    m = json.loads(mfile.read_text(encoding="utf-8"))
    require(m.get("status") == "completed" and
            m.get("protocol") == PROTOCOL and
            m.get("sample") == sample and
            len(m.get("tasks", [])) == 6,
            "E5B_BANKSY_SAMPLE_NOT_COMPLETE")
    expected = [(seed, arm) for seed in SEEDS for arm in
                ("k_blind", "oracle_k")]
    require([(x["seed"], x["arm"]) for x in m["tasks"]] == expected,
            "E5B_BANKSY_TASK_ORDER_MISMATCH")
    for task in m["tasks"]:
        predfile = attempt / task["predictions_file"]
        require(predfile.is_file() and
                sha256(predfile) == task["prediction_sha256"],
                "E5B_BANKSY_PREDICTION_SHA_CHANGED")
    for seed in SEEDS:
        f = attempt / f"seed_{seed}" / "all_resolution_labels.npz"
        require(f.is_file() and
                m.get("resolution_label_sha256", {}).get(str(seed)) ==
                sha256(f), "E5B_BANKSY_RESOLUTION_SHA_CHANGED")
    return m

def run_sample(sample, session):
    require(BANKSY_LIB.is_dir(), "E5B_BANKSY_LIB_NOT_FOUND")
    sys.path.insert(0, str(BANKSY_LIB))
    from banksy.initialize_banksy import initialize_banksy  # noqa: F401

    _, stage = stage_status()
    info = stage["samples"][SAMPLES.index(sample)]
    target = session / sample
    target.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    attempt = target / f"attempt_{stamp}_{os.getpid()}"
    require(not attempt.exists(), "E5B_BANKSY_ATTEMPT_EXISTS")
    attempt.mkdir(parents=False, exist_ok=False)
    mfile = attempt / "manifest.json"
    m = {
        "status": "running", "protocol": PROTOCOL,
        "sample": sample, "expected_tasks": 6,
        "stage_batch_status_sha256": sha256(STAGE / "batch_status.json"),
        "embedding_seed": EMBED_SEED, "seeds": list(SEEDS),
        "resolutions": list(RESOLUTIONS),
        "k_blind_resolution": BLIND_RESOLUTION,
        "oracle_k_is_label_count_informed": True,
        "BANKSY": {
            "num_neighbours": 15, "nbr_weight_decay": "scaled_gaussian",
            "max_m": 1, "lambda": 0.2, "pca_dims": 20,
            "partition_num_nn": 50, "num_iterations": -1,
            "hvg": 2000, "hvg_flavor": "seurat",
        },
        "versions": {n: version(n) for n in (
            "pybanksy", "numpy", "pandas", "scanpy", "anndata", "scipy")},
        "reference_labels_read": False,
        "metrics_computed": False,
        "started_utc": now(), "tasks": [], "resolution_label_sha256": {},
    }
    write_json(mfile, m)
    start = time.perf_counter()
    internal_log = attempt / "banksy_official_stdout.log"
    try:
        with internal_log.open("w", encoding="utf-8") as log:
            with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
                adata, barcodes, provenance = sample_input(sample, info)
                banksy, reduced = make_embedding(adata)
        np.save(attempt / "banksy_20pc_embedding.npy",
                reduced, allow_pickle=False)
        m["source"] = provenance
        m["embedding_sha256"] = sha256(
            attempt / "banksy_20pc_embedding.npy")
        write_json(mfile, m)
        del reduced, adata

        for seed in SEEDS:
            folder = attempt / f"seed_{seed}"
            folder.mkdir(parents=False, exist_ok=False)
            with internal_log.open("a", encoding="utf-8") as log:
                with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
                    print(f"OFFICIAL_BANKSY_LEIDEN seed={seed}")
                    candidates, partitions = fit_seed(banksy, seed,
                                                      SPOTS[SAMPLES.index(sample)])
            np.savez_compressed(
                folder / "all_resolution_labels.npz",
                **{f"r_{j:02d}": partitions[res]
                   for j, res in enumerate(RESOLUTIONS)})
            m["resolution_label_sha256"][str(seed)] = sha256(
                folder / "all_resolution_labels.npz")
            # Compute the complete frozen resolution grid for both arms
            # without reading true tissue labels.
            oracle = ORACLE_K[SAMPLES.index(sample)]
            oracle_choice = min(
                candidates,
                key=lambda row: (abs(row["actual_k"]-oracle),
                                 row["resolution"]))
            blind_choice = next(x for x in candidates if
                                x["resolution"] == BLIND_RESOLUTION)
            for arm, chosen in (
                ("k_blind", blind_choice), ("oracle_k", oracle_choice)):
                labels = partitions[chosen["resolution"]]
                sub = folder / arm
                sub.mkdir(parents=False, exist_ok=False)
                predfile = sub / "predictions.csv"
                pd.DataFrame({
                    "barcode": barcodes, "cluster": labels,
                }).to_csv(predfile, index=False)
                task = {
                    "arm": arm, "seed": seed,
                    "chosen_resolution": chosen["resolution"],
                    "actual_k": chosen["actual_k"],
                    "selection": (
                        "frozen_resolution_1.0_without_reference" if arm=="k_blind"
                        else "nearest_known_K_on_frozen_resolution_grid"),
                    "candidate_trials": candidates,
                    "predictions_file": str(predfile.relative_to(attempt)),
                    "prediction_sha256": sha256(predfile),
                }
                m["tasks"].append(task)
                write_json(mfile, m)
                print(f"E5B_BANKSY_PREDICTION_PASS sample={sample} "
                      f"seed={seed} arm={arm} "
                      f"resolution={chosen['resolution']} "
                      f"actual_k={chosen['actual_k']}", flush=True)
            del candidates, partitions
        del banksy
        require(len(m["tasks"]) == 6, "E5B_BANKSY_SAMPLE_SIX_TASKS_NOT_DONE")
        m["status"] = "completed"
        m["finished_utc"] = now()
        m["seconds"] = round(time.perf_counter()-start, 6)
        write_json(mfile, m)
        validate_sample_attempt(attempt, sample)
        print(f"E5B_BANKSY_SAMPLE_PASS sample={sample} "
              f"tasks=6 seconds={m['seconds']} result={attempt}",
              flush=True)
    except BaseException as exc:
        m.update({"status": "failed", "error": repr(exc),
                  "traceback": traceback.format_exc(),
                  "failed_utc": now()})
        write_json(mfile, m)
        print(f"E5B_BANKSY_SAMPLE_FAILED sample={sample} error={exc!r} "
              f"result={attempt} official_log={internal_log}", flush=True)
        raise

def execute_batch(session=None):
    stage_sha, _ = stage_status()
    require(BANKSY_LIB.is_dir(), "E5B_BANKSY_LIB_NOT_FOUND")
    if session is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        session = ROOT / f"banksy_{stamp}_{os.getpid()}"
        require(not session.exists(), "E5B_BANKSY_SESSION_EXISTS")
        session.mkdir(parents=True, exist_ok=False)
        status = {
            "status": "running", "protocol": PROTOCOL,
            "stage_status_sha256": stage_sha,
            "expected_samples": list(SAMPLES), "expected_tasks": 36,
            "completed_samples": [], "failures": [],
            "started_utc": now(), "reference_labels_read": False,
            "metrics_computed": False,
        }
    else:
        session = Path(session).resolve()
        f = session / "batch_status.json"
        require(f.is_file(), "E5B_BANKSY_RESUME_STATUS_MISSING")
        status = json.loads(f.read_text(encoding="utf-8"))
        require(status.get("protocol") == PROTOCOL and
                status.get("stage_status_sha256") == stage_sha and
                status.get("status") == "halted" and
                status.get("expected_tasks") == 36,
                "E5B_BANKSY_RESUME_NOT_ALLOWED")
        status["status"] = "running"
        status.setdefault("resume_utc", []).append(now())
    status_file = session / "batch_status.json"
    write_json(status_file, status)
    done = {x["sample"]: x for x in status["completed_samples"]}
    try:
        for sid in SAMPLES:
            if sid in done:
                validate_sample_attempt(Path(done[sid]["attempt"]), sid)
                print(f"E5B_BANKSY_REUSED sample={sid}", flush=True)
                continue
            print(f"E5B_BANKSY_SAMPLE_START sample={sid} expected_tasks=6",
                  flush=True)
            ret = subprocess.run([
                sys.executable, str(Path(__file__).resolve()),
                "--child-sample", sid, "--session", str(session),
            ], check=False)
            require(ret.returncode == 0,
                    f"E5B_BANKSY_CHILD_FAILURE sample={sid} "
                    f"exit_code={ret.returncode}")
            attempts = sorted(p for p in (session / sid).glob("attempt_*")
                              if p.is_dir())
            completed_attempts = []
            for attempt in attempts:
                try:
                    m = json.loads(
                        (attempt / "manifest.json").read_text(encoding="utf-8"))
                    if m.get("status") == "completed":
                        completed_attempts.append(attempt)
                except (OSError, ValueError):
                    pass
            require(len(completed_attempts) == 1,
                    "E5B_BANKSY_COMPLETED_ATTEMPT_AMBIGUOUS")
            result = completed_attempts[0]
            validate_sample_attempt(result, sid)
            status["completed_samples"].append({
                "sample": sid, "attempt": str(result),
                "tasks": 6, "manifest_sha256": sha256(result / "manifest.json"),
            })
            done[sid] = status["completed_samples"][-1]
            write_json(status_file, status)
            print(f"E5B_BANKSY_PROGRESS completed={len(done)*6}/36",
                  flush=True)
        require(len(done) == 6, "E5B_BANKSY_SAMPLE_COUNT_INCOMPLETE")
        status["status"] = "completed"
        status["finished_utc"] = now()
        write_json(status_file, status)
        print(f"E5B_BANKSY_FINAL status=completed completed=36/36 "
              f"failed=0 result={status_file}", flush=True)
        print("NO_REFERENCE_LABELS_NO_ARI_NMI", flush=True)
    except BaseException as exc:
        status["status"] = "halted"
        status["failures"].append({
            "error": repr(exc), "traceback": traceback.format_exc(),
            "failed_utc": now()})
        write_json(status_file, status)
        print(f"E5B_BANKSY_HALTED completed={len(done)*6}/36 "
              f"error={exc!r} result={status_file}", flush=True)
        raise

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", action="store_true")
    p.add_argument("--resume", metavar="SESSION")
    p.add_argument("--child-sample", choices=SAMPLES)
    p.add_argument("--session")
    args = p.parse_args()
    if args.child_sample:
        require(args.session and not args.run and not args.resume,
                "E5B_BANKSY_INVALID_CHILD_ARGS")
        run_sample(args.child_sample, Path(args.session))
    elif args.run:
        require(not args.session and not args.resume,
                "E5B_BANKSY_INVALID_BATCH_ARGS")
        execute_batch()
    elif args.resume:
        require(not args.session,
                "E5B_BANKSY_INVALID_RESUME_ARGS")
        execute_batch(args.resume)
    else:
        print("E5B_BANKSY_DRY_RUN samples=6 seeds=3 arms=2 "
              "partitions_per_seed=16 predictions=36, no files written.")

if __name__ == "__main__":
    try:
        main()
    except BaseException as exc:
        print(f"E5B_BANKSY_FATAL {type(exc).__name__}: {exc}",
              file=sys.stderr, flush=True)
        sys.exit(1)
