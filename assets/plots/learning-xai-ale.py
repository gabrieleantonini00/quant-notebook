"""Build a schematic of the two steps behind a one-feature ALE curve."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
LOCAL_DEPS = ROOT / '.qa' / 'plot-deps'
if LOCAL_DEPS.is_dir():
    sys.path.insert(0, str(LOCAL_DEPS))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


plt.rcParams.update({
    'font.family': 'Segoe UI',
    'font.size': 10.5,
    'axes.titlesize': 12,
    'axes.labelsize': 10.5,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.edgecolor': '#cbd5e1',
    'axes.labelcolor': '#334155',
    'text.color': '#0f172a',
    'xtick.color': '#64748b',
    'ytick.color': '#64748b',
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'svg.fonttype': 'none',
    'svg.hashsalt': 'learning-xai-ale',
})

# Each bin is assumed to contain the same number of illustrative applicants.
# Values are average differences in predicted default risk, in percentage points.
edges = [20, 30, 40, 45, 55, 65]
local_change = [2, 4, 3, 9, 6]
midpoints = [(left + right) / 2 for left, right in zip(edges[:-1], edges[1:])]
widths = [right - left for left, right in zip(edges[:-1], edges[1:])]

cumulative = [0]
for change in local_change:
    cumulative.append(cumulative[-1] + change)

# With a linear segment in each equally populated bin, the mean at the bin
# midpoints is the average effect. Subtract it to center ALE at zero.
mean_effect = sum((left + right) / 2 for left, right in zip(cumulative[:-1], cumulative[1:])) / len(local_change)
centered = [value - mean_effect for value in cumulative]
assert local_change[2] == 3
assert abs(sum((left + right) / 2 for left, right in zip(centered[:-1], centered[1:])) / len(local_change)) < 1e-10

fig, (ax_local, ax_ale) = plt.subplots(2, 1, figsize=(8.5, 5.8), sharex=True, layout='constrained')
fig.suptitle('How ALE is built', x=0.09, ha='left', fontsize=15, fontweight='semibold')

colors = ['#60a5a0', '#60a5a0', '#51459b', '#60a5a0', '#60a5a0']
ax_local.bar(midpoints, local_change, width=[width * 0.78 for width in widths],
             color=colors, edgecolor='none', zorder=3)
for x, value in zip(midpoints, local_change):
    ax_local.text(x, value + 0.35, f'+{value} pp', ha='center', va='bottom', fontsize=9.5, color='#334155')
ax_local.set_title('1  Average the prediction change within each observed interval', loc='left', pad=8)
ax_local.set(ylabel='Local change (pp)', ylim=(0, 11), yticks=[0, 5, 10])
ax_local.grid(axis='y', color='#e2e8f0', linewidth=0.8, zorder=0)

ax_ale.plot(edges, centered, color='#51459b', linewidth=2.9, marker='o', markersize=4.5)
ax_ale.axhline(0, color='#94a3b8', linestyle='--', linewidth=1)
ax_ale.set_title('2  Add the local changes, then center the curve at zero', loc='left', pad=8)
ax_ale.set(xlim=(19, 66), ylim=(-12, 18), ylabel='ALE effect (pp)', xlabel='Debt-to-income ratio (%)',
           xticks=edges, yticks=[-10, 0, 10])
ax_ale.grid(axis='y', color='#e2e8f0', linewidth=0.8)
ax_ale.text(64, -6.5, 'Not an individual predicted risk', ha='right', color='#64748b', fontsize=9.5)

output = Path(__file__).resolve().parent
qa = ROOT / '.qa'
qa.mkdir(exist_ok=True)
fig.savefig(output / 'learning-xai-ale.svg', metadata={'Date': None}, bbox_inches='tight')
fig.savefig(qa / 'learning-xai-ale.png', dpi=160, bbox_inches='tight')
plt.close(fig)
print('Generated illustrative ALE construction figure.')
