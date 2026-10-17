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


MOBILE = '--mobile' in sys.argv
SUFFIX = '-mobile' if MOBILE else ''

plt.rcParams.update({
    'font.family': ['DejaVu Sans', 'Arial', 'sans-serif'],
    'font.size': 14 if MOBILE else 15.75,
    'axes.titlesize': 15 if MOBILE else 18,
    'axes.labelsize': 14 if MOBILE else 15.75,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.edgecolor': '#bcb4a5',
    'axes.labelcolor': '#3e4e5f',
    'text.color': '#182b42',
    'xtick.color': '#626d77',
    'ytick.color': '#626d77',
    'figure.facecolor': '#f6f2e9',
    'axes.facecolor': '#f6f2e9',
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

fig, (ax_local, ax_ale) = plt.subplots(2, 1, figsize=(4.2, 7.8) if MOBILE else (8.5, 6.7), sharex=True, layout='constrained')

colors = ['#9ba9b5', '#9ba9b5', '#86623f', '#9ba9b5', '#9ba9b5']
ax_local.bar(midpoints, local_change, width=[width * 0.78 for width in widths],
             color=colors, edgecolor='none', zorder=3)
for x, value in zip(midpoints, local_change):
    ax_local.text(x, value + 0.35, f'+{value} pp', ha='center', va='bottom', fontsize=12 if MOBILE else 14.25, color='#3e4e5f')
ax_local.set_title('1  Local differences', loc='left', pad=8)
ax_local.set(ylabel='Local change (pp)', ylim=(0, 11), yticks=[0, 5, 10])
ax_local.grid(axis='y', color='#dcd6ca', linewidth=0.8, zorder=0)

ax_ale.plot(edges, centered, color='#86623f', linewidth=2.9, marker='o', markersize=4.5)
ax_ale.axhline(0, color='#7b838b', linestyle='--', linewidth=1)
ax_ale.set_title('2  Accumulate and centre', loc='left', pad=8)
ax_ale.set(xlim=(19, 66), ylim=(-12, 18), ylabel='ALE effect (pp)', xlabel='Debt-to-income ratio (%)',
           xticks=edges, yticks=[-10, 0, 10])
ax_ale.grid(axis='y', color='#dcd6ca', linewidth=0.8)
ax_ale.tick_params(axis='x', labelrotation=45 if MOBILE else 0)

output = Path(__file__).resolve().parent
qa = ROOT / '.qa'
qa.mkdir(exist_ok=True)
fig.savefig(output / ('learning-xai-ale' + SUFFIX + '.svg'), metadata={'Date': None}, bbox_inches='tight')
svg = output / ('learning-xai-ale' + SUFFIX + '.svg')
svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines()) + '\n', encoding='utf-8')
fig.savefig(qa / ('learning-xai-ale' + SUFFIX + '.png'), dpi=160, bbox_inches='tight')
plt.close(fig)
print('Generated illustrative ALE construction figure.')
