"""E5a independent read-only phase-end audit: four baselines, 288 predictions.

Requires Python environment from the user's already installed CellCharter venv.
DOES NOT train, select K anew, edit or rewrite any existing result.
Audits original archived CSV/manifest/status, exact barcodes and annotation masks,
SHA256s, per-method frozen K decisions, candidate traces, and recomputed ARI/NMI.

The audit itself writes NEW report JSON and tables only under
  D:/paper/CellCharter_reproduction/results/e5a_phase_audit_v1/
on --run. On failure preserves all evidence and exits nonzero.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import time
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

BASE = Path(r"D:\paper\CellCharter_reproduction")
DATA_ROOT = Path(r"D:\paper\ST_Benchmark_Planning\mvp\data")
RESULTS = BASE / "results"
SESSION_NAMES = {
    "nonspatial": "nonspatial_20261120T095303Z_15120",
    "banksy": "banksy_20261120T101256Z_26540",
    "bayesspace": "bayesspace_20261120T103557Z_11440",
}
SESSIONS = {k: RESULTS / "e5a_baselines_v1" / v
            for k,v in SESSION_NAMES.items()}
SAMPLES = ("151507","151508","151509","151510","151669","151670",
           "151671","151672","151673","151674","151675","151676")
SEEDS = (22911, 7449, 25842)
ARMS = ("oracle_k","k_blind")
METHODS = ("GMM","Leiden","BANKSY","BayesSpace")
SIZES = (4226,4384,4789,4634,3661,3498,4110,4015,3639,3673,3592,3460)
LABELED = (4221,4381,4788,4595,3636,3484,4093,3888,3611,3635,3566,3431)
EXPECTED_N = dict(zip(SAMPLES,SIZES))
EXPECTED_LABELED = dict(zip(SAMPLES,LABELED))
ORACLE = {x:(5 if x in ("151669","151670","151671","151672") else 7)
          for x in SAMPLES}
GRID_K = tuple(range(2,11))
GRID_RES = (0.1,0.15,0.2,0.25,0.3,0.4,0.5,0.65,0.8,
            1.0,1.25,1.5,2.0,2.5,3.0,4.0)
EXPECTED_BY_SESSION = {"nonspatial":144,"banksy":72,"bayesspace":72}
EXPECTED_GRID = {(m,s,r,z) for m in METHODS for s in SAMPLES
                 for r in ARMS for z in SEEDS}
EXPECTED_SCRIPT_SHA = {
    "e5a_nonspatial_baselines_batch_v1.py":
    "4cf7b952452a2e52cbae615e7d949870017f3a418a40b77727aed7346b005266",
    "e5a_banksy_baselines_batch_v1.py":
    "2ff7cb5f71b58973986f82863f474c28d02032c5715926e23af8df08468860da",
    "e5a_bayesspace_baselines_batch_v1_1.R":
    "fed1f66c87a186104c60727d1bd27791a6dd9d389096b06305aac40fc97ccfbe",
}
METHOD_SESSION = {"GMM":"nonspatial","Leiden":"nonspatial",
                  "BANKSY":"banksy","BayesSpace":"bayesspace"}
PROTOCOL = "E5A_PHASE_INDEPENDENT_READONLY_AUDIT_V1"
SHA_CACHE = {}
SRC_CACHE = {}


def ensure(cond,why):
    if not bool(cond):
        raise ValueError(why)


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    path=Path(path)
    ensure(path.is_file(),"FILE_MISSING "+str(path))
    key=(str(path.resolve()).casefold(),path.stat().st_size,
         path.stat().st_mtime_ns)
    if key not in SHA_CACHE:
        h=hashlib.sha256()
        with path.open("rb") as f:
            for block in iter(lambda:f.read(2**20),b""):
                h.update(block)
        SHA_CACHE[key]=h.hexdigest()
    return SHA_CACHE[key]


def check_sha(path,expected,descr):
    ensure(isinstance(expected,str) and len(expected)==64,
           "MISSING_EXPECTED_SHA "+descr)
    observed=sha(path)
    ensure(observed.lower()==expected.lower(),
           "SHA256_CHANGED "+descr+" file="+str(path))
    return observed


def load_json(path):
    path=Path(path)
    ensure(path.is_file(),"JSON_MISSING "+str(path))
    with path.open("r",encoding="utf-8-sig") as f:
        return json.load(f)


def safe_under(value,base):
    # Never follow untrusted manifest references outside approved input/results roots.
    x=Path(value).resolve()
    base=Path(base).resolve()
    ensure(x==base or base in x.parents,
           "MANIFEST_PATH_OUTSIDE_FROZEN_DIRECTORY "+str(x))
    return x


def within_roots(value):
    x=Path(value).resolve()
    allowed=(BASE.resolve(),DATA_ROOT.resolve())
    ensure(any(x==r or r in x.parents for r in allowed),
           "SOURCE_PATH_OUTSIDE_APPROVED_ROOT "+str(x))
    return x


def same_float(a,b,tol=1e-7):
    return math.isfinite(float(a)) and abs(float(a)-float(b))<=tol


def spot_truth(sid):
    if sid in SRC_CACHE:
        return SRC_CACHE[sid]
    d=DATA_ROOT/sid
    pos=d/"spots_aligned.csv"
    lab=d/"manual_layer_annotations.csv"
    ensure(pos.is_file() and lab.is_file(),"GROUNDING_SOURCE_NOT_FOUND "+sid)
    coords=pd.read_csv(pos,dtype={"barcode":str},low_memory=False)
    ensure("barcode" in coords.columns,"COORD_BARCODE_NOT_FOUND")
    bc=coords["barcode"].astype(str).to_numpy()
    ensure(len(bc)==EXPECTED_N[sid] and coords["barcode"].is_unique,
           "SPOT_REFERENCE_ORDER_OR_COUNT_CHANGED "+sid)
    truth=pd.read_csv(lab,dtype={"sample_name":str,"spot_name":str,"layer":str},
                      low_memory=False)
    ensure(all(c in truth.columns
               for c in ("sample_name","spot_name","layer")),
           "MANUAL_LABEL_COLUMNS_INVALID "+sid)
    sub=truth.loc[truth["sample_name"]==sid,["spot_name","layer"]]
    ensure(sub["spot_name"].is_unique and sub["layer"].notna().all(),
           "MANUAL_LABEL_DUPLICATE_OR_NULL "+sid)
    layers=sub.set_index("spot_name")["layer"].reindex(bc)
    mask=layers.notna().to_numpy()
    ensure(int(mask.sum())==EXPECTED_LABELED[sid],
           "MANUAL_LAYER_MASK_NOT_FROZEN "+sid)
    ensure(int(layers[mask].nunique())==ORACLE[sid],
           "MANUAL_LAYER_K_CHANGED "+sid)
    SRC_CACHE[sid]={
        "barcodes":bc,"truth":layers.to_numpy(),"mask":mask,
        "position_sha256":sha(pos),"manual_sha256":sha(lab),
        "n_spots":len(bc),"n_labeled":int(mask.sum())}
    return SRC_CACHE[sid]


def q_tune_check(trial,sid,seed):
    path=safe_under(trial["candidate_trace"],SESSIONS["bayesspace"])
    check_sha(path,trial["candidate_trace_sha256"],
              "BAYESSPACE_QTUNE_"+sid+"_"+str(seed))
    df=pd.read_csv(path)
    ensure(all(c in df.columns for c in ("q","loglik")) and len(df)==9,
           "BAYESSPACE_QTUNE_GRID_SIZE_BAD")
    ks=pd.to_numeric(df.q,errors="raise").astype(int).to_numpy()
    ll=pd.to_numeric(df.loglik,errors="raise").astype(float).to_numpy()
    ensure(list(ks)==list(GRID_K) and np.isfinite(ll).all(),
           "BAYESSPACE_QTUNE_VALUES_BAD")
    return int(min(ks[ll==np.max(ll)]))


def verify_candidate(record,sid,method,arm,seed,pred):
    if method=="GMM":
        details=record.get("details",{})
        trials=details.get("candidate_results",[])
        ensure(len(trials)==(1 if arm=="oracle_k" else 9),
               "GMM_K_GRID_LENGTH_CHANGED")
        grid=[int(t["k"]) for t in trials]
        ensure(grid==([ORACLE[sid]] if arm=="oracle_k" else list(GRID_K)),
               "GMM_K_CANDIDATE_GRID_CHANGED")
        ensure(all(math.isfinite(float(t["bic"])) for t in trials),
               "GMM_BIC_NONFINITE")
        selected=int(details["selected_k"])
        winner=min(trials,key=lambda t:(float(t["bic"]),int(t["k"])))
        ensure(selected==int(winner["k"]) and
               selected==(ORACLE[sid] if arm=="oracle_k" else selected),
               "GMM_K_SELECTION_NOT_REPRODUCIBLE")
        ensure(int(details["actual_k"])==len(np.unique(pred)),
               "GMM_ACTUAL_K_MANIFEST_INCONSISTENT")
        ensure(int(record["selected_or_actual_k"])==len(np.unique(pred)),
               "GMM_SELECTED_OR_ACTUAL_K_INCONSISTENT")
        return {"picked_k":selected,"upper_bound_k":selected==10,
                "selected_resolution":None}
    if method=="Leiden":
        details=record.get("details",{})
        trials=details.get("candidate_results",[])
        expected=GRID_RES if arm=="oracle_k" else (1.0,)
        ensure(len(trials)==len(expected) and
               all(same_float(t["resolution"],r,tol=1e-10)
                   for t,r in zip(trials,expected)),
               "LEIDEN_RESOLUTION_GRID_CHANGED")
        ensure(all(int(t["actual_k"])>=1 for t in trials),
               "LEIDEN_K_TRIAL_INVALID")
        selected=float(details["selected_resolution"])
        best=(min(trials,key=lambda t:
                  (abs(int(t["actual_k"])-ORACLE[sid]),
                   float(t["resolution"]))) if arm=="oracle_k"
              else trials[0])
        ensure(same_float(selected,best["resolution"],tol=1e-10),
               "LEIDEN_ORACLE_SELECTION_WRONG")
        ensure(len(np.unique(pred))==int(best["actual_k"]) and
               len(np.unique(pred))==int(record["selected_or_actual_k"]),
               "LEIDEN_ACTUAL_K_WRONG")
        return {"picked_k":len(np.unique(pred)),"upper_bound_k":False,
                "selected_resolution":selected}
    if method=="BANKSY":
        trials=record["candidate_trials"]
        ensure(len(trials)==len(GRID_RES) and
               all(same_float(t["resolution"],r,tol=1e-10)
                   for t,r in zip(trials,GRID_RES)),
               "BANKSY_RESOLUTION_GRID_CHANGED")
        winner=(min(trials,key=lambda t:
                    (abs(int(t["actual_k"])-ORACLE[sid]),
                     float(t["resolution"]))) if arm=="oracle_k"
                else next(t for t in trials
                          if same_float(t["resolution"],1.0)))
        chosen=float(record["chosen_resolution"])
        ensure(same_float(chosen,winner["resolution"],tol=1e-10),
               "BANKSY_RESOLUTION_SELECTION_WRONG")
        ensure(len(np.unique(pred))==int(winner["actual_k"]) and
               len(np.unique(pred))==int(record["actual_k"]),
               "BANKSY_CLUSTER_COUNT_MANIFEST_MISMATCH")
        archive=safe_under(record["candidate_archive"],SESSIONS["banksy"])
        check_sha(archive,record["candidate_archive_sha256"],
                  "BANKSY_CANDIDATE_ARCHIVE")
        with np.load(archive,allow_pickle=False) as npz:
            keys=[f"r_{j:02d}" for j in range(len(GRID_RES))]
            ensure(sorted(npz.files)==sorted(keys),
                   "BANKSY_NPZ_CANDIDATE_KEYS_CHANGED")
            chosen_key=winner["archive_key"]
            ensure(chosen_key in npz.files,
                   "BANKSY_CHOSEN_PARTITION_NOT_IN_ARCHIVE")
            saved=np.asarray(npz[chosen_key]).astype(str)
            ensure(np.array_equal(saved,pred.astype(str)),
                   "BANKSY_SELECTED_LABELS_NOT_MATCH_NPZ")
        return {"picked_k":len(np.unique(pred)),"upper_bound_k":False,
                "selected_resolution":chosen}
    if method=="BayesSpace":
        selected=int(record["selected_q"])
        ensure(selected in GRID_K and
               int(record["actual_k"])==len(np.unique(pred)),
               "BAYESSPACE_SELECTED_Q_OR_ACTUAL_K_INCONSISTENT")
        qbest=q_tune_check(record,sid,seed)
        ensure(selected==(ORACLE[sid] if arm=="oracle_k" else qbest),
               "BAYESSPACE_SELECTED_Q_NOT_FROZEN")
        ensure(int(record["oracle_prior"])==ORACLE[sid],
               "BAYESSPACE_ORACLE_PRIOR_MISMATCH")
        return {"picked_k":selected,"upper_bound_k":selected==10,
                "selected_resolution":None}
    raise ValueError("UNSUPPORTED_FROZEN_METHOD")


def verify_provenance(record,sid,method):
    src=spot_truth(sid)
    if method in ("GMM","Leiden"):
        provenance=record["input"]
        check_sha(within_roots(provenance["source_25d_path"]),
                  provenance["source_25d_sha256"],
                  "NONSPATIAL_INPUT_25D")
        src_coord=within_roots(provenance.get(
            "source_spots_path",str(DATA_ROOT/sid/"spots_aligned.csv")))
        check_sha(src_coord,provenance["source_spots_sha256"],
                  "NONSPATIAL_COORDS")
        ensure(provenance["source_spots_sha256"]==
               src["position_sha256"],
               "NONSPATIAL_COORDS_DIFFER_FROM_FROZEN")
        if "source_spot_order_sha256" in provenance:
            order_path=within_roots(str(Path(provenance["source_25d_path"])
                                      .parent/(
                "predictions.csv" if sid=="151507" else "spot_order.csv")))
            check_sha(order_path,provenance["source_spot_order_sha256"],
                      "NONSPATIAL_ORIGINAL_SPOT_ORDER")
        status=within_roots(str(Path(provenance["source_25d_path"])
                                .parent/"status.json"))
        check_sha(status,provenance["source_sample_status_sha256"],
                  "NONSPATIAL_ORIGINAL_STATUS")
    elif method=="BANKSY":
        provenance=record["source"]
        ensure(provenance["spots_sha256"]==src["position_sha256"],
               "BANKSY_COORDS_DIFFER_FROM_FROZEN")
        check_sha(within_roots(provenance["spots_path"]),
                  provenance["spots_sha256"],"BANKSY_COORDS")
        check_sha(within_roots(provenance["raw_10x_path"]),
                  provenance["raw_10x_sha256"],"BANKSY_RAW_10X")
        check_sha(safe_under(
            SESSIONS["banksy"]/sid/"banksy_20pc_embedding.npy",
            SESSIONS["banksy"]),
            provenance["banksy_embedding_sha256"],"BANKSY_20PC_EMBEDDING")
        ensure(int(provenance["selected_hvg_count"])==2000,
               "BANKSY_HVG_COUNT_NOT_FROZEN")
    else:
        provenance=load_json(safe_under(record["input_manifest"],
                                        SESSIONS["bayesspace"]))
        ensure(provenance["spots_sha256"]==src["position_sha256"],
               "BAYESSPACE_COORDS_DIFFER_FROM_FROZEN")
        check_sha(within_roots(provenance["spots"]),
                  provenance["spots_sha256"],"BAYESSPACE_COORDS")
        check_sha(within_roots(provenance["tenx_h5"]),
                  provenance["tenx_h5_sha256"],"BAYESSPACE_RAW_10X")
        ensure(int(provenance["spot_count"])==EXPECTED_N[sid],
               "BAYESSPACE_SOURCE_SPOT_COUNT_CHANGED")
    return provenance


def read_prediction(path,sid):
    df=pd.read_csv(path,dtype={"barcode":str,"cluster":str},
                   low_memory=False)
    ensure(list(df.columns)==["barcode","cluster"],
           "PREDICTION_COLUMNS_NOT_FROZEN")
    src=spot_truth(sid)
    bc=df["barcode"].astype(str).to_numpy()
    ensure(len(bc)==src["n_spots"] and
           np.array_equal(bc,src["barcodes"]) and
           pd.Series(bc).is_unique,
           "PREDICTION_SPOT_BARCODE_ORDER_MISMATCH")
    labels=df["cluster"].to_numpy()
    ensure(not pd.Series(labels).isna().any() and
           len(np.unique(labels))>=1,
           "PREDICTION_LABELS_INVALID")
    return labels,src


def metric_verify(record,src,lab,method,arm):
    valid=src["mask"]
    truth=src["truth"][valid]
    pred=lab[valid]
    ari=float(adjusted_rand_score(truth,pred))
    nmi=float(normalized_mutual_info_score(
        truth,pred,average_method="arithmetic"))
    scored=record["metrics"]
    ensure(same_float(scored["ari"],ari,tol=1e-7) and
           same_float(scored["nmi"],nmi,tol=1e-7),
           "ARI_NMI_RECOMPUTE_MISMATCH "
           +method+"/"+arm+" got="+str((ari,nmi))+
           " saved="+str((scored.get("ari"),scored.get("nmi"))))
    n=int(scored.get("n_labeled",scored.get("evaluated_spots",-1)))
    ensure(n==src["n_labeled"],
           "SAME_GROUND_TRUTH_MASK_COUNT_FAILED")
    require_ref=scored.get("reference_sha256")
    ensure(require_ref==src["manual_sha256"],
           "REFERENCE_LABEL_FILE_SHA_CHANGED")
    return ari,nmi


def audit():
    started=utc()
    out_dir=RESULTS/"e5a_phase_audit_v1"/(
        "audit_"+datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        +"_"+str(os.getpid()))
    ensure(not out_dir.exists(),"E5A_AUDIT_OUTPUT_ALREADY_EXISTS")
    out_dir.mkdir(parents=True,exist_ok=False)

    report={
        "protocol":PROTOCOL,"status":"running","started_utc":started,
        "source_sessions":{k:str(v) for k,v in SESSIONS.items()},
        "expected_total":288,"checked":0,"errors":[],
        "method_counts":{}, "warnings":[],
        "audit_only":True,
        "analysis_unit":"3 biological donors, 12 nested sections, 3 technical seeds",
        "effect_claim_policy":"descriptive audit only; no significance or paper improvement claim",
    }
    statuses={}
    checks=[]
    discovered=set()
    manifest_paths=set()
    trials=set()
    sha_script={}

    try:
        for name,session in SESSIONS.items():
            ensure(session.is_dir(),"E5A_SESSION_MISSING "+str(session))
            status=load_json(session/"batch_status.json")
            n=EXPECTED_BY_SESSION[name]
            ensure(status["status"]=="completed" and
                   int(status["completed"])==n and
                   int(status["failed"])==0 and
                   len(status["tasks"])==n,
                   "E5A_BATCH_STATUS_OR_TASK_COUNT_BAD "+name)
            ensure(int(status["expected_tasks"])==n,
                   "E5A_EXPECTED_TASK_COUNT_BAD "+name)
            n_pred=len(list(session.rglob("predictions.csv")))
            ensure(n_pred==n,
                   "PHYSICAL_PREDICTION_CSV_COUNT_BAD "+name+
                   " actual="+str(n_pred))
            statuses[name]={"reported":n,"prediction_files":n_pred}
            for task in status["tasks"]:
                desc=task["manifest"]
                mp=safe_under(desc,session)
                ensure(str(mp) not in manifest_paths,
                       "DUPLICATED_MANIFEST_REFERENCE "+str(mp))
                manifest_paths.add(str(mp))
                rec=load_json(mp)
                sid=str(rec["sample"])
                method=rec["method"]
                arm=rec["regime"]
                seed=int(rec["seed"])
                item=(method,sid,arm,seed)
                ensure(item in EXPECTED_GRID,
                       "TASK_OUTSIDE_FROZEN_GRID "+repr(item))
                ensure(method in METHOD_SESSION and
                       METHOD_SESSION[method]==name,
                       "WRONG_METHOD_SESSION "+repr(item))
                ensure(item not in discovered,
                       "DUPLICATED_TASK "+repr(item))
                discovered.add(item)
                ensure(str(task["sample"])==sid and
                       str(task["regime"])==arm and
                       int(task["seed"])==seed and
                       rec["status"]=="completed",
                       "TASK_VS_MANIFEST_OR_STATUS_BAD "+repr(item))
                if "method" in task:
                    ensure(task["method"]==method,
                           "STATUS_VS_MANIFEST_METHOD_BAD")
                pp=safe_under(rec["prediction_file"],session)
                check_sha(pp,rec["prediction_sha256"],
                          "PREDICTION_FILE "+repr(item))
                labels,src=read_prediction(pp,sid)
                selected=verify_candidate(rec,sid,method,arm,seed,labels)
                provenance=verify_provenance(rec,sid,method)
                ari,nmi=metric_verify(rec,src,labels,method,arm)
                checks.append({
                    "method":method,"sample":sid,"regime":arm,"seed":seed,
                    "n_spots":src["n_spots"],"n_labeled":src["n_labeled"],
                    "actual_k":int(np.unique(labels).size),
                    "selected_k_or_actual":selected["picked_k"],
                    "selected_resolution":selected["selected_resolution"],
                    "k_blind_upper_bound":bool(selected["upper_bound_k"]),
                    "ari_recomputed":ari,"nmi_recomputed":nmi,
                    "prediction_sha256":rec["prediction_sha256"],
                    "manifest_path":str(mp)})
                if len(checks)%24==0:
                    print(f"E5A_PHASE_AUDIT_PROGRESS checked={len(checks)}/288",
                          flush=True)

        ensure(discovered==EXPECTED_GRID,
               "E5A_TASK_GRID_INCOMPLETE missing="+
               str(sorted(EXPECTED_GRID-discovered)[:5]))
        ensure(len(checks)==288,"E5A_VERIFIED_NOT_288")
        # Confirm underlying raw data input is identical between the two
        # spatial baseline implementations for each of the twelve slices.
        for sid in SAMPLES:
            bank=load_json(SESSIONS["banksy"]/sid/"source_manifest.json")
            bs=load_json(SESSIONS["bayesspace"]/sid/"input_manifest.json")
            ensure(bank["raw_10x_sha256"]==bs["tenx_h5_sha256"],
                   "SPATIAL_METHOD_RAW_COUNTS_NOT_SAME "+sid)
            ensure(bank["spots_sha256"]==bs["spots_sha256"],
                   "SPATIAL_METHOD_COORDS_NOT_SAME "+sid)

        for script_name,expected_sha in EXPECTED_SCRIPT_SHA.items():
            check_sha(BASE/script_name,expected_sha,
                      "FROZEN_EXECUTABLE_SCRIPT "+script_name)
            sha_script[script_name]=expected_sha

        df=pd.DataFrame(checks)
        df=df.sort_values(["method","sample","regime","seed"])
        df.to_csv(out_dir/"all_288_prediction_checks.csv",index=False,
                  encoding="utf-8-sig")
        # Descriptive metrics only, grouped by sample then regime/method.
        grouped=df.groupby(["method","regime","sample"],as_index=False).agg(
            mean_seed_ari=("ari_recomputed","mean"),
            mean_seed_nmi=("nmi_recomputed","mean"),
            seed_runs=("seed","count"),
            n_spots=("n_spots","first"),
            n_labeled=("n_labeled","first"))
        ensure(len(grouped)==96 and (grouped.seed_runs==3).all(),
               "METHOD_REGIME_SAMPLE_SEED_GROUPING_BAD")
        grouped.to_csv(out_dir/"sample_level_descriptives.csv",
                       index=False,encoding="utf-8-sig")
        descriptive=grouped.groupby(["method","regime"],as_index=False).agg(
            mean_across_12_sections_ari=("mean_seed_ari","mean"),
            mean_across_12_sections_nmi=("mean_seed_nmi","mean"),
            min_section_ari=("mean_seed_ari","min"),
            max_section_ari=("mean_seed_ari","max"),
            sections=("sample","count"))
        ensure((descriptive.sections==12).all(),
               "DESCRIPTIVE_SECTION_COUNT_CHANGED")
        descriptive.to_csv(out_dir/"method_regime_descriptives.csv",
                           index=False,encoding="utf-8-sig")
        counts=df.groupby(["method","regime"]).size().to_dict()
        report["method_counts"]={
            method:{arm:int(counts.get((method,arm),0))
                    for arm in ARMS}
            for method in METHODS}
        report["checked"]=288
        report["batch_statuses"]=statuses
        report["script_sha256"]=sha_script
        report["data_files_sha256_verified"]=len(SHA_CACHE)
        bound=df.loc[(df.method=="BayesSpace") &
                     (df.regime=="k_blind"),"k_blind_upper_bound"]
        n_bound=int(bound.sum())
        if n_bound:
            report["warnings"].append({
                "code":"BAYESSPACE_KBLIND_SELECTED_UPPER_BOUND",
                "observed_tasks":n_bound,
                "denominator":36,
                "interpretation":"qTune maximizing pseudo-loglik chose q=10 for some tasks; report selection bias/boundary, do not enlarge search after outcomes."})
        unmatched=0
        for sid in SAMPLES:
            p=DATA_ROOT/sid/"spots_aligned.csv"
            # Upstream BayesSpace text output may report isolated spatial spots.
            # No inferred isolated-spot counts are filled in by this audit.
        report["warnings"].append({
            "code":"BIOLOGICAL_REPLICATION_CAVEAT",
            "text":"12 slices are nested in 3 donors; spots, slices, and seeds are not 288 independent biological samples."})
        report["warnings"].append({
            "code":"NATIVE_REPRESENTATIONS_NOT_IDENTICAL",
            "text":"GMM/Leiden use scVI L0 5D; BANKSY and BayesSpace use original counts with distinct native preprocessing; do not call same-feature equivalent benchmark."})
        report["status"]="passed"
    except Exception as exc:
        report["status"]="failed"
        report["errors"].append({
            "type":type(exc).__name__,
            "message":str(exc),
            "traceback":traceback.format_exc(),
            "completed_checks_before_failure":len(checks)})
    report["finished_utc"]=utc()
    (out_dir/"e5a_phase_audit_report.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+"\n",
        encoding="utf-8")
    print(f"E5A_PHASE_AUDIT_FINAL status={report['status']} "
          f"verified={report['checked']}/288 "
          f"errors={len(report['errors'])} "
          f"report={out_dir / 'e5a_phase_audit_report.json'}",
          flush=True)
    if report["status"]=="passed":
        print(f"E5A_PHASE_AUDIT_TABLE {out_dir / 'all_288_prediction_checks.csv'}",
              flush=True)
        print(f"E5A_PHASE_AUDIT_DESCRIPTIVES {out_dir / 'method_regime_descriptives.csv'}",
              flush=True)
        return 0
    print("E5A_PHASE_AUDIT_ERROR "+report["errors"][0]["message"],
          file=sys.stderr,flush=True)
    return 2


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run",action="store_true",
                   help="Run full read-only phase-end audit of 288 saved tasks")
    args=p.parse_args()
    if not args.run:
        print("E5A_PHASE_AUDIT_PLAN sessions=3 methods=4 "
              "slices=12 regimes=2 seeds=3 expected=288")
        print("E5A_PHASE_AUDIT_DRY_RUN_ONLY NO_RESULT_READ_OR_WRITE")
        return 0
    return audit()


if __name__=="__main__":
    raise SystemExit(main())
