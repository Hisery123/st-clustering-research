"""Read-only audit of complete CellCharter E1/E2 multiseed matrix; export statistics.

Usage (Windows, alongside the V2 batch auditor and original GMM task script):
  python e1e2_aggregate_multiseed_v2.py --sample 151509

No training, no change to source results, no p-values. A unique output directory
is created only AFTER every existing prediction and metric passes re-audit.
The ten GMM seeds are technical runs, not ten independent biological samples.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def summary_stats(values: list[float], prefix: str) -> dict:
    if len(values) < 2:
        raise ValueError(f"Need at least 2 observations for sample SD: {prefix}")
    return {
        f"{prefix}_mean": statistics.fmean(values),
        f"{prefix}_sd_across_gmm_seeds": statistics.stdev(values),
        f"{prefix}_median": statistics.median(values),
        f"{prefix}_min": min(values),
        f"{prefix}_max": max(values),
    }


def audit_and_collect(task, batch, sid: str) -> list[dict]:
    rows = []
    for seed in task.SEEDS:
        for condition, blocks in task.CONDITIONS.items():
            info = task.preflight(sid, condition, seed)
            dest = (task.RESULT_ROOT / 'e1e2_multiscale_gmm_v1' / sid /
                    condition / f'seed_{seed}')
            legacy = info['legacy']
            verified = batch.check(condition, info, task, dest, legacy)
            if verified['status'] not in ('NEW_AUDITED', 'LEGACY_AUDITED'):
                raise RuntimeError(f"NOT_AUDITED: sample={sid} seed={seed} {condition} "
                                   f"status={verified['status']}")
            if verified['status'] == 'LEGACY_AUDITED':
                assert legacy is not None and legacy.is_file()
                pfile = legacy
                manifest = json.loads((legacy.parent / 'manifest.json').read_text(encoding='utf-8'))
                historical_name = legacy.name.removesuffix('_predictions.csv')
                fit_seconds = manifest[historical_name].get(
                    'elapsed_fit_predict_seconds',
                    manifest[historical_name].get('elapsed_fit_and_predict_seconds'))
                manifest_file = legacy.parent / 'manifest.json'
            else:
                pfile = dest / 'predictions.csv'
                manifest_file = dest / 'manifest.json'
                manifest = json.loads(manifest_file.read_text(encoding='utf-8'))
                fit_seconds = manifest.get('fit_predict_seconds')
            rows.append({
                'sample': sid,
                'gmm_seed': int(seed),
                'condition': condition,
                'feature_blocks': '+'.join(f'L{b}' for b in blocks),
                'feature_dim': 5 * len(blocks),
                'oracle_k': int(info['k']),
                'n_spots': int(info['n']),
                'n_labeled': int(info['n_labeled_expected']),
                'ari': float(verified['ari']),
                'nmi': float(verified['nmi']),
                'source': verified['status'],
                'fit_predict_seconds_reported': fit_seconds,
                'source_sha256': info['source_sha256'],
                'feature_sha256': info['feature_sha256'],
                'positions_sha256': info['position_sha256'],
                'reference_sha256': info['labels_sha256'],
                'prediction_sha256': sha256_file(pfile),
                'prediction_file': str(pfile),
                'manifest_file': str(manifest_file),
            })
        print(f'AUDIT_SEED_OK sample={sid} seed={seed} verified={len(task.CONDITIONS)}/10', flush=True)
    if len(rows) != len(task.SEEDS) * len(task.CONDITIONS):
        raise RuntimeError(f"WRONG_TOTAL: {len(rows)}")
    return rows


def generate_tables(rows: list[dict], seeds: tuple, conditions: dict) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    full = pd.DataFrame(rows)
    index = {(int(r['gmm_seed']), r['condition']): r for r in rows}
    expected = {(int(seed), name) for seed in seeds for name in conditions}
    if len(index) != len(rows) or set(index) != expected:
        raise RuntimeError('MISSING_OR_DUPLICATE_CELL_IN_MATRIX')
    count_seeds = len(seeds)
    aggregate = []
    for condition in conditions:
        x = [index[(seed, condition)] for seed in seeds]
        item = {
            'sample': x[0]['sample'], 'condition': condition,
            'feature_blocks': x[0]['feature_blocks'],
            'feature_dim': x[0]['feature_dim'],
            'n_gmm_seeds': count_seeds,
            'n_spots': x[0]['n_spots'], 'n_labeled': x[0]['n_labeled'],
        }
        item.update(summary_stats([r['ari'] for r in x], 'ari'))
        item.update(summary_stats([r['nmi'] for r in x], 'nmi'))
        aggregate.append(item)
    aggregate_df = pd.DataFrame(aggregate)

    # Paired seed differences for SAME-DIMENSION 15D comparisons only.
    control = 'cum_L0_L1_L2'
    candidates = [name for name, blocks in conditions.items()
                  if len(blocks) == 3 and name != control]
    paired = []
    paired_summary = []
    for candidate in candidates:
        deltas_ari, deltas_nmi = [], []
        for seed in seeds:
            base = index[(seed, control)]
            trial = index[(seed, candidate)]
            if base['feature_dim'] != trial['feature_dim']:
                raise RuntimeError('PAIRED_CONTRAST_NOT_EQUAL_DIMENSION')
            da = trial['ari'] - base['ari']
            dn = trial['nmi'] - base['nmi']
            deltas_ari.append(da)
            deltas_nmi.append(dn)
            paired.append({
                'sample': base['sample'], 'gmm_seed': int(seed),
                'control': control, 'candidate': candidate,
                'feature_dim': base['feature_dim'],
                'control_ari': base['ari'], 'candidate_ari': trial['ari'], 'delta_ari': da,
                'control_nmi': base['nmi'], 'candidate_nmi': trial['nmi'], 'delta_nmi': dn,
            })
        ps = {'sample': index[(seeds[0], control)]['sample'], 'control': control,
              'candidate': candidate, 'feature_dim': 15, 'n_gmm_seeds': count_seeds,
              'delta_ari_positive_seed_count': sum(v > 0 for v in deltas_ari),
              'delta_nmi_positive_seed_count': sum(v > 0 for v in deltas_nmi)}
        ps.update(summary_stats(deltas_ari, 'delta_ari'))
        ps.update(summary_stats(deltas_nmi, 'delta_nmi'))
        paired_summary.append(ps)
    return full, aggregate_df, pd.DataFrame(paired), pd.DataFrame(paired_summary)


def main() -> None:
    here = Path(__file__).resolve().parent
    runner = here / 'e1e2_safe_batch_runner_v2.py'
    one_task = here / 'e1e2_multiscale_gmm_task.py'
    if not runner.is_file() or not one_task.is_file():
        raise FileNotFoundError('Place this file beside e1e2_safe_batch_runner_v2.py and e1e2_multiscale_gmm_task.py')
    import importlib.util
    spec = importlib.util.spec_from_file_location('e1e2_batch_import', runner)
    if spec is None or spec.loader is None:
        raise RuntimeError('Cannot import e1e2_safe_batch_runner_v2.py')
    batch = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(batch)
    task = batch.load_task()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sample', choices=task.SAMPLES.keys(), required=True)
    args = parser.parse_args()
    sid = args.sample

    # COMPLETELY READ-ONLY THROUGH THIS STAGE. Stop on first mismatch.
    rows = audit_and_collect(task, batch, sid)
    full, summ, paired, psummary = generate_tables(rows, task.SEEDS, task.CONDITIONS)
    print(f'ALL_MATRIX_AUDIT_PASS sample={sid} tasks={len(full)} '
          f'seeds={len(task.SEEDS)} conditions={len(task.CONDITIONS)}', flush=True)
    # Exactly one new folder; NEVER touches original predictions/results.
    output_root = task.RESULT_ROOT / 'e1e2_multiseed_statistics_v2' / sid
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    dest = output_root / f'{stamp}_{uuid.uuid4().hex[:8]}'
    dest.mkdir(parents=True, exist_ok=False)
    files = {
        'all_100_verified_tasks.csv': full,
        'condition_mean_sd_10seeds.csv': summ,
        'paired_equal15d_by_seed.csv': paired,
        'paired_equal15d_summary.csv': psummary,
    }
    for name, df in files.items():
        df.to_csv(dest / name, index=False, float_format='%.12g', encoding='utf-8-sig')
    provenance = {
        'status': 'completed',
        'protocol': 'E1E2_MULTISEED_STATISTICS_V2',
        'generated_utc': datetime.now(timezone.utc).isoformat(),
        'sample': sid,
        'seeds_in_frozen_order': list(task.SEEDS),
        'conditions_in_frozen_order': {name: list(blocks) for name, blocks in task.CONDITIONS.items()},
        'n_verified_cells': len(full),
        'all_task_audits_passed_before_any_output_written': True,
        'no_gmm_fit_or_scvi_training_performed': True,
        'metric_evaluation': 'ARI/NMI against manual layer labels on valid labeled spots',
        'statistics_unit': 'GMM random seed for algorithmic variability within ONE tissue section',
        'historical_manifest_compatibility': 'V2 auditor checks source_file_sha256 and source_feature_sha256 spellings',
        'not_biological_replicates': True,
        'sd': 'sample standard deviation across 10 GMM seed values (ddof=1)',
        'paired_contrasts': 'candidate minus control L0+L1+L2; same 15D, seeds paired',
        'p_values': 'not calculated: 10 seeds are not 10 biological replicates',
        'input_code_sha256': {name: sha256_file(path) for name, path in (
            ('single_task', one_task), ('batch_auditor', runner), ('statistics_script', Path(__file__))
        )},
        'outputs_sha256': {name: sha256_file(dest / name) for name in files},
        'limitations': [
            'One DLPFC section, cannot establish cross-section or across-donor inference.',
            'Number of cumulative neighborhood layers and embedding dimensionality change together.',
            'Oracle-K was defined using reference label category count.',
            'Do not choose a best condition from this development section as an unbiased test result.',
            'Historical seed22911 results are reused, not rerun or treated as extra trials.',
        ],
    }
    (dest / 'provenance.json').write_text(json.dumps(provenance, indent=2, ensure_ascii=False), encoding='utf-8')
    print('CONDITION | MEAN_ARI | SD_ARI | MEAN_NMI | SD_NMI', flush=True)
    for row in summ.to_dict(orient='records'):
        print(f"{row['condition']} | {row['ari_mean']:.6f} | "
              f"{row['ari_sd_across_gmm_seeds']:.6f} | "
              f"{row['nmi_mean']:.6f} | "
              f"{row['nmi_sd_across_gmm_seeds']:.6f}", flush=True)
    print(f'SUMMARY_COMPLETE sample={sid} verified={len(full)} '
          f'conditions={len(summ)} paired_rows={len(paired)}', flush=True)
    print(f'OUTPUT_DIR {dest}', flush=True)
    print('NO_MODEL_TRAINING_OR_ORIGINAL_FILES_CHANGED', flush=True)


if __name__ == '__main__':
    main()
