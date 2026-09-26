"""Rebuild the finance tail-risk figure (requires matplotlib and numpy)."""
from pathlib import Path
from statistics import NormalDist
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DEST = Path(__file__).resolve().parent
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#c6d1cd", "axes.labelcolor": "#253d36",
    "text.color": "#253d36", "xtick.color": "#50665e", "ytick.color": "#50665e",
    "figure.facecolor": "#fcfdf9", "axes.facecolor": "#fcfdf9",
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
fig, ax = plt.subplots(figsize=(10, 4.6), layout="constrained")
ax.plot(x, density(x), color="#306456", lw=2.4)
ax.fill_between(x, density(x), color="#e4eee7")
ax.fill_between(tail, density(tail), color="#ddaa81", label="Worst 5% of daily returns")
ax.axvline(var, color="#aa582d", ls="--", lw=1.8)
ax.axvline(es, color="#315d94", ls="--", lw=1.8)
ax.annotate("VaR threshold\n−1.59%", xy=(var, 0.13), xytext=(-0.65, 0.25),
            arrowprops={"arrowstyle": "-", "color": "#aa582d"}, color="#aa582d")
ax.annotate("ES: average return\nin the tail, −2.01%", xy=(es, 0.08), xytext=(-4.1, 0.22),
            arrowprops={"arrowstyle": "-", "color": "#315d94"}, color="#315d94")
ax.set(xlim=(-4.3,4.3), ylim=(0,0.46), xlabel="Daily return (%)", ylabel="Probability density")
ax.set_title("The threshold and the tail average", loc="left", fontweight="bold", pad=15)
ax.legend(loc="upper right", frameon=False, fontsize=10)
fig.savefig(DEST / "finance-var-es-tail.svg", metadata={"Date": None})
plt.close(fig)

print(f"95% signed-return VaR={var:.6f}%; ES={es:.6f}%")
