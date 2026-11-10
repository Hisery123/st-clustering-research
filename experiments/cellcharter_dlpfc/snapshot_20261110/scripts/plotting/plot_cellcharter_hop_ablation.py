"""Plot DLPFC 151507 CellCharter 0--4-hop exploratory ablation results.

Usage:
 python plot_cellcharter_hop_ablation.py --csv <absolute path to hop_ablation_metrics.csv> --out <output SVG>

Input is the unmodified CSV produced by the unified evaluation script on the researcher's
Windows machine. The figure does not compute significance or select an optimal hop.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter, MultipleLocator

COLS = ['hop','ARI','NMI','boundary_precision','boundary_recall','boundary_f1','spatial_neighbor_agreement']

def plot(csv: Path, out: Path):
    assert csv.is_file(), f'CSV missing: {csv}'
    assert not out.exists(), f'Output exists; refusing overwrite: {out}'
    d = pd.read_csv(csv)
    assert all(col in d.columns for col in COLS), f'Missing required columns: {set(COLS)-set(d.columns)}'
    d=d.sort_values('hop').reset_index(drop=True)
    assert d['hop'].tolist()==[0,1,2,3,4], 'Expected exactly five hops 0-4'
    assert np.isfinite(d[COLS].to_numpy(dtype=float)).all()
    assert (d[COLS[1:]] >= 0).all().all() and (d[COLS[1:]] <= 1).all().all()

    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.titlesize':11,
                         'axes.labelsize':9,'svg.fonttype':'none',
                         'axes.spines.top':False,'axes.spines.right':False})
    fig,axs=plt.subplots(1,3,figsize=(13,4.2),dpi=160,constrained_layout=True)
    x=d['hop'].to_numpy(dtype=int)
    colorA='#285b9f'; colorB='#ba6032'; colorC='#287f6b'
    specs=[
      [('ARI','ARI',colorA,'o'),('NMI','NMI',colorB,'s')],
      [('boundary_precision','Precision',colorA,'o'),('boundary_recall','Recall',colorB,'s'),('boundary_f1','F1',colorC,'^')],
      [('spatial_neighbor_agreement','Same-cluster neighbors',colorA,'o')],
    ]
    titles=['(a) Global label agreement','(b) Reference-boundary detection','(c) Spatial continuity']
    for ax, title, lines in zip(axs,titles,specs):
        for key,name,color,marker in lines:
            y=d[key].to_numpy(float)
            ax.plot(x,y,marker=marker,ms=5.5,lw=1.9,color=color,label=name)
        ax.set_title(title,loc='left',pad=11,fontweight='semibold')
        ax.set_xlabel('Neighborhood aggregation hops')
        ax.set_ylabel('Score')
        ax.set_xticks(x)
        ax.set_xlim(-.25,4.25)
        ax.grid(axis='y',linewidth=.6,alpha=.22)
        ax.legend(loc='best',frameon=False,fontsize=8)
    axs[0].set_ylim(.25,.7)
    axs[1].set_ylim(0,.7)
    axs[2].set_ylim(.4,1.0)
    fig.suptitle('CellCharter v0.3.2 | DLPFC 151507 | Exploratory hop ablation',fontsize=14,fontweight='bold')
    fig.supxlabel('One section, one seed (0); scVI fixed; GMM K=7; feature dimensions: 5, 10, 15, 20, 25',fontsize=8,color='#444444')
    out.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(out,format='svg',bbox_inches='tight')
    plt.close(fig)
    print('CSV_ROWS:',len(d))
    print('SVG_SAVED:',str(out))
    print('SVG_SIZE_BYTES:',out.stat().st_size)
    print('HOP_PLOT_PASS')

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--csv',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    plot(args.csv,args.out)
