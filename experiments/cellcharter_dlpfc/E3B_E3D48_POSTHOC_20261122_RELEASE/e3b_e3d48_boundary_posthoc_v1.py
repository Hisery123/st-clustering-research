"""E3b *partial* posthoc boundary analysis on E3d's 48 frozen AutoK predictions.

NOT the 1200-prediction E1/E2-boundary full cohort, which is not uploaded.
No model training; all predictions are from the SHA-verified E3d ZIP.
All annotations are used only for posthoc evaluation; three independent donors.

Strict metric: undirected edges in Visium six-adjacency graph where BOTH
spots have manual reference layers. Reference edge is positive if its endpoint
layers differ; predicted edge positive if original cluster IDs differ.

Exploratory tolerance: shortest hops on the *line graph* of valid lattice edges.
0 = same edge, 1 = edges share a spot, 2 = endpoints share a single lattice
neighbor edge. Scores use a maximum-cardinality ONE-TO-ONE bipartite matching:
no true edge can be counted multiple times. Report ALL thresholds (0,1,2).
0-hop F1 remains the strict reference; tolerances never replace the strict
metric. This analysis was defined after earlier ARI/NMI results were visible.

Hex/Visium row/column deltas are (0,+/-2),(+/-1,+/-1). Their physical
pixel distances are similar; (+/-2,0) is NOT a nearest neighbor on Visium.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import sys
import zipfile

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_bipartite_matching

SAMPLES = ('151507','151508','151509','151510','151669','151670',
           '151671','151672','151673','151674','151675','151676')
CONDS={'cum_L0_L1':10,'cum_L0_L1_L2':15,'cum_L0_L1_L2_L3':20,
       'cum_L0_L1_L2_L3_L4':25}
OFFSETS=((0,-2),(0,2),(-1,-1),(-1,1),(1,-1),(1,1))
ORIGINAL_AUDIT_SHA='f2560ec0cde25a9b09fcec8816ffac9e844faceb562756ec19f951cfe51fc821'


def must(ok,msg):
    if not bool(ok):raise RuntimeError(msg)


def sha(b):return hashlib.sha256(b).hexdigest()


def file_sha(path):return sha(Path(path).read_bytes())


def read(z,path):return pd.read_csv(io.BytesIO(z.read(path)),dtype=str)


def make_graph(spots,truth_labels):
    co=spots[['array_row','array_col']].apply(pd.to_numeric,errors='raise').to_numpy(dtype=np.int64)
    must(np.isfinite(co).all() and len(np.unique(co,axis=0))==len(co),
         'BAD_LATTICE_COORDINATES')
    mapping={tuple(x):i for i,x in enumerate(co)}
    edge=[];neighbors=[set() for _ in range(len(spots))]
    valid=np.asarray(pd.notna(truth_labels))
    for idx,(r,c) in enumerate(co):
        if not valid[idx]:continue
        for dr,dc in OFFSETS:
            j=mapping.get((int(r+dr),int(c+dc)))
            if j is not None and j>idx and valid[j]:
                edge.append((idx,j))
                neighbors[idx].add(j);neighbors[j].add(idx)
    edge=np.asarray(edge,dtype=np.int32)
    must(len(edge)>0,'NO_VALID_NEIGHBOR_EDGES')
    # Physical-distance consistency detects a wrong row/col neighbor definition
    # if full-resolution pixel coords are provided (all existing samples have).
    if {'pxl_row_in_fullres','pxl_col_in_fullres'} <= set(spots.columns):
        px=spots[['pxl_row_in_fullres','pxl_col_in_fullres']].apply(
            pd.to_numeric,errors='raise').to_numpy(dtype=float)
        dist=np.linalg.norm(px[edge[:,0]]-px[edge[:,1]],axis=1)
        median=float(np.median(dist))
        must(np.isfinite(dist).all() and median>0 and
             np.quantile(dist,.95)<1.25*median,
             'VISIUM_HEX_NEIGHBOR_PIXEL_DISTANCE_INCONSISTENT')
    else:median=None
    positive=np.flatnonzero(truth_labels[edge[:,0]]!=truth_labels[edge[:,1]])
    truth_incident=[[] for _ in range(len(spots))]
    for col,edgeidx in enumerate(positive):
        u,v=edge[edgeidx];truth_incident[u].append(col);truth_incident[v].append(col)
    return edge,neighbors,positive,truth_incident,median


def matched_one_to_one(pred_ids, ref_ids, edge, neighbors, truth_incident, tolerance):
    n_pred,n_ref=len(pred_ids),len(ref_ids)
    if n_pred==0 or n_ref==0:return 0,0
    if tolerance==0:
        # Unique edges, exact matching and no duplicates by construction.
        return len(np.intersect1d(pred_ids,ref_ids,assume_unique=True)),0
    ia=[];ja=[];seen_candidates=0
    for pi,edgeid in enumerate(pred_ids):
        u,v=map(int,edge[edgeid])
        vertices={u,v}
        if tolerance==2:
            vertices.update(neighbors[u]);vertices.update(neighbors[v])
        candidates=set()
        for node in vertices:
            candidates.update(truth_incident[node])
        seen_candidates+=len(candidates)
        ia.extend([pi]*len(candidates))
        ja.extend(candidates)
    must(seen_candidates<=max(1,n_pred)*80,
         'MATCHING_GRAPH_DENSE_UNEXPECTED')
    adjacency=csr_matrix((np.ones(len(ia),dtype=np.int8),(ia,ja)),
                         shape=(n_pred,n_ref))
    adjacency.sum_duplicates()
    assignment=maximum_bipartite_matching(adjacency,perm_type='column')
    return int((assignment!=-1).sum()),int(adjacency.nnz)


def metrics(tp,n_ref,n_pred):
    must(0<=tp<=min(n_ref,n_pred),'INVALID_MATCH_COUNT')
    fp=n_pred-tp;fn=n_ref-tp
    precision=tp/n_pred if n_pred else 0.
    recall=tp/n_ref if n_ref else 0.
    f1=2*tp/(n_pred+n_ref) if n_pred+n_ref else 1.
    return tp,fp,fn,precision,recall,f1


def evaluate(zipfile_path,audit_path,output):
    must(file_sha(audit_path)==ORIGINAL_AUDIT_SHA,'FROZEN_AUDIT_SHA_MISMATCH')
    audit=pd.read_csv(audit_path,dtype={'sample':str})
    must(len(audit)==48 and len(set(zip(audit['sample'],audit['condition'])))==48,
         'E3D_FROZEN_48_CONFIG_GRID_BAD')
    # One-to-one matching sanity tests: exact, shared node, adjacent endpoints.
    toy=np.asarray([(0,1),(1,2),(2,3)],dtype=np.int32)
    nbs=[{1},{0,2},{1,3},{2}]
    refs=[[],[0],[0],[]]
    must(matched_one_to_one(np.array([0]),np.array([1]),toy,nbs,refs,0)[0]==0
         and matched_one_to_one(np.array([0]),np.array([1]),toy,nbs,refs,1)[0]==1
         and matched_one_to_one(np.array([0]),np.array([2]),toy,nbs,[[ ],[],[0],[0]],1)[0]==0
         and matched_one_to_one(np.array([0]),np.array([2]),toy,nbs,[[ ],[],[0],[0]],2)[0]==1,
         'MATCHING_SANITY_TEST_FAILED')
    graph={}; rows=[]; reference_provenance={}
    with zipfile.ZipFile(zipfile_path) as z:
        must(z.testzip() is None,'ZIP_CRC_BAD')
        manifest=pd.read_csv(io.BytesIO(z.read('SOURCE_SHA256.csv')))
        must(len(manifest)==72 and list(manifest.columns)==['RelativePath','OriginalPath','SHA256'],
             'EXPORT_72_MANIFEST_INVALID')
        for rec in manifest.itertuples(index=False):
            must(sha(z.read(rec.RelativePath))==rec.SHA256,
                 'SOURCE_SHA_CHANGED '+rec.RelativePath)
        for sample in SAMPLES:
            sf=f'references\\{sample}\\spots_aligned.csv'
            lf=f'references\\{sample}\\manual_layer_annotations.csv'
            spots=read(z,sf);labs=read(z,lf)
            must(spots.barcode.is_unique and labs.spot_name.notna().all(),
                 'SOURCE_BARCODES_INVALID '+sample)
            selected=labs.loc[labs.sample_name==sample,['spot_name','layer']]
            must(selected.spot_name.is_unique and
                 selected.spot_name.isin(spots.barcode).all(),
                 'LABEL_BARCODES_INVALID '+sample)
            y=selected.set_index('spot_name').layer.reindex(spots.barcode).to_numpy()
            edges,neighbors,ref_ids,incidents,pixel_median=make_graph(spots,y)
            graph[sample]=(spots.barcode.to_numpy(),y,edges,neighbors,ref_ids,incidents)
            reference_provenance[sample]={'labels_sha':sha(z.read(lf)),
                'spots_sha':sha(z.read(sf)),'labeled_spots':int(pd.notna(y).sum()),
                'valid_hex_edges':int(len(edges)),
                'reference_boundary_edges':int(len(ref_ids)),
                'median_hex_pixel_distance':pixel_median}
        print('E3B_E3D48_GRAPH_PASS samples=12 hex_offsets=6 file_sha_verified=72/72',flush=True)
        for rec in audit.itertuples(index=False):
            sample=rec.sample;condition=rec.condition
            predpath=f'predictions\\{sample}\\{condition}\\predictions.csv'
            raw=z.read(predpath)
            must(sha(raw)==rec.prediction_sha256,'ORIGINAL_PREDICTION_SHA_BAD '+predpath)
            p=pd.read_csv(io.BytesIO(raw),dtype={'barcode':str})
            codes,y,edges,neighbors,ref_ids,incidents=graph[sample]
            must(np.array_equal(p.barcode.to_numpy(),codes),'BARCODE_ORDER_BAD '+predpath)
            clust=pd.to_numeric(p.cluster,errors='raise').to_numpy()
            must(np.isfinite(clust).all() and np.array_equal(clust,np.floor(clust))
                 and 0<=min(clust) and max(clust)<int(rec.selected_k),
                 'PRED_CLUSTER_NOT_FROZEN '+predpath)
            pred_ids=np.flatnonzero(clust[edges[:,0]]!=clust[edges[:,1]])
            n_ref=len(ref_ids);n_pred=len(pred_ids)
            strict_expected=int(np.intersect1d(ref_ids,pred_ids,assume_unique=True).size)
            previous=-1
            for tol in (0,1,2):
                tp,n_candidates=matched_one_to_one(pred_ids,ref_ids,edges,neighbors,incidents,tol)
                if tol==0:must(tp==strict_expected,'STRICT_INTERSECTION_MISMATCH')
                must(previous<=tp<=min(n_ref,n_pred),'TOLERANCE_MONOTONICITY_BROKEN')
                previous=tp
                a,b,c,pr,rr,f1=metrics(tp,n_ref,n_pred)
                rows.append({'sample':sample,'donor':'D'+str(SAMPLES.index(sample)//4+1),
                    'condition':condition,'feature_dim':CONDS[condition],
                    'selected_k':int(rec.selected_k),
                    'tolerance_linegraph_hops':tol,
                    'valid_spot_edges':int(len(edges)),
                    'ref_boundary_edges':n_ref,'pred_boundary_edges':n_pred,
                    'matched_tp':a,'unmatched_pred_fp':b,'unmatched_ref_fn':c,
                    'precision':pr,'recall':rr,'f1':f1,
                    'candidate_pair_edges':n_candidates,
                    'prediction_sha256':rec.prediction_sha256})
    result=pd.DataFrame(rows).sort_values(['sample','feature_dim','tolerance_linegraph_hops'])
    must(len(result)==144 and result.f1.between(0,1).all(),
         'E3B_PARTIAL_RESULTS_INVALID')
    paired=result.pivot(index=['sample','donor','feature_dim','condition'],
        columns='tolerance_linegraph_hops',values='f1').reset_index()
    paired.columns=['sample','donor','feature_dim','condition','f1_0hop_strict','f1_1hop','f1_2hop']
    paired['f1_1_minus_0']=paired['f1_1hop']-paired['f1_0hop_strict']
    paired['f1_2_minus_0']=paired['f1_2hop']-paired['f1_0hop_strict']
    desc=result.groupby(['feature_dim','tolerance_linegraph_hops'],as_index=False).agg(
        mean_f1=('f1','mean'),sd_slice_f1=('f1','std'),
        mean_precision=('precision','mean'),mean_recall=('recall','mean'),
        n_slices=('sample','nunique'))
    donors=result.groupby(['donor','feature_dim','tolerance_linegraph_hops'],as_index=False).agg(
        mean_f1=('f1','mean'),n_slices=('sample','nunique'))
    must(len(paired)==48 and len(desc)==12 and len(donors)==36
         and np.all(paired['f1_0hop_strict']<=paired['f1_1hop']+1e-12)
         and np.all(paired['f1_1hop']<=paired['f1_2hop']+1e-12),
         'E3B_PARTIAL_AGGREGATE_BAD')
    must(not output.exists(),'OUTPUT_DIR_EXISTS')
    output.mkdir(parents=True)
    outfiles={
        'all_144_tolerance_metric_rows.csv':result,
        'all_48_strict_and_tolerant_f1.csv':paired,
        'twelve_slice_macro_descriptives.csv':desc,
        'donor_scale_tolerance_summary.csv':donors,
    }
    for name,df in outfiles.items():
        df.to_csv(output/name,index=False,float_format='%.16g',lineterminator='\n')
    report={'status':'passed','name':'E3B_POSTHOC_BOUNDARY_E3D48_ONLY_V1',
        'source_zip_sha256':file_sha(zipfile_path),
        'e3d_frozen_audit_sha256':file_sha(audit_path),
        'analysis_scope':'48 E3d K-blind AutoK predictions ONLY; E1E2 1200 not assessed',
        'selection_timing':'posthoc_after_prior_results_reviewed',
        'independent_donors':3,'nested_slices':12,'n_prediction_grids':48,
        'n_metrics':144,'strict_reference':'tolerance=0',
        'offsets_list':OFFSETS,
        'boundary_mask':'Both endpoints have human layer labels',
        'tolerance':'0/1/2 hops in line graph of valid hex edges',
        'matching':'one-to-one maximum-cardinality bipartite matching',
        'no_model_fit':True,'no_chosen_threshold':True,
        'reference_files_sha_and_spatial_graph':reference_provenance,
        'output_shas':{name:file_sha(output/name) for name in outfiles},
        'caveat':'Tolerant matching is an exploratory leniency score, not evidence of exact localization. K varies with scale; no p-values (donors n=3).'}
    (output/'posthoc_boundary_audit_report.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print('E3B_E3D48_PARTIAL_PASS grids=48/48 metrics=144/144 strict+1hop+2hop donor_n=3 refits=0',flush=True)
    print('E3B_E3D48_OUTPUT='+str(output),flush=True)
    print(desc.to_string(index=False),flush=True)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source-zip',type=Path,required=True)
    ap.add_argument('--audit-csv',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    p=ap.parse_args()
    evaluate(p.source_zip,p.audit_csv,p.output)

if __name__=='__main__':
    try: main()
    except Exception as exc:
        print('E3B_E3D48_PARTIAL_ABORTED '+repr(exc),file=sys.stderr,flush=True)
        raise
