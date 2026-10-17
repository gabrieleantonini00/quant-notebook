"""Build the notebook from HTML notes. No third-party Python dependencies required.

Run: python build_site.py
Templates live in templates/; index.html, all-notes.html, and content.json are generated.
"""
from pathlib import Path
from html.parser import HTMLParser
from html import escape
import argparse
import hashlib
import json
import math
import re

BASE_DIR = Path(__file__).resolve().parent
NOTES_DIR = BASE_DIR / 'notes'
DOMAINS = {
    'statistics': ('Statistics', 'Probability, distributions, inference, ANOVA, and multiple testing.'),
    'econometrics': ('Econometrics', 'Cross-sectional regression, pooled samples, panel data, time series, and spatial dependence.'),
    'learning': ('Statistical Learning', 'Learning from data and evaluating predictions.'),
    'nlp': ('Natural Language Processing', 'Text representations, topic models, and language models.'),
    'finance': ('Quantitative Finance', 'Risk estimation and risk-adjusted performance.'),
    'bayesian': ('Bayesian Statistics', 'Prior beliefs, probabilistic models, and posterior inference.'),
    'setup': ('Machine Setup', 'Development environments and computing workflows.'),
}
ALIASES = {'statistical-learning':'learning','machine-learning':'learning','ml':'learning',
           'natural-language-processing':'nlp','quantitative-finance':'finance',
           'bayesian-statistics':'bayesian','machine-setup':'setup','computing':'setup','environment':'setup'}
PLANNED = {
    'econometrics':[],
    'bayesian':[], 'setup':[],
    'learning':['Supervised learning foundations','Regression and regularization','Classification models','Unsupervised learning','Reinforcement learning'],
}
LEARNING_CATEGORY_PATHS = {
    'classification': ['Supervised Learning', 'Classification'],
    'supervised-learning': ['Supervised Learning'],
}
STATISTICS_CATEGORY_PATHS = {
    'parametric-inference.html': ['Statistical Inference'],
    'anova.html': ['Statistical Inference'],
    'multiple-hypothesis-testing.html': ['Statistical Inference'],
}
ECONOMETRICS_CATEGORY_PATHS = {
    'cross-sectional': ['Cross-Sectional'],
    'pooled-cross-sections': ['Pooled Cross-Sections'],
    'panel-data': ['Panel Data'],
    'time-series': ['Time Series'],
    'spatial-econometrics.html': ['Spatial Econometrics'],
}

class NoteParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.description = ''
        self.title = ''
        self.h1 = ''
        self.headings = []
        self.eyebrow = ''
        self.capture = None
        self.buffer = []
        self.ignored = 0
        self.words = []
        self.order = 999
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ('script','style'): self.ignored += 1
        if tag in ('h1','h2','title'):
            self.capture = tag; self.buffer = []
        elif 'meta-eyebrow' in attrs.get('class',''):
            self.capture = 'eyebrow'; self.buffer = []
        if tag == 'meta':
            if attrs.get('name') == 'description': self.description = attrs.get('content','')
            if attrs.get('name') in ('order','topic-order'):
                try: self.order = int(attrs.get('content','999'))
                except ValueError: pass
    def handle_endtag(self, tag):
        if tag in ('script','style'): self.ignored = max(0,self.ignored-1)
        if self.capture == tag or (self.capture == 'eyebrow' and tag == 'div'):
            text = re.sub(r'\s+',' ',''.join(self.buffer)).strip()
            if self.capture == 'h2': self.headings.append(text)
            elif self.capture == 'eyebrow': self.eyebrow = text
            else: setattr(self,self.capture,text)
            self.capture = None
    def handle_data(self, data):
        if not self.ignored: self.words.extend(data.split())
        if self.capture: self.buffer.append(data)

def parse_note(path):
    parser = NoteParser(); parser.feed(path.read_text(encoding='utf-8'))
    order = parser.order
    if order == 999:
        match = re.search(r'Topic\s*(\d+)',parser.eyebrow,re.I)
        if match: order = int(match.group(1))
    category_path = []
    parts = path.relative_to(NOTES_DIR).parts
    if parts[0] == 'statistical-learning' and len(parts) > 2:
        category_path = LEARNING_CATEGORY_PATHS.get(parts[1], [parts[1].replace('-', ' ').title()])
    elif parts[0] == 'statistics':
        category_path = STATISTICS_CATEGORY_PATHS.get(path.name, [])
    elif parts[0] == 'econometrics':
        category_path = ECONOMETRICS_CATEGORY_PATHS.get(parts[1], [])
    return {'title':parser.h1 or parser.title.split('|')[0].strip(),
            'summary':parser.description, 'topics':parser.headings,
            'link':path.relative_to(BASE_DIR).as_posix(),
            'reading_minutes':max(2,math.ceil(len(parser.words)/210)), 'order':order,
            'category_path':category_path}

def style_note(path):
    text = path.read_text(encoding='utf-8')
    prefix = '../' * (len(path.relative_to(BASE_DIR).parts)-1)
    if 'assets/site.css' not in text:
        tags = f'  <link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml">\n  <link rel="stylesheet" href="{prefix}assets/site.css">\n  <script src="{prefix}assets/notes.js" defer></script>\n'
        text = text.replace('</head>',tags+'</head>',1)
    text = text.replace('<body>','<body class="note-page">',1)
    if 'class="skip-link"' not in text:
        text = text.replace('<body class="note-page">','<body class="note-page">\n  <a class="skip-link" href="#note-content">Skip to article</a>',1)
    text = text.replace('<main class="shell">','<main class="shell" id="note-content">',1)
    # The pinned local KaTeX assets also work without an internet connection.
    if (BASE_DIR/'assets/vendor/katex/katex.min.js').exists():
        text = text.replace('https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/',prefix+'assets/vendor/katex/')
    if path.relative_to(NOTES_DIR).parts[0] in ('finance', 'nlp'):
        # Version shared notebook assets so published pages pick up editorial changes.
        for asset in ('assets/site.css', 'assets/editorial-notes.css', 'assets/nlp.css', 'assets/notes.js',
                      'assets/plots/finance-var-es-tail.svg', 'assets/plots/nlp-llm-parameters.svg'):
            version = hashlib.sha256((BASE_DIR/asset).read_bytes()).hexdigest()[:12]
            url = prefix + asset
            text = re.sub(r'(?<=["\'])' + re.escape(url) + r'(?:\?v=[a-f0-9]+)?(?=["\'])',
                          url + '?v=' + version, text)
    if text != path.read_text(encoding='utf-8'): path.write_text(text,encoding='utf-8')


def render_note_directory(sections, depth=0):
    """Keep the no-JavaScript directory consistent with category navigation."""
    direct, categories = [], {}
    for note in sections:
        path = note.get('category_path', [])
        if depth < len(path):
            categories.setdefault(path[depth], []).append(note)
        else:
            direct.append(note)
    html = ''
    if direct:
        html += '<ul>' + ''.join(
            f'<li><a href="{escape(n["link"], quote=True)}">{escape(n["title"])}</a></li>'
            for n in direct
        ) + '</ul>'
    for category, notes in categories.items():
        level = min(3 + depth, 6)
        html += f'<h{level}>{escape(category)}</h{level}>'
        html += render_note_directory(notes, depth + 1)
    return html


def build_site_manifest(style_notes=True):
    data = {key:{'title':title,'description':description,'sections':[],
                 'has_notes':False,'planned_topics':PLANNED.get(key,[])}
            for key,(title,description) in DOMAINS.items()}
    paths = sorted(p for p in NOTES_DIR.rglob('*.html') if p.name != 'template_note.html')
    for path in paths:
        if style_notes: style_note(path)
        folder = path.relative_to(NOTES_DIR).parts[0]
        key = ALIASES.get(folder,folder)
        if key not in data:
            data[key] = {'title':folder.replace('-',' ').title(),'description':'Study notes.',
                         'sections':[],'has_notes':False,'planned_topics':[]}
        data[key]['sections'].append(parse_note(path))
        data[key]['has_notes'] = True
    for area in data.values():
        area['sections'].sort(key=lambda n:(n['order'],n['title']))
    (BASE_DIR/'content.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    # Escape HTML delimiters so note metadata cannot terminate a script element.
    inline = json.dumps(data,ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    template = (BASE_DIR/'templates/index.html').read_text(encoding='utf-8')
    # A content-based version keeps browser caches from hiding library updates.
    library_version = hashlib.sha256((BASE_DIR/'assets/library.js').read_bytes()).hexdigest()[:12]
    template = template.replace('"assets/library.js"', f'"assets/library.js?v={library_version}"')
    (BASE_DIR/'index.html').write_text(template.replace('/* SITE_DATA */','const areaContent = '+inline+';'),encoding='utf-8')
    groups=[]
    for key,area in data.items():
        if not area['has_notes']: continue
        items=render_note_directory(area['sections'])
        groups.append(f'<section><h2>{escape(area["title"])}</h2>{items}</section>')
    plain='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>All notes · Gabriele Antonini</title><link rel="stylesheet" href="assets/site.css"><link rel="icon" href="assets/favicon.svg"></head><body class="note-page"><header class="shell"><p><a href="index.html">Back to notebook</a></p></header><main class="shell"><article><h1>All study notes</h1>'+''.join(groups)+'</article></main></body></html>'
    (BASE_DIR/'all-notes.html').write_text(plain,encoding='utf-8')
    print(f'Built {len(paths)} notes in {sum(a["has_notes"] for a in data.values())} subjects.')
    return data

if __name__ == '__main__':
    args=argparse.ArgumentParser(); args.add_argument('--index-only',action='store_true')
    build_site_manifest(style_notes=not args.parse_args().index_only)
