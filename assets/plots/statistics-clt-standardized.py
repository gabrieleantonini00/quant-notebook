"""Exact standardized Gamma densities illustrate the CLT, with a mobile layout."""
from pathlib import Path
import math
import runpy
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / '.qa/plot-deps'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent
THEME = runpy.run_path(str(OUT / 'statistics-plot-style.py'))
THEME['apply'](plt)
plt.rcParams.update({'axes.spines.top': False, 'axes.spines.right': False,
                     'svg.hashsalt': 'statistics-clt-editorial'})


def build(mobile=False):
    if mobile:
        fig, axes = plt.subplots(3, 1, figsize=(4.2, 10.5), layout='constrained')
    else:
        fig, axes = plt.subplots(1, 3, figsize=(11.4, 4.4), layout='constrained')
    for ax, n in zip(axes, (1, 5, 30)):
        start = max(-4.0, -math.sqrt(n))
        z = np.linspace(start, 4, 1201)
        y = n + np.sqrt(n) * z
        if n == 1:
            density = np.exp(-y)
        else:
            density = np.zeros_like(y)
            positive = y > 0
            density[positive] = np.exp(.5 * math.log(n) + (n-1)*np.log(y[positive]) - y[positive] - math.lgamma(n))
        normal_x = np.linspace(-4, 4, 1201)
        ax.plot(normal_x, np.exp(-normal_x**2/2)/math.sqrt(2*math.pi),
                color=THEME['INK'], ls=(0, (4, 3)), lw=1.8, label='Normal')
        ax.plot(z, density, color=THEME['BRONZE'], lw=2.5, label='Exact')
        if start > -4:
            ax.plot([-4, start], [0, 0], color=THEME['BRONZE'], lw=2.5)
        ax.set(xlim=(-4, 4), ylim=(0, 1.05 if n == 1 else .52),
               xticks=[-4, -2, 0, 2, 4], xlabel='Standardised mean', ylabel='Density')
        ax.set_title(f'n = {n}', loc='left')
        ax.legend(frameon=False, fontsize=12, loc='upper right')
        ax.grid(axis='y', color=THEME['LINE'], lw=.6)
    stem = 'statistics-clt-standardized' + ('-mobile' if mobile else '')
    fig.savefig(OUT / f'{stem}.svg', metadata={'Date': None}, bbox_inches='tight')
    (ROOT / '.qa').mkdir(exist_ok=True)
    fig.savefig(ROOT / '.qa' / f'{stem}.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    THEME['clean_svg'](OUT / f'{stem}.svg')


if __name__ == '__main__':
    build()
    build(mobile=True)
