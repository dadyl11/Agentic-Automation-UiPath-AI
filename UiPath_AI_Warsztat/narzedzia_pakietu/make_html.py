"""Generuje HTML z instrukcji Markdown.

Użycie (z katalogu UiPath_AI_Warsztat, wymaga pandoc):
  python narzedzia_pakietu/make_html.py instrukcje/Instrukcja_warsztatowa.md Instrukcja_warsztatowa.html "Instrukcja warsztatowa"
  python narzedzia_pakietu/make_html.py instrukcje/Preflight_uczestnika.md Preflight_uczestnika.html "Preflight uczestnika"
PDF: otwórz HTML w przeglądarce, Ctrl+P, Zapisz jako PDF.

Dyrektywy w .md (treść wstawiana z plików pakietu, żeby instrukcja nie rozjechała się z danymi):
  {{prompt: Podsumowanie zgłoszenia}}
      prompt z Prompty_Northstar.txt (sekcja "##### <nazwa>") jako blok do skopiowania
  {{plik: dane/known_issues_do_wklejenia.txt}}
      dowolny plik pakietu jako blok do skopiowania
  {{tabela: dane/zgloszenia.json | REQ-001,REQ-005 | requestId,subject,body,service}}
      tabela z pliku JSON; drugie pole to lista ID (wartości pierwszej kolumny) albo * dla wszystkich,
      trzecie to kolumny w kolejności wyświetlania
  {{diagram: 1A_intake_podsumowanie}}
      diagram SVG z diagramy/<id>.svg (źródło: diagramy/diagramy.json, generator make_diagrams.py)
Tabela bez wiersza nagłówka (| | |) jest wyświetlana jako karta ćwiczenia.
"""
import json, os, re, subprocess, sys

src, out, title = sys.argv[1], sys.argv[2], sys.argv[3]
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TPL = os.path.join(HERE, 'body_only.tpl')
NL = chr(10)
md = open(src, encoding='utf8').read()


def file_block(m):
    path = m.group(1).strip()
    text = open(os.path.join(ROOT, path), encoding='utf8').read().rstrip()
    fence = '````' if '```' in text else '```'
    return fence + 'text' + NL + text + NL + fence


PROMPTS_FILE = 'Prompty_Northstar.txt'


def prompt_block(m):
    # Jeden plik z promptami: sekcja zaczyna się od "##### <nazwa>", linia "Gdzie:" to opis miejsca, nie część promptu
    name = m.group(1).strip()
    text = open(os.path.join(ROOT, PROMPTS_FILE), encoding='utf8').read().replace('\r\n', NL)
    parts = re.split(r'^##### (.+)$', text, flags=re.M)
    sections = {parts[i].strip(): parts[i + 1] for i in range(1, len(parts), 2)}
    if name not in sections:
        sys.exit('Brak promptu "%s" w %s' % (name, PROMPTS_FILE))
    body = [l for l in sections[name].strip(NL).split(NL)]
    if body and body[0].startswith('Gdzie:'):
        body = body[1:]
    body = NL.join(body).strip(NL)
    fence = '````' if '```' in body else '```'
    return fence + 'text' + NL + body + NL + fence


def cell(v):
    if isinstance(v, list):
        v = ', '.join(map(str, v)) or '-'
    elif isinstance(v, bool):
        v = 'true' if v else 'false'
    v = str(v).replace('|', '&#124;').replace(NL, ' ')
    return v if v != '' else '*(puste)*'


def table(m):
    path, ids, cols = [p.strip() for p in m.group(1).split('|')]
    data = json.load(open(os.path.join(ROOT, path), encoding='utf8'))
    cols = [c.strip() for c in cols.split(',')]
    if ids != '*':
        wanted = [i.strip() for i in ids.split(',')]
        index = {str(r.get(cols[0])): r for r in data}
        missing = [i for i in wanted if i not in index]
        if missing:
            raise SystemExit('Brak %s w %s' % (missing, path))
        data = [index[i] for i in wanted]
    rows = ['| ' + ' | '.join(cols) + ' |', '|' + '---|' * len(cols)]
    rows += ['| ' + ' | '.join(cell(r.get(c, '')) for c in cols) + ' |' for r in data]
    return NL.join(rows)


def diagram(m):
    path = os.path.join(ROOT, 'diagramy', m.group(1).strip() + '.svg')
    svg = open(path, encoding='utf8').read().strip()
    return NL + '<div class="diagram">' + svg + '</div>' + NL


md = re.sub(r'[{][{]prompt:([^}]+)[}][}]', prompt_block, md)
md = re.sub(r'[{][{]plik:([^}]+)[}][}]', file_block, md)
md = re.sub(r'[{][{]diagram:([^}]+)[}][}]', diagram, md)
md = re.sub(r'[{][{]tabela:([^}]+)[}][}]', table, md)

# Uppercase section labels (e.g. "PRZED SZKOLENIEM") become small headings.
lines = []
in_fence = False
for ln in md.split(NL):
    s = ln.strip()
    if s.startswith('```'):
        in_fence = not in_fence
    if in_fence or s.startswith('```'):
        lines.append(ln)
        continue
    if (re.fullmatch(r'[A-ZĄĆĘŁŃÓŚŹŻ0-9 :()/.,\-–+•]{3,}', s)
            and not s.startswith(('#', '|', '-')) and re.search(r'[A-ZĄĆĘŁŃÓŚŹŻ]{3}', s)):
        ln = '#### ' + s
    if ln.startswith('|') and lines and lines[-1].strip() and not lines[-1].startswith('|'):
        lines.append('')
    lines.append(ln)
md = NL.join(lines)

body = subprocess.run(['pandoc', '-f', 'gfm-autolink_bare_uris', '-t', 'html', '--toc', '--toc-depth=1', '-s',
                       '--template', TPL],
                      input=md.encode('utf8'), capture_output=True, check=True).stdout.decode('utf8')
body = body.replace(chr(13), '')

css = """
:root { --ink:#142F47; --accent:#087F8C; --muted:#536878; --line:#C9D3DB; --bg:#F6F5F0; --card:#FFFFFF; --head:#142F47; --headtxt:#FFFFFF; --zebra:#EDF1F3; --warn:#D9822B; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --ink:#E3EAF0; --accent:#6AD1CE; --muted:#A9BCCB; --line:#33495C; --bg:#0F1B26; --card:#162636; --head:#22405C; --headtxt:#FFFFFF; --zebra:#1B2E40; --warn:#E8A15A; } }
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--ink); font: 16px/1.55 'Segoe UI', Calibri, system-ui, sans-serif; }
main { max-width: 900px; margin: 0 auto; padding: 32px 16px 64px; }
nav#TOC { background:var(--card); border:1px solid var(--line); border-radius:8px; padding:12px 20px; margin-bottom:32px; }
nav#TOC::before { content:'Spis treści'; display:block; font-weight:700; color:var(--accent); margin-bottom:4px; }
nav#TOC ul { margin:0; padding-left:18px; columns: 2; column-gap: 32px; }
nav#TOC a { color:var(--ink); text-decoration:none; }
nav#TOC a:hover { color:var(--accent); }
h1 { font-size: 1.7rem; border-bottom: 3px solid var(--accent); padding-bottom: 6px; margin: 56px 0 14px; }
h1:first-of-type { margin-top: 0; }
h2 { font-size: 1.25rem; color:var(--accent); margin-top: 30px; border-left: 4px solid var(--accent); padding-left: 10px; }
h3 { font-size: 1.05rem; margin: 20px 0 6px; }
h4 { font-size: .85rem; letter-spacing: .06em; color:var(--accent); margin: 22px 0 6px; }
p { margin: 6px 0; }
ol, ul { padding-left: 24px; }
li { margin: 3px 0; }
code { background: var(--zebra); padding: 1px 5px; border-radius: 4px; font-size: .9em; }
pre { background: var(--card); border: 1px solid var(--line); border-left: 4px solid var(--accent); border-radius: 6px; padding: 12px 14px; overflow-x: auto; white-space: pre-wrap; }
pre code { background: none; padding: 0; font-size: .88rem; }
blockquote { margin: 14px 0; padding: 10px 14px; background: var(--zebra); border-left: 4px solid var(--warn); border-radius: 6px; }
blockquote p { margin: 2px 0; }
.tablewrap { overflow-x: auto; margin: 10px 0; }
table { border-collapse: collapse; width: 100%; background: var(--card); font-size: .92rem; }
th { background: var(--head); color: var(--headtxt); text-align: left; padding: 6px 9px; }
td { border: 1px solid var(--line); padding: 6px 9px; vertical-align: top; }
tr:nth-child(even) td { background: var(--zebra); }
table.card td { background: var(--card); }
table.card td:first-child { width: 150px; font-weight: 600; color: var(--accent); }
.diagram { margin: 14px 0; overflow-x: auto; }
.diagram svg { display: block; max-width: 100%; height: auto; }
footer { max-width:900px; margin:0 auto; padding: 0 16px 32px; color: var(--muted); font-size: .85rem; }
@media (max-width: 640px) { nav#TOC ul { columns: 1; } h1 { font-size: 1.4rem; } table.card td:first-child { width: auto; } }
@media print {
  @page { size: A4; margin: 18mm 16mm 20mm; @bottom-center { content: 'UiPath AI | Northstar | Materiał warsztatowy • 1.2 | str. ' counter(page); font-size: 8pt; color: #536878; } }
  :root { --ink:#142F47; --accent:#087F8C; --line:#C9D3DB; --bg:#FFFFFF; --card:#FFFFFF; --zebra:#F2F5F7; --head:#142F47; }
  body { font-size: 10.5pt; }
  main { max-width: none; padding: 0; }
  nav#TOC { break-after: page; border: none; padding: 0; }
  h1 { break-before: page; margin-top: 0; font-size: 17pt; }
  nav#TOC + h1, h1:first-of-type { break-before: auto; }
  h1, h2, h3, h4 { break-after: avoid; }
  tr, li, pre, blockquote, .diagram { break-inside: avoid; }
  th { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  footer { display: none; }
}
"""


def wrap_table(m):
    t = m.group(1)
    if '<thead' not in t:
        t = t.replace('<table>', '<table class="card">', 1)
    return '<div class="tablewrap">' + t + '</div>'


body = re.sub(r'(<table>.*?</table>)', wrap_table, body, flags=re.S)
doc = f"""<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>{css}</style>
</head>
<body>
<main>
{body}
</main>
<footer>UiPath AI | Northstar | Materiał warsztatowy • wersja 1.2 • 8 października 2026. Wydruk do PDF: Ctrl+P → Zapisz jako PDF.</footer>
</body>
</html>
"""
open(out, 'w', encoding='utf8', newline='').write(doc)
print('ok', out, len(doc))
