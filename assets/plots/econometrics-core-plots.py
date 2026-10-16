"""Reproduce the illustrative panel, AR(1), and GARCH figures in the notes."""
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

h = np.arange(0, 11)
mu, phi, sigma, current = 2., .7, 1., 5.
mean = mu + phi ** h * (current - mu)
variance = sigma ** 2 * (1 - phi ** (2 * h)) / (1 - phi ** 2)
assert np.allclose(mean[1:4], [4.1, 3.47, 3.029])
assert np.allclose(variance[1:4], [1., 1.49, 1.7301])
fig, ax = plt.subplots(figsize=(9.6, 4.8), layout='constrained')
ax.set_title('AR(1): the mean reverts, prediction uncertainty grows', loc='left', pad=18, weight='semibold')
ax.fill_between(h, mean - 1.9599639845 * np.sqrt(variance),
                mean + 1.9599639845 * np.sqrt(variance),
                color='#dbeafe', label='Pointwise Gaussian 95% prediction interval')
ax.plot(h, mean, 'o-', color='#2563eb', label='Conditional forecast', linewidth=2.2, markersize=4)
ax.axhline(mu, color='#64748b', linestyle='--', linewidth=1.4, label='Unconditional mean = 2')
ax.set(xlabel='Forecast horizon', ylabel='Outcome (illustrative units)', xlim=(0, 10), xticks=h)
ax.grid(axis='y', alpha=.18)
ax.legend(loc='upper right', frameon=False, fontsize=9)
finish(fig, 'econometrics-ar1-forecast')

omega, alpha, beta, h_current, innovation = .05, .1, .85, 4., -3.
first = omega + alpha * innovation ** 2 + beta * h_current
long_run = omega / (1 - alpha - beta)
horizon = np.arange(1, 61)
forecast = long_run + (alpha + beta) ** (horizon - 1) * (first - long_run)
assert np.isclose(first, 4.35) and np.isclose(long_run, 1.)
assert np.isclose(forecast[9], 3.111334020778027, atol=1e-8)
fig, ax = plt.subplots(figsize=(9.6, 4.8), layout='constrained')
ax.set_title('GARCH(1,1): persistent variance gradually settles', loc='left', pad=18, weight='semibold')
ax.plot(horizon, forecast, color='#2563eb', linewidth=2.4, label='Conditional innovation variance forecast')
ax.scatter([1, 10], [first, forecast[9]], color='#2563eb', zorder=3)
ax.annotate('h = 1: 4.35', (1, first), xytext=(9, 4.35), fontsize=10)
ax.annotate('h = 10: 3.111', (10, forecast[9]), xytext=(17, 3.25), fontsize=10,
            arrowprops={'arrowstyle': '-', 'color': '#94a3b8'})
ax.axhline(long_run, color='#64748b', linestyle='--', linewidth=1.5,
           label='Unconditional variance = 1')
ax.set(xlabel='Forecast horizon', ylabel='Variance (squared percentage points)',
       xlim=(0, 60), ylim=(.7, 4.7))
ax.grid(axis='y', alpha=.18)
ax.legend(loc='upper right', frameon=False, fontsize=9, bbox_to_anchor=(1, .82))
finish(fig, 'econometrics-garch-forecast')
print('Created three figures; numerical examples verified.')
