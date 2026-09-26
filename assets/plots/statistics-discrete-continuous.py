"""Rebuild the discrete and continuous CDF comparison (matplotlib + numpy)."""
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

OUT = Path(__file__).resolve().parent
QA = ROOT / '.qa'
QA.mkdir(exist_ok=True)

plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 11,
    'axes.titlesize': 12,
    'axes.labelsize': 11,
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
    'svg.hashsalt': 'statistics-discrete-continuous',
})


def finish(fig, stem):
    fig.savefig(OUT / f'{stem}.svg', metadata={'Date': None}, bbox_inches='tight')
    fig.savefig(QA / f'{stem}.png', dpi=160, bbox_inches='tight')
    plt.close(fig)


purple, purple_light = '#7051af', '#dcd1ed'
k = np.arange(5)
mass = np.array([math.comb(4, int(n)) / 16 for n in k])
cumulative = np.cumsum(mass)
assert np.isclose(mass.sum(), 1)
assert np.isclose(cumulative[2], 11 / 16)

fig, (ax, ax_cdf) = plt.subplots(2, 1, figsize=(5.1, 6.0), layout='constrained')
fig.suptitle('Discrete  ·  Binomial(4, 0.5)', x=0.06, ha='left', fontsize=15, fontweight='medium')
ax.bar(k, mass, width=0.72, color=[purple if n <= 2 else purple_light for n in k])
ax.set(xlim=(-0.55, 4.55), ylim=(0, 0.46), xticks=k, ylabel='Probability', xlabel='Count  k')
ax.set_title('PMF  ·  individual probabilities', loc='left', pad=10)
ax.text(4.48, 0.43, 'Add bars through k = 2', ha='right', va='top', fontsize=10, color=purple)
ax_cdf.step([-0.55, 0, 1, 2, 3, 4, 4.55], [0, *cumulative, 1],
            where='post', color=purple, lw=2.4)
ax_cdf.scatter([2], [cumulative[2]], color=purple, zorder=4, s=42)
ax_cdf.axvline(2, color=purple, alpha=0.45, ls='--', lw=1)
ax_cdf.annotate('F(2) = 0.6875', xy=(2, cumulative[2]), xytext=(2.55, 0.52),
                arrowprops={'arrowstyle': '-', 'color': purple, 'lw': 1},
                color=purple, fontsize=11)
ax_cdf.set(xlim=(-0.55, 4.55), ylim=(0, 1.08), xticks=k,
           yticks=[0, 0.25, 0.5, 0.75, 1], ylabel='Cumulative probability', xlabel='Count  k')
ax_cdf.set_title('CDF  ·  sum of probability masses', loc='left', pad=10)
finish(fig, 'statistics-discrete-cdf')

blue, blue_light = '#28699d', '#c9dcea'
normal = NormalDist()
x = np.linspace(-3.8, 3.8, 1001)
pdf = np.exp(-x*x/2) / math.sqrt(2*math.pi)
cdf = np.array([normal.cdf(float(value)) for value in x])
threshold = 0.5
at_threshold = normal.cdf(threshold)
assert abs(at_threshold - 0.6914624612740131) < 1e-12

fig, (ax, ax_cdf) = plt.subplots(2, 1, figsize=(5.1, 6.0), layout='constrained')
fig.suptitle('Continuous  ·  Standard normal', x=0.06, ha='left', fontsize=15, fontweight='medium')
ax.plot(x, pdf, color=blue, lw=2.4)
ax.fill_between(x, pdf, where=x <= threshold, color=blue_light)
ax.axvline(threshold, color=blue, alpha=0.45, ls='--', lw=1)
ax.text(-3.55, 0.34, 'Area = 0.6915', color=blue, fontsize=11)
ax.set(xlim=(-3.8, 3.8), ylim=(0, 0.45), ylabel='Density', xlabel='Value  x')
ax.set_title('PDF  ·  area to the left of 0.5', loc='left', pad=10)
ax_cdf.plot(x, cdf, color=blue, lw=2.4)
ax_cdf.scatter([threshold], [at_threshold], color=blue, zorder=4, s=42)
ax_cdf.axvline(threshold, color=blue, alpha=0.45, ls='--', lw=1)
ax_cdf.annotate('F(0.5) ≈ 0.6915', xy=(threshold, at_threshold), xytext=(1.1, 0.5),
                arrowprops={'arrowstyle': '-', 'color': blue, 'lw': 1},
                color=blue, fontsize=11)
ax_cdf.set(xlim=(-3.8, 3.8), ylim=(0, 1.08),
           yticks=[0, 0.25, 0.5, 0.75, 1], ylabel='Cumulative probability', xlabel='Value  x')
ax_cdf.set_title('CDF  ·  integral of the density', loc='left', pad=10)
finish(fig, 'statistics-continuous-cdf')

print(f'PMF sum = {mass.sum():.4f}; F_discrete(2) = {cumulative[2]:.4f}; '
      f'F_continuous(0.5) = {at_threshold:.4f}')
