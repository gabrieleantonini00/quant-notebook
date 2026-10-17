"""Constructed two-by-three cell means illustrate additive and interacting effects."""
from pathlib import Path
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
                     'svg.hashsalt': 'statistics-anova-interaction'})

BASE = np.array([2., 3., 4.])
ADDITIVE = np.array([4., 5., 6.])
INTERACTION = np.array([3., 5., 7.])
assert np.allclose(ADDITIVE - BASE, 2.)
assert not np.allclose(INTERACTION - BASE, (INTERACTION - BASE)[0])


def build(mobile=False):
    shape, size = ((2, 1), (4.2, 7.6)) if mobile else ((1, 2), (9., 4.1))
    fig, axes = plt.subplots(*shape, figsize=size, layout='constrained')
    for ax, other, heading in zip(axes, (ADDITIVE, INTERACTION), ('Additive means', 'Interaction')):
        ax.plot([1, 2, 3], BASE, color=THEME['INK'], marker='o',
                lw=2.3, ms=7, label='A1')
        ax.plot([1, 2, 3], other, color=THEME['BRONZE'], marker='s',
                ls=(0, (4, 2)), lw=2.3, ms=7, label='A2')
        ax.set(xlim=(.8, 3.2), ylim=(1, 8.3), xticks=[1, 2, 3],
               xticklabels=['B1', 'B2', 'B3'], yticks=[2, 4, 6, 8],
               xlabel='Level of factor B', ylabel='Illustrative cell mean')
        ax.set_title(heading, loc='left', fontsize=17)
        ax.legend(frameon=False, ncol=2, loc='upper left', fontsize=13)
        ax.grid(axis='y', color=THEME['LINE'], linewidth=.7)
    stem = 'statistics-anova-interaction' + ('-mobile' if mobile else '')
    fig.savefig(OUT / f'{stem}.svg', metadata={'Date': None}, bbox_inches='tight')
    fig.savefig(ROOT / '.qa' / f'{stem}.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    THEME['clean_svg'](OUT / f'{stem}.svg')


if __name__ == '__main__':
    build()
    build(mobile=True)
