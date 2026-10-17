"""Reproducible spatial-network and SAR-impact figures in desktop/mobile layouts."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
LOCAL_DEPS = ROOT / '.qa' / 'plot-deps'
if LOCAL_DEPS.is_dir():
    sys.path.insert(0, str(LOCAL_DEPS))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch
from matplotlib.colors import ListedColormap
import numpy as np

PAPER, INK, BRONZE, MUTED, LINE = '#f6f2e9', '#182b42', '#86623f', '#626d77', '#dcd6ca'
plt.rcParams.update({
    'font.family': ['DejaVu Sans', 'Arial', 'sans-serif'], 'font.size': 15,
    'axes.titlesize': 17, 'axes.labelsize': 15, 'text.color': INK,
    'axes.labelcolor': INK, 'xtick.color': MUTED, 'ytick.color': MUTED,
    'axes.edgecolor': LINE, 'axes.spines.top': False, 'axes.spines.right': False,
    'figure.facecolor': PAPER, 'axes.facecolor': PAPER,
    'svg.fonttype': 'none', 'svg.hashsalt': 'spatial-editorial',
})
OUT, QA = Path(__file__).resolve().parent, ROOT / '.qa'
QA.mkdir(exist_ok=True)
W = np.array([[0,.5,.5,0],[.5,0,0,.5],[.5,0,0,.5],[0,.5,.5,0]])
labels = ['A', 'B', 'C', 'D']
assert np.allclose(W.sum(axis=1), 1) and np.allclose(np.diag(W), 0)
assert np.isclose((W @ W)[0,0], .5)
rho, beta = .4, 1.
S = np.linalg.solve(np.eye(4) - rho * W, beta * np.eye(4))
effects = S[:,0]
assert np.allclose(effects, [23/21,5/21,5/21,2/21])
assert np.isclose(np.trace(S)/4, 23/21)
assert np.isclose(S.sum()/4, 5/3)
assert np.isclose(S.sum()/4 - np.trace(S)/4, 4/7)

def save(fig, stem):
    path = OUT / (stem + '.svg')
    fig.savefig(path, metadata={'Date': None}, bbox_inches='tight', pad_inches=.18)
    path.write_text('\n'.join(line.rstrip() for line in path.read_text(encoding='utf-8').splitlines())+'\n', encoding='utf-8')
    fig.savefig(QA / (stem + '.png'), dpi=150, bbox_inches='tight', pad_inches=.18)
    plt.close(fig)

def network(ax):
    positions = [(0,1),(1,1),(0,0),(1,0)]
    for i,j in [(0,1),(0,2),(1,3),(2,3)]:
        ax.add_patch(FancyArrowPatch(positions[i],positions[j],arrowstyle='<->',
                     shrinkA=26,shrinkB=26,mutation_scale=17,color=BRONZE,linewidth=1.7))
    for name,pos in zip(labels,positions):
        ax.add_patch(Circle(pos,.15,facecolor=PAPER,edgecolor=INK,linewidth=1.4))
        ax.text(*pos,name,ha='center',va='center',fontsize=21,color=INK)
    ax.set(xlim=(-.3,1.3),ylim=(-.3,1.3),aspect='equal')
    ax.axis('off')
    ax.set_title('Neighbour network', pad=18, loc='left')
    ax.text(.5,-.25,'Each arrow has weight 0.5',ha='center',va='top',fontsize=14,color=MUTED)

def matrix(ax):
    ax.imshow(W,cmap=ListedColormap([PAPER,INK]),vmin=0,vmax=.5)
    ax.set(xticks=range(4),yticks=range(4),xticklabels=labels,yticklabels=labels)
    ax.xaxis.tick_top()
    ax.tick_params(length=0,pad=9)
    for i in range(4):
        for j in range(4):
            ax.text(j,i,'0.5' if W[i,j] else '0',ha='center',va='center',
                    color=PAPER if W[i,j] else MUTED,fontsize=16)
    for v in np.arange(-.5,4,1):
        ax.axhline(v,color=LINE,lw=1)
        ax.axvline(v,color=LINE,lw=1)
    ax.set_xlabel('Source location j',labelpad=12)
    ax.set_ylabel('Receiving location i',labelpad=12)
    ax.set_title('Weights matrix W',loc='left',pad=22)
    for spine in ax.spines.values():
        spine.set_visible(False)

for mobile in (False,True):
    suffix = '-mobile' if mobile else ''
    if mobile:
        fig,(ax1,ax2)=plt.subplots(2,1,figsize=(5,9.3),layout='constrained',gridspec_kw={'height_ratios':[1,1.15]})
    else:
        fig,(ax1,ax2)=plt.subplots(1,2,figsize=(10,4.8),layout='constrained',gridspec_kw={'width_ratios':[1,1.12]})
    network(ax1)
    matrix(ax2)
    save(fig,'econometrics-spatial-weights'+suffix)

    fig,ax=plt.subplots(figsize=(5,5.5) if mobile else (10,4.9),layout='constrained')
    y=np.arange(4)
    base=np.array([1.,0,0,0])
    ax.barh(y,base,height=.52,color=INK,label='Initial local effect',zorder=3)
    ax.barh(y,effects-base,left=base,height=.52,color=BRONZE,label='Spatial propagation',zorder=3)
    for yi,value in zip(y,effects):
        ax.text(value+.025,yi,f'+{value:.3f}',ha='left',va='center',fontsize=16,color=INK)
    ax.set(yticks=y,yticklabels=['A, origin','B, neighbour','C, neighbour','D, two steps'],
           xlim=(0,1.39),xticks=[0,.5,1],xlabel='Change in outcome')
    ax.invert_yaxis()
    ax.tick_params(axis='y',length=0,pad=10)
    ax.grid(axis='x',color=LINE,lw=.8,zorder=0)
    ax.spines['left'].set_visible(False)
    ax.set_title('Response to a change in A',loc='left',pad=55 if mobile else 42)
    ax.legend(loc='lower left',bbox_to_anchor=(0,1.02),ncol=1 if mobile else 2,
              frameon=False,fontsize=13,handlelength=1.2,columnspacing=1.3,borderaxespad=0)
    save(fig,'econometrics-spatial-spillovers'+suffix)
