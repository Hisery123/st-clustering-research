"""E5b external 360/360 frozen prediction audit, THEN reference-only ARI/NMI.

No model fitting, no parameter tuning, no modifications to previous outputs.
Phase 1: independently verify all six-patient data masks, source SHA,
6 feature files, and 216 CellCharter+72 nonspatial+36 BANKSY+36 BayesSpace
predictions against their manifests and prespecified unlabeled K policies.
Phase 2: ONLY IF exactly all 360 unique predictions pass, open the six
reference_only label CSVs and compute per-prediction ARI and arithmetic NMI.
Write original per-seed scores, patient-level summaries and paired effect sizes.
Patient n=6; seeds/spots are NOT independent biological replicates.
Default read-only, --run writes ONLY a new isolated audit directory.
All scores reflect tissue pathologist regions, not cell-type ground truth.
Script is not yet executed or validated on user's Windows system.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import traceback
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

ROOT = Path(r"D:\paper\CellCharter_reproduction\results\e5b_external_v1")
BASE = Path(r"D:\paper\CellCharter_reproduction")
STAGE = ROOT / "input_stage_20261121T083911Z_14272"
FEAT = ROOT / "features_20261121T090400Z_28460"
CC = ROOT / "cellcharter_cluster_20261121T100504Z_29172"
NON = ROOT / "nonspatial_20261121T104630Z_22052"
BANK = ROOT / "banksy_20261121T133058Z_31292"
BS = ROOT / "bayesspace_20261121T135133Z_25840"
SAMPLES = ("1142243F", "1160920F", "CID4290",
           "CID4465", "CID44971", "CID4535")
N_MODEL = (4784, 4895, 2426, 1211, 1160, 1125)
N_EVAL = (4665, 4846, 2419, 1207, 1159, 1028)
ORACLE = (5, 7, 3, 3, 6, 6)
SEEDS = (22911, 7449, 25842)
ARMS = ("k_blind", "oracle_k")
SCALES = {
    "L0_5D": (0,), "L0L1_10D": (0,1),
    "A_L0L1L2_15D": (0,1,2),
    "L0L1L2L3_20D": (0,1,2,3),
    "L0L1L2L3L4_25D": (0,1,2,3,4),
    "B_L0L1L4_15D": (0,1,4),
}
RES = (0.1,0.15,0.2,0.25,0.3,0.4,0.5,0.65,
       0.8,1.0,1.25,1.5,2.0,2.5,3.0,4.0)
METHODS = ("CellCharter","GMM","Leiden","BANKSY","BayesSpace")
PROTOCOL = "E5B_FINAL_360_PREDICTIONS_AUDIT_AND_EVAL_V1"
EXPECTED_SHA = {
    "e5b_prepare_inputs_v1.py": "c37e435a77cb5b7f00242004bb9a1646b686c83a16d6ab34f3c609515e661d52",
    "e5b_scvi_feature_batch_v1.py": "28f792587a54ac8cb436d82f888dc9a39a2cff204168021ff8591a3f05a2b558",
    "e5b_cellcharter_cluster_batch_v1.py": "d8df95cd86116a2a4aec2a6f0b4cf2f63e2a1425956198bb1afe6c1baf91c1aa",
    "e5b_nonspatial_baselines_batch_v1.py": "2defb2821370a4c8e60ad6450276a6cd695b5bd26f6a26d6c3cd5c7cc02ec7f1",
    "e5b_banksy_baselines_batch_v1.py": "c80a1e7c97d563c8b9e7a83e97c83d7b8c021f583c6b82b91225b9be69ade927",
    "e5b_bayesspace_baselines_batch_v1.R": "7d0f4e08e7db6c913e55776e67c62a9b92de99d282fbd6bb408b5c41e7585e68",
}
EXCLUDE = {"", "artefact", "na", "uncertain"}

def demand(ok, msg):
    if not bool(ok):
        raise RuntimeError(msg)

def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1048576), b""):
            h.update(b)
    return h.hexdigest()

def check_sha(path, expected, tag):
    demand(Path(path).is_file(), "MISSING_FILE "+str(path))
    demand(isinstance(expected,str) and
           sha(path)==expected, "SHA_CHANGED "+tag+" "+str(path))

def jload(path):
    demand(Path(path).is_file(), "JSON_MISSING "+str(path))
    return json.loads(Path(path).read_text(encoding="utf-8"))

def dump(path, val):
    Path(path).write_text(
        json.dumps(val,indent=2,ensure_ascii=False,allow_nan=False)+"\n",
        encoding="utf-8")

def check_status(path, protocol, key, count):
    state = jload(path/"batch_status.json")
    demand(state.get("protocol")==protocol and state.get("status")=="completed"
           and len(state.get(key, []))==count,
           "BATCH_STATUS_NOT_COMPLETED "+str(path))
    return state

def pred(path, sample, expected_sha, min_k=1, max_k=99):
    """Read predictions for file-level validation; not a metric calculation."""
    check_sha(path,expected_sha,"PREDICTIONS")
    df = pd.read_csv(path,dtype={"barcode":str})
    demand(list(df.columns)==["barcode","cluster"],"PRED_COLUMNS "+str(path))
    ix = SAMPLES.index(sample)
    demand(len(df)==N_MODEL[ix] and df.barcode.is_unique and
           df.barcode.notna().all() and df.cluster.notna().all(),
           "PRED_SPOT_COUNT_OR_BARCODE "+str(path))
    lab = pd.to_numeric(df.cluster,errors="raise").to_numpy()
    demand(np.isfinite(lab).all() and np.array_equal(lab,np.rint(lab)),
           "PRED_CLUSTER_NONINTEGER "+str(path))
    lab = lab.astype(np.int64)
    actual = int(np.unique(lab).size)
    demand(min_k<=actual<=max_k and
           np.min(lab)>=0, "PRED_CLUSTER_RANGE "+str(path))
    return df.barcode.to_numpy(),lab,actual

def phase1():
    for filename, digest in EXPECTED_SHA.items():
        check_sha(BASE/filename,digest,"LOCAL_FROZEN_EXECUTION_SCRIPT")

    stage = jload(STAGE/"batch_status.json")
    demand(stage.get("status")=="completed" and
           stage.get("total_model_spots")==15601 and
           stage.get("total_eval_spots")==15324 and
           [x["sample"] for x in stage.get("samples",[])]==list(SAMPLES),
           "STAGE_STATUS_INVALID")
    expected_barcodes = {}
    for idx,sample in enumerate(SAMPLES):
        rec = stage["samples"][idx]
        for fn, dig in rec["input_files_sha256"].items():
            check_sha(STAGE/"inputs"/sample/fn,dig,"STAGED_INPUT")
        check_sha(STAGE/"reference_only"/f"{sample}_reference_labels.csv",
                  rec["reference_labels_sha256"],"REF_FILE_PROVENANCE_ONLY")
        f = STAGE/"inputs"/sample/"model_spots.csv"
        spots = pd.read_csv(f,dtype={"barcode":str})
        demand(len(spots)==N_MODEL[idx] and spots.barcode.is_unique,
               "STAGED_SPOT_COUNT "+sample)
        expected_barcodes[sample]=spots.barcode.to_numpy()

    feat = check_status(FEAT,"E5B_EXTERNAL_SCVI_FEATURES_FROZEN_V1",
                        "completed",6)
    demand(not feat.get("failed") and
           [x["sample"] for x in feat["completed"]]==list(SAMPLES),
           "FEATURE_BATCH_CONTENTS_INVALID")
    for sample in SAMPLES:
        f = FEAT/sample
        state=jload(f/"status.json")
        ix=SAMPLES.index(sample)
        demand(state.get("status")=="completed" and
               state.get("n_spots")==N_MODEL[ix] and
               state.get("latent_shape")==[N_MODEL[ix],5] and
               state.get("aggregate_shape")==[N_MODEL[ix],25],
               "FEATURE_SAMPLE_STATUS_INVALID "+sample)
        for filename,key in (
            ("scvi_latent.npy","scvi_latent_sha256"),
            ("cellcharter_aggregated.npy","source_25d_sha256"),
            ("spot_order.csv","spot_order_sha256"),
        ):
            check_sha(f/filename,state[key],"FEATURE")
        order=pd.read_csv(f/"spot_order.csv",dtype={"barcode":str})
        demand(np.array_equal(order.barcode.to_numpy(),expected_barcodes[sample]),
               "FEATURE_SPOT_ORDER_BAD "+sample)
        z = np.load(f/"scvi_latent.npy",allow_pickle=False)
        aggr=np.load(f/"cellcharter_aggregated.npy",allow_pickle=False,mmap_mode="r")
        demand(z.shape==(N_MODEL[ix],5) and
               aggr.shape==(N_MODEL[ix],25) and
               np.isfinite(z).all() and np.isfinite(aggr).all() and
               np.array_equal(z,np.asarray(aggr[:,:5])),
               "FEATURE_AGGREGATE_L0_MISMATCH "+sample)

    all_records=[]
    seen=set()
    def add(sample,method,config,arm,seed,path,digest,selected_k,actual_k):
        key=(sample,method,config,arm,int(seed))
        demand(key not in seen,"DUPLICATED_TASK "+repr(key))
        seen.add(key)
        barcodes, labels, actual = pred(path,sample,digest)
        demand(np.array_equal(barcodes,expected_barcodes[sample]),
               "CROSS_METHOD_BARCODE_ORDER_MISMATCH "+repr(key))
        demand(actual == int(actual_k),
               "ACTUAL_K_MANIFEST_MISMATCH "+repr(key))
        demand(actual<=int(selected_k),"ACTUAL_K_EXCEEDS_SELECTED "+repr(key))
        all_records.append({
            "sample":sample,"method":method,"config":config,
            "arm":arm,"seed":int(seed),"chosen_k":int(selected_k),
            "actual_k":int(actual),"pred_file":str(path),
            "pred_sha256":digest,
        })

    cc=check_status(CC,"E5B_CELLCHARTER_FROZEN_CLUSTER_BATCH_V1",
                    "completed_configs",36)
    demand(cc.get("expected_predictions")==216 and
           not cc.get("failures"),"CC_BATCH_FAILURES")
    cc_grid=set()
    for info in cc["completed_configs"]:
        sample,config=info["sample"],info["condition"]
        demand(sample in SAMPLES and config in SCALES and
               (sample,config) not in cc_grid,"CC_CONFIG_GRID_INVALID")
        cc_grid.add((sample,config))
        attempt=Path(info["attempt"])
        check_sha(attempt/"manifest.json",info["manifest_sha256"],"CC_MANIFEST")
        m=jload(attempt/"manifest.json")
        demand(m.get("status")=="completed" and
               m.get("protocol")=="E5B_CELLCHARTER_FROZEN_CLUSTER_BATCH_V1" and
               m.get("sample")==sample and m.get("condition")==config and
               tuple(m.get("blocks",[]))==SCALES[config] and
               m.get("feature_dim")==5*len(SCALES[config]) and
               len(m.get("predictions",[]))==6,
               "CC_CONFIG_MANIFEST_INVALID "+sample+" "+config)
        for fname, digest in m["autok_sha256"].items():
            check_sha(attempt/fname,digest,"CC_AUTOK")
        summary=jload(attempt/"autok_summary.json")
        autok_k=int(summary["selected_k"])
        demand(2<=autok_k<=10 and
               autok_k==int(m["autok_selected_k"]) and
               summary.get("candidate_K")==list(range(2,11)) and
               summary.get("internal_K")==list(range(1,12)) and
               summary.get("runs_per_internal_K")==5 and
               len(summary.get("stability_by_k",{}))==9,
               "CC_AUTOK_SUMMARY_INVALID "+sample+" "+config)
        score=[]
        for k in range(2,11):
            vals=summary["stability_by_k"][str(k)]["values"]
            a=np.asarray(vals,dtype=float)
            demand(a.size>0 and np.isfinite(a).all(),
                   "CC_STABILITY_INVALID")
            score.append(float(summary["stability_by_k"][str(k)]["mean"]))
        demand(autok_k==2+int(np.argmax(score)),"CC_AUTOK_ARGMAX_MISMATCH")
        with np.load(attempt/"all_k_run_labels.npz",
                     allow_pickle=False) as archive:
            for k in range(1,12):
                key=f"k_{k}"
                demand(key in archive and
                       archive[key].shape==(5,N_MODEL[SAMPLES.index(sample)]),
                       "CC_AUTOK_ALL_K_FIVE_RUNS_INCOMPLETE")
        for j,info_pred in enumerate(m["predictions"]):
            arm=ARMS[j//3]
            seed=SEEDS[j%3]
            demand(info_pred["arm"]==arm and info_pred["seed"]==seed,
                   "CC_TASK_SEED_ARM_ORDER_BAD")
            k=autok_k if arm=="k_blind" else ORACLE[SAMPLES.index(sample)]
            demand(info_pred["chosen_k"]==k,
                   "CC_CHOSEN_K_BAD "+sample+" "+config)
            add(sample,"CellCharter",config,arm,seed,
                attempt/info_pred["file"],info_pred["sha256"],
                k,info_pred["actual_k"])
    demand(len(cc_grid)==36,"CC_SIX_PATIENT_SIX_SCALE_GRID_INCOMPLETE")
    print("E5B_AUDIT_STAGE_PASS method=CellCharter checked=216",flush=True)

    non=check_status(NON,"E5B_NONSPATIAL_GMM_LEIDEN_FROZEN_V1",
                     "completed",72)
    demand(non.get("expected")==72 and not non.get("failures"),
           "NON_BATCH_FAILURES")
    for info in non["completed"]:
        sample,method,arm,seed=info["task"]
        demand(sample in SAMPLES and method in ("GMM","Leiden") and
               arm in ARMS and seed in SEEDS,"NON_TASK_GRID_INVALID")
        folder=Path(info["path"])
        check_sha(folder/"manifest.json",info["manifest_sha256"],"NON_MANIFEST")
        m=jload(folder/"manifest.json")
        demand(m.get("status")=="completed" and
               m.get("task")==info["task"],"NON_TASK_MANIFEST_INVALID")
        d=m["details"]
        if method=="GMM":
            results=d["candidate_results"]
            expect=range(2,11) if arm=="k_blind" else (
                ORACLE[SAMPLES.index(sample)],)
            demand([x["k"] for x in results]==list(expect),
                   "GMM_K_GRID_CHANGED")
            choice=min(results,key=lambda x:(x["bic"],x["k"]))["k"]
            demand(choice==d["selected_k"],"GMM_BIC_SELECTION_WRONG")
            chosen_k=int(choice)
        else:
            results=d["candidate_results"]
            expect=RES if arm=="oracle_k" else (1.0,)
            demand(np.allclose([x["resolution"] for x in results],list(expect),
                               atol=1e-12,rtol=0),
                   "LEIDEN_RESOLUTION_GRID_CHANGED")
            choice=(min(results,key=lambda x:(
                abs(x["actual_k"]-ORACLE[SAMPLES.index(sample)]),
                x["resolution"])) if arm=="oracle_k" else results[0])
            demand(abs(d["selected_resolution"]-choice["resolution"])<1e-12,
                   "LEIDEN_RESOLUTION_CHOICE_WRONG")
            chosen_k=int(choice["actual_k"])
        add(sample,method,"L0_5D",arm,seed,folder/"predictions.csv",
            m["prediction_sha256"],chosen_k,m["n_actual_k"])
    print("E5B_AUDIT_STAGE_PASS method=GMM_Leiden checked=72",flush=True)

    bank=check_status(BANK,"E5B_BANKSY_FROZEN_SIX_PATIENTS_V1",
                      "completed_samples",6)
    demand(bank.get("expected_tasks")==36 and not bank.get("failures"),
           "BANK_BATCH_FAILURES")
    for info in bank["completed_samples"]:
        sample=info["sample"]
        attempt=Path(info["attempt"])
        check_sha(attempt/"manifest.json",info["manifest_sha256"],
                  "BANK_MANIFEST")
        m=jload(attempt/"manifest.json")
        demand(m.get("status")=="completed" and
               m.get("sample")==sample and len(m.get("tasks",[]))==6,
               "BANK_SAMPLE_MANIFEST_INVALID")
        for j,rec in enumerate(m["tasks"]):
            seed=SEEDS[j//2]
            arm=ARMS[j%2]
            demand(rec["seed"]==seed and rec["arm"]==arm,
                   "BANK_SEED_ARM_ORDER_INVALID")
            trials=rec["candidate_trials"]
            demand(len(trials)==16 and
                   np.allclose([x["resolution"] for x in trials],RES,
                               atol=1e-12,rtol=0),
                   "BANK_16_RESOLUTION_GRID_CHANGED")
            choice=(trials[RES.index(1.0)] if arm=="k_blind" else
                    min(trials,key=lambda x:(
                        abs(x["actual_k"]-ORACLE[SAMPLES.index(sample)]),
                        x["resolution"])))
            demand(abs(rec["chosen_resolution"]-choice["resolution"])<1e-12 and
                   rec["actual_k"]==choice["actual_k"],
                   "BANK_CHOSEN_RESOLUTION_WRONG")
            archive=attempt/f"seed_{seed}"/"all_resolution_labels.npz"
            check_sha(archive,m["resolution_label_sha256"][str(seed)],
                      "BANK_RESOLUTION_ARCHIVE")
            pth=attempt/rec["predictions_file"]
            bc,lab,_=pred(pth,sample,rec["prediction_sha256"])
            with np.load(archive,allow_pickle=False) as data:
                key=choice["archive_key"]
                demand(key in data and
                       np.array_equal(lab,np.asarray(data[key])),
                       "BANK_PREDICTION_NOT_FROZEN_GRID_PARTITION")
            # pred() above validates each archive label, add() validates unique grid
            add(sample,"BANKSY","BANKSY_native",arm,seed,
                pth,rec["prediction_sha256"],
                choice["actual_k"],rec["actual_k"])
    print("E5B_AUDIT_STAGE_PASS method=BANKSY checked=36",flush=True)

    bs=check_status(BS,"E5B_BAYESSPACE_FROZEN_SIX_PATIENTS_V1",
                    "completed_samples",6)
    demand(bs.get("expected_tasks")==36 and not bs.get("failures"),
           "BS_BATCH_FAILURES")
    for info in bs["completed_samples"]:
        sample=info["sample"]
        attempt=Path(info["attempt"])
        check_sha(attempt/"sample_manifest.json",
                  info["manifest_sha256"],"BS_SAMPLE_MANIFEST")
        m=jload(attempt/"sample_manifest.json")
        demand(m.get("status")=="completed" and
               m.get("sample")==sample and len(m.get("tasks",[]))==6,
               "BS_SAMPLE_MANIFEST_INVALID")
        for j,rec in enumerate(m["tasks"]):
            seed=SEEDS[j//2]
            arm=ARMS[j%2]
            demand(int(rec["seed"])==seed and rec["arm"]==arm,
                   "BS_SEED_ARM_ORDER_INVALID")
            qtune=attempt/rec["q_tune_file"]
            check_sha(qtune,rec["q_tune_sha256"],"BS_QTUNE_CANDIDATES")
            trial=pd.read_csv(qtune)
            demand(list(trial.columns)==["q","loglik"] and
                   np.array_equal(trial.q.to_numpy(),np.arange(2,11)) and
                   np.isfinite(trial.loglik.to_numpy()).all(),
                   "BS_QTUNE_FROZEN_GRID_OR_LOG_LIK_BAD")
            q_blind=int(trial.loc[trial.loglik==trial.loglik.max(),"q"].min())
            q=(q_blind if arm=="k_blind" else ORACLE[SAMPLES.index(sample)])
            demand(int(rec["selected_q"])==q,"BS_SELECTED_Q_NOT_FROZEN_RULE")
            pth=attempt/rec["predictions_file"]
            add(sample,"BayesSpace","BayesSpace_native",arm,seed,pth,
                rec["prediction_sha256"],q,rec["actual_k"])
    print("E5B_AUDIT_STAGE_PASS method=BayesSpace checked=36",flush=True)
    demand(len(all_records)==360 and len(seen)==360,
           f"INCOMPLETE_OR_DUPLICATE_TOTAL {len(all_records)}")
    expect={(s,"CellCharter",c,a,k) for s in SAMPLES for c in SCALES
            for a in ARMS for k in SEEDS}
    expect|={(s,m,"L0_5D",a,k) for s in SAMPLES
             for m in ("GMM","Leiden") for a in ARMS for k in SEEDS}
    expect|={(s,"BANKSY","BANKSY_native",a,k) for s in SAMPLES
             for a in ARMS for k in SEEDS}
    expect|={(s,"BayesSpace","BayesSpace_native",a,k) for s in SAMPLES
             for a in ARMS for k in SEEDS}
    demand(seen==expect,"ALL_360_TASK_GRID_NOT_EXACTLY_AS_FROZEN")
    return all_records,expected_barcodes,stage

def phase2(all_records,orders,stage):
    """Deliberate label access is strictly downstream of full phase1 PASS."""
    truth={}
    reference_info=[]
    for idx,sample in enumerate(SAMPLES):
        ref=STAGE/"reference_only"/f"{sample}_reference_labels.csv"
        check_sha(ref,stage["samples"][idx]["reference_labels_sha256"],
                  "EVAL_REFERENCE_SHA")
        df=pd.read_csv(ref,dtype=str,keep_default_na=False)
        demand(list(df.columns)==["barcode","Classification","can_evaluate"],
               "REFERENCE_COLUMNS_BAD")
        demand(len(df)==N_MODEL[idx] and
               np.array_equal(df.barcode.to_numpy(),orders[sample]) and
               df.barcode.is_unique and
               set(df.can_evaluate.unique())<={"0","1"},
               "REFERENCE_SPOT_ALIGNMENT_INVALID")
        labels=df.Classification.astype(str).str.strip()
        mask=~labels.str.casefold().isin(EXCLUDE)
        demand(np.array_equal(mask.to_numpy(),df.can_evaluate.eq("1").to_numpy())
               and int(mask.sum())==N_EVAL[idx]
               and labels[mask].nunique()==ORACLE[idx],
               "REFERENCE_FROZEN_MASK_CLASS_COUNTS_CHANGED")
        truth[sample]=(labels.to_numpy(),mask.to_numpy())
        reference_info.append({
            "sample":sample,"model_spots":N_MODEL[idx],
            "eval_spots":N_EVAL[idx],"excluded":N_MODEL[idx]-N_EVAL[idx],
            "oracle_label_categories":ORACLE[idx],
            "reference_sha256":sha(ref),
        })
    scores=[]
    for item in all_records:
        sample=item["sample"]
        b,labels,actual=pred(
            Path(item["pred_file"]),sample,item["pred_sha256"])
        demand(np.array_equal(b,orders[sample]),
               "EVALUATION_SPOT_ORDER_CHANGED")
        y,mask=truth[sample]
        ar=float(adjusted_rand_score(y[mask],labels[mask]))
        nm=float(normalized_mutual_info_score(
            y[mask],labels[mask],average_method="arithmetic"))
        demand(np.isfinite(ar) and np.isfinite(nm) and
               -1.0<=ar<=1.0 and -1e-9<=nm<=1+1e-9,
               "NONFINITE_OR_OUT_OF_RANGE_METRIC")
        scores.append({
            "sample":sample,"method":item["method"],
            "config":item["config"],"arm":item["arm"],
            "seed":item["seed"],"chosen_k":item["chosen_k"],
            "actual_k":actual,"n_evaluated":int(mask.sum()),
            "ari":ar,"nmi":nm,"prediction_sha256":item["pred_sha256"],
            "prediction_file":item["pred_file"],
        })
    scores=pd.DataFrame(scores)
    keys=["sample","method","config","arm"]
    patient=(scores.groupby(keys,as_index=False).agg(
        n_seed=("seed","nunique"),ari_mean=("ari","mean"),
        ari_sd=("ari","std"),nmi_mean=("nmi","mean"),nmi_sd=("nmi","std"),
        actual_k_min=("actual_k","min"),actual_k_max=("actual_k","max")))
    demand(len(patient)==120 and (patient.n_seed==3).all(),
           "THREE_SEED_PATIENT_AGGREGATION_INVALID")
    pairs=[]
    for arm in ARMS:
        for sample in SAMPLES:
            sample_p=patient[(patient["sample"]==sample)&
                             (patient["arm"]==arm)]
            for metric in ("ari_mean","nmi_mean"):
                get=lambda method,config:float(sample_p[
                    (sample_p["method"]==method)&
                    (sample_p["config"]==config)][metric].iloc[0])
                a=get("CellCharter","A_L0L1L2_15D")
                b=get("CellCharter","B_L0L1L4_15D")
                base=get("CellCharter","L0_5D")
                pairs.extend([
                    {"sample":sample,"arm":arm,"metric":metric,
                     "comparison":"CC_A15_minus_CC_L0",
                     "delta":a-base},
                    {"sample":sample,"arm":arm,"metric":metric,
                     "comparison":"CC_B15_minus_CC_A15",
                     "delta":b-a},
                ])
                for method,config in (
                    ("GMM","L0_5D"),("Leiden","L0_5D"),
                    ("BANKSY","BANKSY_native"),
                    ("BayesSpace","BayesSpace_native")):
                    pairs.append({
                        "sample":sample,"arm":arm,"metric":metric,
                        "comparison":"CC_A15_minus_"+method,
                        "delta":a-get(method,config),
                    })
    paired=pd.DataFrame(pairs)
    demand(len(paired)==6*2*2*6,
           "PATIENT_PAIR_COMPARISON_TASK_COUNT_CHANGED")
    return scores,patient,paired,reference_info

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run",action="store_true",
                   help="Read all outputs, independently validate, then score")
    args=p.parse_args()
    if not args.run:
        print("E5B_AUDIT_DRY_RUN expected=360 samples=6 "
              "NO_MODEL_FIT_NO_LABEL_ACCESS_NO_FILES_WRITTEN",flush=True)
        return 0
    out=ROOT/"phase_audit_v1"/(
        "audit_"+datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        +"_"+str(os.getpid()))
    demand(not out.exists(),"AUDIT_SESSION_EXISTS")
    out.mkdir(parents=True,exist_ok=False)
    reportfile=out/"audit_report.json"
    report={
        "protocol":PROTOCOL,"status":"running",
        "started_utc":datetime.now(timezone.utc).isoformat(),
        "model_fit_performed":False,"params_changed":False,
        "reference_labels_read_only_after_360_predictions_verified":True,
        "expected_predictions":360,"independent_biological_patients":6,
        "sources":[str(x) for x in (STAGE,FEAT,CC,NON,BANK,BS)],
        "local_code_sha256":EXPECTED_SHA,
    }
    dump(reportfile,report)
    try:
        records,orders,stage=phase1()
        report["phase1"]="passed"
        report["verified_predictions"]=len(records)
        report["verified_utc"]=datetime.now(timezone.utc).isoformat()
        dump(reportfile,report)
        print("E5B_AUDIT_PREDICTIONS_PASS verified=360/360 "
              "errors=0 labels_not_yet_read=True",flush=True)
        scores,patient,paired,refs=phase2(records,orders,stage)
        scores.to_csv(out/"all_360_prediction_metrics.csv",index=False)
        patient.to_csv(out/"patient_three_seed_summary.csv",index=False)
        paired.to_csv(out/"patient_paired_effects.csv",index=False)
        report.update({
            "status":"passed","phase2":"passed",
            "completed_utc":datetime.now(timezone.utc).isoformat(),
            "metrics":"sklearn adjusted_rand_score; normalized_mutual_info_score average_method=arithmetic",
            "evaluation_reference":refs,
            "all_metrics_count":int(len(scores)),
            "patient_method_config_arm_count":int(len(patient)),
            "patient_paired_comparisons_count":int(len(paired)),
            "files_sha256":{
                file:sha(out/file) for file in (
                    "all_360_prediction_metrics.csv",
                    "patient_three_seed_summary.csv",
                    "patient_paired_effects.csv")
            },
            "no_p_values_or_technical_pseudoreplication":True,
        })
        dump(reportfile,report)
        print("E5B_PHASE_AUDIT_FINAL status=passed "
              "verified=360/360 metrics=360/360 errors=0 "
              f"report={reportfile}",flush=True)
        for filename in (
            "all_360_prediction_metrics.csv",
            "patient_three_seed_summary.csv",
            "patient_paired_effects.csv"):
            print(f"E5B_PHASE_AUDIT_FILE {out/filename}",flush=True)
        print("NO_REFIT_NO_PARAM_CHANGE_PATIENT_N6",flush=True)
        return 0
    except BaseException as exc:
        report.update({
            "status":"failed","error":repr(exc),
            "traceback":traceback.format_exc(),
            "failed_utc":datetime.now(timezone.utc).isoformat(),
        })
        dump(reportfile,report)
        print(f"E5B_PHASE_AUDIT_FAILED error={exc!r} "
              f"report={reportfile}",file=sys.stderr,flush=True)
        return 2

if __name__=="__main__":
    sys.exit(main())
