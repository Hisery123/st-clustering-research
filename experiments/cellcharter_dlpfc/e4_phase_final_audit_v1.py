"""One-time post-run audit of all 12 real-data E4 visualization outputs.

Read only source data, batch status, existing SVG/CSV/manifest. Writes one
separate audit_report.json (and no figures) to a NEW audit subdirectory.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree

import h5py
import numpy as np
import pandas as pd
from scipy import sparse

BASE = Path(r'D:\paper\CellCharter_reproduction')
SESSION = BASE / 'results' / 'e4_spatial_visualization_v1' / 'batch_20261120T080609Z_4732'
SAMPLES = ('151507','151508','151509','151510','151669','151670',
           '151671','151672','151673','151674','151675','151676')
MARKERS = ('MOBP', 'PCP4', 'SNAP25')
EXPECTED_COUNTS = (4226,4384,4789,4634,3661,3498,4110,4015,3639,3673,3592,3460)
PLOT_SCRIPT = BASE / 'e4_spatial_visualization_batch_v1.py'
PLOT_SCRIPT_SHA256 = '78adf071e00ac2da33a8cb98d3254ffc05a787d9047bd39b44785640571d8d3c'


def check(ok, message):
    if not ok:
        raise ValueError(message)


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def decode(x):
    return x.decode('utf-8') if isinstance(x, bytes) else str(x)


def validate_file(path, saved_sha):
    check(path.is_file() and path.stat().st_size > 0, 'MISSING_OR_EMPTY_FILE '+str(path))
    check(sha256(path) == saved_sha, 'SHA_MISMATCH '+str(path))


def expected_filenames(sid):
    return {
        f'{sid}_reference_A_B_spatial.svg',
        f'{sid}_MOBP_PCP4_SNAP25_expression.svg',
        f'{sid}_reference_A_B_confusion.svg',
        f'{sid}_marker_expression_raw_and_log1p10k.csv',
        f'{sid}_reference_vs_A_confusion_counts.csv',
        f'{sid}_reference_vs_B_confusion_counts.csv',
    }


def examine(sid, expected_n, record):
    folder = SESSION / sid
    manifest = load(folder/'e4_sample_manifest.json')
    check(manifest == record, 'BATCH_VS_MANIFEST_INCONSISTENT')
    check(record['status'] == 'completed' and record['sample'] == sid,
          'SAMPLE_NOT_COMPLETED')
    check(record['spots'] == expected_n, 'SPOT_TOTAL_MISMATCH')
    check(record['labeled'] + record['unlabeled'] == expected_n,
          'LABEL_COUNT_MISMATCH')
    names = expected_filenames(sid)
    check(set(record['output_sha256']) == names, 'OUTPUT_NAMELIST_MISMATCH')
    check(set(Path(p).name for p in record['output_files']) == names,
          'OUTPUT_PATHLIST_MISMATCH')
    check(all(Path(p).parent == folder for p in record['output_files']),
          'OUTPUT_PATH_ESCAPE')
    check(set(record['input_sha256']) ==
          {'spots', 'labels', 'h5', 'A_predictions', 'B_predictions'},
          'INPUT_LIST_INCOMPLETE')
    for key, name in record['output_sha256'].items():
        validate_file(folder / key, name)
        if key.endswith('.svg'):
            root = ElementTree.parse(folder / key).getroot()
            check(root.tag.endswith('}svg') or root.tag == 'svg',
                  'SVG_XML_INVALID '+key)
    for key, digest in record['input_sha256'].items():
        validate_file(Path(record['input_files'][key]), digest)

    source = record['input_files']
    spots = pd.read_csv(source['spots'], dtype={'barcode':str})
    annotations = pd.read_csv(source['labels'],
                              dtype={'sample_name':str, 'spot_name':str, 'layer':str})
    a = pd.read_csv(source['A_predictions'], dtype={'barcode':str})
    b = pd.read_csv(source['B_predictions'], dtype={'barcode':str})
    check(len(spots) == expected_n and spots['barcode'].is_unique,
          'SPOTS_BAD')
    check(len(a) == len(b) == expected_n and a['barcode'].is_unique and b['barcode'].is_unique,
          'PREDICTIONS_BAD')
    check(set(spots['barcode']) == set(a['barcode']) == set(b['barcode']),
          'PREDICTION_BARCODES_MISMATCH')
    annotated = annotations.loc[annotations['sample_name']==sid, ['spot_name','layer']]
    check(annotated['spot_name'].is_unique and annotated['layer'].notna().all(),
          'ANNOTATIONS_BAD')
    df = spots[['barcode']].merge(annotated.rename(columns={'spot_name':'barcode'}),
                                on='barcode', how='left', validate='one_to_one')
    check(df['layer'].notna().sum() == record['labeled'], 'ANNOTATED_SPOT_COUNT_WRONG')
    for key, pred in [('A', a), ('B', b)]:
        df = df.merge(pred.rename(columns={'cluster':key}), on='barcode',
                      how='left', validate='one_to_one')
        check(df[key].notna().all() and df[key].nunique()==record[key+'_k'],
              key+'_CLUSTER_MISMATCH')
        df[key] = pd.to_numeric(df[key], errors='raise').astype(int)
        labeled = df.loc[df['layer'].notna()]
        expected_ct = pd.crosstab(labeled['layer'], labeled[key]).reindex(
            index=sorted(labeled['layer'].unique()),
            columns=sorted(df[key].unique()), fill_value=0
        )
        csvfile = folder/f'{sid}_reference_vs_{key}_confusion_counts.csv'
        got_ct = pd.read_csv(csvfile, index_col=0)
        # The saved CSV always has the original integer cluster IDs as column labels.
        got_ct.columns = [int(x) for x in got_ct.columns]
        check(got_ct.equals(expected_ct), 'CONFUSION_MATRIX_INCORRECT_'+key)
        check(int(got_ct.to_numpy().sum()) == record['labeled'],
              'CONFUSION_TOTAL_INCORRECT_'+key)

    marker_path = folder/f'{sid}_marker_expression_raw_and_log1p10k.csv'
    marker_table = pd.read_csv(marker_path, dtype={'barcode':str})
    expected_columns = ['barcode'] + [k for gene in MARKERS
                                     for k in (gene+'_raw_counts', gene+'_log1p_CP10K')]
    check(list(marker_table.columns) == expected_columns and len(marker_table)==expected_n,
          'MARKER_CSV_SHAPE_OR_COLUMNS')
    check(marker_table['barcode'].tolist() == spots['barcode'].tolist(),
          'MARKER_ORDER_MISMATCH')
    with h5py.File(source['h5'], 'r') as f:
        g = f['matrix']
        gene_names = [decode(x) for x in g['features']['name'][()]]
        bc = [decode(x) for x in g['barcodes'][()]]
        check(len(set(bc))==len(bc), 'H5_DUPLICATE_BARCODES')
        col_ix = pd.Index(bc).get_indexer(spots['barcode'])
        check(np.all(col_ix>=0), 'H5_BARCODE_MISSING')
        mat = sparse.csc_matrix((g['data'][()],g['indices'][()],g['indptr'][()]),
                                shape=tuple(int(x) for x in g['shape'][()]))
    totals = np.asarray(mat[:,col_ix].sum(axis=0)).ravel().astype(float)
    check(int((totals==0).sum())==record['spots_zero_total_UMI'],
          'SPOT_LIBRARY_SIZE_ZERO_COUNT_MISMATCH')
    for gene in MARKERS:
        row_ix = [i for i, x in enumerate(gene_names) if x == gene]
        check(len(row_ix)==record['markers'][gene]['feature_rows'],
              gene+'_FEATURE_ROW_COUNT_MISMATCH')
        raw = np.asarray(mat[row_ix,:][:,col_ix].sum(axis=0)).ravel().astype(float)
        norm = np.log1p(10000.0 * raw / np.maximum(totals,1.0))
        got_raw = pd.to_numeric(marker_table[gene+'_raw_counts']).to_numpy(float)
        got_norm = pd.to_numeric(marker_table[gene+'_log1p_CP10K']).to_numpy(float)
        check(np.allclose(got_raw,raw,rtol=1e-7,atol=1e-7),
              gene+'_RAW_EXPRESSION_MISMATCH')
        check(np.allclose(got_norm,norm,rtol=1e-7,atol=1e-7),
              gene+'_NORMALIZED_EXPRESSION_MISMATCH')
        check(int((raw>0).sum()) == record['markers'][gene]['spots_with_nonzero'],
              gene+'_NONZERO_COUNT_MISMATCH')
    return {'sample':sid, 'spots':int(expected_n), 'labeled':record['labeled'],
            'outputs':len(names), 'marker_values_recomputed':True,
            'confusions_recomputed':True}


def main():
    check(sha256(PLOT_SCRIPT) == PLOT_SCRIPT_SHA256, 'E4_PLOT_SCRIPT_CHANGED')
    batch = load(SESSION/'e4_batch_status.json')
    check(batch['protocol']=='E4_SPATIAL_MARKER_REAL_DATA_BATCH_V1',
          'WRONG_E4_BATCH_PROTOCOL')
    check(batch['status']=='completed' and batch['pass_count']==12
          and batch['failure_samples']==[], 'E4_BATCH_NOT_SUCCESSFULLY_COMPLETE')
    check(list(batch['samples']) == list(SAMPLES), 'E4_SAMPLE_ORDER_WRONG')
    checked = []
    issues = []
    for i,(sid,n) in enumerate(zip(SAMPLES, EXPECTED_COUNTS),1):
        try:
            checked.append(examine(sid, n, batch['samples'][sid]))
            print(f'E4_PHASE_AUDIT_PASS {i}/12 sample={sid} svg=3 csv=3', flush=True)
        except Exception as e:
            message = f'{sid} {type(e).__name__}: {e}'
            issues.append(message)
            print(f'E4_PHASE_AUDIT_FAILURE {message}', flush=True)
    report = {
        'protocol':'E4_SPATIAL_MARKER_PHASE_AUDIT_V1',
        'timestamp_utc':datetime.now(timezone.utc).isoformat(),
        'status':'passed' if len(checked)==12 and not issues else 'failed',
        'checked_samples':len(checked), 'expected_samples':12,
        'checked_outputs':sum(x['outputs'] for x in checked),
        'svg_checked':3*len(checked), 'csv_checked':3*len(checked),
        'original_batch_dir':str(SESSION),
        'source_batch_sha256':sha256(SESSION/'e4_batch_status.json'),
        'audit_scope':'file SHA, SVG XML, reference-vs-prediction confusion recomputation, 10x raw and normalized marker value recomputation',
        'limits':'Automatic artifact audit is not a human review of visual legibility or biological interpretation.',
        'issues':issues, 'samples':checked,
    }
    root = BASE/'results'/'e4_spatial_visualization_v1'/'phase_audit_v1'
    out = root/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_'+str(os.getpid()))
    out.mkdir(parents=True,exist_ok=False)
    final=out/'e4_phase_audit_report.json'
    final.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(f"E4_PHASE_AUDIT_FINAL status={report['status']} verified={len(checked)}/12 "
          f"svg={report['svg_checked']}/36 csv={report['csv_checked']}/36 "
          f"errors={len(issues)}",flush=True)
    print('E4_PHASE_AUDIT_REPORT '+str(final),flush=True)
    return 0 if report['status']=='passed' else 2

if __name__=='__main__':
    try:
        sys.exit(main())
    except Exception as e:
        print(f'E4_PHASE_AUDIT_ABORT {type(e).__name__}: {e}', file=sys.stderr,flush=True)
        sys.exit(1)
