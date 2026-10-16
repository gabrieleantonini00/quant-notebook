"""Rebuild the finance tail-risk figure (requires matplotlib and numpy)."""
from pathlib import Path
from statistics import NormalDist
import math
import sys

LOCAL_DEPS = Path(__file__).resolve().parents[2] / '.qa' / 'plot-deps'
if LOCAL_DEPS.is_dir():
    sys.path.insert(0, str(LOCAL_DEPS))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DEST = Path(__file__).resolve().parent
QA = DEST.parents[1] / '.qa'
QA.mkdir(exist_ok=True)
# All figure text is exactly 1.5 times its previous font size (below 2x).
TEXT_SCALE = 1.5
assert 1 < TEXT_SCALE <= 2
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11 * TEXT_SCALE,
    "axes.titlesize": 13.2 * TEXT_SCALE,
    "axes.labelsize": 11 * TEXT_SCALE,
    "xtick.labelsize": 11 * TEXT_SCALE, "ytick.labelsize": 11 * TEXT_SCALE,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#dcd6ca", "axes.labelcolor": "#182b42",
    "text.color": "#182b42", "xtick.color": "#626d77", "ytick.color": "#626d77",
    "figure.facecolor": "#f6f2e9", "axes.facecolor": "#f6f2e9",
    "svg.fonttype": "none", "svg.hashsalt": "study-notes-finance-learning",
})

mu, sigma, alpha = 0.05, 1.0, 0.95  # daily return in percentage points
z = NormalDist().inv_cdf(1 - alpha)
var = mu + sigma * z
es = mu - sigma * math.exp(-z*z/2) / math.sqrt(2*math.pi) / (1-alpha)
assert round(var, 4) == -1.5949 and round(es, 4) == -2.0127
x = np.linspace(-4.3, 4.3, 1601)
density = lambda a: np.exp(-0.5*((a-mu)/sigma)**2) / (sigma*np.sqrt(2*np.pi))
tail = np.linspace(x[0], var, 400)
fig, ax = plt.subplots(figsize=(10, 5.4), layout="constrained")
ax.plot(x, density(x), color="#182b42", lw=2.3)
ax.fill_between(x, density(x), color="#e8e2d6")
ax.fill_between(tail, density(tail), color="#cbb18c", label="Worst 5%")
ax.axvline(var, color="#86623f", ls="--", lw=1.8)
ax.axvline(es, color="#182b42", ls=":", lw=1.8)
ax.annotate("VaR threshold\n−1.59%", xy=(var, 0.12), xytext=(-0.45, 0.14),
            arrowprops={"arrowstyle": "-", "color": "#86623f"}, color="#86623f")
ax.annotate("ES: tail mean\n−2.01%", xy=(es, 0.075), xytext=(-4.1, 0.29),
            arrowprops={"arrowstyle": "-", "color": "#182b42"}, color="#182b42")
ax.set(xlim=(-4.3,4.3), ylim=(0,0.48), xlabel="Daily return (%)", ylabel="Probability density",
       xticks=[-4,-2,0,2,4], yticks=[0,.1,.2,.3,.4])
ax.set_title("The threshold and the tail average", loc="left", fontfamily="DejaVu Serif",
             fontweight="normal", pad=20)
ax.legend(loc="upper right", frameon=False, fontsize=10 * TEXT_SCALE)
fig.savefig(DEST / "finance-var-es-tail.svg", metadata={"Date": None})
svg_path = DEST / 'finance-var-es-tail.svg'
svg_path.write_text('\n'.join(line.rstrip() for line in svg_path.read_text(encoding='utf-8').splitlines()) + '\n', encoding='utf-8')
fig.savefig(QA / 'finance-var-es-tail.png', dpi=150)
plt.close(fig)

print(f"95% signed-return VaR={var:.6f}%; ES={es:.6f}%")
