"""Generuje poglądowe diagramy SVG ćwiczeń z diagramy/diagramy.json.

Użycie (z katalogu UiPath_AI_Warsztat):
  python narzedzia_pakietu/make_diagrams.py
Wynik: diagramy/<id>.svg. W instrukcji: {{diagram: 1A_intake_podsumowanie}} (wstawia make_html.py).
Kolory jak w prezentacji: granat 142F47, morski 087F8C, DejaVu Sans.
"""
import json, os
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DIR = os.path.join(ROOT, 'diagramy')

INK, ACCENT, MUTED, LINE = '#142F47', '#087F8C', '#536878', '#8A9BA8'
# rodzaj -> (wypełnienie, obrys, kolor tekstu, etykieta legendy)
STYL = {
    'io':        ('#FFFFFF', '#8A9BA8', INK,       'wejście / wynik'),
    'krok':      ('#EDF1F3', '#8A9BA8', INK,       'krok'),
    'ai':        ('#E0F3F4', ACCENT,    INK,       'wywołanie AI'),
    'decyzja':   ('#FFF4E5', '#D9822B', INK,       'decyzja'),
    'narzedzie': ('#E6ECF2', INK,       INK,       'narzędzie'),
    'czlowiek':  ('#F3E9F7', '#8E5BA6', INK,       'człowiek'),
    'agent':     (INK,       INK,       '#FFFFFF', 'agent'),
    'zasob':     ('#F6F5F0', MUTED,     INK,       'zasób platformy'),
}
W, H, GAP, PAD = 168, 62, 34, 24
TOP = 72


def wrap(text, limit=19):
    words, lines, cur = text.split(), [], ''
    for w in words:
        if cur and len(cur) + 1 + len(w) > limit:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + ' ' + w).strip()
    lines.append(cur)
    return lines[:2]


def box(x, y, el):
    fill, stroke, color, _ = STYL[el['r']]
    out = []
    if el['r'] == 'decyzja':
        out.append('<rect x="%d" y="%d" width="%d" height="%d" rx="%d" fill="%s" stroke="%s" stroke-width="1.6" stroke-dasharray="5 3"/>'
                   % (x, y, W, H, H // 2, fill, stroke))
    else:
        out.append('<rect x="%d" y="%d" width="%d" height="%d" rx="8" fill="%s" stroke="%s" stroke-width="1.6"/>'
                   % (x, y, W, H, fill, stroke))
    lines = wrap(el['t'])
    sub = el.get('s')
    n = len(lines) + (1 if sub else 0)
    ty = y + H / 2 - (n - 1) * 8 + 5
    for ln in lines:
        out.append('<text x="%d" y="%.1f" text-anchor="middle" font-size="13.5" font-weight="700" fill="%s">%s</text>'
                   % (x + W // 2, ty, color, escape(ln)))
        ty += 16
    if sub:
        subc = '#C9E7EA' if el['r'] == 'agent' else MUTED
        out.append('<text x="%d" y="%.1f" text-anchor="middle" font-size="11.5" fill="%s">%s</text>'
                   % (x + W // 2, ty, subc, escape(sub)))
    return out


def arrow(x1, y1, x2, y2, label=None):
    out = ['<path d="M%d %d L%d %d" stroke="%s" stroke-width="1.6" fill="none" marker-end="url(#MID)"/>'
           % (x1, y1, x2, y2, LINE)]
    if label:
        out.append('<text x="%d" y="%d" font-size="11" fill="%s" font-style="italic">%s</text>'
                   % (x1 + 6, (y1 + y2) // 2 + 4, ACCENT, escape(label)))
    return out


def render(d):
    row = d['rzad']
    xs = [PAD + i * (W + GAP) for i in range(len(row))]
    y0 = TOP
    body = []
    for i, el in enumerate(row):
        body += box(xs[i], y0, el)
        if i:
            body += arrow(xs[i - 1] + W, y0 + H // 2, xs[i] - 2, y0 + H // 2)
    width = xs[-1] + W + PAD
    bottom = y0 + H

    g = d.get('galezie')
    if g:
        srcs = g['z'] if isinstance(g['z'], list) else [g['z']] * len(g['elementy'])
        y1 = y0 + H + 58
        for src, el in zip(srcs, g['elementy']):
            x = xs[src]
            body += arrow(x + W // 2, y0 + H, x + W // 2, y1 - 2, el.get('etykieta'))
            body += box(x, y1, el)
        bottom = y1 + H

    p = d.get('pod')
    if p:
        n = len(p['elementy'])
        y1 = y0 + H + 70
        total = n * W + (n - 1) * 18
        cx = xs[p['z']] + W // 2
        start = max(PAD, cx - total // 2)
        width = max(width, start + total + PAD)
        busy = y0 + H + 30
        body.append('<path d="M%d %d V%d" stroke="%s" stroke-width="1.6" fill="none"/>' % (cx, y0 + H, busy, LINE))
        for k, el in enumerate(p['elementy']):
            x = start + k * (W + 18)
            body.append('<path d="M%d %d H%d V%d" stroke="%s" stroke-width="1.4" fill="none" marker-end="url(#MID)"/>'
                        % (cx, busy, x + W // 2, y1 - 2, LINE))
            body += box(x, y1, el)
        bottom = y1 + H

    used = []
    for el in row + (g['elementy'] if g else []) + (p['elementy'] if p else []):
        if el['r'] not in used:
            used.append(el['r'])
    ly = bottom + 30
    lx = PAD
    legend = []
    for r in used:
        fill, stroke, _, label = STYL[r]
        dash = ' stroke-dasharray="4 2"' if r == 'decyzja' else ''
        legend.append('<rect x="%d" y="%d" width="14" height="14" rx="3" fill="%s" stroke="%s"%s/>' % (lx, ly - 11, fill, stroke, dash))
        legend.append('<text x="%d" y="%d" font-size="11.5" fill="%s">%s</text>' % (lx + 20, ly, MUTED, escape(label)))
        lx += 34 + int(len(label) * 6.6)
    height = ly + 34
    head = [
        '<text x="%d" y="30" font-size="17" font-weight="700" fill="%s">%s</text>' % (PAD, INK, escape(d['tytul'])),
        '<text x="%d" y="50" font-size="12.5" fill="%s">%s</text>' % (PAD, ACCENT, escape(d['podpis'])),
    ]
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" role="img" aria-label="%s" '
           'font-family="DejaVu Sans, Segoe UI, Arial, sans-serif">' % (width, height, width, height, escape(d['tytul'], {'"': '&quot;'})),
           '<defs><marker id="MID" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
           '<path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker></defs>' % LINE,
           '<rect width="100%" height="100%" rx="10" fill="#FFFFFF" stroke="#C9D3DB"/>']
    svg += head + body + legend + ['</svg>']
    # id znacznika strzałki unikalny per diagram: kilka SVG trafia do jednego HTML
    return '\n'.join(svg).replace('MID', 'arr-' + d['id'])


def main():
    data = json.load(open(os.path.join(DIR, 'diagramy.json'), encoding='utf8'))
    for d in data['diagramy']:
        path = os.path.join(DIR, d['id'] + '.svg')
        open(path, 'w', encoding='utf8', newline='\n').write(render(d))
        print('ok', os.path.relpath(path, ROOT))


if __name__ == '__main__':
    main()
