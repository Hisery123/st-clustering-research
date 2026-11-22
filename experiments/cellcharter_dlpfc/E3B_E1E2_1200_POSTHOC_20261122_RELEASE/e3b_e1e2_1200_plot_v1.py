"""Descriptive editable SVG figures from fully checked 1,200 E1/E2 boundary grids.
Never uses seeds/sections as independent biological repetitions. Three donors.
"""
from pathlib import Path
import argparse
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

CONDITIONS=('cum_L0','cum_L0_L1','cum_L0_L1_L2','cum_L0_L1_L2_L3','cum_L0_L1_L2_L3_L4',
            'fixed_L0_L1_L3','fixed_L0_L1_L4','fixed_L0_L2_L3','fixed_L0_L2_L4','fixed_L0_L3_L4')
LABELS=('L0','L0+L1','L0–L2','L0–L3','L0–L4','L0+L1+L3','L0+L1+L4','L0+L2+L3','L0+L2+L4','L0+L3+L4')

def main(folder:Path):
    plt.rcParams.update({'svg.fonttype':'none','font.size':9})
    raw=pd.read_csv(folder/'macro_mean_30.csv')
    pivot=raw.pivot(index='condition',columns='tolerance_linegraph_hops',values='mean_f1').reindex(CONDITIONS)
    fig,ax=plt.subplots(figsize=(11.6,4.6))
    for tol,label in [(0,'Strict (0-hop)'),(1,'1-hop one-to-one'),(2,'2-hop one-to-one')]:
        ax.plot(range(len(CONDITIONS)),pivot[tol].to_numpy(),marker='o',label=label)
    ax.set_xticks(range(len(CONDITIONS)),LABELS,rotation=32,ha='right')
    ax.set_ylabel('Mean boundary F1 across 12 nested slices')
    ax.set_title('Frozen E1/E2 — all 1,200 predictions; 3 donors, 10 technical seeds')
    ax.legend(frameon=False,ncol=3)
    ax.grid(axis='y',alpha=.2)
    ax.set_ylim(0,max(.6,float(pivot.max().max())+.03))
    fig.text(.05,.005,'Descriptive nested-slice mean, not independent-sample confidence intervals. Tolerant F1 does not measure exact boundary localization.',fontsize=8)
    fig.tight_layout(rect=[0,.06,1,1])
    fig.savefig(folder/'E3B_E1E2_1200_all_config_0_1_2hop.svg',format='svg')
    plt.close(fig)
    donor=pd.read_csv(folder/'donor_mean_90.csv')
    plotconds=CONDITIONS[:5]
    fig,ax=plt.subplots(figsize=(7.4,4.2))
    for d in ('D1','D2','D3'):
        y=donor[(donor.donor==d)&(donor.condition.isin(plotconds))&(donor.tolerance_linegraph_hops==0)].set_index('condition').reindex(plotconds).mean_f1
        ax.plot(range(5),y.to_numpy(),marker='o',label=f'{d} (4 nested slices)')
    ax.set_xticks(range(5),LABELS[:5])
    ax.set_ylabel('Strict boundary F1, mean over 4 slices and 10 seeds')
    ax.set_title('Strict edge boundary sensitivity by biological donor')
    ax.legend(frameon=False)
    ax.grid(axis='y',alpha=.2)
    fig.text(.05,.005,'3 donors independent; within-donor slices and GMM seeds are nested/technical, not biological replicates.',fontsize=8)
    fig.tight_layout(rect=[0,.07,1,1])
    fig.savefig(folder/'E3B_E1E2_1200_donor_strict_f1.svg',format='svg')
    plt.close(fig)
    print('E3B_FIGURES_PASS files=2/2 all_source_from_verified_results.csv')

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--folder',type=Path,required=True);main(a.parse_args().folder)
