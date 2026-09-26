"""Rebuild the selected, publicly disclosed LLM parameter comparison.

Figures are manufacturer-reported and intentionally not an annual average.
For MoE models, ``active`` means parameters used per token, not a smaller
checkpoint. Sources are the official model releases below.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
LOCAL_DEPS = ROOT / '.qa' / 'plot-deps'
if LOCAL_DEPS.is_dir():
    sys.path.insert(0, str(LOCAL_DEPS))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


MODELS = [
    {'year': 2019, 'name': 'GPT-2', 'total': 1.5, 'active': None,
     'source': 'https://openai.com/index/gpt-2-1-5b-release/'},
    {'year': 2020, 'name': 'GPT-3', 'total': 175, 'active': None,
     'source': 'https://openai.com/index/language-models-are-few-shot-learners/'},
    {'year': 2023, 'name': 'Llama 2', 'total': 70, 'active': None,
     'source': 'https://ai.meta.com/research/publications/llama-2-open-foundation-and-fine-tuned-chat-models/'},
    {'year': 2024, 'name': 'Llama 3.1', 'total': 405, 'active': None,
     'source': 'https://ai.meta.com/research/publications/the-llama-3-herd-of-models'},
    {'year': 2025, 'name': 'gpt-oss-120b', 'total': 117, 'active': 5.1,
     'source': 'https://openai.com/index/introducing-gpt-oss/'},
    {'year': 2025, 'name': 'Llama 4 Maverick', 'total': 400, 'active': 17,
     'source': 'https://ai.meta.com/blog/llama-4-multimodal-intelligence/'},
    {'year': 2026, 'name': 'Gemma 4 31B', 'total': 31, 'active': None,
     'source': 'https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/'},
    {'year': 2026, 'name': 'Gemma 4 26B MoE', 'total': 26, 'active': 3.8,
     'source': 'https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/'},
    {'year': 2026, 'name': 'Qwen3.5-397B', 'total': 397, 'active': 17,
     'source': 'https://huggingface.co/Qwen/Qwen3.5-397B-A17B'},
]
assert all(model['total'] > 0 and
           (model['active'] is None or 0 < model['active'] < model['total'])
           for model in MODELS)

plt.rcParams.update({
    'font.family': 'Segoe UI',
    'font.size': 10.5,
    'axes.titlesize': 15,
    'axes.labelsize': 10.5,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.spines.left': False,
    'axes.edgecolor': '#cbd5e1',
    'axes.labelcolor': '#334155',
    'text.color': '#0f172a',
    'xtick.color': '#64748b',
    'ytick.color': '#334155',
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'svg.fonttype': 'none',
    'svg.hashsalt': 'nlp-llm-parameters',
})

fig, ax = plt.subplots(figsize=(9.2, 6.35), layout='constrained')
ax.set_xscale('log')
ax.set_xlim(1, 950)
ax.set_ylim(-0.7, len(MODELS) - 0.3)
ax.set_xticks([1, 10, 100])
ax.set_xticklabels(['1B', '10B', '100B'])
ax.grid(axis='x', color='#e2e8f0', linewidth=0.85, which='major')
ax.tick_params(axis='y', length=0, pad=12)
ax.set_xlabel('Parameters (billions, log scale)', labelpad=10)
ax.set_title('How large are published language models?', loc='left', pad=30, fontweight='semibold')

dense_color = '#334e68'
active_color = '#25877f'
total_color = '#54459b'
ys = list(reversed(range(len(MODELS))))
ax.set_yticks(ys)
ax.set_yticklabels([f"{model['year']}   {model['name']}" for model in MODELS])

for y, model in zip(ys, MODELS):
    total = model['total']
    active = model['active']
    ax.axhline(y, color='#f1f5f9', linewidth=0.8, zorder=0)
    if active is None:
        ax.scatter(total, y, s=105, color=dense_color, zorder=3)
        ax.annotate(f'{total:g}B', (total, y), xytext=(9, 0), textcoords='offset points',
                    va='center', color=dense_color, fontsize=9.5)
    else:
        ax.plot([active, total], [y, y], color='#c4bce2', linewidth=3, solid_capstyle='round', zorder=1)
        ax.scatter(active, y, s=92, color=active_color, zorder=3)
        ax.scatter(total, y, s=92, color=total_color, zorder=3)
        ax.annotate(f'{active:g} active  /  {total:g} total', (total, y),
                    xytext=(9, 0), textcoords='offset points', va='center',
                    color='#4b5563', fontsize=9.1)

legend = [
    Line2D([0], [0], marker='o', linestyle='none', color=dense_color, label='Dense: total = active', markersize=8),
    Line2D([0], [0], marker='o', linestyle='none', color=active_color, label='MoE: active per token', markersize=8),
    Line2D([0], [0], marker='o', linestyle='none', color=total_color, label='MoE: total', markersize=8),
]
ax.legend(handles=legend, loc='upper left', bbox_to_anchor=(0, 1.04),
          ncol=3, frameon=False, fontsize=9.1, handletextpad=0.4, columnspacing=1.1)

output = Path(__file__).resolve().parent
qa = ROOT / '.qa'
qa.mkdir(exist_ok=True)
sources = '\n'.join(f"{m['year']} {m['name']}: {m['source']}" for m in MODELS)
fig.savefig(output / 'nlp-llm-parameters.svg',
            metadata={'Date': None, 'Description': 'Official sources:\n' + sources},
            bbox_inches='tight')
fig.savefig(qa / 'nlp-llm-parameters.png', dpi=160, bbox_inches='tight')
plt.close(fig)
print('Generated selected LLM parameter comparison from published counts.')
