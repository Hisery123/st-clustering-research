"""Analyze uploaded 1920 non-Oracle-K metrics + archived E1/E2 48-group statistics.

Research provenance: new metrics is user-uploaded CSV sha256 50c624...;
old 48 groups were independently aggregated on 2026-11-20 from GitHub
experiments/cellcharter_dlpfc/E1E2_20261119_RELEASE/derived/all_1200_tasks.csv
blob SHA 1c28d9242572a573bdbae75a98475d714b2b7b8b.
Old group mean and sample SD are encoded to 6 decimal places in
'e3c_oracle_summary_packed.txt'; metadata SHA prefix 16 hex chars in
'e3c_oracle_sha_prefix_reference.txt'. These are derivatives of 480
original Oracle-K rows, not original rows. No per-seed old records are
reconstructed or imputed. To produce a complete 2400-row dataset,
read the original GitHub 1200-row CSV and select original 480 rows.
"""
from pathlib import Path
import csv,collections,statistics,hashlib,math,io,json,zipfile
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

ROOT=Path(__file__).resolve().parent
UP=ROOT/'e3c_newK_metrics_1920.csv'
SAMPLES=['151507','151508','151509','151510','151669','151670','151671','151672','151673','151674','151675','151676']
CONDITIONS=['cum_L0_L1','cum_L0_L1_L2','cum_L0_L1_L2_L3','cum_L0_L1_L2_L3_L4']
DIM=[10,15,20,25]
SEEDS=[22911,7449,25842,10379,6690,26128,21059,22159,32389,12815]
KVAL=[5,6,7,8,9]
DONOR={s: ('Br5292' if i < 4 else 'Br5595' if i < 8 else 'Br8100') for i,s in enumerate(SAMPLES)}
assert hashlib.sha256(UP.read_bytes()).hexdigest()=='50c624a9133d0ad885cd69d53929047f6398729699498771b20c86537bff92f2', 'Uploaded CSV changed after review'

def dump(name, records, fieldnames):
    with (ROOT/name).open('w',encoding='utf-8-sig',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=fieldnames,extrasaction='ignore')
        wr.writeheader();wr.writerows(records)

def mean(values):return statistics.mean(values)
def sd(values):return statistics.stdev(values)

with UP.open(encoding='utf-8-sig',newline='') as f:
    data=list(csv.DictReader(f))
assert len(data)==1920
look=collections.defaultdict(list)
seen=set()
for r in data:
    s,c,k,seed=r['sample'],r['condition'],int(r['k']),int(r['seed'])
    o=5 if s in SAMPLES[4:8] else 7
    assert (s,c,k,seed) not in seen, 'duplicate new key'
    seen.add((s,c,k,seed))
    assert s in SAMPLES and c in CONDITIONS and k in KVAL and seed in SEEDS and k != o
    assert int(r['oracle_k'])==o and int(r['feature_dim'])==DIM[CONDITIONS.index(c)]
    for value in ('ari','nmi'):
        a=float(r[value]);assert math.isfinite(a) and (-1<=a<=1 if value=='ari' else 0<=a<=1)
    assert int(r['n_evaluated'])>0
    assert all(len(r[z])==64 for z in ('source_sha256','feature_sha256','reference_sha256','prediction_sha256'))
    look[(s,c,k)].append(r)
assert len(look)==12*4*4 and all(len(v)==10 for v in look.values())
assert all((s,c,k,seed) in seen for s in SAMPLES for c in CONDITIONS for k in KVAL if k != (5 if s in SAMPLES[4:8] else 7) for seed in SEEDS)

old_ref={}
for line in (ROOT/'e3c_oracle_sha_prefix_reference.txt').read_text().splitlines():
    ss,n,k,src,ref,*feat=line.split()
    assert len(feat)==4
    old_ref[ss]={'n':int(n),'k':int(k),'src':src,'ref':ref,'feat':feat}
assert set(old_ref)==set(SAMPLES)
oldstats={}
for line in (ROOT/'e3c_oracle_summary_packed.txt').read_text().splitlines():
    sid,packed=line.split()
    assert len(packed)==64, sid
    for ci,c in enumerate(CONDITIONS):
        part=packed[ci*16:(ci+1)*16]
        a,b,aa,bb=[int(part[i:i+4],36)/1e6 for i in (0,4,8,12)]
        oldstats[(sid,c,old_ref[sid]['k'])]={'ari_mean':a,'nmi_mean':b,'ari_sd_seed':aa,'nmi_sd_seed':bb}
assert len(oldstats)==48

# Verify cross-source matching of sample, 10-seed, n-labeled, and SHA prefixes.
for s in SAMPLES:
    for ci,c in enumerate(CONDITIONS):
        meta=[r for (ss,cc,k),vv in look.items() if ss==s and cc==c for r in vv]
        assert len(meta)==40,(s,c)
        v=old_ref[s]
        assert all(int(r['n_evaluated'])==v['n'] for r in meta), (s,c,'n_labeled mismatch')
        assert all(int(r['oracle_k'])==v['k'] for r in meta)
        for key,val in [('source_sha256',v['src']),('reference_sha256',v['ref']),('feature_sha256',v['feat'][ci])]:
            assert all(r[key].startswith(val) for r in meta), (s,c,key,'hash prefix mismatch')
        assert set(int(r['seed']) for r in meta)==set(SEEDS)

# combine 192 fresh groups + 48 archived oracle groups (group stats not per-seed old data)
summary=[]
for s in SAMPLES:
    for c,d in zip(CONDITIONS,DIM):
        for k in KVAL:
            oracle=(k==old_ref[s]['k'])
            if oracle:
                x=oldstats[(s,c,k)]
            else:
                rr=look[(s,c,k)]
                x={'ari_mean':mean([float(r['ari']) for r in rr]),
                   'nmi_mean':mean([float(r['nmi']) for r in rr]),
                   'ari_sd_seed':sd([float(r['ari']) for r in rr]),
                   'nmi_sd_seed':sd([float(r['nmi']) for r in rr])}
            summary.append(dict(sample=s,donor=DONOR[s],condition=c,feature_dim=d,k=k,
                                oracle_k=old_ref[s]['k'],is_oracle_reused=oracle,n_seed=10,
                                n_evaluated=old_ref[s]['n'],**x))
assert len(summary)==240
bykey={(r['sample'],r['k'],r['feature_dim']):r for r in summary}

# macro across slices, not pooled seed/spot; subgroup donor means descriptive
kgroup=[]
for k in KVAL:
    for d in DIM:
        rr=[r for r in summary if r['k']==k and r['feature_dim']==d]
        assert len(rr)==12
        kgroup.append(dict(k=k,feature_dim=d,n_slices=12,n_donors=3,
                      ari_slice_macro_mean=mean([r['ari_mean'] for r in rr]),
                      ari_sd_across_slices=sd([r['ari_mean'] for r in rr]),
                      nmi_slice_macro_mean=mean([r['nmi_mean'] for r in rr]),
                      nmi_sd_across_slices=sd([r['nmi_mean'] for r in rr]),
                      n_oracle_slices=sum(r['is_oracle_reused'] for r in rr)))

dgroup=[]
for donor in ['Br5292','Br5595','Br8100']:
    for k in KVAL:
        for d in DIM:
            a=[r for r in summary if r['donor']==donor and r['k']==k and r['feature_dim']==d]
            assert len(a)==4
            dgroup.append(dict(donor=donor,k=k,feature_dim=d,n_slices=4,
                               ari_mean=mean([r['ari_mean'] for r in a]),nmi_mean=mean([r['nmi_mean'] for r in a])))

pairs=[]
for s in SAMPLES:
    for k in KVAL:
        for x,y in [(10,15),(15,20),(20,25),(15,25),(10,25)]:
            a,b=bykey[(s,k,x)],bykey[(s,k,y)]
            pairs.append(dict(sample=s,donor=DONOR[s],k=k,dim_from=x,dim_to=y,
                              delta_ari=b['ari_mean']-a['ari_mean'],delta_nmi=b['nmi_mean']-a['nmi_mean'],
                              use_oracle_reused=(a['is_oracle_reused'] or b['is_oracle_reused'])))

# Best-in-grid is labeled descriptive/post hoc, NOT unsupervised K selection.
rank=[]
for s in SAMPLES:
    for d in DIM:
        r0=[r for r in summary if r['sample']==s and r['feature_dim']==d]
        bestari=max(r0,key=lambda r:r['ari_mean']);bestnmi=max(r0,key=lambda r:r['nmi_mean'])
        rank.append(dict(sample=s,donor=DONOR[s],feature_dim=d,oracle_k=old_ref[s]['k'],
                         posthoc_best_k_by_ari=bestari['k'],best_ari=bestari['ari_mean'],
                         posthoc_best_k_by_nmi=bestnmi['k'],best_nmi=bestnmi['nmi_mean']))

for f,records in [('e3c_slice_K_depth_240groups.csv',summary),('e3c_macro_K_depth_20groups.csv',kgroup),('e3c_donor_K_depth_60groups.csv',dgroup),('e3c_paired_scale_differences_300.csv',pairs),('e3c_posthoc_oracle_comparison_48.csv',rank)]:
    dump(f,records,list(records[0].keys()))
dump('e3c_oracle_48group_archived_mean_sd.csv',[dict(sample=s,condition=c,k=k,n_seed=10,**x) for (s,c,k),x in sorted(oldstats.items())],['sample','condition','k','n_seed','ari_mean','nmi_mean','ari_sd_seed','nmi_sd_seed'])

# academic SVG figures: no CI/p-value; n=3 donors identified
plt.rcParams.update({'svg.fonttype':'none','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(1,2,figsize=(11.8,4.3),layout='constrained')
for ax,metric in zip(axes,['ari','nmi']):
    for d in DIM:
        y=[next(r[f'{metric}_slice_macro_mean'] for r in kgroup if r['k']==k and r['feature_dim']==d) for k in KVAL]
        ax.plot(KVAL,y,marker='o',lw=1.8,label=f'{d}D (L0–L{d//5-1})')
    ax.set_xlabel('Fixed K (predeclared)');ax.set_ylabel(f'{metric.upper()} · 12-slice macro mean')
    ax.set_xticks(KVAL);ax.grid(alpha=.20)
axes[0].legend(fontsize=8,loc='best')
fig.suptitle('E3c | Fixed-K sensitivity of four cumulative neighborhood scales',fontsize=12)
fig.text(.5,-.035,'Descriptive only · 12 sections nested in 3 donors · Oracle-K 480 reused / new-K 1920 fitted · no label-free K selection',ha='center',fontsize=8)
fig.savefig(ROOT/'e3c_Fig1_K_depth_macro_ARI_NMI.svg',bbox_inches='tight');plt.close(fig)

fig,axes=plt.subplots(1,2,figsize=(12,4.3),layout='constrained')
for ax,metric in zip(axes,['ari','nmi']):
    for x,y in [(10,15),(15,20),(20,25)]:
        yy=[mean([a[f'delta_{metric}'] for a in pairs if a['k']==k and a['dim_from']==x and a['dim_to']==y]) for k in KVAL]
        ax.plot(KVAL,yy,marker='o',label=f'{y}D – {x}D')
    ax.axhline(0,color='gray',lw=0.8)
    ax.set_xlabel('Fixed K');ax.set_ylabel(f'Mean paired Δ{metric.upper()} · 12 slices')
    ax.set_xticks(KVAL);ax.grid(alpha=.20)
axes[0].legend(fontsize=9)
fig.suptitle('E3c | Marginal gain when adding one neighborhood block',fontsize=12)
fig.text(.5,-.035,'Contrast within same sample and K; seed-averaged scores · 12 nested sections / 3 donors · descriptive, not inferential',ha='center',fontsize=8)
fig.savefig(ROOT/'e3c_Fig2_depth_increment_effects.svg',bbox_inches='tight');plt.close(fig)

fig,ax=plt.subplots(figsize=(8,6),layout='constrained')
mat=np.array([[next(p['delta_ari'] for p in pairs if p['sample']==s and p['k']==k and p['dim_from']==15 and p['dim_to']==25) for k in KVAL] for s in SAMPLES])
lim=max(abs(mat.min()),abs(mat.max()))
im=ax.imshow(mat,cmap='RdBu_r',vmin=-lim,vmax=lim,aspect='auto')
ax.set_xticks(range(5),KVAL);ax.set_yticks(range(12),SAMPLES);ax.set_xlabel('Fixed K');ax.set_ylabel('DLPFC section (grouped by donor)')
for v in [3.5,7.5]:ax.axhline(v,color='black',lw=1)
for i in range(12):
 for j in range(5):
  val=mat[i,j];ax.text(j,i,f'{val:+.3f}',ha='center',va='center',fontsize=7,color='white' if abs(val)>0.60*lim else 'black')
cbar=fig.colorbar(im,ax=ax,shrink=.85);cbar.set_label('ΔARI: 25D – 15D (10-seed mean)')
ax.set_title('E3c | Cross-section heterogeneity in scale effect')
fig.savefig(ROOT/'e3c_Fig3_scale_effect_slice_K_heatmap.svg',bbox_inches='tight');plt.close(fig)

# text summary for interpretation
report=[]
report.append('E3c K-SENSITIVITY INDEPENDENT CSV ANALYSIS — 2026-11-20')
report.append('Source NEW: user-uploaded CSV '+hashlib.sha256(UP.read_bytes()).hexdigest())
report.append('Source Oracle: GitHub E1/E2 archived all_1200_tasks.csv blob SHA 1c28d9242572a573bdbae75a98475d714b2b7b8b')
report.append('New: 1920 individual task records fully keyed and audited; old: 480 historical Oracle-K tasks aggregated into 48 mean+SD summaries (6-decimal precision).')
report.append('Combined: 240 sample×depth×K groups each has exactly 10 seeds. We do NOT claim to have a full original 2400-row merged file.')
report.append('Old-vs-new cross-source n_labeled / sourceSHA16 / refSHA16 / featureSHA16 / oracleK checks passed for all 48 sample×depth groups.')
report.append('K is predetermined, no label-free AutoK; best K according to ARI/NMI is post hoc descriptive only.')
report.append('Donor independent n=3; 12 sections are nested; seeds computational replicates. No p-values, independent CI or universal improvements claimed.')
report.append('ARI & NMI: sample-macro 12 slices, unweighted across slices; marginal scale comparisons matched within section and fixed K.')
report.append('\nMEAN METRICS BY K AND DEPTH')
for r in kgroup:report.append('K=%d %2dD ARI=%+.6f NMI=%.6f (%d oracle slices)'%(r['k'],r['feature_dim'],r['ari_slice_macro_mean'],r['nmi_slice_macro_mean'],r['n_oracle_slices']))
report.append('\nPAIRED SCALE EFFECTS ACROSS K (12 SLICES EACH)')
for k in KVAL:
 for x,y in [(10,15),(15,20),(20,25),(15,25)]:
  f=[a for a in pairs if a['k']==k and a['dim_from']==x and a['dim_to']==y]
  dar=[a['delta_ari'] for a in f];dnm=[a['delta_nmi'] for a in f]
  report.append(f'K={k} {y}D-{x}D ΔARI mean={mean(dar):+.6f} +/- {sd(dar):.6f} between slices, positives={sum(z>0 for z in dar)}/12; ΔNMI mean={mean(dnm):+.6f}, positives={sum(z>0 for z in dnm)}/12')
report.append('\nDONOR MEAN 25D-15D ΔARI / ΔNMI BY K')
for k in KVAL:
 for donor in ['Br5292','Br5595','Br8100']:
  f=[a for a in pairs if a['k']==k and a['dim_from']==15 and a['dim_to']==25 and a['donor']==donor]
  report.append('K=%d donor=%s ΔARI=%+.6f ΔNMI=%+.6f'%(k,donor,mean([x['delta_ari'] for x in f]),mean([x['delta_nmi'] for x in f])))
report.append('\nPOSTHOC BEST K across 48 sample*depth combos (NOT AutoK)')
report.append('By ARI: '+repr(dict(sorted(collections.Counter(r['posthoc_best_k_by_ari'] for r in rank).items()))))
report.append('By NMI: '+repr(dict(sorted(collections.Counter(r['posthoc_best_k_by_nmi'] for r in rank).items()))))
print('\n'.join(report));(ROOT/'e3c_summary_audit.txt').write_text('\n'.join(report)+'\n',encoding='utf-8')
# ZIP compact analysis artifacts, exclude original source 695KB (user already has it)
files=['e3c_summary_audit.txt','e3c_slice_K_depth_240groups.csv','e3c_macro_K_depth_20groups.csv','e3c_donor_K_depth_60groups.csv','e3c_paired_scale_differences_300.csv','e3c_posthoc_oracle_comparison_48.csv','e3c_oracle_48group_archived_mean_sd.csv','e3c_Fig1_K_depth_macro_ARI_NMI.svg','e3c_Fig2_depth_increment_effects.svg','e3c_Fig3_scale_effect_slice_K_heatmap.svg','build_e3c_review.py','e3c_oracle_summary_packed.txt','e3c_oracle_sha_prefix_reference.txt']
with zipfile.ZipFile(ROOT/'E3c_K敏感性_初步统计与SVG_20261120.zip','w',zipfile.ZIP_DEFLATED) as z:
 for name in files:z.write(ROOT/name,arcname=name)
print('ARTIFACTS',[(name,(ROOT/name).stat().st_size) for name in files]);print('ZIP', (ROOT/'E3c_K敏感性_初步统计与SVG_20261120.zip').stat().st_size)
