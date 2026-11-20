"""Frozen E5a BANKSY 1.3.5, 12 DLPFC slices, two K regimes, three seeds.

Use official BANKSY Python core: initialize_banksy -> generate_banksy_matrix
-> pca_umap (20 PCs, UMAP disabled) -> run_Leiden_partition, without the
run_banksy_multiparam plotting wrapper. This preserves the BANKSY algorithm
and avoids creating ~600 non-scientific transient figures. No reference
annotations enter the embedding, neighborhood graph, K choice, or fitting.

Each slice+seed evaluates all 16 FROZEN resolutions exactly once. The
oracle-K report picks closest actual K to externally provided class-count
prior (five or seven); K-blind keeps resolution 1.0. Both use the same
partition candidates transparently. Raw predictions for BOTH arms are
written BEFORE any reference annotations are opened for evaluation.

--run: completes all 12 x 3 seed x 2 regimes = 72 tasks, or halts on
a genuine input/library error, retaining evidence without overwriting.
Default: read-only task plan, does not create any results.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.metadata as metadata
import json
import os
import random
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path(r"D:\paper\CellCharter_reproduction")
DATA_ROOT = Path(r"D:\paper\ST_Benchmark_Planning\mvp\data")
RESULT_ROOT = BASE / "results"
BANKSY_LIB = BASE / "third_party" / "e5a_banksy_libs"

SAMPLES = ("151507", "151508", "151509", "151510", "151669", "151670",
           "151671", "151672", "151673", "151674", "151675", "151676")
SPOT_COUNTS = (4226, 4384, 4789, 4634, 3661, 3498, 4110, 4015,
               3639, 3673, 3592, 3460)
LABEL_COUNTS = (4221, 4381, 4788, 4595, 3636, 3484, 4093, 3888,
                3611, 3635, 3566, 3431)
EXPECTED_SPOTS = dict(zip(SAMPLES, SPOT_COUNTS))
EXPECTED_LABELED = dict(zip(SAMPLES, LABEL_COUNTS))
ORACLE_K = {sid:(5 if sid in {"151669","151670","151671","151672"} else 7)
            for sid in SAMPLES}
SEEDS = (22911, 7449, 25842)
REGIMES = ("oracle_k", "k_blind")
RESOLUTIONS = (0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.65,
               0.8, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0)
FIXED_BLIND_RESOLUTION = 1.0
BANKSY_EMBEDDING_SEED = 22911
PROTOCOL = "E5A_BANKSY_CORE_12S_DUALK_3SEED_V1"
EXPECTED_TASKS = len(SAMPLES) * len(SEEDS) * len(REGIMES)


def require(condition, error):
    if not condition:
        raise ValueError(error)


def now():
    return datetime.now(timezone.utc).isoformat()


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path, payload):
    Path(path).write_text(json.dumps(payload, ensure_ascii=False,
                                    allow_nan=False, indent=2)+"\n",
                          encoding="utf-8")


def pkgversion(name):
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return "not_recorded"


def decode(b):
    return b.decode("utf-8") if isinstance(b, (bytes, np.bytes_)) else str(b)


def sample_inputs(sid):
    from scipy import sparse
    import h5py
    import anndata as ad
    import scanpy as sc

    folder = DATA_ROOT / sid
    positions = folder / "spots_aligned.csv"
    reference = folder / "manual_layer_annotations.csv"
    matrix_file = folder / "filtered_feature_bc_matrix.h5"
    for p in (positions, reference, matrix_file):
        require(p.is_file(), "SOURCE_FILE_MISSING " + str(p))

    spots = pd.read_csv(positions, dtype={"barcode":str})
    require(len(spots) == EXPECTED_SPOTS[sid] and spots["barcode"].is_unique,
            "SPOTS_COUNT_OR_BARCODES_MISMATCH")
    cols = ("pxl_col_in_fullres", "pxl_row_in_fullres")
    require(all(x in spots for x in cols), "SPATIAL_COORDINATES_NOT_FOUND")
    xy = spots[list(cols)].to_numpy(dtype=np.float64)
    require(np.isfinite(xy).all(), "INVALID_SPATIAL_COORDINATES")
    with h5py.File(matrix_file, "r") as f:
        g = f["matrix"]
        require(all(k in g for k in ("data", "indices", "indptr",
                                    "shape", "barcodes", "features")),
                "10X_H5_REQUIRED_FIELD_MISSING")
        names = [decode(b) for b in g["barcodes"][()]]
        genes = [decode(b) for b in g["features"]["name"][()]]
        dims = tuple(int(x) for x in g["shape"][()])
        require(len(names) == dims[1] and len(genes) == dims[0],
                "10X_H5_DIMENSIONS_INVALID")
        require(len(set(names)) == len(names), "DUPLICATED_H5_BARCODES")
        matrix = sparse.csc_matrix(
            (g["data"][()],g["indices"][()],g["indptr"][()]),shape=dims)
    require(np.isfinite(matrix.data).all() and np.all(matrix.data >= 0),
            "NONFINITE_OR_NEGATIVE_RAW_COUNTS")
    barcode_index = pd.Index(names).get_indexer(spots["barcode"])
    require(np.all(barcode_index >= 0),
            "UNMATCHED_10X_BARCODES count=" + str(int((barcode_index < 0).sum())))
    counts = matrix[:,barcode_index].T.tocsr()
    require(counts.shape[0] == EXPECTED_SPOTS[sid], "10X_SPOT_SHAPE_INVALID")
    require(np.all(np.asarray(counts.sum(axis=1)).ravel()>0),
            "ZERO_UMI_SPOT_BLOCKS_BANKSY_LOGNORMALIZE")
    del matrix
    obs = pd.DataFrame(index=pd.Index(spots["barcode"],name="barcode"))
    obs["x"] = xy[:,0]
    obs["y"] = xy[:,1]
    var = pd.DataFrame(index=pd.Index(genes,name="gene_symbol"))
    adata = ad.AnnData(X=counts, obs=obs, var=var)
    adata.var_names_make_unique()
    adata.obsm["coord_xy"] = xy

    # FROZEN native expression preprocessing. No annotation file opened.
    sc.pp.normalize_total(adata, target_sum=10000)
    sc.pp.log1p(adata)
    sc.pp.highly_variable_genes(adata, flavor="seurat",
                                n_top_genes=2000, subset=False)
    high_var = adata.var["highly_variable"].to_numpy()
    require(int(high_var.sum()) == 2000, "BANKSY_2000_HVG_NOT_AVAILABLE")
    adata = adata[:,high_var].copy()
    require(adata.n_obs == EXPECTED_SPOTS[sid] and adata.n_vars == 2000,
            "BANKSY_PREPROCESSING_CHANGED_DIMENSIONS")
    require(np.isfinite(adata.X.data).all()
            if sparse.issparse(adata.X) else np.isfinite(adata.X).all(),
            "BANKSY_PREPROCESSING_NONFINITE")
    provenance = {
        "spots_path":str(positions), "spots_sha256":sha256(positions),
        "raw_10x_path":str(matrix_file), "raw_10x_sha256":sha256(matrix_file),
        "reference_file":str(reference), # existence check only; not opened
        "spot_count":int(adata.n_obs),
        "selected_hvg_count":int(adata.n_vars),
        "selected_hvg_names_sha256":hashlib.sha256(
            "\n".join(adata.var_names).encode("utf-8")).hexdigest(),
        "spatial_columns":list(cols),
        "expression_preprocessing":"sc.pp.normalize_total(target_sum=10000) then sc.pp.log1p then HVG(seurat,2000)",
    }
    return adata, np.asarray(spots["barcode"]), provenance


def make_banksy_embedding(adata):
    from banksy.initialize_banksy import initialize_banksy
    from banksy.embed_banksy import generate_banksy_matrix
    from banksy_utils.umap_pca import pca_umap

    random.seed(BANKSY_EMBEDDING_SEED)
    np.random.seed(BANKSY_EMBEDDING_SEED)

    banksy = initialize_banksy(
        adata, ("x","y","coord_xy"), num_neighbours=15,
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
    require(reduced.shape == (adata.n_obs,20) and np.isfinite(reduced).all(),
            "BANKSY_REDUCED_EMBEDDING_INVALID")
    return banksy, np.asarray(reduced,dtype=np.float32)


def fit_seed(banksy, seed, n):
    from banksy.cluster_methods import run_Leiden_partition
    random.seed(seed)
    np.random.seed(seed)
    results, _ = run_Leiden_partition(
        banksy_dict=banksy,
        resolutions=list(RESOLUTIONS),
        num_nn=50,
        num_iterations=-1,
        partition_seed=seed,
        match_labels=False,
        annotations=None,
        max_labels=None,
        verbose=False)
    require(len(results) == len(RESOLUTIONS), "BANKSY_RESOLUTION_RESULTS_COUNT_BAD")
    candidates=[]
    partitions={}
    for j,res in enumerate(RESOLUTIONS):
        mask = np.isclose(results["resolution"].to_numpy(dtype=float),res,atol=1e-12,rtol=0)
        require(int(mask.sum())==1,"BANKSY_RESOLUTION_ROW_INVALID "+str(res))
        row=results.loc[mask].iloc[0]
        labels=np.asarray(row["labels"].dense,dtype=np.int64)
        require(labels.shape==(n,) and np.all(labels>=0)
                and np.all(np.isfinite(labels)),"BANKSY_PARTITION_INVALID")
        actual=int(np.unique(labels).size)
        require(actual==int(row["num_labels"]),"BANKSY_ACTUAL_K_REPORTED_BAD")
        candidates.append({"resolution":res,"actual_k":actual,
                           "archive_key":f"r_{j:02d}"})
        partitions[res]=labels.copy()
    return candidates, partitions


def evaluate_after_prediction(sid, barcodes, prediction):
    from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score
    path=DATA_ROOT / sid / "manual_layer_annotations.csv"
    annotations=pd.read_csv(path,dtype={"sample_name":str,
                                        "spot_name":str,"layer":str})
    subset=annotations.loc[annotations["sample_name"]==sid,
                           ["spot_name","layer"]]
    require(subset["spot_name"].is_unique and subset["layer"].notna().all(),
            "REFERENCE_DUPLICATES_OR_NULL")
    truth=subset.set_index("spot_name")["layer"].reindex(barcodes)
    valid=truth.notna().to_numpy()
    require(int(valid.sum())==EXPECTED_LABELED[sid],
            "REFERENCE_MASK_COUNT_BAD")
    require(int(truth[valid].nunique())==ORACLE_K[sid],
            "REFERENCE_CLASS_COUNT_BAD")
    require(prediction.shape==(len(barcodes),),
            "PREDICTION_VS_TRUTH_LENGTH_BAD")
    return {
        "ari":float(adjusted_rand_score(truth[valid].to_numpy(),
                                       prediction[valid])),
        "nmi":float(normalized_mutual_info_score(truth[valid].to_numpy(),
                                                prediction[valid])),
        "evaluated_spots":int(valid.sum()),
        "reference_sha256":sha256(path),
        "reference_used":"only_after_both_regimes_predictions_saved",
    }


def run():
    import scanpy as sc
    import numpy as np
    require(EXPECTED_TASKS==72 and len(set(SAMPLES))==12 and
            FIXED_BLIND_RESOLUTION in RESOLUTIONS,
            "TASK_MATRIX_INVALID")
    require(BANKSY_LIB.is_dir(),"BANKSY_THIRD_PARTY_DIRECTORY_NOT_FOUND")
    sys.path.insert(0,str(BANKSY_LIB))
    from banksy.initialize_banksy import initialize_banksy  # noqa: F401

    root = RESULT_ROOT/"e5a_baselines_v1"
    session = root/("banksy_"+datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                    +"_"+str(os.getpid()))
    session.mkdir(parents=True,exist_ok=False)
    state_path=session/"batch_status.json"
    state={
        "protocol":PROTOCOL,"status":"running","started_utc":now(),
        "expected_tasks":72,"completed":0,"failed":0,"samples":SAMPLES,
        "seeds":SEEDS,"regimes":REGIMES,
        "lambda":0.2,"neighbors_spatial":15,"pca_dims":20,
        "neighbors_embedding":50,"resolutions":RESOLUTIONS,
        "blind_resolution":FIXED_BLIND_RESOLUTION,
        "oracle_k":ORACLE_K, "hvg_count":2000,
        "BANKSY_package":"pybanksy","BANKSY_version":pkgversion("pybanksy"),
        "scanpy_version":pkgversion("scanpy"),
        "numpy_version":np.__version__,
        "compute_device":"cpu",
        "source_labels_use":"annotation first opened after both regime prediction CSV files are saved",
        "tasks":[],"failure":None
    }
    write_json(state_path,state)
    ordinal=0
    try:
        for sid in SAMPLES:
            batch_start=time.perf_counter()
            sample_dir=session/sid
            sample_dir.mkdir(exist_ok=False)
            internal_log=sample_dir/"banksy_official_stdout.log"
            print(f"E5A_BANKSY_SAMPLE_START sample={sid} expected=6",flush=True)
            with internal_log.open("w",encoding="utf-8") as captured:
                with contextlib.redirect_stdout(captured), contextlib.redirect_stderr(captured):
                    adata, barcodes, source=sample_inputs(sid)
                    banksy, embedded=make_banksy_embedding(adata)
            np.save(sample_dir/"banksy_20pc_embedding.npy",
                    embedded,allow_pickle=False)
            source["banksy_embedding_sha256"]=sha256(sample_dir/"banksy_20pc_embedding.npy")
            del embedded, adata
            write_json(sample_dir/"source_manifest.json",source)
            for seed in SEEDS:
                seed_start=time.perf_counter()
                seed_dir=sample_dir/f"seed_{seed}"
                seed_dir.mkdir(exist_ok=False)
                with internal_log.open("a",encoding="utf-8") as captured:
                    with contextlib.redirect_stdout(captured),contextlib.redirect_stderr(captured):
                        print(f"OFFICIAL_BANKSY_LEIDEN seed={seed}")
                        candidates,partitions=fit_seed(banksy,seed,len(barcodes))
                arrs={f"r_{j:02d}":partitions[r] for j,r in enumerate(RESOLUTIONS)}
                archive_path=seed_dir/"all_resolution_labels.npz"
                np.savez_compressed(archive_path,**arrs)
                archive_sha=sha256(archive_path)

                best = min(candidates,key=lambda r:(
                    abs(r["actual_k"]-ORACLE_K[sid]),r["resolution"]))
                picked={
                    "oracle_k":best,
                    "k_blind":next(x for x in candidates
                                   if x["resolution"]==FIXED_BLIND_RESOLUTION),
                }
                # Both predictions physically saved before reference is opened.
                predicted={}
                for regime in REGIMES:
                    choice=picked[regime]
                    labels=partitions[choice["resolution"]]
                    target=seed_dir/regime
                    target.mkdir(exist_ok=False)
                    predfile=target/"predictions.csv"
                    pd.DataFrame({"barcode":barcodes,
                                  "cluster":labels}).to_csv(predfile,index=False)
                    predicted[regime]=(labels.copy(), predfile, choice)
                for regime in REGIMES:
                    ordinal+=1
                    labels, predfile, choice=predicted[regime]
                    report=evaluate_after_prediction(sid,barcodes,labels)
                    task={
                        "status":"completed","sample":sid,
                        "method":"BANKSY","regime":regime,"seed":seed,
                        "oracle_k_prior":ORACLE_K[sid],
                        "actual_k":choice["actual_k"],
                        "chosen_resolution":choice["resolution"],
                        "selection":("nearest_actual_K_on_frozen_resolution_grid"
                                     if regime=="oracle_k" else
                                     "fixed_resolution_without_reference_labels"),
                        "candidate_trials":candidates,
                        "candidate_archive":str(archive_path),
                        "candidate_archive_sha256":archive_sha,
                        "prediction_file":str(predfile),
                        "prediction_sha256":sha256(predfile),
                        "source":source,
                        "metrics":report,
                        "wall_seconds_for_shared_seed":round(
                            time.perf_counter()-seed_start,5),
                        "finished_utc":now(),
                    }
                    manifest_path=predfile.parent/"manifest.json"
                    write_json(manifest_path,task)
                    state["tasks"].append({
                        "sample":sid,"regime":regime,"seed":seed,
                        "status":"completed","manifest":str(manifest_path)})
                    state["completed"]+=1
                    write_json(state_path,state)
                    print(f"E5A_BANKSY_PASS {ordinal}/72 sample={sid} "
                          f"regime={regime} seed={seed} "
                          f"actual_k={choice['actual_k']} "
                          f"resolution={choice['resolution']}",flush=True)
                del candidates, partitions, arrs
            print(f"E5A_BANKSY_SAMPLE_PASS sample={sid} "
                  f"seconds={time.perf_counter()-batch_start:.2f}",flush=True)
            del banksy
        state["status"]="completed"
        state["finished_utc"]=now()
        write_json(state_path,state)
        print(f"E5A_BANKSY_FINAL status=completed completed=72/72 failed=0 "
              f"summary={state_path}",flush=True)
        return 0
    except Exception as exc:
        state["status"]="halted"
        state["failed"]=1
        state["failure"]={"type":type(exc).__name__,"message":repr(exc),
                          "traceback":traceback.format_exc()}
        state["finished_utc"]=now()
        write_json(state_path,state)
        print(f"E5A_BANKSY_HALTED completed={state['completed']}/72 "
              f"error={type(exc).__name__}: {exc} "
              f"summary={state_path}",flush=True)
        return 2


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run",action="store_true",
                        help="Perform complete 72-task BANKSY batch")
    args=parser.parse_args()
    if not args.run:
        print("E5A_BANKSY_PLAN samples=12 seeds=3 regimes=oracle_k,k_blind "
              "partitions_per_seed=16 tasks=72")
        print("E5A_BANKSY_DRY_RUN_ONLY NO_TRAINING_NO_FILES_WRITTEN")
        raise SystemExit(0)
    raise SystemExit(run())
