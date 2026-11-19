"""Frozen CellCharter DLPFC E3c K-grid sensitivity: safe ONE-GMM task.

By default: READ-ONLY preflight. Explicit --fit: fit exactly one previously
uncomputed non-Oracle-K task and save in a NEW E3c directory.

Frozen grid: 12 samples x 4 cumulative feature configurations x K 5..9 x
10 E1/E2 seeds. Existing Oracle-K E1/E2 cells are AUDITED and REUSED,
never re-trained. K is fixed by the predeclared grid, NOT inferred via AutoK.

The user operates this script on their own Windows machine; this file has
not been executed against the user's real Windows data by ChatGPT.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import importlib.metadata as metadata
import json
import random
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

EXPECTED_CORE_SHA256 = {
    'e1e2_multiscale_gmm_task.py': 'd447dd2cc812616d3589c40f0fd586df3e78d89aec032ad4a82bb433465b958a',
    'e1e2_safe_batch_runner_v2.py': '22ae7b4cd5b8b652f493168fb7b037eb886a466ab1bdba0c734aec912b2f37e4',
    'e1e2_aggregate_multiseed_v2.py': 'e8ef524c1cab24834c2160e1c06df1da94234c9c9ce72457b9d1d07defc9fce5',
}
CONDITIONS = {
    'cum_L0_L1': (0, 1),
    'cum_L0_L1_L2': (0, 1, 2),
    'cum_L0_L1_L2_L3': (0, 1, 2, 3),
    'cum_L0_L1_L2_L3_L4': (0, 1, 2, 3, 4),
}
SEEDS = (22911, 7449, 25842, 10379, 6690, 26128, 21059, 22159, 32389, 12815)
SAMPLES = ('151507', '151508', '151509', '151510',
           '151669', '151670', '151671', '151672',
           '151673', '151674', '151675', '151676')
KS = (5, 6, 7, 8, 9)
PROTOCOL = 'E3C_K_GRID_SENSITIVITY_V1'
CLUSTER_CONFIG = {
    'covariance_type': 'full',
    'init_strategy': 'kmeans',
    'convergence_tolerance': 0.001,
    'covariance_regularization': 1e-6,
    'trainer_params': {
        'accelerator': 'cpu', 'devices': 1,
        'max_epochs': 100, 'enable_progress_bar': False,
    },
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def demand(ok: bool, message: str):
    if not ok:
        raise RuntimeError(message)


def import_script(path: Path, alias: str):
    spec = importlib.util.spec_from_file_location(alias, path)
    demand(spec is not None and spec.loader is not None,
           f'CANNOT_IMPORT: {path}')
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def source_check(here: Path):
    for name, expected in EXPECTED_CORE_SHA256.items():
        path = here / name
        demand(path.is_file(), f'MISSING_FROZEN_SCRIPT: {path}')
        observed = sha256(path)
        demand(observed == expected,
               f'CODE_SHA256_MISMATCH {name}: observed={observed} expected={expected}')
    e1 = import_script(here / 'e1e2_multiscale_gmm_task.py', 'e3c_frozen_e1_task')
    demand(tuple(e1.SEEDS) == SEEDS, 'SEED_GRID_MISMATCH')
    demand(set(e1.SAMPLES) == set(SAMPLES), 'SAMPLE_GRID_MISMATCH')
    demand(all(e1.CONDITIONS.get(c) == blocks for c, blocks in CONDITIONS.items()),
           'FEATURE_BLOCKS_MISMATCH')
    return e1


def destination(e1, sid: str, cond: str, k: int, seed: int) -> Path:
    return (e1.RESULT_ROOT / 'e3c_k_sensitivity_v1' / sid / cond /
            f'k_{k}' / f'seed_{seed}')


def reference(e1, info):
    """Only invoked after a completed fit, or for an existing-results audit."""
    import numpy as np
    import pandas as pd
    manual = pd.read_csv(info['label_path'], dtype={'sample_name': str, 'spot_name': str})
    manual = manual.loc[manual['sample_name'] == info['sid'], ['spot_name', 'layer']]
    demand(len(manual) == info['n_labeled_expected'], 'REFERENCE_COUNT_MISMATCH')
    demand(not manual['spot_name'].duplicated().any(), 'REFERENCE_DUPLICATE_BARCODE')
    demand(manual['layer'].notna().all(), 'REFERENCE_MISSING_LAYER')
    demand(manual['layer'].nunique() == e1.SAMPLES[info['sid']][2],
           'REFERENCE_ORACLE_LAYER_COUNT_MISMATCH')
    demand(manual['spot_name'].isin(info['positions']['barcode']).all(),
           'REFERENCE_BARCODE_OUTSIDE_SAMPLE')
    truth = manual.set_index('spot_name')['layer'].reindex(info['positions']['barcode'])
    valid = truth.notna().to_numpy()
    demand(int(valid.sum()) == info['n_labeled_expected'],
           'REFERENCE_VALID_MASK_COUNT_MISMATCH')
    return truth, valid


def audit_existing(e1, info, k: int, out: Path):
    """Read-only full provenance, predictions and ARI/NMI re-audit."""
    import numpy as np
    import pandas as pd
    from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score
    paths = [out / 'manifest.json', out / 'predictions.csv', out / 'metrics.json']
    demand(all(p.is_file() for p in paths), f'EXISTING_OUTPUT_INCOMPLETE {out}')
    manifest = json.loads(paths[0].read_text(encoding='utf-8'))
    metrics = json.loads(paths[2].read_text(encoding='utf-8'))
    for key, expected in {
        'status': 'completed', 'protocol': PROTOCOL,
        'sample': info['sid'], 'condition': info['condition'],
        'gmm_seed': info['seed'],
        'fixed_k': k, 'oracle_k_reference_only': info['k'],
        'feature_blocks': list(info['blocks']),
        'feature_dim': info['feature_dim'],
        'source_sha256': info['source_sha256'],
        'positions_sha256': info['position_sha256'],
        'reference_sha256': info['labels_sha256'],
        'feature_sha256': info['feature_sha256'],
        'manual_labels_used_for_fit': False,
        'k_selection_policy': 'PREDECLARED_FIXED_GRID_NOT_AUTOK',
        'cluster': CLUSTER_CONFIG,
    }.items():
        demand(manifest.get(key) == expected, f'OUTPUT_MANIFEST_MISMATCH {key}: {out}')
    demand(manifest.get('prediction_sha256') == sha256(paths[1]),
           f'PREDICTION_SHA_MISMATCH {out}')
    demand(manifest.get('e1e2_code_sha256') == EXPECTED_CORE_SHA256,
           f'FROZEN_CODE_PROVENANCE_MISMATCH {out}')
    pred = pd.read_csv(paths[1], dtype={'barcode': str})
    demand(list(pred.columns) == ['barcode', 'cluster'], 'PREDICTION_COLUMNS_MISMATCH')
    demand(len(pred) == info['n'] and pred['barcode'].is_unique,
           'PREDICTION_ROW_OR_DUPLICATE_MISMATCH')
    demand(np.array_equal(pred['barcode'].to_numpy(), info['positions']['barcode'].to_numpy()),
           'PREDICTION_BARCODE_ORDER_MISMATCH')
    clusters = pred['cluster'].to_numpy()
    demand(np.isin(clusters, np.arange(k)).all(), 'PREDICTION_CLUSTER_RANGE_MISMATCH')
    truth, valid = reference(e1, info)
    ari = float(adjusted_rand_score(truth.to_numpy()[valid], clusters[valid]))
    nmi = float(normalized_mutual_info_score(truth.to_numpy()[valid], clusters[valid]))
    demand(metrics.get('n_evaluated') == int(valid.sum()), 'METRIC_N_MISMATCH')
    demand(metrics.get('oracle_k_used') is False, 'METRIC_ORACLE_FLAG_INVALID')
    demand(metrics.get('selection_policy') == 'fixed_predeclared_K_grid_sensitivity',
           'METRIC_K_POLICY_MISMATCH')
    demand(abs(metrics.get('ari', -999) - ari) <= 1e-10, 'METRIC_ARI_MISMATCH')
    demand(abs(metrics.get('nmi', -999) - nmi) <= 1e-10, 'METRIC_NMI_MISMATCH')
    return ari, nmi


def fit_one(e1, info, k: int, out: Path):
    """Fits ONE new non-Oracle-K task. Never modifies E1/E2 outputs."""
    import numpy as np
    import pandas as pd
    import anndata as ad
    import torch
    import cellcharter as cc
    from pytorch_lightning.overrides.distributed import IndexBatchSamplerWrapper
    from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

    demand(k != info['k'], 'ORACLE_K_MUST_BE_REUSED_FROM_E1E2')
    demand(not out.exists(), f'EXISTING_OUTPUT_NOT_OVERWRITTEN: {out}')
    versions = {}
    for pkg in ('cellcharter','torchgmm','torch','numpy','scikit-learn','pytorch-lightning','anndata'):
        try:
            versions[pkg] = metadata.version(pkg)
        except metadata.PackageNotFoundError:
            versions[pkg] = 'NOT_RECORDED'
    manifest = {
        'status': 'running', 'protocol': PROTOCOL,
        'sample': info['sid'], 'condition': info['condition'],
        'gmm_seed': info['seed'], 'fixed_k': k,
        'k_selection_policy': 'PREDECLARED_FIXED_GRID_NOT_AUTOK',
        'oracle_k_reference_only': info['k'],
        'manual_labels_used_for_fit': False,
        'feature_blocks': list(info['blocks']),
        'feature_dim': info['feature_dim'],
        'n_spots': info['n'], 'n_labeled_expected': info['n_labeled_expected'],
        'source_file': info['source_path'], 'source_sha256': info['source_sha256'],
        'positions_sha256': info['position_sha256'],
        'reference_sha256': info['labels_sha256'],
        'feature_sha256': info['feature_sha256'],
        'cluster': CLUSTER_CONFIG,
        'e1e2_code_sha256': EXPECTED_CORE_SHA256,
        'versions': versions, 'python': sys.version,
        'started_utc': datetime.now(timezone.utc).isoformat(),
    }
    out.mkdir(parents=True, exist_ok=False)

    def save():
        (out / 'manifest.json').write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
    save()
    try:
        random.seed(info['seed'])
        np.random.seed(info['seed'])
        torch.manual_seed(info['seed'])
        IndexBatchSamplerWrapper._batch_sampler = property(lambda self: self._sampler)
        adata = ad.AnnData(X=np.zeros((info['n'], 1), dtype=np.float32))
        adata.obs_names = pd.Index(info['positions']['barcode'].to_numpy())
        adata.obsm['X_cellcharter'] = info['selected']
        model = cc.tl.Cluster(
            n_clusters=k, random_state=info['seed'],
            covariance_type=CLUSTER_CONFIG['covariance_type'],
            init_strategy=CLUSTER_CONFIG['init_strategy'],
            convergence_tolerance=CLUSTER_CONFIG['convergence_tolerance'],
            covariance_regularization=CLUSTER_CONFIG['covariance_regularization'],
            trainer_params=CLUSTER_CONFIG['trainer_params'],
        )
        start = time.perf_counter()
        model.fit(adata)
        clusters = np.asarray(model.predict(adata), dtype=np.int64)
        secs = float(time.perf_counter() - start)
        demand(clusters.shape == (info['n'],), 'PREDICTION_LENGTH_MISMATCH')
        demand(np.isin(clusters, np.arange(k)).all(), 'PREDICTION_RANGE_MISMATCH')
        pfile = out / 'predictions.csv'
        pd.DataFrame({'barcode': adata.obs_names.to_numpy(), 'cluster': clusters}).to_csv(pfile, index=False)
        manifest['prediction_sha256'] = sha256(pfile)
        manifest['fit_predict_seconds'] = round(secs, 6)
        manifest['cluster_sizes'] = np.bincount(clusters, minlength=k).tolist()
        save()

        # Open reference labels ONLY AFTER fitting + prediction was persisted.
        truth, valid = reference(e1, info)
        metrics = {
            'ari': float(adjusted_rand_score(truth.to_numpy()[valid], clusters[valid])),
            'nmi': float(normalized_mutual_info_score(truth.to_numpy()[valid], clusters[valid])),
            'n_evaluated': int(valid.sum()),
            'oracle_k_used': False,
            'selection_policy': 'fixed_predeclared_K_grid_sensitivity',
        }
        (out / 'metrics.json').write_text(json.dumps(metrics, indent=2), encoding='utf-8')
        manifest['metrics'] = metrics
        manifest['status'] = 'completed'
        manifest['finished_utc'] = datetime.now(timezone.utc).isoformat()
        save()
        # Independent re-audit of newly produced predictions and metrics.
        ari, nmi = audit_existing(e1, info, k, out)
        print(f'E3C_TASK_COMPLETE sample={info["sid"]} condition={info["condition"]} '
              f'k={k} seed={info["seed"]} ARI={ari:.6f} NMI={nmi:.6f} '
              f'fit_seconds={secs:.3f}', flush=True)
        print(f'RESULT_DIR {out}', flush=True)
    except BaseException as exc:
        manifest['status'] = 'failed'
        manifest['error'] = repr(exc)
        manifest['traceback'] = traceback.format_exc()
        manifest['finished_utc'] = datetime.now(timezone.utc).isoformat()
        save()
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sample', choices=SAMPLES, required=True)
    parser.add_argument('--condition', choices=tuple(CONDITIONS), required=True)
    parser.add_argument('--k', type=int, choices=KS, required=True)
    parser.add_argument('--seed', type=int, choices=SEEDS, required=True)
    parser.add_argument('--fit', action='store_true',
                        help='Explicitly fit ONE new non-Oracle-K task; default is read-only')
    args = parser.parse_args()

    here = Path(__file__).resolve().parent
    e1 = source_check(here)
    # This validates original cached feature hash, barcodes, mask source and condition.
    # It does NOT read layer labels to select K or alter the feature cache.
    info = e1.preflight(args.sample, args.condition, args.seed)
    demand(info['blocks'] == CONDITIONS[args.condition], 'BLOCKS_MISMATCH')
    out = destination(e1, args.sample, args.condition, args.k, args.seed)
    print(f'E3C_PRECHECK_SOURCE_OK sample={args.sample} condition={args.condition} '
          f'feature_dim={info["feature_dim"]} K={args.k} seed={args.seed} '
          f'original_oracle_K={info["k"]} source_sha256={info["source_sha256"]}', flush=True)

    # Reuse the EXISTING E1/E2 prediction. Audit it; do not train or copy it.
    if args.k == info['k']:
        e1v2 = import_script(here / 'e1e2_safe_batch_runner_v2.py', 'e3c_frozen_e1_auditor')
        old_dest = (e1.RESULT_ROOT / 'e1e2_multiscale_gmm_v1' /
                    args.sample / args.condition / f'seed_{args.seed}')
        existing = e1v2.check(args.condition, info, e1, old_dest, info['legacy'])
        demand(existing['status'] in ('NEW_AUDITED', 'LEGACY_AUDITED'),
               f'ORACLE_K_E1E2_NOT_AUDITED: {existing}')
        print(f'E3C_E1E2_REUSED_AUDITED status={existing["status"]} '
              f'ARI={existing["ari"]:.6f} NMI={existing["nmi"]:.6f}', flush=True)
        print('NO_TRAINING_NO_FILES_WRITTEN', flush=True)
        return

    if out.exists():
        ari, nmi = audit_existing(e1, info, args.k, out)
        print(f'E3C_EXISTING_AUDITED sample={args.sample} condition={args.condition} '
              f'K={args.k} seed={args.seed} ARI={ari:.6f} NMI={nmi:.6f}', flush=True)
        print('NO_TRAINING_NO_FILES_WRITTEN', flush=True)
        return

    print(f'E3C_PREFLIGHT_PASS sample={args.sample} condition={args.condition} '
          f'K={args.k} seed={args.seed} NEW_TASK', flush=True)
    if not args.fit:
        print('DRY_RUN_ONLY NO_TRAINING_NO_FILES_WRITTEN', flush=True)
        return
    fit_one(e1, info, args.k, out)


if __name__ == '__main__':
    main()
