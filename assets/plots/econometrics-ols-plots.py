"""Reproduce OLS loss contours and an orthogonal-projection schematic."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
LOCAL_DEPS = ROOT / '.qa' / 'plot-deps'
if LOCAL_DEPS.is_dir():
    sys.path.insert(0, str(LOCAL_DEPS))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import numpy as np

OUT, QA = Path(__file__).resolve().parent, ROOT / '.qa'
QA.mkdir(exist_ok=True)
PAPER, INK, BRONZE, MUTED, LINE = '#f6f2e9', '#182b42', '#86623f', '#626d77', '#dcd6ca'
plt.rcParams.update({
    'font.family': ['DejaVu Sans', 'Arial', 'sans-serif'], 'font.size': 15,
    'text.color': INK, 'axes.labelcolor': INK, 'xtick.color': MUTED, 'ytick.color': MUTED,
    'axes.edgecolor': LINE, 'axes.spines.top': False, 'axes.spines.right': False,
    'figure.facecolor': PAPER, 'axes.facecolor': PAPER,
    'svg.fonttype': 'none', 'svg.hashsalt': 'econometrics-ols-editorial',
})


def finish(fig, stem, mobile):
    stem += '-mobile' if mobile else ''
    p = OUT/(stem+'.svg')
    fig.savefig(p,metadata={'Date':None},bbox_inches='tight',pad_inches=.18)
    p.write_text('\n'.join(line.rstrip() for line in p.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')
    fig.savefig(QA/(stem+'.png'),dpi=150,bbox_inches='tight',pad_inches=.18)
    plt.close(fig)


x = np.array([1.,2.,3.,4.])
y = np.array([2.,3.,5.,4.])
X = np.column_stack([np.ones(len(x)),x])
beta = np.linalg.lstsq(X,y,rcond=None)[0]
residual = y-X@beta
rss = residual@residual
assert np.allclose(beta,[1.5,.8]) and np.isclose(rss,1.8)
assert np.allclose(X.T@residual,0)
b0,b1 = np.meshgrid(np.linspace(-4,7,400),np.linspace(-1.5,3.1,400))
loss = np.sum((y[:,None,None]-b0[None,:,:]-x[:,None,None]*b1[None,:,:])**2,axis=0)
assert np.all(np.linalg.eigvalsh(2*X.T@X)>0)

fitted_vector = np.array([3.,0.])
residual_vector = np.array([0.,2.])
observed_vector = fitted_vector+residual_vector
assert np.isclose(fitted_vector@residual_vector,0)
assert np.isclose(observed_vector@observed_vector,fitted_vector@fitted_vector+residual_vector@residual_vector)

for mobile in (False,True):
    plt.rcParams.update({'font.size':17 if mobile else 15,'axes.labelsize':16 if mobile else 15})
    fig,ax = plt.subplots(figsize=(5.6,5.0) if mobile else (8.8,4.8),layout='constrained')
    contours = ax.contour(b0,b1,loss,levels=[3,6,12,24],colors=INK,linewidths=1.15)
    ax.clabel(contours,fmt='%g',fontsize=14 if mobile else 13,inline_spacing=7)
    ax.scatter(*beta,color=BRONZE,s=48,zorder=5)
    ax.annotate('OLS minimum\n(1.5, 0.8)',beta,xytext=(3.4,1.9),fontsize=15 if mobile else 14,
                color=BRONZE,ha='center',arrowprops={'arrowstyle':'-','color':BRONZE,'lw':1.2},
                bbox={'facecolor':PAPER,'edgecolor':'none','pad':3})
    ax.set(xlabel='Intercept b₀',ylabel='Slope b₁',xlim=(-4,7),ylim=(-1.5,3.1))
    ax.grid(color=LINE,lw=.7,zorder=0)
    finish(fig,'econometrics-ols-loss',mobile)

    fig,ax = plt.subplots(figsize=(5.6,4.5) if mobile else (8.8,4.8),layout='constrained')
    ax.axhspan(-.07,.07,color=LINE,alpha=.6,zorder=0)
    ax.plot([-.4,4.7],[0,0],color=MUTED,lw=1,zorder=1)
    for start,end,colour in [(np.zeros(2),observed_vector,INK),
                              (np.zeros(2),fitted_vector,INK),
                              (fitted_vector,observed_vector,BRONZE)]:
        ax.add_patch(FancyArrowPatch(start,end,arrowstyle='->',mutation_scale=17,
                                    color=colour,lw=2,shrinkA=0,shrinkB=0,zorder=3))
    ax.plot([2.8,2.8,3],[0,.2,.2],color=BRONZE,lw=1.2,zorder=4)
    ax.scatter([0],[0],color=INK,s=20,zorder=5)
    ax.text(-.09,-.13,'0',ha='right',va='top',fontsize=15)
    ax.text(3.13,2.11,r'Observed $y$',fontsize=17,ha='left',va='center')
    ax.text(1.4,-.27,r'Fitted $\widehat y=X\widehat\beta$',fontsize=17,ha='center',va='top')
    ax.text(3.18,.98,'Residual\n'+r'$\widehat u=y-\widehat y$',fontsize=16,ha='left',va='center',color=BRONZE)
    ax.text(4.7,-.67,'Regressor-space slice',ha='right',va='center',color=MUTED,fontsize=14)
    ax.set(xlim=(-.45,5.1),ylim=(-.85,2.55),aspect='equal')
    ax.axis('off')
    # Outline the mathematical labels so hats and Greek letters retain their
    # layout on browsers without the plotting runtime's specialised fonts.
    with plt.rc_context({'svg.fonttype':'path'}):
        finish(fig,'econometrics-ols-projection',mobile)

print('Created four SVGs; OLS coefficients, normal equations and orthogonal decomposition verified.')
