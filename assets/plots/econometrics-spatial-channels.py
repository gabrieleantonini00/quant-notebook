"""Draw comparable SVG equation-dependency diagrams for SAR, SLX, SEM and SDM.

A and B are the adjacent pair in the notebook's four-location network.
Other neighbours are omitted, not removed from the underlying model.
No raster assets or third-party dependencies are required.
"""
from pathlib import Path
from html import escape

OUT = Path(__file__).resolve().parent
PAPER, INK, BRONZE, MUTED, LINE = '#f6f2e9', '#182b42', '#86623f', '#626d77', '#dcd6ca'


def text(x, y, label, size=22, colour=INK, anchor='middle'):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" fill="{colour}">{label}</text>'


def variable(letter, subscript):
    return f'<tspan font-style="italic">{letter}</tspan><tspan baseline-shift="sub" font-size="65%">{subscript}</tspan>'


def node(x, y, letter, location):
    labels = {'y': ['House prices'], 'x': ['Local services'],
              'u': ['Unobserved', 'price component']}[letter]
    parts = [f'<rect x="{x-90}" y="{y-43}" width="180" height="86" rx="9" fill="{PAPER}" stroke="{INK}" stroke-width="1.3"/>']
    for line, label in enumerate(labels):
        parts.append(text(x, y - (21 if len(labels) == 2 else 11) + 20 * line,
                          label, size=18 if len(labels) == 2 else 20))
    parts.append(text(x, y + 23, variable(letter, location), size=24))
    return ''.join(parts)


def arrow(x1, y1, x2, y2, spatial=False, dashed=False, both=False):
    colour = BRONZE if spatial else INK
    marker = 'spatial' if spatial else 'local'
    dash = ' stroke-dasharray="7 5"' if dashed else ''
    start = f' marker-start="url(#{marker})"' if both else ''
    return (f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="{colour}" stroke-width="2"'
            f'{dash}{start} marker-end="url(#{marker})"/>')


def coefficient(x, y, label):
    # Paper under a label keeps crossing lines visually separate from the text.
    return (f'<rect x="{x-30}" y="{y-20}" width="60" height="29" fill="{PAPER}"/>'
            + text(x, y, label, size=20, colour=BRONZE))


for model in ('sar', 'slx', 'sem', 'sdm'):
    sem = model == 'sem'
    height = 535 if sem else 445
    description = {
        'sar': 'Local services affect local house prices. House prices interact across neighbouring areas.',
        'slx': 'Local services affect house prices locally and in the neighbouring area. There is no price feedback.',
        'sem': 'Local innovations enter unobserved price components, which interact across areas and enter house prices.',
        'sdm': 'Spillovers from local services and interaction between house prices operate together.',
    }[model]
    parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="560" height="{height}" viewBox="0 0 560 {height}" role="img" aria-labelledby="title desc">
<title id="title">{model.upper()} dependence channels</title>
<desc id="desc">{escape(description)} Other neighbouring locations are omitted.</desc>
<defs>''']
    for name, colour in [('local', INK), ('spatial', BRONZE)]:
        parts.append(f'<marker id="{name}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M1 1 L9 5 L1 9" fill="none" stroke="{colour}" stroke-width="1.4"/></marker>')
    parts += ['</defs>', f'<rect width="560" height="{height}" fill="{PAPER}"/>',
              '<g font-family="Inter, Arial, sans-serif">',
              text(110, 30, 'Neighbourhood A', size=19, colour=MUTED),
              text(450, 30, 'Neighbourhood B', size=19, colour=MUTED)]

    # Draw links before nodes so arrow shafts never run through variable labels.
    if model in ('sar', 'sdm'):
        parts += [arrow(206, 120, 354, 120, spatial=True, both=True),
                  coefficient(280, 96, 'ρw')]
    if model in ('slx', 'sdm'):
        parts += [arrow(200, 300, 354, 145, spatial=True, dashed=True),
                  arrow(360, 300, 206, 145, spatial=True, dashed=True),
                  coefficient(238, 192, 'θ<tspan baseline-shift="sub" font-size="65%">k</tspan>w'),
                  coefficient(322, 192, 'θ<tspan baseline-shift="sub" font-size="65%">k</tspan>w')]
    if sem:
        parts += [arrow(206, 330, 354, 330, spatial=True, both=True),
                  coefficient(280, 306, 'λw')]
    for x, loc in [(110, 'A'), (450, 'B')]:
        parts += [arrow(x, 281, x, 169), node(x, 120, 'y', loc),
                  node(x, 330, 'u' if sem else 'x', loc)]
        if sem:
            parts += [arrow(x, 426, x, 379), text(x, 454, 'Local innovation', size=18),
                      text(x, 483, variable('ε', loc), size=24)]
        else:
            parts += [text(x-25 if loc == 'A' else x+25, 235,
                           'β<tspan baseline-shift="sub" font-size="65%">k</tspan>', size=21,
                           anchor='end' if loc == 'A' else 'start')]
    if sem:
        parts += [text(280, 526, 'Unobserved components are spatially linked', size=18, colour=MUTED)]
    elif model == 'sar':
        parts += [text(280, 428, 'House prices influence each other', size=18, colour=MUTED)]
    elif model == 'slx':
        parts += [text(280, 420, 'Services in A also affect prices in B, and vice versa', size=18, colour=MUTED),
                  text(280, 440, 'No price-to-price feedback', size=18, colour=MUTED)]
    else:
        parts += [text(280, 428, 'Service spillovers + house-price feedback', size=18, colour=MUTED)]
    parts += ['</g>', '</svg>']
    (OUT / f'econometrics-spatial-{model}-channels.svg').write_text('\n'.join(parts)+'\n', encoding='utf-8')
