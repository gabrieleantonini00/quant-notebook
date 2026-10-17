"""Generate responsive CBOW network schematics using the notebook's palette."""
from html import escape
from pathlib import Path
import re

OUT = Path(__file__).resolve().parent
INK = '#182b42'
BRONZE = '#86623f'
PAPER = '#f6f2e9'
LINE = '#bcb4a5'
MUTED = '#626d77'


def text(x, y, label, size=16, color=INK, math=False, weight=None):
    family = 'Georgia, serif' if math else 'Inter, Segoe UI, sans-serif'
    attrs = f'font-family="{family}" font-size="{size}" fill="{color}"'
    if math:
        attrs += ' font-style="italic"'
    if weight:
        attrs += f' font-weight="{weight}"'
    content = escape(label)
    if math:
        content = re.sub(r'_([A-Za-z])', rf'<tspan baseline-shift="sub" font-size="{size*.7:g}">\1</tspan>', content)
    return f'<text x="{x}" y="{y}" text-anchor="middle" {attrs}>{content}</text>'


def path(d, color=LINE, width=1.2, arrow=False):
    marker = ' marker-end="url(#arrow)"' if arrow else ''
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"{marker}/>'


def neuron(x, y, label, accent=False, radius=17):
    color = BRONZE if accent else INK
    return (f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{PAPER}" stroke="{color}" stroke-width="1.5"/>'
            + text(x, y+5, label, 16, color, math=True))


def onehot(cx, y, label, active, small=False):
    spacing, radius, font = (20, 10, 12) if small else (28, 12, 14)
    xs = [cx-spacing*1.5, cx-spacing*.5, cx+spacing*1.5]
    result = [text(cx, y-29, label, 17, math=True)]
    for i, x in enumerate(xs):
        fill, color = (BRONZE, PAPER) if i == active else (PAPER, MUTED)
        result.append(f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{fill}" stroke="{LINE if i != active else BRONZE}"/>')
        result.append(text(x, y+4, '1' if i == active else '0', font, color))
    result.append(text(cx+spacing*.5, y+4, '⋯', font, MUTED))
    return ''.join(result)


def annotation(cx, y, lines, width=140):
    height = 24*len(lines)+10
    result = [f'<rect x="{cx-width/2}" y="{y-19}" width="{width}" height="{height}" fill="{PAPER}"/>']
    for i, label in enumerate(lines):
        result.append(text(cx, y+i*24, label, 16 if i==0 else 14, BRONZE if i==0 else MUTED, math=i==0))
    return ''.join(result)


def desktop():
    elements = [
        text(100, 30, 'CONTEXT', 13, MUTED),
        text(370, 30, 'MEAN EMBEDDING', 13, MUTED),
        text(570, 30, 'LOGITS', 13, MUTED),
        text(751, 30, 'TARGET PROBABILITY', 12, MUTED),
    ]
    input_ys = [110, 230, 350]
    hidden_ys = [145, 230, 315]
    output_ys = [95, 185, 285, 375]
    for y in input_ys:
        for h in hidden_ys:
            elements.append(path(f'M 162 {y} L 352 {h}', width=1))
    for h in hidden_ys:
        for u in output_ys:
            elements.append(path(f'M 388 {h} L 552 {u}', width=1))
    for y, label, active in zip(input_ys, ['x₁', 'xᵢ', 'x_C'], [1, 0, 2]):
        elements.append(onehot(100, y, label, active))
    for y, label in zip(hidden_ys, ['h₁', 'h₂', 'h_d']):
        elements.append(neuron(370, y, label))
    elements.append(text(370, 279, '⋮', 22, MUTED))
    for y, label in zip(output_ys, ['u₁', 'u₂', 'u_c', 'u_D']):
        elements.append(neuron(570, y, label, accent=label=='u_c'))
    elements.append(text(570, 242, '⋮', 22, MUTED))
    elements.append(annotation(256, 198, ['W shared', 'D × d'], width=116))
    elements.append(annotation(470, 206, ['W′', 'd × D'], width=78))
    elements.append(path('M 604 75 L 616 75 L 616 395 L 604 395'))
    elements.append(path('M 616 235 L 690 235', BRONZE, 1.5, arrow=True))
    elements.append(text(654, 212, 'softmax', 14, BRONZE))
    elements.append(text(757, 242, 'P(w_c | context)', 18, math=True))
    elements.append(path('M 697 258 L 818 258'))
    elements.append(text(757, 282, 'central word', 13, MUTED))
    elements.extend([
        text(100, 422, 'xᵢ ∈ ℝ¹ˣᴰ', 16, math=True),
        text(370, 390, 'h = (1/C) ∑ᵢ xᵢW', 18, math=True),
        text(370, 422, 'h ∈ ℝ¹ˣᵈ', 16, math=True),
        text(570, 422, 'u = hW′ ∈ ℝ¹ˣᴰ', 16, math=True),
    ])
    return 840, 450, ''.join(elements)


def mobile():
    elements = [text(180, 24, 'CONTEXT ONE-HOT VECTORS', 13, MUTED)]
    input_xs = [60, 180, 300]
    hidden_xs = [90, 150, 270]
    output_xs = [60, 140, 220, 300]
    for x in input_xs:
        for h in hidden_xs:
            elements.append(path(f'M {x} 102 L {h} 233', width=1))
    for h in hidden_xs:
        for u in output_xs:
            elements.append(path(f'M {h} 267 L {u} 413', width=1))
    for x, label, active in zip(input_xs, ['x₁', 'xᵢ', 'x_C'], [1, 0, 2]):
        elements.append(onehot(x, 88, label, active, small=True))
    elements.append(annotation(180, 150, ['W shared', 'D × d'], width=130))
    elements.append(annotation(180, 211, ['Mean embedding h'], width=208))
    for x, label in zip(hidden_xs, ['h₁', 'h₂', 'h_d']):
        elements.append(neuron(x, 250, label))
    elements.append(text(210, 255, '⋯', 20, MUTED))
    elements.append(annotation(180, 298, ['h = (1/C) ∑ᵢ xᵢW'], width=286))
    elements.append(annotation(180, 350, ['W′', 'u = hW′,  d × D'], width=170))
    for x, label in zip(output_xs, ['u₁', 'u₂', 'u_c', 'u_D']):
        elements.append(neuron(x, 430, label, accent=label=='u_c'))
    elements.append(text(180, 436, '⋯', 18, MUTED))
    elements.append(path('M 40 458 L 40 470 L 320 470 L 320 458'))
    elements.append(path('M 180 470 L 180 545', BRONZE, 1.5, arrow=True))
    elements.append(annotation(180, 509, ['softmax'], width=104))
    elements.append(text(180, 580, 'P(w_c | context)', 22, math=True))
    elements.append(text(180, 609, 'central word', 14, MUTED))
    return 360, 636, ''.join(elements)


def save(name, layout):
    width, height, content = layout()
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">CBOW network: context words to the central-word probability</title>
<desc id="desc">One-hot context vectors share the input matrix W. Their projections are averaged into the d-dimensional vector h. A separate matrix W prime produces D vocabulary logits. Softmax normalizes the complete logit vector to obtain word probabilities. Only a few coordinates are drawn.</desc>
<defs><marker id="arrow" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 0 L 8 4 L 0 8 Z" fill="{BRONZE}"/></marker></defs>
<rect width="{width}" height="{height}" fill="{PAPER}"/>
{content}
</svg>
'''
    (OUT / name).write_text(svg, encoding='utf-8')


if __name__ == '__main__':
    save('nlp-cbow-network.svg', desktop)
    save('nlp-cbow-network-mobile.svg', mobile)
    print('Generated CBOW network diagrams for desktop and mobile.')
