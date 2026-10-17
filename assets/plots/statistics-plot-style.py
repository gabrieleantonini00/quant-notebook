"""Shared editorial theme for the statistics figures."""
from pathlib import Path

PAPER = '#f6f2e9'
INK = '#182b42'
BRONZE = '#86623f'
MUTED = '#626d77'
LINE = '#dcd6ca'
SOFT_INK = '#b6bec5'
SOFT_BRONZE = '#d8c7b5'


def apply(plt):
    plt.rcParams.update({
        'font.family': 'DejaVu Sans', 'font.size': 15,
        'axes.titlesize': 17, 'axes.labelsize': 15,
        'xtick.labelsize': 14, 'ytick.labelsize': 14,
        'axes.edgecolor': LINE, 'axes.labelcolor': INK,
        'text.color': INK, 'xtick.color': MUTED, 'ytick.color': MUTED,
        'figure.facecolor': PAPER, 'axes.facecolor': PAPER,
        'savefig.facecolor': PAPER, 'svg.fonttype': 'none',
    })


def clean_svg(path):
    path = Path(path)
    path.write_text('\n'.join(line.rstrip() for line in path.read_text(encoding='utf-8').splitlines()) + '\n', encoding='utf-8')
