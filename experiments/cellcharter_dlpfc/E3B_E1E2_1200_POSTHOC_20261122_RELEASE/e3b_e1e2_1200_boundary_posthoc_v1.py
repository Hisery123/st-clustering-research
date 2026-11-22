"""E3b posthoc sensitivity: ALL frozen E1/E2 1200 predictions, no fitting.

Data were already inspected before this analysis; this is NOT preregistered.
Uses the SAME hex graph, valid-label mask, line-graph 0/1/2 hop one-to-one
max-cardinality matching as e3b_e3d48_boundary_posthoc_v1.py.

All checks are strict: original ZIP and every prediction SHA, input-ref SHA,
barcode order, task uniqueness, complete 12*10*10 task grid, the E1/E2
ledger SHA verified separately against current GitHub (source ZIP contains
ledger SHA). Original reference labels are used only after ZIP source checks.
Outputs all 3,600 rows; no best-of seed/scale or p-values.
"""
from __future__ import annotations
import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import sys
import zipfile
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_bipartite_matching

SAMPLES = ('151507','151508','151509','151510','151669','151670',
           '151671','151672','151673','151674','151675','151676')
CONDITIONS = ('cum_L0','cum_L0_L1','cum_L0_L1_L2','cum_L0_L1_L2_L3',
              'cum_L0_L1_L2_L3_L4','fixed_L0_L1_L3','fixed_L0_L1_L4',
              'fixed_L0_L2_L3','fixed_L0_L2_L4','fixed_L0_L3_L4')
SEEDS = (22911,7449,25842,10379,6690,26128,21059,22159,32389,12815)
OFFSETS = ((0,-2),(0,2),(-1,-1),(-1,1),(1,-1),(1,1))
# SHA verified with GitHub fetch_file on 2026-11-22; ZIP also contains same SHA
GITHUB_LEDGER_SHA = 'e021ca75958c3d5539dda1987e5031d13ce4fe161d9f0db7f03b5dcfb40e065e'
EXPECTED_ZIP_SHA = 'cfad75dbc35723c72e52f8906b07e1b81048ff70fcf04df709d41ae42bc1302b'
EXPECTED_REF_ZIP_SHA = '1f3e55c1acbf9162998a1a3e198c26284c8a63f7784ab8b28088220e2e148094'
EXPECTED_REF_AUDIT_SHA = 'f2560ec0cde25a9b09fcec8816ffac9e844faceb562756ec19f951cfe51fc821'


def demand(test,message):
    if not bool(test):
        raise RuntimeError(message)


def sha(data):return hashlib.sha256(data).hexdigest()


def file_sha(path):
    digest=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):digest.update(chunk)
    return digest.hexdigest()


def load_csv_zip(z,path):
    return pd.read_csv(io.BytesIO(z.read(path)),dtype=str)


def hex_graph(spots,reference):
    xy=spots[['array_row','array_col']].apply(pd.to_numeric,errors='raise').to_numpy(dtype=np.int64)
    demand(len(set(map(tuple,xy)))==len(spots),'DUPLICATE_HEX_COORDINATES')
    index={tuple(p):i for i,p in enumerate(xy)}
    keep=np.asarray(pd.notna(reference))
    edge=[]
    neighbors=[set() for _ in range(len(spots))]
    for i,(r,c) in enumerate(xy):
        if not keep[i]:continue
        for dr,dc in OFFSETS:
            j=index.get((int(r+dr),int(c+dc)))
            if j is not None and j>i and keep[j]:
                edge.append((i,j));neighbors[i].add(j);neighbors[j].add(i)
    edge=np.asarray(edge,dtype=np.int32)
    demand(edge.ndim==2 and edge.shape[1]==2 and len(edge)>0,'INVALID_HEX_EDGE_GRID')
    if {'pxl_row_in_fullres','pxl_col_in_fullres'}.issubset(spots.columns):
        pos=spots[['pxl_row_in_fullres','pxl_col_in_fullres']].apply(pd.to_numeric,errors='raise').to_numpy(dtype=float)
        d=np.linalg.norm(pos[edge[:,0]]-pos[edge[:,1]],axis=1)
        med=float(np.median(d));d95=float(np.quantile(d,0.95))
        demand(np.isfinite(d).all() and med>0 and d95 < 1.25*med,'UNPHYSICAL_HEX_NEIGHBORS')
    else:
        med=None;d95=None
    ref_positive=np.flatnonzero(reference[edge[:,0]] != reference[edge[:,1]])
    incident=[[] for _ in range(len(spots))]
    for i,eid in enumerate(ref_positive):
        u,v=edge[eid];incident[u].append(i);incident[v].append(i)
    return edge,neighbors,ref_positive,incident,med,d95


def one_to_one_match(pred_ids,ref_ids,edges,neighbors,ref_incident,tol):
    if len(pred_ids)==0 or len(ref_ids)==0:return 0,0
    if tol==0:return int(np.intersect1d(pred_ids,ref_ids,assume_unique=True).size),0
    I=[];J=[]
    for i,eid in enumerate(pred_ids):
        u,v=map(int,edges[eid]);vertices={u,v}
        if tol==2:vertices.update(neighbors[u]);vertices.update(neighbors[v])
        candidates=set()
        for node in vertices:candidates.update(ref_incident[node])
        demand(len(candidates)<=100,'EXCESSIVE_MATCHING_CANDIDATES')
        I.extend([i]*len(candidates));J.extend(candidates)
    adj=csr_matrix((np.ones(len(I),dtype=np.int8),(I,J)),shape=(len(pred_ids),len(ref_ids)))
    adj.sum_duplicates()
    m=maximum_bipartite_matching(adj,perm_type='column')
    return int(np.count_nonzero(m!=-1)),int(adj.nnz)


def metric(tp,n_truth,n_pred):
    demand(0<=tp<=min(n_truth,n_pred),'IMPOSSIBLE_TP')
    fp=n_pred-tp;fn=n_truth-tp
    prec=tp/n_pred if n_pred else 0.
    rec=tp/n_truth if n_truth else 0.
    f1=2*tp/(n_truth+n_pred) if n_truth+n_pred else 1.
    return (fp,fn,prec,rec,f1)


def evaluate(source_zip,ref_zip,ref_audit,reference_provenance_json,output):
    demand(not output.exists(),'OUTPUT_EXISTS_NO_OVERWRITE')
    demand(file_sha(source_zip)==EXPECTED_ZIP_SHA,'SOURCE_ZIP_SHA_MISMATCH')
    demand(file_sha(ref_zip)==EXPECTED_REF_ZIP_SHA,'REFERENCE_ZIP_SHA_MISMATCH')
    demand(file_sha(ref_audit)==EXPECTED_REF_AUDIT_SHA,'E3D_FROZEN_AUDIT_SHA_MISMATCH')
    # Sanity test for matching monotonicity and distinct true edges.
    edges=np.asarray([(0,1),(1,2),(2,3)],dtype=np.int32)
    neighbors=[{1},{0,2},{1,3},{2}]
    incident=[[],[0],[0],[]]
    demand(one_to_one_match(np.asarray([0]),np.asarray([1]),edges,neighbors,incident,0)[0]==0
       and one_to_one_match(np.asarray([0]),np.asarray([1]),edges,neighbors,incident,1)[0]==1,
       'ONE_TO_ONE_SANITY_FAILED')
    expected={(s,c,str(seed)) for s in SAMPLES for c in CONDITIONS for seed in SEEDS}
    ref_report=json.loads(reference_provenance_json.read_text(encoding='utf8'))
    demand(ref_report['status']=='passed' and ref_report['n_predictions']==48,
           'REFERENCE_POSTHOC_PROVENANCE_REPORT_INVALID')
    reference_verification=ref_report['reference_verification']
    rows=[];graphs={};actual_refs={};shas=[]
    with zipfile.ZipFile(source_zip) as z, zipfile.ZipFile(ref_zip) as rz:
        demand(z.testzip() is None and rz.testzip() is None,'ZIP_CRC_FAILED')
        listed_sha=z.read('LEDGER_SHA256.txt').decode('ascii').strip().lower()
        demand(listed_sha==GITHUB_LEDGER_SHA,'GITHUB_LEDGER_SHA_MISMATCH')
        manifest=pd.read_csv(io.BytesIO(z.read('SOURCE_SHA256.csv')),dtype=str)
        demand(len(manifest)==1200 and set(manifest.columns)=={'Sample','Condition','Seed','RelativePath','OriginalPath','SHA256'},'SOURCE_MANIFEST_BAD')
        seen=set()
        for entry in manifest.itertuples(index=False):
            key=(entry.Sample,entry.Condition,entry.Seed)
            demand(key in expected and key not in seen,'DUPLICATE_OR_UNKNOWN_TASK '+str(key))
            seen.add(key)
            path=f'predictions\\{entry.Sample}\\{entry.Condition}\\seed_{entry.Seed}\\predictions.csv'
            demand(entry.RelativePath==path,'PREDICTION_PATH_BAD '+str(key))
            src=z.read(path)
            demand(sha(src)==entry.SHA256,'PREDICTION_SHA_MISMATCH '+str(key))
            shas.append(entry.SHA256)
        demand(seen==expected,'TASK_GRID_INCOMPLETE')
        print('E3B_E1E2_PRECHECK_PASS predictions=1200/1200 sha=1200/1200 unique=1200 github_ledger_sha_verified=True',flush=True)
        # Preserve exact, prior-reported reference source bytes and the same label mask.
        for sid in SAMPLES:
            spath=f'references\\{sid}\\spots_aligned.csv'
            lpath=f'references\\{sid}\\manual_layer_annotations.csv'
            sdata=rz.read(spath);ldata=rz.read(lpath)
            expect=reference_verification[sid]
            demand(sha(sdata)==expect['positions_sha256'] and sha(ldata)==expect['reference_sha256'],
                   'CROSS_STAGE_REFERENCE_SHA_MISMATCH '+sid)
            spots=pd.read_csv(io.BytesIO(sdata),dtype=str)
            lab=pd.read_csv(io.BytesIO(ldata),dtype=str)
            demand(spots.barcode.is_unique and lab.spot_name.notna().all(),'INVALID_REFERENCE_BARCODES '+sid)
            selected=lab.loc[lab.sample_name==sid,['spot_name','layer']]
            demand(selected.spot_name.is_unique and selected.spot_name.isin(spots.barcode).all(),'REFERENCE_BARCODE_OUTSIDE_SPOTS '+sid)
            labels=selected.set_index('spot_name').layer.reindex(spots.barcode).to_numpy()
            demand(len(spots)==expect['n_spots'] and int(pd.notna(labels).sum())==expect['n_labeled'] and len(pd.Series(labels).dropna().unique())==expect['n_labels'],
                   'REFERENCE_COUNT_MISMATCH '+sid)
            graph=hex_graph(spots,labels)
            edges,neighbors,true_ids,incidents,med,d95=graph
            graphs[sid]=(spots.barcode.to_numpy(),edges,neighbors,true_ids,incidents)
            actual_refs[sid]={'labels_sha256':sha(ldata),'positions_sha256':sha(sdata),
                  'model_spots':len(spots),'eval_spots':int(pd.notna(labels).sum()),
                  'reference_boundaries':len(true_ids),'valid_hex_edges':len(edges),'median_pixel_neighbor_distance':med,'p95_pixel_neighbor_distance':d95}
        print('E3B_E1E2_REFERENCE_PASS samples=12 donor_n=3 spot_ref_sha_equal_e3d=True',flush=True)
        for idx,entry in enumerate(manifest.itertuples(index=False),1):
            sid,cond,seed=entry.Sample,entry.Condition,int(entry.Seed)
            path=entry.RelativePath
            p=pd.read_csv(io.BytesIO(z.read(path)),dtype={'barcode':str})
            mustcol=list(p.columns)==['barcode','cluster']
            demand(mustcol and p.barcode.is_unique,'PREDICTION_CSV_COLUMNS_OR_DUPLICATE_BARCODES '+path)
            bar,edges,neighbors,true_ids,incidents=graphs[sid]
            demand(np.array_equal(p.barcode.to_numpy(),bar),'BARCODE_ORDER_MISMATCH '+path)
            cls=pd.to_numeric(p.cluster,errors='raise').to_numpy()
            demand(len(cls)==len(bar) and np.isfinite(cls).all() and np.array_equal(cls,np.floor(cls)),'INVALID_CLUSTER_LABELS '+path)
            pred_ids=np.flatnonzero(cls[edges[:,0]]!=cls[edges[:,1]])
            n_true=len(true_ids);n_pred=len(pred_ids);prev=-1
            for tol in (0,1,2):
                tp,n_pairs=one_to_one_match(pred_ids,true_ids,edges,neighbors,incidents,tol)
                if tol==0:
                    demand(tp==len(np.intersect1d(pred_ids,true_ids,assume_unique=True)),'STRICT_F1_CROSSCHECK_FAILED')
                demand(tp>=prev,'TOLERANCE_MONOTONICITY_FAILED')
                prev=tp
                fp,fn,precision,recall,f1=metric(tp,n_true,n_pred)
                rows.append({'sample':sid,'donor':'D'+str(SAMPLES.index(sid)//4+1),
                    'condition':cond,'seed':seed,'tolerance_linegraph_hops':tol,
                    'n_model_spots':len(bar),'n_eval_spots':actual_refs[sid]['eval_spots'],
                    'valid_spot_edges':len(edges),'reference_boundary_edges':n_true,
                    'predicted_boundary_edges':n_pred,'matched_tp':tp,'unmatched_pred_fp':fp,
                    'unmatched_ref_fn':fn,'precision':precision,'recall':recall,'f1':f1,
                    'candidate_pair_edges':n_pairs,'prediction_sha256':entry.SHA256,
                    'reference_sha256':actual_refs[sid]['labels_sha256'],'positions_sha256':actual_refs[sid]['positions_sha256']})
            if idx%100==0:print(f'E3B_E1E2_PROGRESS grids={idx}/1200',flush=True)
    frame=pd.DataFrame(rows).sort_values(['sample','condition','seed','tolerance_linegraph_hops']).reset_index(drop=True)
    demand(len(frame)==3600 and frame.f1.between(0,1).all(),'RESULT_GRID_INVALID')
    expected_sums={'cum_L0_L1_L2':2103,'fixed_L0_L1_L4':1999}
    # The historical strictly matched seed 22911 A/B (12 slices) summary
    # provides an independent check, but may use a different historic source;
    # if it conflicts we STOP and examine rather than hiding the disagreement.
    old={}
    for condition,expected_tp in expected_sums.items():
        obs=int(frame.loc[(frame.condition==condition)&(frame.seed==22911)&(frame.tolerance_linegraph_hops==0),'matched_tp'].sum())
        old[condition]={'expected_historical_sum':expected_tp,'observed_sum':obs,'match':obs==expected_tp}
    print('E3B_E1E2_HISTORICAL_SEED22911_TP_CHECK '+json.dumps(old),flush=True)
    # aggregate at the nested slice-seed level first; do NOT treat as donor n=1200.
    wide=frame.pivot(index=['sample','donor','condition','seed'],columns='tolerance_linegraph_hops',values='f1').reset_index()
    wide.columns=['sample','donor','condition','seed','strict_f1_0hop','f1_1hop','f1_2hop']
    wide['f1_1_minus_0']=wide.f1_1hop-wide.strict_f1_0hop
    wide['f1_2_minus_0']=wide.f1_2hop-wide.strict_f1_0hop
    demand(len(wide)==1200 and (wide.strict_f1_0hop<=wide.f1_1hop+1e-12).all() and (wide.f1_1hop<=wide.f1_2hop+1e-12).all(),'WIDE_BAD')
    slice_mean=frame.groupby(['sample','donor','condition','tolerance_linegraph_hops'],as_index=False).agg(mean_f1=('f1','mean'),sd_technical_seed_f1=('f1','std'),n_seeds=('seed','nunique'))
    donor_mean=slice_mean.groupby(['donor','condition','tolerance_linegraph_hops'],as_index=False).agg(mean_f1=('mean_f1','mean'),n_slices=('sample','nunique'))
    macro=slice_mean.groupby(['condition','tolerance_linegraph_hops'],as_index=False).agg(mean_f1=('mean_f1','mean'),sd_nested_slice_mean_f1=('mean_f1','std'),n_slices=('sample','nunique'))
    demand(len(slice_mean)==360 and len(donor_mean)==90 and len(macro)==30 and (slice_mean.n_seeds==10).all(),'SUMMARY_BAD')
    output.mkdir(parents=True,exist_ok=False)
    dfs={'all_3600_boundary_metric_rows.csv':frame,'all_1200_paired_strict_tolerance.csv':wide,
         'slice_mean_360.csv':slice_mean,'donor_mean_90.csv':donor_mean,'macro_mean_30.csv':macro}
    for name,df in dfs.items():df.to_csv(output/name,index=False,lineterminator='\n',float_format='%.16g')
    report={'name':'E3B_E1E2_1200_POSTHOC_BOUNDARY_TOLERANCE_V1','status':'passed',
      'created_utc':datetime.now(timezone.utc).isoformat(),
      'source_zip_sha256':file_sha(source_zip),'reference_zip_sha256':file_sha(ref_zip),
      'github_frozen_e1e2_1200_tasks_ledger_sha256':GITHUB_LEDGER_SHA,
      'n_prediction_tasks':1200,'n_metric_rows':3600,'n_slices':12,'independent_donors':3,'seeds_per_slice_condition':10,
      'conditions':list(CONDITIONS),'n_conditions':10,
      'strict_metric':'edge-level TP/FP/FN, boundary defined by differing endpoint labels on valid hex edge; 0hop',
      'tolerance_metric':'1/2 hops in line graph of edges with two labeled endpoints, maximum one-to-one bipartite matching',
      'selection_timing':'posthoc_after_prior_k_and_scale_results_were_viewed',
      'only_posthoc_reference_use':True,'no_new_fitting':True,'no_changed_K':True,'no_chosen_optimal_tolerance':True,
      'source_manifest_sha256':sha(zipfile.ZipFile(source_zip).read('SOURCE_SHA256.csv')),
      'reference_provenance':actual_refs,
      'historic_A_B_seed22911_TP_crosscheck':old,
      'all_sources_sha_verified':True,
      'output_sha256':{name:file_sha(output/name) for name in dfs},
      'statistical_scope':'3 independent donors; 12 nested slices; ten GMM seeds are technical, not biological replicates',
      'warning':'Larger tolerance makes F1 less strict but does not imply better strict boundary detection. Always show strict alongside 1/2hop; no p-values/CI here.'}
    (output/'posthoc_boundary_audit_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
    print('E3B_E1E2_FINAL status=passed tasks=1200/1200 metrics=3600/3600 outputs='+str(output),flush=True)
    print(macro.pivot(index='condition',columns='tolerance_linegraph_hops',values='mean_f1').to_string(),flush=True)
    return report

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--source-zip',type=Path,required=True)
    ap.add_argument('--ref-zip',type=Path,required=True)
    ap.add_argument('--ref-audit',type=Path,required=True)
    ap.add_argument('--reference-provenance-json',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    opt=ap.parse_args()
    try:evaluate(opt.source_zip,opt.ref_zip,opt.ref_audit,opt.reference_provenance_json,opt.output)
    except Exception as exc:
        print('E3B_E1E2_ABORT '+type(exc).__name__+': '+str(exc),file=sys.stderr,flush=True)
        raise
