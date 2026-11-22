"""E3d DLPFC posthoc evaluation: 12 spatial slices nested in 3 donors.

Read-only posthoc label evaluation from the frozen E3d 48-task prediction ZIP.
This procedure is explicitly POST-RESULTS (2026-11-22), NOT preregistered.
The ZIP is an exported subset of existing Windows source CSVs. The original
AutoK/GMM predictions, selected K, masks and hyperparameters are never changed.

Inputs: --source-zip e3d_posthoc_inputs_20261122.zip, --audit-csv
         E3D_20261122_RELEASE/derived/all_48_autok_audit.csv.
Outputs: new --output directory: 48 original posthoc ARI/NMI, 48 slice-paired
         effects, 12 donor summaries, condition descriptives, audit JSON.
Validation must fully PASS before any metrics are calculated.

Metrics: sklearn adjusted_rand_score, normalized_mutual_info_score with
average_method='arithmetic'; independently cross-check contingency formulas.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
from pathlib import Path
import sys
import zipfile
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from scipy.special import comb
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

SAMPLES = ('151507','151508','151509','151510','151669','151670',
           '151671','151672','151673','151674','151675','151676')
CONDITIONS = {'cum_L0_L1':10,'cum_L0_L1_L2':15,
              'cum_L0_L1_L2_L3':20,'cum_L0_L1_L2_L3_L4':25}
DONOR = {sample: 'D'+str(i//4+1) for i,sample in enumerate(SAMPLES)}
ORIGINAL_AUDIT_SHA = 'f2560ec0cde25a9b09fcec8816ffac9e844faceb562756ec19f951cfe51fc821'
# Independent fixed references taken from E1E2_20261119_RELEASE/derived/all_1200_tasks.csv
# on GitHub before calculating this posthoc analysis. For each sample:
# SHA256 of frozen reference file, SHA256 of frozen spots file, model spots,
# evaluated spots, reference layer categories.
REFERENCE = {
'151507': ('00b0d2599702ddd1506e6bcb41b0c6fa636f290c3355b605f7d34b49034de428','f90fcc5a38959d248da14b614afb96a647d1a7c82ea490f6e2634349b6cf017c',4226,4221,7),
'151508': ('93e4458575b148891efa99ec2f1d233cc623125dfe9d8ea3f260912e1d1174ef','c7008a34887d1af22721d185aa6123570cb11fcd0da9b98235c5f04330f105dc',4384,4381,7),
'151509': ('52d802d5d54e6e1e63b7f2fce086b9bc9d1403b70bc4d6df19edcb2dc5326812','98d8cbda6951a443288274ca5ece16597bf8984a539fe9d09ce0232f64bbc2ea',4789,4788,7),
'151510': ('3f328c4347e75383ecceba209a19ae46b7dfb5494f03766c36e1fc0a60ae2fc1','7ff723d19deae2b15b67ed21c70f02cf76a1ad56312e1bdf17be17a6b31d89d9',4634,4595,7),
'151669': ('c1ea5b4d3fcc43ef7dcb7dd5001c922263013084391035dd1f71c32a13c39afb','c0bf8e032b0643e68c5cd68523e2723d913a2d2d287340e671db13183b9011f3',3661,3636,5),
'151670': ('66b2a1c28ae6cb547213835bc80f1179f1f549efa5551227b86d31e06a288c20','131cf73c209eb3cc56d86e3eac4100a07ca988e4d58a205c46e4edad83a08fdf',3498,3484,5),
'151671': ('de40372c82d30b1b5f97df3ea84c6856923b3d63028a45d9415369ec9e145824','b8ed247edd53976bd0c1030006903a34e4990aebf5d2a73ee9509dd2e8ca11f0',4110,4093,5),
'151672': ('ac92222b88058f2cbd8e2a1f0af1a14d3c1f235426d74d2fa1f87eec76fecbc0','ae213db83e2e56d0c8c393673a66b9c8dd14db63c0f7180d7ba88adcc1950281',4015,3888,5),
'151673': ('271538a67dd85092a797735a391657262f68b72d3470064271303d58e28ce0ed','96bdbff316a547fa14f7c94eb5f1a7f5734ea913f2710e21af4a1d175affc36e',3639,3611,7),
'151674': ('44e3c308f8251974222ab772f74c0f2eca2e2ab17ca9bd3338a5751b440eccbb','a3c95069a93910772766681b6e02bd901e3f27fc56a49799fd7d43cdbd925ba8',3673,3635,7),
'151675': ('a111565746647185093d5ac6d1a3b5c403a02c88b0019428b3a1b58691c1117f','d9ba6d5cee484a9962c2cdb87d87b3dad4293decf6afed88351af1cf2031777c',3592,3566,7),
'151676': ('7dae6c8eb72873e43ac88279b99f63bff483857e651d2641007a7fa53925f864','1236cb9f78d2806c75404d0afcc615e023859bd75c628aec6d8dfaf34cbae89a',3460,3431,7),
}


def require(condition, reason):
    if not bool(condition):
        raise RuntimeError(reason)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def file_sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as fh:
        for b in iter(lambda: fh.read(1<<20), b''):
            h.update(b)
    return h.hexdigest()


def readcsv(z, name):
    return pd.read_csv(io.BytesIO(z.read(name)), dtype=str)


def independent_scores(y_true,y_pred):
    # Independent contingency-table check, avoiding sklearn's metric wrappers.
    a,_=pd.factorize(y_true,sort=False)
    b,_=pd.factorize(y_pred,sort=False)
    n=len(a)
    num_a=int(a.max())+1;num_b=int(b.max())+1
    tab=np.zeros((num_a,num_b),dtype=np.int64)
    np.add.at(tab,(a,b),1)
    rows=tab.sum(axis=1); cols=tab.sum(axis=0)
    sum_pairs=float(comb(tab,2,exact=False).sum())
    sum_rows=float(comb(rows,2,exact=False).sum())
    sum_cols=float(comb(cols,2,exact=False).sum())
    expected=(sum_rows*sum_cols)/comb(n,2,exact=False)
    highest=(sum_rows+sum_cols)/2
    ari=(sum_pairs-expected)/(highest-expected)
    prob=tab/n
    pi=rows/n;pj=cols/n
    mi=float(sum(float(x)*math.log(float(x)/(float(pi[i])*float(pj[j])))
                 for i,j in zip(*np.nonzero(tab)) if (x:=prob[i,j])>0))
    ent_i=float(-sum(v*math.log(v) for v in pi if v>0))
    ent_j=float(-sum(v*math.log(v) for v in pj if v>0))
    nmi=2*mi/(ent_i+ent_j)
    return ari,nmi


def evaluate(source_zip,audit_csv,output):
    require(file_sha(audit_csv)==ORIGINAL_AUDIT_SHA,
            'E3D_FROZEN_AUDIT_CSV_SHA_MISMATCH')
    audit=pd.read_csv(audit_csv,dtype={'sample':str})
    require(audit.shape==(48,22) and set(audit['sample'])==set(SAMPLES)
            and set(audit['condition'])==set(CONDITIONS),'E3D_AUDIT_GRID_OR_COLUMNS_BAD')
    audit_keys=list(zip(audit['sample'],audit['condition']))
    require(len(set(audit_keys))==48 and set(audit_keys)=={
        (s,c) for s in SAMPLES for c in CONDITIONS},'E3D_AUDIT_TASK_MISSING_OR_DUPLICATE')
    all_pred=[]
    truth={}
    provenance={}
    with zipfile.ZipFile(source_zip) as z:
        require(z.testzip() is None,'SOURCE_ZIP_CRC_BAD')
        all_files={n for n in z.namelist() if not n.endswith('\\') and not n.endswith('/')}
        require(len(all_files)==73 and 'SOURCE_SHA256.csv' in all_files,
                'SOURCE_ZIP_EXPECTED_72_INPUTS_PLUS_MANIFEST')
        manifest=pd.read_csv(io.BytesIO(z.read('SOURCE_SHA256.csv')),encoding='utf-8-sig')
        require(list(manifest.columns)==['RelativePath','OriginalPath','SHA256']
                and len(manifest)==72,'EXPORT_MANIFEST_BAD')
        names=manifest['RelativePath'].tolist()
        require(len(set(names))==72 and all_files==set(names)|{'SOURCE_SHA256.csv'},
                'EXPORT_MANIFEST_NAMES_NOT_EXACT')
        for row in manifest.itertuples(index=False):
            path=row.RelativePath
            require(path.startswith(('predictions\\','references\\')) and
                    '..' not in path and len(row.SHA256)==64,'EXPORT_PATH_OR_SHA_BAD')
            require(sha(z.read(path))==row.SHA256.lower(),
                    'SOURCE_INPUT_SHA_MISMATCH '+path)
        print('E3D_POSTHOC_INPUT_SHA_PASS files=72/72',flush=True)
        # Verify ALL source paths, labels and barcode order, before evaluating.
        for sample in SAMPLES:
            p=f'references\\{sample}\\spots_aligned.csv'
            l=f'references\\{sample}\\manual_layer_annotations.csv'
            ref_sha,pos_sha,n_spots,n_labeled,k=REFERENCE[sample]
            require(sha(z.read(p))==pos_sha and sha(z.read(l))==ref_sha,
                    'E1E2_REFERENCE_SHA_MISMATCH '+sample)
            spots=readcsv(z,p)
            labels=readcsv(z,l)
            require('barcode' in spots and spots['barcode'].is_unique and
                    len(spots)==n_spots and spots['barcode'].notna().all() and
                    (spots['in_tissue']=='1').all(),'SPOTS_NOT_FROZEN '+sample)
            require(list(labels.columns)==['sample_name','spot_name','layer'],
                    'REFERENCE_SCHEMA_CHANGED '+sample)
            selected=labels.loc[labels['sample_name']==sample,['spot_name','layer']]
            require(selected['spot_name'].is_unique and
                    selected['spot_name'].notna().all() and
                    selected['spot_name'].isin(spots['barcode']).all() and
                    selected['layer'].notna().all(),'REFERENCE_BARCODES_BAD '+sample)
            y=selected.set_index('spot_name')['layer'].reindex(spots['barcode']).to_numpy()
            valid=pd.notna(y)
            require(int(valid.sum())==n_labeled and len(set(y[valid]))==k,
                    'FROZEN_REFERENCE_MASK_CHANGED '+sample)
            if 'manual_layer' in spots.columns:
                require(np.array_equal(pd.notna(spots['manual_layer']),valid) and
                        np.array_equal(spots['manual_layer'].to_numpy()[valid],y[valid]),
                        'SPOTS_EMBEDDED_REFERENCE_CONFLICT '+sample)
            truth[sample]=(y,valid,spots['barcode'].to_numpy())
            provenance[sample]={'reference_sha256':ref_sha,'positions_sha256':pos_sha,
                                'n_spots':n_spots,'n_labeled':n_labeled,'n_labels':k,
                                'donor':DONOR[sample]}
        require(len(truth)==12,'SOURCE_REFERENCE_INCOMPLETE')
        for row in audit.itertuples(index=False):
            sample,condition=str(row.sample),row.condition
            pred_name=f'predictions\\{sample}\\{condition}\\predictions.csv'
            raw=z.read(pred_name)
            require(sha(raw)==row.prediction_sha256,
                    'FROZEN_E3D_PRED_SHA_MISMATCH '+pred_name)
            require(int(row.dim)==CONDITIONS[condition] and
                    int(row.spots)==REFERENCE[sample][2],
                    'FROZEN_E3D_DIM_OR_SPOTS_CHANGED '+pred_name)
            stability=[float(getattr(row,f'stability_k{k}')) for k in range(2,11)]
            chosen=int(row.selected_k)
            require(all(math.isfinite(x) for x in stability) and
                    chosen==2+int(np.argmax(stability)) and
                    chosen in range(2,11) and
                    bool(row.boundary_hit)==(chosen in (2,10)),
                    'E3D_AUTOK_K_TRACE_MISMATCH '+pred_name)
            prediction=pd.read_csv(io.BytesIO(raw),dtype={'barcode':str})
            require(list(prediction.columns)==['barcode','cluster'] and
                    prediction['barcode'].is_unique and
                    len(prediction)==int(row.spots),
                    'E3D_PRED_CSV_SCHEMA_BAD '+pred_name)
            y,valid,barcodes=truth[sample]
            require(np.array_equal(prediction['barcode'].to_numpy(),barcodes),
                    'E3D_PRED_BARCODE_ORDER_MISMATCH '+pred_name)
            cluster=pd.to_numeric(prediction['cluster'],errors='raise').to_numpy()
            require(np.isfinite(cluster).all() and
                    np.array_equal(cluster,np.floor(cluster)) and
                    int(cluster.min())==0 and int(cluster.max())<chosen,
                    'E3D_PRED_CLUSTER_INVALID '+pred_name)
            all_pred.append((sample,condition,chosen,row.prediction_sha256,
                             cluster.astype(np.int32),int(len(set(cluster))),bool(row.boundary_hit)))
        require(len(all_pred)==48,'E3D_48_PREDICTIONS_MISSING')
        print('E3D_POSTHOC_PREDICTIONS_PASS verified=48/48 labels_not_used_for_selection=True',flush=True)
    # All checks pass. Only now compute scores using the already-aligned truth.
    records=[]
    for sample,condition,chosen,pred_sha,cluster,n_clusters,boundary in all_pred:
        y,valid,_=truth[sample]
        ref=y[valid]; fitted=cluster[valid]
        ari=float(adjusted_rand_score(ref,fitted))
        nmi=float(normalized_mutual_info_score(ref,fitted,average_method='arithmetic'))
        chk_ari,chk_nmi=independent_scores(ref,fitted)
        require(abs(ari-chk_ari)<1e-10 and abs(nmi-chk_nmi)<1e-10,
                'INDEPENDENT_METRIC_RECALC_MISMATCH '+sample+' '+condition)
        records.append({'sample':sample,'donor':DONOR[sample],
            'condition':condition,'feature_dim':CONDITIONS[condition],
            'selected_k':chosen,'actual_clusters_all_spots':n_clusters,
            'boundary_hit':boundary,'model_spots':REFERENCE[sample][2],
            'evaluated_spots':int(valid.sum()),'reference_categories':REFERENCE[sample][4],
            'ari':ari,'nmi':nmi,'prediction_sha256':pred_sha,
            'reference_sha256':REFERENCE[sample][0],
            'spots_sha256':REFERENCE[sample][1]})
    result=pd.DataFrame(records).sort_values(['sample','feature_dim']).reset_index(drop=True)
    require(result.shape==(48,15),'POSTHOC_METRIC_ROWS_OR_COLUMNS_CHANGED')
    require(result.ari.between(-1,1).all() and result.nmi.between(0,1).all()
            and result[['ari','nmi']].notna().all().all(), 'POSTHOC_METRICS_BAD')
    # Four comparisons per sample; descriptive slice paired deltas are NOT 12 donors.
    piv=result.pivot(index='sample',columns='feature_dim',values=['ari','nmi','selected_k'])
    comparisons=((15,10),(20,15),(25,20),(25,15))
    diff=[]
    for sample in SAMPLES:
        for a,b in comparisons:
            diff.append({'sample':sample,'donor':DONOR[sample],
                'comparison':f'{a}D_minus_{b}D','high_dim':a,'low_dim':b,
                'ari_delta':float(piv.loc[sample,('ari',a)]-piv.loc[sample,('ari',b)]),
                'nmi_delta':float(piv.loc[sample,('nmi',a)]-piv.loc[sample,('nmi',b)]),
                'high_selected_k':int(piv.loc[sample,('selected_k',a)]),
                'low_selected_k':int(piv.loc[sample,('selected_k',b)])})
    diff=pd.DataFrame(diff)
    desc=result.groupby('feature_dim',sort=True).agg(
         mean_ari=('ari','mean'),sd_slice_ari=('ari','std'),
         mean_nmi=('nmi','mean'),sd_slice_nmi=('nmi','std'),
         min_ari=('ari','min'),max_ari=('ari','max'),
         min_nmi=('nmi','min'),max_nmi=('nmi','max'),
         boundary_hits=('boundary_hit','sum'),n_slices=('sample','nunique')).reset_index()
    donor=result.groupby(['donor','feature_dim'],sort=True).agg(
         n_slices=('sample','nunique'),mean_ari=('ari','mean'),
         mean_nmi=('nmi','mean'),boundary_hits=('boundary_hit','sum')).reset_index()
    require(len(diff)==48 and len(desc)==4 and len(donor)==12 and
            (donor.n_slices==4).all() and int(result.boundary_hit.sum())==10,
            'POSTHOC_FINAL_AGGREGATE_INVALID')
    require(not output.exists(),'POSTHOC_OUTPUT_ALREADY_EXISTS')
    output.mkdir(parents=True)
    files={'all_48_posthoc_ari_nmi.csv':result,
           'all_48_paired_slice_effects.csv':diff,
           'four_scale_descriptives.csv':desc,
           'three_donor_scale_summary.csv':donor}
    for name,df in files.items():
        df.to_csv(output/name,index=False,float_format='%.16g',lineterminator='\n')
    report={
        'experiment':'E3D_AUTOK_POSTHOC_LABEL_EVALUATION_V1',
        'status':'passed','created_utc':datetime.now(timezone.utc).isoformat(),
        'analysis_timing':'posthoc_after_E3c_E5a_E5b_known',
        'used_labels_only_for_posthoc_metrics':True,'refits':0,'changed_K':False,
        'source_zip_sha256':file_sha(source_zip),
        'source_zip_file':source_zip.name,
        'source_export_manifest_sha256':sha(zipfile.ZipFile(source_zip).read('SOURCE_SHA256.csv')),
        'original_e3d_audit_sha256':file_sha(audit_csv),
        'source_label_provenance':'E1E2_20261119_RELEASE/derived/all_1200_tasks.csv',
        'n_predictions':48,'independent_donors':3,'nested_slices':12,
        'selected_k_boundary_hits':int(result.boundary_hit.sum()),
        'metrics':'ARI adjusted_rand_score, NMI normalized_mutual_info_score average_method=arithmetic',
        'independent_contingency_metric_crosscheck_passed':True,
        'reference_verification':provenance,
        'outputs_sha256':{name:file_sha(output/name) for name in files},
        'inference_limitation':'n=3 independent donors; no p-values; do not treat slices/spots as independent',
        'no_seed_pseudoreplication':True,
        'warning':'AutoK selected K changes with feature depth, so depth contrasts also change K; not a controlled same-K spatial effect.'
    }
    (output/'posthoc_audit_report.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print('E3D_POSTHOC_EVAL_PASS metrics=48/48 refs=12/12 independent_checks=48/48',flush=True)
    print('E3D_POSTHOC_FINAL status=passed files=5 refits=0 independent_donors=3',flush=True)
    print('E3D_POSTHOC_OUTPUT='+str(output),flush=True)
    print(desc.to_string(index=False),flush=True)
    return 0


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source-zip',type=Path,required=True)
    ap.add_argument('--audit-csv',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    return evaluate(args.source_zip,args.audit_csv,args.output)

if __name__=='__main__':
    try: sys.exit(main())
    except Exception as exc:
        print('E3D_POSTHOC_ABORTED '+repr(exc),file=sys.stderr,flush=True)
        raise
