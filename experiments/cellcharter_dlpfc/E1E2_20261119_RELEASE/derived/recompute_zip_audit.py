from pathlib import Path
from zipfile import ZipFile
from collections import defaultdict, Counter
import json, hashlib, io, sys
import pandas as pd
import numpy as np
ZIP=Path(sys.argv[1]) if len(sys.argv)>1 else Path('e1e2_12slices_statistics_20261119_095251.zip')
OUT=Path(sys.argv[2]) if len(sys.argv)>2 else Path('e1e2_full_audit')
OUT.mkdir(exist_ok=True)
EXPECTED_SAMPLES=['151507','151508','151509','151510']+[str(i) for i in range(151669,151677)]
EXPECTED_CONDS=['cum_L0','cum_L0_L1','cum_L0_L1_L2','cum_L0_L1_L2_L3','cum_L0_L1_L2_L3_L4','fixed_L0_L1_L3','fixed_L0_L1_L4','fixed_L0_L2_L3','fixed_L0_L2_L4','fixed_L0_L3_L4']
SEEDS=[22911,7449,25842,10379,6690,26128,21059,22159,32389,12815]
SUFFIXES=['all_100_verified_tasks.csv','condition_mean_sd_10seeds.csv','paired_equal15d_by_seed.csv','paired_equal15d_summary.csv','provenance.json']
fail=[]; warnings=[];all_tasks=[];all_sum=[];all_pair=[];all_pair_summary=[];source_info=[]
with ZipFile(ZIP) as z:
 groups=defaultdict(dict)
 for nm in z.namelist():
  p=nm.replace('\\','/').split('/')
  if len(p)==4 and p[-1] in SUFFIXES:
   groups[p[1]][p[-1]]=nm
 if set(groups)!=set(EXPECTED_SAMPLES): fail.append(('sample_groups',sorted(groups)))
 for sample in EXPECTED_SAMPLES:
  g=groups[sample]
  if set(g)!=set(SUFFIXES): fail.append((sample,'missing_files',set(SUFFIXES)-set(g)))
  prov=json.loads(z.read(g['provenance.json']))
  if str(prov['sample'])!=sample: fail.append((sample,'provenance_wrong_sample'))
  if prov['n_verified_cells']!=100: fail.append((sample,'n_verified_cells'))
  if list(prov['conditions_in_frozen_order'])!=EXPECTED_CONDS: fail.append((sample,'condition_order'))
  if prov['seeds_in_frozen_order']!=SEEDS: fail.append((sample,'seeds'))
  if prov['no_gmm_fit_or_scvi_training_performed'] is not True: fail.append((sample,'stat_generation_training'))
  if prov['not_biological_replicates'] is not True: fail.append((sample,'bio_repeats'))
  for suff in SUFFIXES[:-1]:
   b=z.read(g[suff]); got=hashlib.sha256(b).hexdigest(); ref=prov.get('outputs_sha256',{}).get(suff)
   if got!=ref: fail.append((sample,'file_sha256',suff,got,ref))
  t=pd.read_csv(io.BytesIO(z.read(g[SUFFIXES[0]])),dtype={'sample':str});s=pd.read_csv(io.BytesIO(z.read(g[SUFFIXES[1]])),dtype={'sample':str});p=pd.read_csv(io.BytesIO(z.read(g[SUFFIXES[2]])),dtype={'sample':str});q=pd.read_csv(io.BytesIO(z.read(g[SUFFIXES[3]])),dtype={'sample':str})
  for nm,df,rows in [('tasks',t,100),('conditions',s,10),('paired',p,50),('paired_summaries',q,5)]:
   if len(df)!=rows:fail.append((sample,nm,'length',len(df),rows))
   if set(df['sample'])!={sample}:fail.append((sample,nm,'sample_field'))
   if df.isna().any().any():fail.append((sample,nm,'missing_values',df.isna().sum().to_dict()))
  if len(t[['condition','gmm_seed']].drop_duplicates())!=100:fail.append((sample,'duplicate_tasks'))
  if set(t.condition)!=set(EXPECTED_CONDS):fail.append((sample,'wrong_conditions'))
  if set(t.gmm_seed)!=set(SEEDS):fail.append((sample,'wrong_seeds'))
  if sorted(t.groupby('gmm_seed').size())!=[10]*10:fail.append((sample,'seed_count'))
  if sorted(t.groupby('condition').size())!=[10]*10:fail.append((sample,'condition_count'))
  if len(set(t.oracle_k))!=1:fail.append((sample,'nonconstant_k'))
  if int(t.oracle_k.iloc[0])!=(5 if 151669<=int(sample)<=151672 else 7):fail.append((sample,'wrong_k',t.oracle_k.iloc[0]))
  if len(set(t.n_spots))!=1 or len(set(t.n_labeled))!=1:fail.append((sample,'nonconstant_spot_counts'))
  for c in ['ari','nmi']:
   if t[c].isna().any() or not t[c].between(-1.,1.).all():fail.append((sample,c,'metric_range'))
  for f in ['source_sha256','positions_sha256','reference_sha256']:
   if len(set(t[f]))!=1:fail.append((sample,'source_not_constant',f))
  # verify hashes of static metadata same within each section
  if sorted(s.n_gmm_seeds.unique())!=[10]:fail.append((sample,'summary_count'))
  if set(s.condition)!=set(EXPECTED_CONDS):fail.append((sample,'summary_conditions'))
  if sorted(p.candidate.unique())!=sorted(EXPECTED_CONDS[5:]):fail.append((sample,'paired_cands'))
  if set(p.gmm_seed)!=set(SEEDS):fail.append((sample,'paired_seeds'))
  if sorted(p.groupby('candidate').size())!=[10]*5:fail.append((sample,'paired_count'))
  if len(p[['candidate','gmm_seed']].drop_duplicates())!=50:fail.append((sample,'paired_duplicate'))
  if (p.control!='cum_L0_L1_L2').any() or (p.feature_dim!=15).any():fail.append((sample,'paired_reference'))
  for _, row in s.iterrows():
   subset=t[t.condition==row.condition]
   if len(subset)!=10:continue
   for m in ['ari','nmi']:
    checks=[(m+'_mean',subset[m].mean()),(m+'_sd_across_gmm_seeds',subset[m].std(ddof=1)),(m+'_median',subset[m].median()),(m+'_min',subset[m].min()),(m+'_max',subset[m].max())]
    for key,expected in checks:
     if not np.isclose(row[key],expected,rtol=0,atol=1e-10): fail.append((sample,'summary_value_mismatch',row.condition,key,row[key],expected))
   for k in ['feature_dim','n_spots','n_labeled']:
    if row[k]!=subset[k].iloc[0]: fail.append((sample,'summary_other_mismatch',row.condition,k))
  ctrl=t[t.condition=='cum_L0_L1_L2'].set_index('gmm_seed')
  for _,r in p.iterrows():
   a=t[(t.condition==r.candidate)&(t.gmm_seed==r.gmm_seed)]
   if len(a)!=1:continue
   a=a.iloc[0];b=ctrl.loc[r.gmm_seed]
   for m in ['ari','nmi']:
    for label,value in [('control_'+m,b[m]),('candidate_'+m,a[m]),('delta_'+m,a[m]-b[m])]:
     if not np.isclose(r[label],value,rtol=0,atol=1e-10):fail.append((sample,'paired_mismatch',r.candidate,r.gmm_seed,label))
  for _,r in q.iterrows():
   x=p[p.candidate==r.candidate]
   for m in ['ari','nmi']:
    vals=x['delta_'+m];checks=[('delta_'+m+'_positive_seed_count',(vals>0).sum()),('delta_'+m+'_mean',vals.mean()),('delta_'+m+'_sd_across_gmm_seeds',vals.std(ddof=1)),('delta_'+m+'_median',vals.median()),('delta_'+m+'_min',vals.min()),('delta_'+m+'_max',vals.max())]
    for key,expected in checks:
     if not np.isclose(r[key],expected,atol=1e-10,rtol=0):fail.append((sample,'paired_summary_mismatch',r.candidate,key))
  all_tasks.append(t); all_sum.append(s);all_pair.append(p);all_pair_summary.append(q)
  source_info.append({'sample':sample,'oracle_k':t.oracle_k.iloc[0],'spots':t.n_spots.iloc[0],'labeled_spots':t.n_labeled.iloc[0], 'sources':str(t.source.value_counts().to_dict()),'source_sha256':t.source_sha256.iloc[0],'positions_sha256':t.positions_sha256.iloc[0],'reference_sha256':t.reference_sha256.iloc[0]})
T=pd.concat(all_tasks,ignore_index=True); S=pd.concat(all_sum,ignore_index=True);P=pd.concat(all_pair,ignore_index=True);Q=pd.concat(all_pair_summary,ignore_index=True); source_df=pd.DataFrame(source_info)
for name,d in [('all_1200_tasks.csv',T),('all_120_condition_stats.csv',S),('all_600_seed_paired.csv',P),('all_60_paired_stats.csv',Q),('sample_metadata.csv',source_df)]:d.to_csv(OUT/name,index=False,float_format='%.12g')
# per sample: best config by metric, and all controls
summary=[]
for sample in EXPECTED_SAMPLES:
 s=S[S['sample']==sample].set_index('condition')
 row={'sample':sample,'oracle_k':int(source_df.set_index('sample').loc[sample,'oracle_k'])}
 for m in ['ari','nmi']:
  row[f'best_{m}']=s[f'{m}_mean'].idxmax();row[f'best_{m}_value']=s[f'{m}_mean'].max()
  row[f'control15d_{m}']=s.loc['cum_L0_L1_L2',f'{m}_mean']
  for candidate in EXPECTED_CONDS[5:]:row[f'{candidate}_delta_{m}']=s.loc[candidate,f'{m}_mean']-s.loc['cum_L0_L1_L2',f'{m}_mean']
  row[f'full25d_delta_{m}']=s.loc['cum_L0_L1_L2_L3_L4',f'{m}_mean']-s.loc['cum_L0_L1_L2',f'{m}_mean']
 summary.append(row)
D=pd.DataFrame(summary);D.to_csv(OUT/'sample_effects_vs_control.csv',index=False,float_format='%.12g')
# paired effect of five candidates across 12 sections, descriptive only
out=[]
for cand in EXPECTED_CONDS[5:]:
 row={'candidate':cand}
 for m in ['ari','nmi']:
  vals=D[f'{cand}_delta_{m}']
  row[f'{m}_mean_delta_across_12_slices']=vals.mean();row[f'{m}_median_slice_delta']=vals.median();row[f'{m}_positive_slices']=int((vals>0).sum());row[f'{m}_negative_slices']=int((vals<0).sum());row[f'{m}_min_slice_delta']=vals.min();row[f'{m}_max_slice_delta']=vals.max()
  for k in [5,7]:
   vk=D.loc[D.oracle_k==k,f'{cand}_delta_{m}']
   row[f'{m}_k{k}_positive_slices']=int((vk>0).sum());row[f'{m}_k{k}_slice_mean_delta']=vk.mean()
 out.append(row)
agg=pd.DataFrame(out);agg.to_csv(OUT/'candidate_12slice_descriptive.csv',index=False,float_format='%.12g')
# global stability, metrics
print('*** AUDIT ***')
print('FILES',len(source_df)*5,'TASKS',len(T),'CONDITION_STATS',len(S),'SEED_PAIRS',len(P),'PAIR_SUMMARIES',len(Q))
print('HASH_RECALC all provenance outputs SHA256 checked; failures=',len(fail));print('WARNINGS=',len(warnings))
print('SOURCE',T.source.value_counts().to_dict());print('K counts',T.groupby('oracle_k')['sample'].nunique().to_dict())
print('METADATA\n',source_df[['sample','oracle_k','spots','labeled_spots','sources']].to_string(index=False))
print('BEST_BY_SLICE\n',D[['sample','oracle_k','best_ari','best_ari_value','best_nmi','best_nmi_value']].to_string(index=False))
print('CANDIDATES\n',agg.to_string(index=False))
print('B=L0L1L4 A=L0L1L2 delta per sample\n',D[['sample','oracle_k','fixed_L0_L1_L4_delta_ari','fixed_L0_L1_L4_delta_nmi']].to_string(index=False))
print('ERRORS',fail[:30]);print('FAIL_COUNT',len(fail))
(OUT/'audit.json').write_text(json.dumps({'zip':ZIP.name,'sha256':hashlib.sha256(ZIP.read_bytes()).hexdigest(),'n_samples':len(source_df),'n_tasks':len(T),'n_condition_summaries':len(S),'n_seed_pairs':len(P),'n_pair_summaries':len(Q),'number_of_failures':len(fail),'failures':fail},indent=2,ensure_ascii=False,default=str))
if fail:sys.exit(1)
