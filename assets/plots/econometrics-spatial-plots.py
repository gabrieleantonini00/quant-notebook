"""Draw the reproducible four-district spatial-weights and SAR illustrations."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
LOCAL_DEPS = ROOT / '.qa' / 'plot-deps'
if LOCAL_DEPS.is_dir():
    sys.path.insert(0, str(LOCAL_DEPS))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np

plt.rcParams.update({
    'font.family': 'Segoe UI',
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.titleweight': 'semibold',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.edgecolor': '#cbd5e1',
    'axes.labelcolor': '#334155',
    'text.color': '#0f172a',
    'xtick.color': '#475569',
    'ytick.color': '#475569',
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'svg.fonttype': 'none',
    'svg.hashsalt': 'econometrics-spatial-plots',
})

OUT = Path(__file__).resolve().parent
QA = ROOT / '.qa'
QA.mkdir(exist_ok=True)

W = np.array([
    [0, .5, .5, 0],
    [.5, 0, 0, .5],
    [.5, 0, 0, .5],
    [0, .5, .5, 0],
])
labels = ['A', 'B', 'C', 'D']
outcomes = [10, 40, 20, 30]
assert np.allclose(W.sum(axis=1), 1)
assert (W @ outcomes)[0] == 30
assert (W @ W)[0, 0] > 0

fig, (ax_map, ax_w) = plt.subplots(1, 2, figsize=(9.2, 4.3), layout='constrained',
                                  gridspec_kw={'width_ratios': [1, 1.12]})
fig.suptitle('Who counts as a neighbor?', x=.06, ha='left', fontsize=17, fontweight='semibold')
ax_map.set_title('Four adjacent districts', loc='left', pad=13)
positions = [(0, 1), (1, 1), (0, 0), (1, 0)]
fills = ['#dbeafe', '#d1fae5', '#e0e7ff', '#fef3c7']
for name, value, (x, y), color in zip(labels, outcomes, positions, fills):
    ax_map.add_patch(Rectangle((x, y), .97, .97, facecolor=color,
                               edgecolor='white', linewidth=3))
    ax_map.text(x + .485, y + .57, name, ha='center', va='center', fontsize=23,
                fontweight='semibold')
    ax_map.text(x + .485, y + .30, f'y = {value}', ha='center', va='center',
                color='#475569', fontsize=11)
ax_map.text(1, -.21, 'Shared edge = neighbor', ha='center', va='top', color='#64748b')
ax_map.set(xlim=(-.07, 2.06), ylim=(-.3, 2.06), aspect='equal')
ax_map.axis('off')

ax_w.set_title('Row-standardized weights  W', loc='left', pad=13)
ax_w.imshow(W, cmap='Blues', vmin=0, vmax=.65)
ax_w.set(xticks=range(4), yticks=range(4), xticklabels=labels, yticklabels=labels)
ax_w.xaxis.tick_top()
ax_w.tick_params(length=0, pad=8)
for row in range(4):
    for col in range(4):
        value = W[row, col]
        ax_w.text(col, row, '0.5' if value else '0', ha='center', va='center',
                  color='#fff' if value else '#64748b', fontsize=12,
                  fontweight='semibold' if value else 'normal')
for i in np.arange(-.5, 4, 1):
    ax_w.axhline(i, color='white', linewidth=2)
    ax_w.axvline(i, color='white', linewidth=2)
ax_w.set_xlabel('Neighbor  j', labelpad=12)
ax_w.set_ylabel('District  i', labelpad=12)
fig.savefig(OUT / 'econometrics-spatial-weights.svg', metadata={'Date': None}, bbox_inches='tight')
fig.savefig(QA / 'econometrics-spatial-weights.png', dpi=160, bbox_inches='tight')
plt.close(fig)

rho = .4
beta = 1.
effects = np.linalg.solve(np.eye(4) - rho * W, np.array([beta, 0, 0, 0]))
S = np.linalg.inv(np.eye(4) - rho * W) * beta
assert np.allclose(effects, [1.0952380952380953, .23809523809523808,
                             .23809523809523808, .09523809523809523])
assert np.allclose(np.trace(S) / 4, effects[0])
assert np.isclose(S.sum() / 4, 5 / 3)

fig, ax = plt.subplots(figsize=(9.2, 4.7), layout='constrained')
fig.suptitle('A change in A reaches every district', x=.08, ha='left',
             fontsize=17, fontweight='semibold')
x = np.arange(4)
ax.bar(x, effects, width=.58,
       color=['#2563eb', '#0d9488', '#0d9488', '#d97706'], zorder=3)
ax.axhline(beta, color='#94a3b8', linestyle=(0, (4, 4)), linewidth=1.2, zorder=2)
ax.text(3.42, beta + .03, 'β = 1', color='#64748b', ha='right', va='bottom')
for xi, value in zip(x, effects):
    ax.text(xi, value + .035, f'+{value:.3f}', ha='center', va='bottom',
            fontweight='semibold', color='#334155')
ax.set(xticks=x, xticklabels=['A\norigin', 'B\nneighbor', 'C\nneighbor', 'D\ntwo steps away'],
       ylim=(0, 1.32), ylabel='Change in outcome', yticks=[0, .25, .5, .75, 1])
ax.grid(axis='y', color='#e2e8f0', linewidth=.8, zorder=0)
ax.text(0, .64, 'Own effect\n+ feedback', ha='center', color='white', fontsize=10)
ax.text(1.5, .48, 'Spillovers', ha='center', color='#0f766e', fontsize=11)
fig.savefig(OUT / 'econometrics-spatial-spillovers.svg', metadata={'Date': None}, bbox_inches='tight')
fig.savefig(QA / 'econometrics-spatial-spillovers.png', dpi=160, bbox_inches='tight')
plt.close(fig)
