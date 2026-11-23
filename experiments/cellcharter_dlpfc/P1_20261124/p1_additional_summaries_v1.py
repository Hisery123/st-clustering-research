"""P1 (2026-11-24) additional read-only descriptive summaries (T9, T10).

Reads only frozen CSVs already in this repository; no training, refitting or re-prediction.
Both tables are POST-HOC descriptive re-aggregations defined while writing the thesis text.
Usage: python p1_additional_summaries_v1.py <experiments/cellcharter_dlpfc> <out_dir>
"""
import csv, hashlib, os, sys
from collections import defaultdict
from statistics import mean, stdev
R, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
INPUTS, OUTS = [], []
def rd(p):
    p = os.path.join(R, p); INPUTS.append(p)
    with open(p, newline='', encoding='utf-8-sig') as f: return list(csv.DictReader(f))
def wr(name, rows):
    p = os.path.join(OUT, name)
    with open(p, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader()
        for r in rows: w.writerow({k: (round(v, 6) if isinstance(v, float) else v) for k, v in r.items()})
    OUTS.append(p)

# T9: fixed-K grid (K=5..9) -- which K maximises slice-level ARI, relative to the reference layer count
g = rd("E3C_20261120_RELEASE/e3c_slice_K_depth_240groups.csv")
t9 = []
for dim in ['10', '15', '20', '25']:
    by = defaultdict(dict)
    for r in g:
        if r['feature_dim'] == dim: by[r['sample']][int(r['k'])] = (float(r['ari_mean']), int(r['oracle_k']))
    for s in sorted(by):
        ks = by[s]; best = max(ks, key=lambda k: ks[k][0]); ok = next(iter(ks.values()))[1]
        t9.append(dict(feature_dim=int(dim), sample=s, oracle_k=ok, ari_best_k_in_grid=best,
                       ari_at_best_k=ks[best][0], ari_at_oracle_k=ks[ok][0],
                       best_k_below_oracle=best < ok, best_k_equals_oracle=best == ok, posthoc=True))
wr("T9_fixedK_grid_ari_preferred_k.csv", t9)
summ = []
for dim in ['10', '15', '20', '25']:
    for ok in [5, 7]:
        rr = [r for r in t9 if r['feature_dim'] == int(dim) and r['oracle_k'] == ok]
        summ.append(dict(feature_dim=int(dim), oracle_k=ok, n_slices=len(rr),
                         n_best_below_oracle=sum(r['best_k_below_oracle'] for r in rr),
                         n_best_equal_oracle=sum(r['best_k_equals_oracle'] for r in rr),
                         mean_ari_best=mean(r['ari_at_best_k'] for r in rr), mean_ari_oracle=mean(r['ari_at_oracle_k'] for r in rr),
                         note="grid lower bound is K=5, so K<5 is never observable for oracle_k=5 slices", posthoc=True))
wr("T9b_fixedK_grid_preferred_k_summary.csv", summ)

# T10: DLPFC Oracle-K overview of CellCharter configurations and baselines (descriptive; different seed counts)
c = rd("E1E2_20261119_RELEASE/derived/all_120_condition_stats.csv")
cc = defaultdict(list)
for r in c: cc[r['condition']].append((float(r['ari_mean']), float(r['nmi_mean'])))
d = rd("E5A_20261122_RELEASE/derived/method_regime_descriptives.csv")
t10 = []
for cond, lab in [('cum_L0', 'CellCharter L0 5D'), ('cum_L0_L1', 'CellCharter 10D'), ('cum_L0_L1_L2', 'CellCharter A15D'),
                  ('fixed_L0_L1_L4', 'CellCharter B15D'), ('cum_L0_L1_L2_L3', 'CellCharter 20D'), ('cum_L0_L1_L2_L3_L4', 'CellCharter 25D')]:
    v = cc[cond]
    t10.append(dict(method=lab, regime='oracle_k', n_seeds_per_slice=10, ari_12slice_mean=mean(x[0] for x in v), ari_sd_slices=stdev([x[0] for x in v]),
                    nmi_12slice_mean=mean(x[1] for x in v), source='E1E2 all_120_condition_stats'))
for r in d:
    if r['regime'] == 'oracle_k':
        t10.append(dict(method=r['method'], regime='oracle_k', n_seeds_per_slice=3, ari_12slice_mean=float(r['mean_across_12_sections_ari']),
                        ari_sd_slices='', nmi_12slice_mean=float(r['mean_across_12_sections_nmi']), source='E5A method_regime_descriptives'))
wr("T10_dlpfc_oracleK_overview.csv", t10)

# T11: breast-cancer patient-level ARI/NMI per method/config and arm (3-seed means; frozen external protocol)
e = rd("E5B_20261122_RELEASE/derived/patient_three_seed_summary.csv")
t11 = [dict(patient=r['sample'], arm=r['arm'], method=r['method'], config=r['config'], ari_mean=float(r['ari_mean']), ari_seed_sd=float(r['ari_sd']),
            nmi_mean=float(r['nmi_mean']), actual_k=f"{r['actual_k_min']}-{r['actual_k_max']}") for r in e]
t11.sort(key=lambda r: (r['arm'], r['patient'], r['method'], r['config']))
wr("T11_breast_patient_level_all_methods.csv", t11)

def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for ch in iter(lambda: f.read(1 << 20), b''): h.update(ch)
    return h.hexdigest()
with open(os.path.join(OUT, "MANIFEST_SHA256.csv"), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['role', 'path', 'sha256'])
    w.writerow(['script', os.path.basename(__file__), sha(__file__)])
    for p in sorted(set(INPUTS)): w.writerow(['input', os.path.relpath(p, R).replace('\\', '/'), sha(p)])
    for p in OUTS: w.writerow(['output', os.path.basename(p), sha(p)])
print("P1_SUMMARIES_DONE", len(OUTS))
