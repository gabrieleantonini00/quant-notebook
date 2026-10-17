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

MOBILE = '--mobile' in sys.argv
SUFFIX = '-mobile' if MOBILE else ''

plt.rcParams.update({
    'font.family': ['DejaVu Sans', 'Arial', 'sans-serif'],
    'font.size': 14 if MOBILE else 15.75,
    'axes.titlesize': 15 if MOBILE else 18,
    'axes.labelsize': 14 if MOBILE else 15.75,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.edgecolor': '#bcb4a5',
    'axes.labelcolor': '#3e4e5f',
    'text.color': '#182b42',
    'xtick.color': '#626d77',
    'ytick.color': '#626d77',
    'figure.facecolor': '#f6f2e9',
    'axes.facecolor': '#f6f2e9',
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

fig, (ax_avg, ax_ind) = plt.subplots(2, 1, figsize=(4.2, 7.8) if MOBILE else (8.5, 6.7), sharex=True, sharey=True, layout='constrained')

for ax in (ax_avg, ax_ind):
    ax.set(xlim=(20, 60), ylim=(0, 1), yticks=[0, 0.25, 0.5, 0.75, 1], ylabel='Predicted risk')
    ax.grid(axis='y', color='#dcd6ca', linewidth=0.8)
    ax.plot(x, pdp, color='#86623f', linewidth=2.8, label='PDP · average')

ax_avg.set_title('PDP · average response', loc='left', pad=10)


for index, row in enumerate(ice):
    ax_ind.plot(x, row, color='#9ba9b5', linewidth=1.8, alpha=0.9, zorder=1, label='ICE' if index == 0 else None)
ax_ind.plot(x, pdp, color='#86623f', linewidth=2.8, zorder=3)
ax_ind.set_title('ICE · individual responses', loc='left', pad=10)
ax_avg.legend(frameon=False, loc='upper left', fontsize=12 if MOBILE else 14)
ax_ind.legend(frameon=False, loc='upper left', ncol=2, fontsize=12 if MOBILE else 14)
ax_ind.set_xlabel('Debt-to-income ratio (%)')
ax_ind.set_xticks([20, 30, 40, 50, 60])


output = Path(__file__).resolve().parent
qa = ROOT / '.qa'
qa.mkdir(exist_ok=True)
fig.savefig(output / ('learning-xai-pdp-ice' + SUFFIX + '.svg'), metadata={'Date': None}, bbox_inches='tight')
svg = output / ('learning-xai-pdp-ice' + SUFFIX + '.svg')
svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines()) + '\n', encoding='utf-8')
fig.savefig(qa / ('learning-xai-pdp-ice' + SUFFIX + '.png'), dpi=160, bbox_inches='tight')
plt.close(fig)
print('Generated PDP/ICE figure from five synthetic individual curves.')
