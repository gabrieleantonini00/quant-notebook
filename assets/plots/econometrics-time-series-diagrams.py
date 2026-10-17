"""Named-variable diagrams for lagged VAR prediction and VECM adjustment."""
from pathlib import Path

OUT = Path(__file__).resolve().parent
PAPER, INK, BRONZE, MUTED = '#f6f2e9', '#182b42', '#86623f', '#626d77'


def text(x, y, label, size=20, colour=INK):
    return f'<text x="{x}" y="{y}" text-anchor="middle" font-size="{size}" fill="{colour}">{label}</text>'


def symbol(letter, sub):
    return f'<tspan font-style="italic">{letter}</tspan><tspan baseline-shift="sub" font-size="65%">{sub}</tspan>'


def box(x, y, label, notation, width=180, height=84):
    return (f'<rect x="{x-width/2}" y="{y-height/2}" width="{width}" height="{height}" rx="9" fill="{PAPER}" stroke="{INK}" stroke-width="1.3"/>'
            + text(x,y-10,label,size=19) + text(x,y+23,notation,size=24))


def arrow(x1,y1,x2,y2,spatial=False):
    colour = BRONZE if spatial else INK
    marker = 'accent' if spatial else 'ink'
    return f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="{colour}" stroke-width="2" marker-end="url(#{marker})"/>'


def coefficient(x,y,sub):
    return (f'<rect x="{x-27}" y="{y-21}" width="54" height="30" fill="{PAPER}"/>'
            + text(x,y,symbol('a',sub),size=22,colour=BRONZE))


def start(height,title,description):
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="560" height="{height}" viewBox="0 0 560 {height}" role="img" aria-labelledby="title desc">',
             f'<title id="title">{title}</title><desc id="desc">{description}</desc><defs>']
    for marker,colour in [('ink',INK),('accent',BRONZE)]:
        parts.append(f'<marker id="{marker}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M1 1 L9 5 L1 9" fill="none" stroke="{colour}" stroke-width="1.4"/></marker>')
    return parts+['</defs>',f'<rect width="560" height="{height}" fill="{PAPER}"/>','<g font-family="Inter, Arial, sans-serif">']


def save(parts,name):
    (OUT/(name+'.svg')).write_text('\n'.join(parts+['</g>','</svg>'])+'\n',encoding='utf-8')


parts = start(455,'VAR(1): inflation and the policy rate',
              'Both past inflation and the past policy interest rate enter each current equation. Arrows run from the previous period to the current period.')
parts += [text(110,30,'Past information',colour=MUTED),text(450,30,'Current outcomes',colour=MUTED),
          text(110,60,'t − 1',size=19,colour=MUTED),text(450,60,'t',size=19,colour=MUTED),
          arrow(206,140,354,140),arrow(206,320,354,320),
          arrow(200,160,354,295,True),arrow(200,295,354,160,True),
          coefficient(280,116,'11'),coefficient(280,296,'22'),
          coefficient(238,200,'21'),coefficient(322,200,'12')]
for x,sub in [(110,'t−1'),(450,'t')]:
    parts += [box(x,140,'Inflation',symbol('π',sub)),box(x,320,'Policy interest rate',symbol('i',sub))]
parts += [text(280,420,'Every equation uses both lagged variables',size=19,colour=MUTED),
          text(280,447,'Predictive links, not identified causal effects',size=17,colour=MUTED)]
save(parts,'econometrics-timeseries-var-links')

parts = start(580,'Consumption–income error correction',
              'A positive gap between past consumption and 0.8 times past income contributes negatively to consumption growth and positively to income growth under the illustrated adjustment signs.')
parts += [arrow(130,138,210,194),arrow(430,138,350,194),
          arrow(220,306,130,369,True),arrow(340,306,430,369,True),
          box(130,90,'Consumption',symbol('C','t−1')),box(430,90,'Disposable income',symbol('Y','t−1')),
          f'<rect x="95" y="200" width="370" height="100" rx="9" fill="{PAPER}" stroke="{BRONZE}" stroke-width="1.5"/>',
          text(280,231,'Positive long-run gap',colour=BRONZE),
          text(280,273,symbol('z','t−1')+' = '+symbol('C','t−1')+' − 0.8'+symbol('Y','t−1')+' &gt; 0',size=24),
          box(130,420,'Consumption growth',symbol('α','C')+' '+symbol('z','t−1')+' &lt; 0',width=220,height=90),
          box(430,420,'Income growth',symbol('α','Y')+' '+symbol('z','t−1')+' &gt; 0',width=220,height=90),
          text(130,495,'Negative contribution',size=18,colour=BRONZE),
          text(430,495,'Positive contribution',size=18,colour=BRONZE),
          text(280,540,'Both contributions push the gap down',size=20,colour=MUTED),
          text(280,570,'Other short-run terms and shocks omitted',size=17,colour=MUTED)]
save(parts,'econometrics-timeseries-error-correction')
