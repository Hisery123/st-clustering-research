from pathlib import Path
import pandas as pd, numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import sys
ROOT=Path(sys.argv[1] if len(sys.argv)>1 else '.')
B=pd.read_csv(ROOT/'B_vs_A_12slices.csv',dtype={'sample':str})
for metric,name in [('ari','B_vs_A_ARI_12slices.svg'),('nmi','B_vs_A_NMI_12slices.svg')]:
 fig,ax=plt.subplots(figsize=(11.2,4.5))
 xx=np.arange(12);ax.bar(xx,B[f'delta_{metric}'].values,width=.75,alpha=.85)
 ax.set_xticks(xx,B['sample'],rotation=45,ha='right');ax.axhline(0,lw=1.2,color='black')
 for v in [3.5,7.5]:ax.axvline(v,color='grey',linestyle='--',lw=1,alpha=.6)
 ax.set_ylabel(f'Δ{metric.upper()} (candidate – control)')
 ax.set_title('Equal-dimension feature swap: L0+L1+L4 vs L0+L1+L2')
 ax.set_ylim((-0.075,0.072) if metric=='ari' else (-0.051,0.054))
 ax.yaxis.set_major_formatter(FormatStrFormatter('%.02f'))
 for x,s in [(1.5,'Donor 1 / K=7'),(5.5,'Donor 2 / K=5'),(9.5,'Donor 3 / K=7')]:
  ax.text(x,1.025,s,ha='center',va='bottom',transform=ax.get_xaxis_transform(),fontsize=10)
 ax.spines[['top','right']].set_visible(False);fig.tight_layout();fig.savefig(ROOT/name,format='svg',bbox_inches='tight');plt.close(fig)
fig,ax=plt.subplots(figsize=(8.4,4.6))
for i,donor in enumerate(['Donor 1','Donor 2','Donor 3']):
 d=B[B.donor==donor];vals=d['delta_ari'].values;xs=i+np.array([-.21,-.07,.07,.21])
 ax.plot(xs,vals,'o',alpha=.75,label='Section-level seed mean' if i==0 else None)
 ax.plot([i-.3,i+.3],[vals.mean()]*2,lw=3,label='Mean across four sections' if i==0 else None)
ax.set_xticks([0,1,2],['Donor 1\nK=7','Donor 2\nK=5','Donor 3\nK=7']);ax.axhline(0,color='black',lw=1)
ax.set_ylabel('ΔARI (L0+L1+L4 minus L0+L1+L2)');ax.set_title('Section effects clustered by donor (descriptive)')
ax.legend(loc='upper right',fontsize=8);ax.spines[['top','right']].set_visible(False)
fig.tight_layout();fig.savefig(ROOT/'B_vs_A_donor_ARI.svg',format='svg',bbox_inches='tight');plt.close(fig)
