"""Draw the exact standard-normal tail regions for a two-sided Wald test."""
from pathlib import Path
from statistics import NormalDist
import math
import sys

ROOT = Path(__file__).resolve().parents[2]
LOCAL_DEPS = ROOT / '.qa' / 'plot-deps'
if LOCAL_DEPS.is_dir():
    sys.path.insert(0, str(LOCAL_DEPS))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


ALPHA = 0.05
OBSERVED = 2.15
NORMAL = NormalDist()
CRITICAL = NORMAL.inv_cdf(1 - ALPHA / 2)
P_VALUE = 2 * (1 - NORMAL.cdf(OBSERVED))
assert abs(CRITICAL - 1.959963984540054) < 1e-12
assert abs(P_VALUE - 0.031555214) < 1e-8
assert OBSERVED > CRITICAL

plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 10.5,
    'axes.titlesize': 12,
    'axes.labelsize': 10.5,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.edgecolor': '#b9c4d1',
    'axes.labelcolor': '#435266',
    'text.color': '#1d2939',
    'xtick.color': '#5f6e7f',
    'ytick.color': '#5f6e7f',
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'svg.fonttype': 'none',
    'svg.hashsalt': 'statistics-two-sided-test',
})


def density(values):
    return np.exp(-np.asarray(values) ** 2 / 2) / math.sqrt(2 * math.pi)


def draw_panel(ax, cutoff, color, heading, total, tail, label):
    # Each filled polygon starts exactly at its mathematical boundary.
    x = np.linspace(-4.5, 4.5, 1601)
    for lo, hi in ((-4.5, -cutoff), (cutoff, 4.5)):
        tail_x = np.linspace(lo, hi, 401)
        ax.fill_between(tail_x, density(tail_x), 0, color=color, alpha=0.73, linewidth=0)
    ax.plot(x, density(x), color='#293949', lw=2.1)
    for boundary in (-cutoff, cutoff):
        ax.vlines(boundary, 0, density(boundary), color=color, lw=1.6, linestyle=(0, (4, 3)))
    ax.text(-cutoff - 0.08, 0.11, f'−{cutoff:.2f}', ha='right', color=color, fontweight='medium')
    ax.text(cutoff + 0.08, 0.11, f'+{cutoff:.2f}', ha='left', color=color, fontweight='medium')
    ax.text(-3.65, 0.045, f'{tail:.4f}', ha='center', color='#8b3c42' if label == 'p' else '#83561d', fontweight='medium')
    ax.text(3.65, 0.045, f'{tail:.4f}', ha='center', color='#8b3c42' if label == 'p' else '#83561d', fontweight='medium')
    ax.text(4.35, 0.36, f'Total {label} = {total:.4f}', ha='right', color='#435266')
    ax.set(xlim=(-4.5, 4.5), ylim=(0, 0.43), xticks=range(-4, 5), yticks=[0, 0.2, 0.4], ylabel='Density')
    ax.set_title(heading, loc='left', pad=9, fontweight='medium')
    ax.spines['left'].set_visible(False)
    ax.tick_params(axis='y', length=0)


fig, (ax_rejection, ax_p) = plt.subplots(2, 1, figsize=(8.6, 5.6), sharex=True, layout='constrained')
draw_panel(ax_rejection, CRITICAL, '#e1aa54', 'Rejection region  ·  |W| ≥ 1.96', ALPHA, ALPHA / 2, 'α')
draw_panel(ax_p, OBSERVED, '#c85b60', 'Observed p-value  ·  |W| ≥ 2.15', P_VALUE, P_VALUE / 2, 'p')
ax_p.set_xlabel('Standard normal test statistic  W')
ax_p.tick_params(axis='x', labelbottom=True)

out = Path(__file__).resolve().parent
qa = ROOT / '.qa'
qa.mkdir(exist_ok=True)
fig.savefig(out / 'statistics-two-sided-test.svg', metadata={'Date': None}, bbox_inches='tight')
fig.savefig(qa / 'statistics-two-sided-test.png', dpi=160, bbox_inches='tight')
plt.close(fig)
print(f'critical = ±{CRITICAL:.5f}; rejection tails = {ALPHA / 2:.5f} each; '
      f'p-value tails = {P_VALUE / 2:.6f} each; total p = {P_VALUE:.6f}')
