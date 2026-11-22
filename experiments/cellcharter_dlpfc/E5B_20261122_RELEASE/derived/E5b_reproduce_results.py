"""Reproduce the E5b figures from the three user-supplied CSV files.

Usage: python E5b_reproduce_results.py
Only reads original CSVs in this directory; saves three editable SVG plots.
No external files, model refits, or post-hoc hyperparameter choices.
"""
from __future__ import annotations
import csv
from pathlib import Path
from collections import defaultdict
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DIR = Path(__file__).resolve().parent
with (DIR / 'patient_three_seed_summary.csv').open(encoding='utf-8-sig', newline='') as f:
    patients = list(csv.DictReader(f))
with (DIR / 'patient_paired_effects.csv').open(encoding='utf-8-sig', newline='') as f:
    pairs = list(csv.DictReader(f))

PATIENTS = ('1142243F','1160920F','CID4290','CID4465','CID44971','CID4535')
SCALES = ('L0_5D','L0L1_10D','A_L0L1L2_15D','L0L1L2L3_20D','L0L1L2L3L4_25D')
SCALE_LABELS=('L0 5D','L0+L1 10D','A 15D','20D','25D')
COMPS = ('CC_A15_minus_CC_L0','CC_A15_minus_GMM', 'CC_A15_minus_Leiden',
         'CC_A15_minus_BANKSY', 'CC_A15_minus_BayesSpace')
COMP_LABELS = ('A15 - L0','A15 - GMM','A15 - Leiden','A15 - BANKSY','A15 - BayesSpace')


def get_score(sample, method, config, metric):
    vals = [r for r in patients if r['sample']==sample and r['method']==method
            and r['config']==config and r['arm']=='k_blind']
    assert len(vals)==1
    return float(vals[0][metric+'_mean'])


def differences_plot(metric, outname):
    fig, ax = plt.subplots(figsize=(9.2,5.2), constrained_layout=True)
    # Six points for the six independent patients; tiny vertical offsets are
    # purely visual and do not change the measured value.
    offsets = np.linspace(-.21,.21,6)
    for j, patient in enumerate(PATIENTS):
        xy=[]
        for comp in COMPS:
            r=[z for z in pairs if z['sample']==patient and z['arm']=='k_blind'
               and z['metric']==metric+'_mean' and z['comparison']==comp]
            assert len(r)==1
            xy.append(float(r[0]['delta']))
        yy=np.arange(len(COMPS))[::-1]+offsets[j]
        ax.scatter(xy, yy, label=patient, s=42, zorder=3)
    means=[]
    for comp in COMPS:
        values=[float(z['delta']) for z in pairs if z['arm']=='k_blind'
                and z['metric']==metric+'_mean' and z['comparison']==comp]
        assert len(values)==6
        means.append(np.mean(values))
    ax.scatter(means,np.arange(len(COMPS))[::-1],marker='D',s=65,
               label='Six-patient mean',zorder=4)
    ax.axvline(0,linewidth=1.2,linestyle='--')
    ax.set_yticks(np.arange(len(COMPS))[::-1], COMP_LABELS)
    ax.set_xlabel(f'Patient-paired difference in {metric.upper()} (positive favors A15)')
    ax.set_title('E5b external cohort | K-blind | six independent patients')
    ax.grid(axis='x',alpha=.28)
    ax.legend(loc='center left',bbox_to_anchor=(1.01,.5),fontsize=8)
    ax.text(.01,-.18,'Each point = one patient (mean of 3 technical seeds).'
            ' Diamonds = unweighted mean across 6 patients.',
            transform=ax.transAxes, fontsize=9)
    fig.savefig(DIR / outname,format='svg',bbox_inches='tight')
    plt.close(fig)


def scale_plot():
    fig, ax=plt.subplots(figsize=(8.9,5.2),constrained_layout=True)
    for patient in PATIENTS:
        scores=[get_score(patient,'CellCharter',c,'ari') for c in SCALES]
        ax.plot(np.arange(5),scores,marker='o',label=patient)
    ax.set_xticks(np.arange(5),SCALE_LABELS)
    ax.set_xlabel('Frozen cumulative CellCharter spatial representation')
    ax.set_ylabel('ARI (patient mean of 3 technical seeds)')
    ax.set_title('E5b | K-blind | multi-scale heterogeneity by patient')
    ax.axhline(0,linestyle='--',linewidth=1)
    ax.grid(axis='y',alpha=.25)
    ax.legend(fontsize=8)
    ax.text(.01,-.18,'n=6 independent patients; lines are descriptive, not a pooled spot-level analysis.',
            transform=ax.transAxes, fontsize=9)
    fig.savefig(DIR / 'E5b_Kblind_CumulativeScale_ARI.svg',format='svg',bbox_inches='tight')
    plt.close(fig)

if __name__=='__main__':
    differences_plot('ari','E5b_Kblind_PatientPaired_ARI.svg')
    differences_plot('nmi','E5b_Kblind_PatientPaired_NMI.svg')
    scale_plot()
    for p in ('E5b_Kblind_PatientPaired_ARI.svg','E5b_Kblind_PatientPaired_NMI.svg',
              'E5b_Kblind_CumulativeScale_ARI.svg'):
        print(p, (DIR/p).stat().st_size)
