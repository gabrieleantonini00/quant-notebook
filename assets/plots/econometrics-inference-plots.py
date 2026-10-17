"""Reproduce residual diagnostics and the instrumental-variable mechanism."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / '.qa' / 'plot-deps'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parent
PAPER, INK, BRONZE, MUTED, LINE = '#f6f2e9', '#182b42', '#86623f', '#626d77', '#dcd6ca'
plt.rcParams.update({
    'font.family': ['DejaVu Sans', 'Arial', 'sans-serif'], 'font.size': 15,
    'text.color': INK, 'axes.labelcolor': INK, 'xtick.color': MUTED, 'ytick.color': MUTED,
    'axes.edgecolor': LINE, 'axes.spines.top': False, 'axes.spines.right': False,
    'figure.facecolor': PAPER, 'axes.facecolor': PAPER,
    'svg.fonttype': 'none', 'svg.hashsalt': 'econometrics-inference-editorial',
})


def save(fig, name):
    path = OUT / (name + '.svg')
    fig.savefig(path, metadata={'Date': None}, bbox_inches='tight', pad_inches=.18)
    path.write_text('\n'.join(s.rstrip() for s in path.read_text(encoding='utf-8').splitlines())+'\n', encoding='utf-8')
    fig.savefig(ROOT / '.qa' / (name + '.png'), dpi=140, bbox_inches='tight', pad_inches=.18)
    plt.close(fig)


rng = np.random.default_rng(417)
x = np.linspace(0, 6, 240)
X = np.column_stack((np.ones(x.size), x))
noise = rng.normal(size=x.size)
outcomes = [2 + 1.3*x + .8*noise,
            2 + 1.3*x + (.18+.33*x)*noise,
            2 + 1.3*x + .6*(x-3)**2 + .8*noise]
titles = ['Constant variance', 'Increasing variance', 'Misspecified mean']
data = []
for y in outcomes:
    fitted = X @ np.linalg.lstsq(X, y, rcond=None)[0]
    residual = y - fitted
    assert np.allclose(X.T @ residual, 0, atol=1e-10)
    data.append((fitted, residual))
assert np.var(data[1][1][-60:]) > 6*np.var(data[1][1][:60])

for mobile in (False, True):
    fig, axes = plt.subplots(3, 1, figsize=(5.6, 11.8), layout='constrained') if mobile else plt.subplots(1, 3, figsize=(12.6, 4.4), layout='constrained')
    for ax, (fitted, residual), title in zip(axes, data, titles):
        ax.axhline(0, color=MUTED, lw=1, ls=(0, (4, 3)), zorder=1)
        ax.scatter(fitted, residual, s=14 if mobile else 12, color=INK, alpha=.5, linewidths=0, zorder=2)
        bins = np.array_split(np.argsort(fitted), 10)
        ax.plot([fitted[b].mean() for b in bins], [residual[b].mean() for b in bins], color=BRONZE, lw=2, zorder=3)
        ax.set_title(title, loc='left', fontsize=18 if mobile else 17, pad=14)
        ax.set_xlabel('Fitted outcome', fontsize=16 if mobile else 15)
        ax.set_ylabel('OLS residual', fontsize=16 if mobile else 15)
        ax.tick_params(labelsize=14 if mobile else 13)
        ax.set_ylim(-5.5, 5.5)
        ax.grid(axis='y', color=LINE, lw=.6)
    save(fig, 'econometrics-residual-diagnostics' + ('-mobile' if mobile else ''))


def iv_diagram(mobile):
    # A native SVG keeps all labels searchable, with a separate portrait layout.
    from html import escape
    width, height = (480, 650) if mobile else (900, 430)
    nodes = ({'z': (24, 40, 230, 92), 'x': (24, 265, 230, 92), 'y': (24, 490, 230, 92), 'u': (290, 265, 166, 92)} if mobile else
             {'z': (25, 265, 230, 92), 'x': (335, 265, 230, 92), 'y': (645, 265, 230, 92), 'u': (490, 35, 230, 92)})
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
             '<title id="title">Instrumental variables: a random training offer</title>',
             '<desc id="desc">A random offer changes training participation, which affects earnings. Unobserved motivation affects both participation and earnings. Validity assumes that the offer is independent of the confounder and has no direct effect on earnings.</desc>',
             f'<rect width="100%" height="100%" fill="{PAPER}"/>',
             '<defs>' + ''.join(f'<marker id="arrow-{n}" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto" markerUnits="userSpaceOnUse"><path d="M0,0 L9,4.5 L0,9" fill="{c}"/></marker>' for n, c in [('ink', INK), ('bronze', BRONZE), ('muted', MUTED)]) + '</defs>',
             '<g font-family="Inter, Arial, sans-serif">']
    def arrow(path, color='ink', dashed=False):
        c = {'ink': INK, 'bronze': BRONZE, 'muted': MUTED}[color]
        parts.append(f'<path d="{path}" fill="none" stroke="{c}" stroke-width="2.3"'+(' stroke-dasharray="6 5"' if dashed else '')+f' marker-end="url(#arrow-{color})"/>')
    def label(x, y, text, color=INK, size=20, anchor='middle'):
        parts.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" fill="{color}" font-size="{size}">{escape(text)}</text>')
    if mobile:
        arrow('M139 137 L139 258', 'bronze')
        arrow('M139 362 L139 483')
        arrow('M285 311 L261 311', 'muted', True)
        arrow('M373 363 L373 536 L261 536', 'muted', True)
        label(154, 197, 'Relevance', BRONZE, 20, 'start')
        label(154, 424, 'Effect', INK, 20, 'start')
    else:
        arrow('M260 311 L328 311', 'bronze')
        arrow('M570 311 L638 311')
        arrow('M557 132 L466 258', 'muted', True)
        arrow('M653 132 L752 258', 'muted', True)
        label(295, 250, 'Relevance', BRONZE, 18)
        label(605, 250, 'Effect', INK, 18)
    labels = {'z': ['Random training', 'offer (Z)'], 'x': ['Training', 'participation (X)'],
              'y': ['Earnings (Y)'], 'u': ['Unobserved', 'motivation (U)']}
    for name, (nx, ny, nw, nh) in nodes.items():
        color = BRONZE if name == 'z' else MUTED if name == 'u' else INK
        parts.append(f'<rect x="{nx}" y="{ny}" width="{nw}" height="{nh}" rx="3" fill="#fbf8f1" stroke="{color}" stroke-width="1.3"/>')
        rows = labels[name]
        for j, row in enumerate(rows):
            label(nx+nw/2, ny+nh/2+7+(j-(len(rows)-1)/2)*27, row, color, 21 if mobile else 22)
    label(width/2, height-25, 'Dashed arrows: unobserved confounding', MUTED, 18 if mobile else 20)
    parts += ['</g>', '</svg>']
    path = OUT / ('econometrics-iv-mechanism' + ('-mobile' if mobile else '') + '.svg')
    path.write_text('\n'.join(parts)+'\n', encoding='utf-8')

iv_diagram(False)
iv_diagram(True)
print('Created four inference SVGs; fitted residual orthogonality and increasing dispersion verified.')
