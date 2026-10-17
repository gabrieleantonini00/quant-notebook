"""Illustrations for one-way ANOVA and multiple hypothesis testing notes."""
from pathlib import Path
import sys
import runpy

ROOT = Path(__file__).resolve().parents[2]
LOCAL_DEPS = ROOT / '.qa' / 'plot-deps'
if LOCAL_DEPS.is_dir():
    sys.path.insert(0, str(LOCAL_DEPS))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({
    'font.family': 'Segoe UI', 'font.size': 11, 'axes.titlesize': 15,
    'axes.spines.top': False, 'axes.spines.right': False,
    'axes.edgecolor': '#dcd6ca', 'axes.labelcolor': '#182b42',
    'text.color': '#182b42', 'xtick.color': '#626d77',
    'ytick.color': '#626d77', 'figure.facecolor': '#f6f2e9',
    'axes.facecolor': '#f6f2e9', 'svg.fonttype': 'none',
    'svg.hashsalt': 'statistics-anova-mht-plots',
})

THEME = runpy.run_path(str(Path(__file__).resolve().parent / 'statistics-plot-style.py'))
THEME['apply'](plt)
OUT = Path(__file__).resolve().parent
QA = ROOT / '.qa'
QA.mkdir(exist_ok=True)

# Balanced illustrative one-way ANOVA.
groups = [np.array([4, 5, 6]), np.array([6, 7, 8]), np.array([8, 9, 10])]
means = [float(g.mean()) for g in groups]
grand = float(np.concatenate(groups).mean())
ss_between = sum(len(g) * (g.mean() - grand) ** 2 for g in groups)
ss_within = sum(((g - g.mean()) ** 2).sum() for g in groups)
assert (means, grand, ss_between, ss_within) == ([5., 7., 9.], 7., 24., 6.)

fig, ax = plt.subplots(figsize=(8.8, 5.1), layout='constrained')
fig.suptitle('Between-group and within-group variation', x=.08, ha='left',
             fontsize=19, fontweight='semibold')
colors = ['#182b42', '#626d77', '#86623f']
for i, (g, mean, color) in enumerate(zip(groups, means, colors), 1):
    ax.scatter(np.array([i-.12, i, i+.12]), g, s=90, color=color,
               edgecolor='white', linewidth=1.2, zorder=4)
    ax.plot([i-.28, i+.28], [mean, mean], color=color, linewidth=3.2, zorder=3)
ax.axhline(grand, color='#626d77', linestyle=(0, (5, 4)), linewidth=1.4)
ax.text(.62, grand+.18, 'Grand mean = 7', color='#626d77', fontsize=13.5)
ax.annotate('', xy=(2.48, 9), xytext=(2.48, 7),
            arrowprops={'arrowstyle': '<->', 'color': '#86623f', 'lw': 1.7})
ax.text(2.4, 10.6, 'Between-group variation', va='center', color='#86623f', fontsize=13.5)
ax.annotate('', xy=(1.45, 6), xytext=(1.45, 5),
            arrowprops={'arrowstyle': '<->', 'color': '#182b42', 'lw': 1.7})
ax.text(.62, 4.4, 'Within-group\nvariation', va='center', color='#182b42', fontsize=13.5)
ax.set(xlim=(.55, 3.75), ylim=(3.5, 11.1), xticks=[1, 2, 3],
       xticklabels=['Group A', 'Group B', 'Group C'], ylabel='Observed outcome',
       yticks=[4, 5, 6, 7, 8, 9, 10])
ax.grid(axis='y', color='#dcd6ca', linewidth=.8, zorder=0)
fig.savefig(OUT / 'statistics-anova-variation.svg', metadata={'Date': None}, bbox_inches='tight')
fig.savefig(QA / 'statistics-anova-variation.png', dpi=160, bbox_inches='tight')
plt.close(fig)
THEME['clean_svg'](OUT / 'statistics-anova-variation.svg')

p = np.array([.001, .004, .006, .012, .018, .026, .041, .09, .30, .70])
m, alpha = len(p), .05
ranks = np.arange(1, m+1)
harmonic = sum(1 / j for j in ranks)
bonf = np.full(m, alpha/m)
holm = alpha / (m-ranks+1)
bh = ranks*alpha/m
by = bh/harmonic

def step_down_count(values, thresholds):
    count = 0
    for value, threshold in zip(values, thresholds):
        if value > threshold:
            break
        count += 1
    return count

assert (int((p <= bonf).sum()), step_down_count(p, holm),
        max([0] + [int(r) for r, value, cutoff in zip(ranks, p, bh) if value <= cutoff]),
        max([0] + [int(r) for r, value, cutoff in zip(ranks, p, by) if value <= cutoff])) == (2, 3, 6, 1)

fig, ax = plt.subplots(figsize=(8.8, 5.3), layout='constrained')
fig.suptitle('How adjustment changes the cutoff', x=.08, ha='left',
             fontsize=19, fontweight='semibold')
ax.plot(ranks, bh, color='#86623f', linewidth=2.5, label='BH threshold')
ax.plot(ranks, by, color='#182b42', linestyle='--', linewidth=2.5, label='BY threshold')
ax.plot(ranks, holm, color='#86623f', linestyle=':', linewidth=2.2, label='Holm threshold')
ax.axhline(alpha/m, color='#626d77', linestyle=(0, (4, 3)), linewidth=1.8,
           label='Bonferroni threshold')
ax.scatter(ranks[:7], p[:7], color='#182b42', s=46, zorder=5, label='Sorted p-values')
ax.text(6.18, p[5]+.001, 'sixth: 0.026', fontsize=12.825, color='#182b42')
ax.set(xlim=(.7, 7.2), ylim=(0, .056), xticks=range(1, 8),
       xlabel='Rank of p-value (smallest first)', ylabel='p-value or cutoff',
       yticks=[0, .01, .02, .03, .04, .05],
       yticklabels=['0', '.01', '.02', '.03', '.04', '.05'])
ax.grid(axis='y', color='#dcd6ca', linewidth=.8)
ax.legend(loc='upper left', ncol=2, frameon=False, fontsize=12.825)
fig.savefig(OUT / 'statistics-multiple-testing-thresholds.svg', metadata={'Date': None}, bbox_inches='tight')
fig.savefig(QA / 'statistics-multiple-testing-thresholds.png', dpi=160, bbox_inches='tight')
plt.close(fig)
THEME['clean_svg'](OUT / 'statistics-multiple-testing-thresholds.svg')
