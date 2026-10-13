"""Buduje zip dla uczestników: ../UiPath_AI_Pakiet_warsztatowy.zip (obok folderu UiPath_AI_Warsztat).

Użycie (z katalogu UiPath_AI_Warsztat): python narzedzia_pakietu/make_zip.py
Przed budową wygeneruj HTML, tabele i prezentację, jeśli zmieniły się pliki źródłowe. Zamknij Excela i PowerPointa.
Poza zipem: pliki robocze prowadzącego (EXCLUDE). Pakiet importu prowadzącego (../pakiet_importu) nigdy nie trafia do zipa.
"""
import os, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(os.path.dirname(ROOT), 'UiPath_AI_Pakiet_warsztatowy.zip')
PREFIX = os.path.basename(ROOT)

EXCLUDE_DIRS = {'screeny', '__pycache__', 'png'}
EXCLUDE_FILES = {'CLAUDE.md', 'make_deck.py', 'deck_tresc.py', 'make_diagrams.py', 'make_tables.py', 'make_zip.py', 'diagramy.json'}
EXCLUDE_PREFIX = ('~$', '.')

files = []
for d, dirs, names in os.walk(ROOT):
    dirs[:] = sorted(x for x in dirs if x not in EXCLUDE_DIRS and not x.startswith('.'))
    for n in sorted(names):
        if n in EXCLUDE_FILES or n.startswith(EXCLUDE_PREFIX):
            continue
        files.append(os.path.join(d, n))

locked = [f for f in files if os.path.exists(os.path.join(os.path.dirname(f), '~$' + os.path.basename(f)))]
if locked:
    sys.exit('Zamknij plik(i) w Office: ' + ', '.join(os.path.relpath(f, ROOT) for f in locked))

with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
    for f in files:
        z.write(f, os.path.join(PREFIX, os.path.relpath(f, ROOT)).replace(os.sep, '/'))
print('ok', OUT, len(files), 'plików', round(os.path.getsize(OUT) / 1024), 'KB')
