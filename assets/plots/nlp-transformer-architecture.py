"""Generate desktop and mobile diagrams of the original post-norm Transformer."""
from pathlib import Path
import runpy

OUT = Path(__file__).resolve().parent
COMMON = runpy.run_path(str(OUT / 'nlp-cbow-network.py'))
text, path = COMMON['text'], COMMON['path']
INK, BRONZE, PAPER, LINE, MUTED = (COMMON[k] for k in ('INK', 'BRONZE', 'PAPER', 'LINE', 'MUTED'))


def box(cx, y, width, height, labels, accent=False, size=15):
    border = BRONZE if accent else LINE
    elements = [f'<rect x="{cx-width/2:g}" y="{y}" width="{width}" height="{height}" fill="{PAPER}" stroke="{border}" stroke-width="1.2"/>']
    first = y + height/2 - (len(labels)-1)*10 + 5
    for i, label in enumerate(labels):
        baseline = first+i*20
        if label == '× √d_model':
            elements.append(f'<text x="{cx}" y="{baseline}" text-anchor="middle" font-family="Georgia, serif" font-size="{size}" fill="{INK}">× √d<tspan baseline-shift="sub" font-size="{size*.7:g}">model</tspan></text>')
        else:
            elements.append(text(cx, baseline, label, size, INK))
    return ''.join(elements)


def plus(cx, cy):
    return (f'<circle cx="{cx}" cy="{cy}" r="13" fill="{PAPER}" stroke="{BRONZE}" stroke-width="1.4"/>'
            + text(cx, cy+5, '+', 20, BRONZE))


def frame(x, y, w, h):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{LINE}" stroke-width=".9" stroke-dasharray="4 5"/>'


def flow(x, start, end):
    return path(f'M {x} {start} L {x} {end}', INK, 1.25, arrow=True)


def bypass(cx, start, side, target, edge):
    return path(f'M {cx} {start} H {side} V {target} H {edge}', MUTED, 1.1, arrow=True)


def desktop():
    e, d = 225, 622
    parts = [frame(92, 282, 252, 298), frame(489, 187, 252, 393)]
    parts.extend([
        text(164, 270, 'ENCODER', 13, MUTED), text(319, 270, '× N', 16, BRONZE),
        text(555, 175, 'DECODER', 13, MUTED), text(716, 175, '× N', 16, BRONZE),
        text(e, 723, 'Source tokens', 16), text(d, 723, 'Target tokens, shifted right', 15),
        flow(e, 704, 688), flow(d, 704, 688),
        flow(e, 644, 623), flow(d, 644, 623),
        flow(e, 597, 536), flow(d, 597, 536),
        flow(e, 480, 462), flow(e, 430, 402), flow(e, 354, 336),
        flow(d, 488, 470), flow(d, 440, 416), flow(d, 368, 350),
        flow(d, 320, 296), flow(d, 248, 230), flow(d, 200, 144),
        flow(d, 106, 82), flow(d, 50, 35),
        bypass(e, 550, 112, 446, 140), bypass(e, 416, 112, 320, 140),
        bypass(d, 550, 724, 455, 707), bypass(d, 429, 724, 335, 707),
        bypass(d, 309, 724, 215, 707),
        path(f'M {e} 304 V 224 H 420 V 392 H 537', BRONZE, 1.7, arrow=True),
        text(e, 209, 'Encoder memory', 16, BRONZE),
        text(470, 381, 'K, V', 15, BRONZE), text(638, 433, 'Q', 14, BRONZE),
        text(d, 25, 'Next-token probabilities', 17),
    ])
    for cx in [e, d]:
        parts.append(box(cx, 644, 200, 44, ['Token Embedding', '× √d_model'], size=15))
        parts.append(plus(cx, 610))
        parts.append(path(f'M {cx-113} 610 H {cx-14}', BRONZE, 1.2, arrow=True))
        parts.append(text(cx-122, 580, 'Positional', 12, MUTED))
        parts.append(text(cx-122, 597, 'encoding', 12, MUTED))
    parts.extend([
        box(e, 480, 170, 56, ['Multi-Head', 'Self-Attention'], accent=True),
        box(e, 430, 170, 32, ['Add & Norm'], size=15),
        box(e, 354, 170, 48, ['Position-Wise', 'Feed-Forward']),
        box(e, 304, 170, 32, ['Add & Norm'], size=15),
        box(d, 488, 170, 48, ['Masked Multi-Head', 'Self-Attention'], accent=True, size=15),
        box(d, 440, 170, 30, ['Add & Norm'], size=15),
        box(d, 368, 170, 48, ['Multi-Head', 'Cross-Attention'], accent=True),
        box(d, 320, 170, 30, ['Add & Norm'], size=15),
        box(d, 248, 170, 48, ['Position-Wise', 'Feed-Forward']),
        box(d, 200, 170, 30, ['Add & Norm'], size=15),
        box(d, 106, 170, 38, ['Linear Projection']),
        box(d, 50, 170, 32, ['Softmax']),
    ])
    return 840, 740, ''.join(parts)


def mobile():
    cx = 180
    parts = [frame(60, 174, 240, 238), frame(60, 638, 240, 352)]
    parts.extend([
        text(cx, 27, 'Source tokens', 17), text(117, 164, 'ENCODER', 13, MUTED),
        text(279, 164, '× N', 16, BRONZE),
        text(cx, 494, 'Target tokens, shifted right', 16),
        text(117, 626, 'DECODER', 13, MUTED), text(279, 626, '× N', 16, BRONZE),
        flow(cx, 35, 55), flow(cx, 99, 115), flow(cx, 141, 187),
        flow(cx, 237, 255), flow(cx, 285, 303), flow(cx, 349, 367),
        flow(cx, 397, 425),
        bypass(cx, 179, 72, 270, 92), bypass(cx, 294, 72, 382, 92),
        path('M 80 443 H 28 V 789 H 92', BRONZE, 1.7, arrow=True),
        text(44, 776, 'K, V', 13, BRONZE),
        flow(cx, 502, 520), flow(cx, 564, 577), flow(cx, 603, 648),
        flow(cx, 698, 716), flow(cx, 746, 764), flow(cx, 814, 832),
        flow(cx, 862, 880), flow(cx, 926, 944), flow(cx, 974, 1015),
        flow(cx, 1051, 1073), flow(cx, 1105, 1130),
        bypass(cx, 632, 288, 731, 268), bypass(cx, 755, 288, 847, 268),
        bypass(cx, 871, 288, 959, 268), text(197, 758, 'Q', 14, BRONZE),
    ])
    for y in [55, 520]:
        parts.append(box(cx, y, 200, 44, ['Token Embedding', '× √d_model'], size=15))
    for y in [128, 590]:
        parts.append(plus(cx, y))
        parts.append(path(f'M 107 {y} H 166', BRONZE, 1.2, arrow=True))
        parts.append(text(71, y-6, 'Positional', 12, MUTED))
        parts.append(text(71, y+11, 'encoding', 12, MUTED))
    parts.extend([
        box(cx, 187, 176, 50, ['Multi-Head', 'Self-Attention'], accent=True),
        box(cx, 255, 176, 30, ['Add & Norm'], size=15),
        box(cx, 303, 176, 46, ['Position-Wise', 'Feed-Forward']),
        box(cx, 367, 176, 30, ['Add & Norm'], size=15),
        box(cx, 425, 200, 36, ['Encoder memory'], accent=True),
        box(cx, 648, 176, 50, ['Masked Multi-Head', 'Self-Attention'], accent=True, size=15),
        box(cx, 716, 176, 30, ['Add & Norm'], size=15),
        box(cx, 764, 176, 50, ['Multi-Head', 'Cross-Attention'], accent=True),
        box(cx, 832, 176, 30, ['Add & Norm'], size=15),
        box(cx, 880, 176, 46, ['Position-Wise', 'Feed-Forward']),
        box(cx, 944, 176, 30, ['Add & Norm'], size=15),
        box(cx, 1015, 176, 36, ['Linear Projection']),
        box(cx, 1073, 176, 32, ['Softmax']),
        text(cx, 1152, 'Next-token probabilities', 17),
    ])
    return 360, 1176, ''.join(parts)


def save(name, layout):
    width, height, content = layout()
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">Transformer encoder and decoder architecture</title>
<desc id="desc">The source token embeddings plus positional encodings enter N encoder blocks. Each block applies self-attention and a feed-forward network, with residual connections and post-layer normalization. Right-shifted target embeddings plus positional encodings enter N decoder blocks with causal self-attention, cross-attention to the final encoder memory, and a feed-forward network. Decoder states provide the cross-attention queries, while encoder memory supplies keys and values to every decoder layer. A linear projection and softmax produce next-token probabilities.</desc>
<defs><marker id="arrow" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 0 L 8 4 L 0 8 Z" fill="{BRONZE}"/></marker></defs>
<rect width="{width}" height="{height}" fill="{PAPER}"/>
{content}
</svg>
'''
    (OUT / name).write_text(svg, encoding='utf-8')


if __name__ == '__main__':
    save('nlp-transformer-architecture.svg', desktop)
    save('nlp-transformer-architecture-mobile.svg', mobile)
    print('Generated encoder-decoder Transformer diagrams for desktop and mobile.')
