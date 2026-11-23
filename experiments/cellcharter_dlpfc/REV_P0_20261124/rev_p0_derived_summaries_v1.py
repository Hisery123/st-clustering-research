"""REV_P0 (2026-11-24) read-only descriptive summaries for the CellCharter thesis unit.

Reads ONLY frozen, already-published CSVs of this repository (and, for T7, the
official CSoGroup/cellcharter_analyses result CSVs downloaded read-only).  It does
not train, refit, re-predict, or modify any input.  All outputs are new files in
REV_P0_20261124/derived/.  Every output is a DESCRIPTIVE re-aggregation; items
marked posthoc=True were defined after the corresponding results had been seen.

Usage (repo root = folder containing experiments/):
  python rev_p0_derived_summaries_v1.py <experiments/cellcharter_dlpfc> <official_csv_dir> <out_dir>
"""
import csv, hashlib, sys, os
from collections import defaultdict
from statistics import mean, stdev

R, OFF, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(OUT, exist_ok=True)
INPUTS = []

def rd(path):
    INPUTS.append(path)
    with open(path, newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

def rraw(path):
    INPUTS.append(path)
    with open(path, newline='', encoding='utf-8-sig') as f:
        return list(csv.reader(f))

def wr(name, rows, cols):
    p = os.path.join(OUT, name)
    with open(p, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for r in rows: w.writerow({k: (round(v, 6) if isinstance(v, float) else v) for k, v in r.items()})
    return p

def sd(v): return stdev(v) if len(v) > 1 else float('nan')
def donor(s):
    s = int(s); return 'D1' if s < 151600 else ('D2' if s < 151673 else 'D3')
DEV = {'151507', '151508'}                       # project development slices (B15D nomination)
OFFICIAL_TUNING = {'151507', '151672', '151673'}  # Varrone et al. 2024 tuning set
OUTS = []

# ---------- T1 E1/E2 depth + equal-dim configs, Oracle-K, 10 GMM seeds ----------
c = rd(f"{R}/E1E2_20261119_RELEASE/derived/all_120_condition_stats.csv")
by = defaultdict(list)
for r in c: by[r['condition']].append(r)
ref15 = {r['sample']: float(r['ari_mean']) for r in by['cum_L0_L1_L2']}
t1 = []
for cond, rows in sorted(by.items(), key=lambda x: (int(x[1][0]['feature_dim']), x[0])):
    a = [float(r['ari_mean']) for r in rows]; n = [float(r['nmi_mean']) for r in rows]
    d = defaultdict(list)
    for r in rows: d[donor(r['sample'])].append(float(r['ari_mean']))
    test9 = [float(r['ari_mean']) for r in rows if r['sample'] not in OFFICIAL_TUNING]
    t1.append(dict(condition=cond, feature_blocks=rows[0]['feature_blocks'], feature_dim=int(rows[0]['feature_dim']),
        n_slices=len(rows), ari_slice_macro=mean(a), ari_sd_across_slices=sd(a), ari_min_slice=min(a), ari_max_slice=max(a),
        nmi_slice_macro=mean(n), nmi_sd_across_slices=sd(n),
        ari_D1=mean(d['D1']), ari_D2=mean(d['D2']), ari_D3=mean(d['D3']),
        mean_within_slice_gmm_seed_sd_ari=mean(float(r['ari_sd_across_gmm_seeds']) for r in rows),
        mean_within_slice_gmm_seed_sd_nmi=mean(float(r['nmi_sd_across_gmm_seeds']) for r in rows),
        n_slices_ari_below_A15=sum(float(r['ari_mean']) < ref15[r['sample']] for r in rows),
        ari_macro_9_official_test_slices_posthoc=mean(test9)))
OUTS.append(wr("T1_e1e2_oracleK_depth_uncertainty.csv", t1, list(t1[0].keys())))

# ---------- T2 B15D vs A15D, every aggregation reported separately ----------
b = rd(f"{R}/E1E2_20261119_RELEASE/derived/B_vs_A_12slices.csv")
sp = [r for r in rd(f"{R}/E1E2_20261119_RELEASE/derived/all_600_seed_paired.csv") if r['candidate'] == 'fixed_L0_L1_L4']
eff = rd(f"{R}/E5B_20261122_RELEASE/derived/patient_paired_effects.csv")
def summ(label, vals, posthoc, note):
    return dict(aggregation=label, n_units=len(vals), mean_delta=mean(vals), n_positive=sum(x > 0 for x in vals),
                min_delta=min(vals), max_delta=max(vals), posthoc=posthoc, note=note)
t2 = [
 summ("DLPFC 12 slices, ARI (10-seed mean per slice) [prespecified E1/E2 grid]", [float(r['delta_ari']) for r in b], False, "primary"),
 summ("DLPFC 12 slices, NMI", [float(r['delta_nmi']) for r in b], False, "primary"),
 summ("DLPFC 10 slices excl. dev 151507/151508, ARI", [float(r['delta_ari']) for r in b if r['sample'] not in DEV], True,
      "sensitivity: removes slices on which B was nominated; leaves only 2 D1 slices"),
 summ("DLPFC 10 slices excl. dev 151507/151508, NMI", [float(r['delta_nmi']) for r in b if r['sample'] not in DEV], True, "sensitivity"),
]
for dn in ['Donor 1', 'Donor 2', 'Donor 3']:
    t2.append(summ(f"DLPFC {dn} (4 slices), ARI", [float(r['delta_ari']) for r in b if r['donor'] == dn], False, "donor-level descriptive"))
t2.append(summ("DLPFC 120 slice-x-GMM-seed pairs, ARI", [float(r['delta_ari']) for r in sp], False, "seeds are NOT biological replicates"))
s229 = [r for r in sp if r['gmm_seed'] == '22911']
t2.append(summ("DLPFC seed 22911, 12 slices, ARI", [float(r['delta_ari']) for r in s229], False, "single-seed history"))
t2.append(summ("DLPFC seed 22911, 10 non-dev slices, ARI", [float(r['delta_ari']) for r in s229 if r['sample'] not in DEV], False,
               "matches the earlier 10-section single-seed observation"))
for arm in ['k_blind', 'oracle_k']:
    for met in ['ari_mean', 'nmi_mean']:
        v = [float(r['delta']) for r in eff if r['arm'] == arm and r['metric'] == met and r['comparison'] == 'CC_B15_minus_CC_A15']
        t2.append(summ(f"E5b 6 patients, {arm}, {met.split('_')[0].upper()} (3-seed mean per patient)", v, False, "external cohort, frozen protocol"))
OUTS.append(wr("T2_B15D_minus_A15D_all_aggregations.csv", t2, list(t2[0].keys())))

# ---------- T3 E3b boundary P/R/F1 + boundary-edge counts (posthoc) ----------
rows = rd(f"{R}/E3B_E1E2_1200_POSTHOC_20261122_RELEASE/derived/all_3600_boundary_metric_rows.csv")
cell = defaultdict(lambda: defaultdict(list))
for r in rows:
    cell[(r['condition'], int(r['tolerance_linegraph_hops']))][r['sample']].append(r)
t3 = []
for (cond, hop), slices in sorted(cell.items(), key=lambda x: (x[0][0], x[0][1])):
    per = {}
    for s, rr in slices.items():
        per[s] = {k: mean(float(x[k]) for x in rr) for k in ['f1', 'precision', 'recall', 'predicted_boundary_edges', 'reference_boundary_edges', 'valid_spot_edges']}
    f1 = [v['f1'] for v in per.values()]
    t3.append(dict(condition=cond, tolerance_hops=hop, n_slices=len(per), f1_macro=mean(f1), f1_sd_across_slices=sd(f1),
        precision_macro=mean(v['precision'] for v in per.values()), recall_macro=mean(v['recall'] for v in per.values()),
        pred_boundary_edges_macro=mean(v['predicted_boundary_edges'] for v in per.values()),
        ref_boundary_edges_macro=mean(v['reference_boundary_edges'] for v in per.values()),
        pred_to_ref_boundary_ratio_macro=mean(v['predicted_boundary_edges'] / v['reference_boundary_edges'] for v in per.values()),
        posthoc=True))
OUTS.append(wr("T3_e3b_boundary_precision_recall_counts.csv", t3, list(t3[0].keys())))

# ---------- T4 E3d AutoK selected-K behaviour (K selection itself was frozen; ARI is posthoc) ----------
d = rd(f"{R}/E3D_POSTHOC_20261122_RELEASE/derived/all_48_posthoc_ari_nmi.csv")
t4 = []
for dim in ['10', '15', '20', '25']:
    rr = [r for r in d if r['feature_dim'] == dim]
    ks = [int(r['selected_k']) for r in rr]; refk = [int(r['reference_categories']) for r in rr]
    dd = defaultdict(list)
    for r in rr: dd[r['donor']].append(float(r['ari']))
    t4.append(dict(feature_dim=int(dim), n_slices=len(rr), selected_k_list=';'.join(f"{r['sample']}:{r['selected_k']}" for r in rr),
        n_k_eq_2=sum(k == 2 for k in ks), n_k_eq_10=sum(k == 10 for k in ks), n_boundary_hits=sum(r['boundary_hit'] == 'True' for r in rr),
        n_k_equal_reference_count=sum(k == q for k, q in zip(ks, refk)), mean_abs_k_minus_reference=mean(abs(k - q) for k, q in zip(ks, refk)),
        ari_macro_posthoc=mean(float(r['ari']) for r in rr), ari_sd_across_slices=sd([float(r['ari']) for r in rr]),
        ari_D1=mean(dd['D1']), ari_D2=mean(dd['D2']), ari_D3=mean(dd['D3']),
        autok_stability_repeats_this_study=5, autok_repeats_varrone2024_dlpfc_joint=10))
OUTS.append(wr("T4_e3d_autok_selected_k.csv", t4, list(t4[0].keys())))

# ---------- T5 baseline K-blind rules and search-bound hits ----------
chk = rd(f"{R}/E5A_20261122_RELEASE/derived/all_288_prediction_checks.csv")
desc = {(r['method'], r['regime']): r for r in rd(f"{R}/E5A_20261122_RELEASE/derived/method_regime_descriptives.csv")}
e5 = rd(f"{R}/E5B_20261122_RELEASE/derived/patient_three_seed_summary.csv")
m360 = rd(f"{R}/E5B_20261122_RELEASE/derived/all_360_prediction_metrics.csv")
rule = {'GMM': 'BIC minimum over K=2..10 (scikit-learn GMM on L0 5D)', 'Leiden': 'fixed resolution 1.0 (no K selection)',
        'BANKSY': 'fixed Leiden resolution 1.0 (no K selection)',
        'BayesSpace': 'qTune q=2..10, max mean pseudo-log-likelihood (frozen; differs from official elbow advice)'}
t5 = []
for mth in ['GMM', 'Leiden', 'BANKSY', 'BayesSpace']:
    kb = [r for r in chk if r['method'] == mth and r['regime'] == 'k_blind']
    ext = [r for r in m360 if r['method'] == mth and r['arm'] == 'k_blind']
    def e5m(arm, col): return mean(float(r[col]) for r in e5 if r['method'] == mth and r['arm'] == arm)
    t5.append(dict(method=mth, k_blind_rule=rule[mth],
        dlpfc_kblind_tasks=len(kb), dlpfc_kblind_upper_bound_hits=sum(r['k_blind_upper_bound'] == 'True' for r in kb),
        dlpfc_kblind_actual_k_range=f"{min(int(r['actual_k']) for r in kb)}-{max(int(r['actual_k']) for r in kb)}",
        e5b_kblind_tasks=len(ext), e5b_kblind_actual_k_eq_10=sum(int(r['actual_k']) == 10 for r in ext),
        dlpfc_ari_kblind=float(desc[(mth, 'k_blind')]['mean_across_12_sections_ari']), dlpfc_ari_oracle=float(desc[(mth, 'oracle_k')]['mean_across_12_sections_ari']),
        dlpfc_nmi_kblind=float(desc[(mth, 'k_blind')]['mean_across_12_sections_nmi']), dlpfc_nmi_oracle=float(desc[(mth, 'oracle_k')]['mean_across_12_sections_nmi']),
        e5b_ari_kblind=e5m('k_blind', 'ari_mean'), e5b_ari_oracle=e5m('oracle_k', 'ari_mean'),
        e5b_nmi_kblind=e5m('k_blind', 'nmi_mean'), e5b_nmi_oracle=e5m('oracle_k', 'nmi_mean')))
OUTS.append(wr("T5_baseline_kblind_rules_and_bound_hits.csv", t5, list(t5[0].keys())))

# ---------- T6 E5b patient-level CellCharter A15D context ----------
t6 = []
for r in e5:
    if r['method'] == 'CellCharter' and r['config'] == 'A_L0L1L2_15D':
        t6.append(dict(patient=r['sample'], arm=r['arm'], a15_ari_mean=float(r['ari_mean']), a15_ari_seed_sd=float(r['ari_sd']),
                       a15_nmi_mean=float(r['nmi_mean']), actual_k=f"{r['actual_k_min']}-{r['actual_k_max']}"))
for t in t6:
    for r in eff:
        if r['sample'] == t['patient'] and r['arm'] == t['arm'] and r['metric'] == 'ari_mean':
            t['dARI_' + r['comparison']] = float(r['delta'])
OUTS.append(wr("T6_e5b_patient_level_A15D.csv", t6, list(t6[0].keys())))

# ---------- T7 official CellCharter DLPFC individual benchmark vs this study (descriptive only) ----------
def offcsv(name):
    rows = rraw(os.path.join(OFF, name)); out = {}
    for r in rows[1:]:
        v = [float(x) for x in r[1:] if x not in ('', 'NA')]
        out[r[0].strip('"')] = (mean(v), sd(v), len(v))
    return out
o_cc = offcsv("ARI_CellCharter_hvgs5000_nlatent5_nhoodlayers4_gpu.csv")
o_bs = offcsv("ARI_BayesSpace_hvg1000_pc15_gamma3_nrep5000.csv")
o_st = offcsv("ARI_STAGATE_hvgs5000_hidden_dim1024_nlatent30_gpu.csv")
ours = {r['sample']: r for r in by['cum_L0_L1_L2_L3_L4']}
bs_or = defaultdict(list)
for r in chk:
    if r['method'] == 'BayesSpace' and r['regime'] == 'oracle_k': bs_or[r['sample']].append(float(r['ari_recomputed']))
t7 = []
for s in sorted(o_cc):
    t7.append(dict(slice=s, donor=donor(s), official_role='tuning' if s in OFFICIAL_TUNING else 'test',
        official_cellcharter_L4_mean_ari=o_cc[s][0], official_cellcharter_sd=o_cc[s][1], official_n_reps=o_cc[s][2],
        this_study_25D_mean_ari=float(ours[s]['ari_mean']), this_study_25D_gmm_seed_sd=float(ours[s]['ari_sd_across_gmm_seeds']),
        diff_this_minus_official=float(ours[s]['ari_mean']) - o_cc[s][0],
        official_bayesspace_mean_ari=o_bs[s][0], this_study_bayesspace_oracle_mean_ari=mean(bs_or[s]),
        official_stagate_mean_ari=o_st[s][0]))
for label, keep in [('MACRO_12', lambda r: True), ('MACRO_9_official_test', lambda r: r['official_role'] == 'test'),
                    ('MACRO_3_official_tuning', lambda r: r['official_role'] == 'tuning')]:
    kk = [r for r in t7 if keep(r)]
    t7.append(dict(slice=label, donor='', official_role='', official_n_reps='',
        **{k: mean(r[k] for r in kk) for k in ['official_cellcharter_L4_mean_ari', 'official_cellcharter_sd', 'this_study_25D_mean_ari',
            'this_study_25D_gmm_seed_sd', 'diff_this_minus_official', 'official_bayesspace_mean_ari', 'this_study_bayesspace_oracle_mean_ari', 'official_stagate_mean_ari']}))
cols7 = list(t7[0].keys())
OUTS.append(wr("T7_official_dlpfc_individual_benchmark_vs_this_study.csv", t7, cols7))

# official tuning grid: nhood layers 2/3/4
tune = rraw(os.path.join(OFF, "ARI_CellCharter_tuning.csv"))
tg = defaultdict(list)
for r in tune[1:]:
    smp, hvg, nl, nd = r[0].split('_')
    tg[(hvg, nl, nd)].append((smp, mean(float(x) for x in r[1:] if x)))
t8 = []
for (hvg, nl, nd), v in sorted(tg.items(), key=lambda x: (int(x[0][0]), int(x[0][1]), int(x[0][2]))):
    row = dict(hvg=int(hvg), n_latent=int(nl), nhood_layers=int(nd), mean_ari_over_tuning_slices=mean(x[1] for x in v), n_tuning_slices=len(v))
    for smp, a in v: row['ari_' + smp] = a
    t8.append(row)
OUTS.append(wr("T8_official_cellcharter_tuning_grid.csv", t8, ['hvg', 'n_latent', 'nhood_layers', 'mean_ari_over_tuning_slices', 'n_tuning_slices', 'ari_151507', 'ari_151672', 'ari_151673']))

# ---------- SHA manifest ----------
def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for ch in iter(lambda: f.read(1 << 20), b''): h.update(ch)
    return h.hexdigest()
with open(os.path.join(OUT, "MANIFEST_SHA256.csv"), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['role', 'path', 'sha256'])
    w.writerow(['script', os.path.basename(__file__), sha(__file__)])
    for p in sorted(set(INPUTS)): w.writerow(['input', os.path.relpath(p, os.path.dirname(R)).replace('\\', '/') if p.startswith(R) else 'official/' + os.path.basename(p), sha(p)])
    for p in OUTS: w.writerow(['output', os.path.basename(p), sha(p)])
print("REV_P0_SUMMARIES_DONE", len(OUTS), "tables")
