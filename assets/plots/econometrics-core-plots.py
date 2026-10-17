"""Reproduce the panel figure and run the editorial time-series figure generator."""
from pathlib import Path
import sys

LOCAL_DEPS = Path(__file__).resolve().parents[2] / '.qa' / 'plot-deps'
if LOCAL_DEPS.is_dir():
    sys.path.insert(0, str(LOCAL_DEPS))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parent
QA = OUT.parents[1] / '.qa'
QA.mkdir(exist_ok=True)
plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 11,
    'axes.spines.top': False, 'axes.spines.right': False,
    'axes.edgecolor': '#cbd5e1', 'axes.labelcolor': '#334155',
    'text.color': '#0f172a', 'xtick.color': '#475569', 'ytick.color': '#475569',
    'figure.facecolor': 'white', 'axes.facecolor': 'white',
    'svg.fonttype': 'none', 'svg.hashsalt': 'econometrics-core-plots',
})


def finish(fig, name):
    fig.savefig(OUT / (name + '.svg'), metadata={'Date': None})
    fig.savefig(QA / (name + '.png'), dpi=140)
    plt.close(fig)


x = np.arange(1., 7.)
y = np.array([12., 14., 16., 8., 10., 12.])
pooled = np.linalg.lstsq(np.column_stack([np.ones(6), x]), y, rcond=None)[0]
within_x = x.reshape(2, 3) - x.reshape(2, 3).mean(axis=1, keepdims=True)
within_y = y.reshape(2, 3) - y.reshape(2, 3).mean(axis=1, keepdims=True)
within_slope = (within_x * within_y).sum() / (within_x ** 2).sum()
assert np.isclose(pooled[1], -4 / 7) and np.isclose(within_slope, 2)
fig, ax = plt.subplots(figsize=(9.6, 4.8), layout='constrained')
ax.set_title('Within-unit changes and the pooled fit', loc='left', pad=18, weight='semibold')
for slc, name, color in [(slice(0, 3), 'Unit A: within slope = 2', '#2563eb'),
                         (slice(3, 6), 'Unit B: within slope = 2', '#0d9488')]:
    ax.plot(x[slc], y[slc], 'o-', color=color, linewidth=2.4, markersize=7, label=name)
xx = np.linspace(.7, 6.3, 100)
ax.plot(xx, pooled[0] + pooled[1] * xx, '--', color='#b45309', linewidth=2,
        label='Pooled slope = -0.571')
ax.set(xlabel='Regressor x (illustrative units)', ylabel='Outcome y (illustrative units)',
       xlim=(.7, 6.3), ylim=(6, 18), xticks=x)
ax.grid(axis='y', alpha=.18)
ax.legend(loc='lower left', frameon=False, fontsize=9)
finish(fig, 'econometrics-panel-within')

# Time-series figures have their own editorial generator, including mobile layouts.
import runpy
runpy.run_path(str(OUT / "econometrics-time-series-plots.py"), run_name="__main__")
print("Created panel and time-series figures; numerical illustrations verified.")
