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
    return (f'<circle cx="{x}" cy="{y}" r="30" fill="{PAPER}" stroke="{INK}" stroke-width="1.5"/>'
            + text(x, y + 7, variable(letter, location), size=25))


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
    height = 435 if sem else 365
    description = {
        'sar': 'Local covariates enter local outcomes. Outcomes interact across neighbouring locations.',
        'slx': 'Covariates enter outcomes locally and across locations. There is no outcome feedback.',
        'sem': 'Innovations enter errors, errors interact across locations, and errors enter local outcomes.',
        'sdm': 'Covariate spillovers and outcome interaction operate together.',
    }[model]
    parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="{height}" viewBox="0 0 600 {height}" role="img" aria-labelledby="title desc">
<title id="title">{model.upper()} dependence channels</title>
<desc id="desc">{escape(description)} Other neighbouring locations are omitted.</desc>
<defs>''']
    for name, colour in [('local', INK), ('spatial', BRONZE)]:
        parts.append(f'<marker id="{name}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M1 1 L9 5 L1 9" fill="none" stroke="{colour}" stroke-width="1.4"/></marker>')
    parts += ['</defs>', f'<rect width="600" height="{height}" fill="{PAPER}"/>',
              '<g font-family="Inter, Arial, sans-serif">',
              text(110, 30, 'Location A', size=19, colour=MUTED),
              text(490, 30, 'Location B', size=19, colour=MUTED),
              f'<path d="M300 55 V{height-65}" stroke="{LINE}" stroke-width="1"/>']

    # Draw links before nodes so arrow shafts never run through variable labels.
    if model in ('sar', 'sdm'):
        parts += [arrow(146, 110, 454, 110, spatial=True, both=True),
                  coefficient(300, 87, 'ρw')]
    if model in ('slx', 'sdm'):
        parts += [arrow(140, 255, 459, 124, spatial=True, dashed=True),
                  arrow(460, 255, 141, 124, spatial=True, dashed=True),
                  coefficient(203, 158, 'θ<tspan baseline-shift="sub" font-size="65%">k</tspan>w'),
                  coefficient(397, 158, 'θ<tspan baseline-shift="sub" font-size="65%">k</tspan>w')]
    if sem:
        parts += [arrow(146, 270, 454, 270, spatial=True, both=True),
                  coefficient(300, 247, 'λw')]
    for x, loc in [(110, 'A'), (490, 'B')]:
        parts += [arrow(x, 234, x, 146), node(x, 110, 'y', loc),
                  node(x, 270, 'u' if sem else 'x', loc)]
        if sem:
            parts += [arrow(x, 354, x, 306), text(x, 389, variable('ε', loc), size=25)]
        else:
            parts += [text(x-27 if loc == 'A' else x+27, 198,
                           'β<tspan baseline-shift="sub" font-size="65%">k</tspan>', size=21,
                           anchor='end' if loc == 'A' else 'start')]
    if sem:
        parts += [text(300, 426, 'Spatial dependence acts through u', size=18, colour=MUTED)]
    elif model == 'sar':
        parts += [text(300, 350, 'Outcome feedback', size=18, colour=MUTED)]
    elif model == 'slx':
        parts += [text(300, 350, 'Covariate spillovers, no outcome feedback', size=18, colour=MUTED)]
    else:
        parts += [text(300, 350, 'Covariate spillovers + outcome feedback', size=18, colour=MUTED)]
    parts += ['</g>', '</svg>']
    (OUT / f'econometrics-spatial-{model}-channels.svg').write_text('\n'.join(parts)+'\n', encoding='utf-8')
