"""Rebuild the illustrative PDP/ICE comparison (matplotlib and numpy)."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
LOCAL_DEPS = ROOT / '.qa' / 'plot-deps'
if LOCAL_DEPS.is_dir():
    sys.path.insert(0, str(LOCAL_DEPS))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams.update({
    'font.family': 'Segoe UI',
    'font.size': 10.5,
    'axes.titlesize': 12,
    'axes.labelsize': 10.5,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.edgecolor': '#cbd5e1',
    'axes.labelcolor': '#334155',
    'text.color': '#0f172a',
    'xtick.color': '#64748b',
    'ytick.color': '#64748b',
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'svg.fonttype': 'none',
    'svg.hashsalt': 'learning-xai-pdp-ice',
})


def sigmoid(value):
    return 1 / (1 + np.exp(-value))


x = np.linspace(20, 60, 321)  # illustrative debt-to-income ratio, in percent
intercepts = np.array([-1.3, -0.7, -0.1, 0.4, 0.8])
slopes = np.array([0.25, 0.45, 0.7, 0.35, 0.9])
ice = sigmoid(intercepts[:, None] + slopes[:, None] * ((x[None, :] - 40) / 10))
pdp = ice.mean(axis=0)
assert ice.shape == (5, len(x))
assert np.allclose(pdp, ice.mean(axis=0))
assert np.all((ice >= 0) & (ice <= 1))

fig, (ax_avg, ax_ind) = plt.subplots(2, 1, figsize=(8.5, 5.7), sharex=True, sharey=True, layout='constrained')

for ax in (ax_avg, ax_ind):
    ax.set(xlim=(20, 60), ylim=(0, 1), yticks=[0, 0.25, 0.5, 0.75, 1], ylabel='Predicted default risk')
    ax.grid(axis='y', color='#e2e8f0', linewidth=0.8)
    ax.plot(x, pdp, color='#51459b', linewidth=2.8, label='PDP · average')

ax_avg.set_title('PDP  ·  one average curve', loc='left', pad=10)
ax_avg.text(59, 0.07, 'Mean across five hypothetical applicants', ha='right', color='#64748b', fontsize=9.5)

for row in ice:
    ax_ind.plot(x, row, color='#60a5a0', linewidth=1.5, alpha=0.78, zorder=1)
ax_ind.plot(x, pdp, color='#51459b', linewidth=2.8, zorder=3)
ax_ind.set_title('ICE  ·  the five individual curves behind that average', loc='left', pad=10)
ax_ind.set_xlabel('Debt-to-income ratio (%)')
ax_ind.set_xticks([20, 30, 40, 50, 60])
ax_ind.text(59, 0.07, 'Teal: individuals     Purple: PDP mean', ha='right', color='#64748b', fontsize=9.5)

output = Path(__file__).resolve().parent
qa = ROOT / '.qa'
qa.mkdir(exist_ok=True)
fig.savefig(output / 'learning-xai-pdp-ice.svg', metadata={'Date': None}, bbox_inches='tight')
fig.savefig(qa / 'learning-xai-pdp-ice.png', dpi=160, bbox_inches='tight')
plt.close(fig)
print('Generated PDP/ICE figure from five synthetic individual curves.')
