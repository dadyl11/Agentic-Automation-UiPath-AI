"""Generuje fikcyjne formularze zgłoszeń do demo IXP (poza pakietem uczestników):
  demo_ixp/formularze/  5 PDF-ów do projektu IXP (różne układy tych samych 5 pól: requestId, requesterEmail, subject, body, service)
  demo_ixp/do_demo/     2 PDF-y na pokaz na żywo (nie wgrywane do projektu)
Dane z UiPath_AI_Warsztat/dane/zgloszenia.json. Sam tekst cyfrowy (bez skanów, tabel obrazkowych), font DejaVu z polskimi znakami.

Użycie: python demo_ixp/make_formularze.py
"""
import json, os, sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'UiPath_AI_Warsztat', 'dane', 'zgloszenia.json')

try:
    import matplotlib
    FD = os.path.join(os.path.dirname(matplotlib.__file__), 'mpl-data', 'fonts', 'ttf')
except ImportError:
    sys.exit('Brak matplotlib (font DejaVu).')
pdfmetrics.registerFont(TTFont('R', os.path.join(FD, 'DejaVuSans.ttf')))
pdfmetrics.registerFont(TTFont('B', os.path.join(FD, 'DejaVuSans-Bold.ttf')))

W, H = A4
M = 2 * cm
REQ = {r['requestId']: r for r in json.load(open(DATA, encoding='utf8'))}


def text(c, x, y, s, font='R', size=10, color=(0, 0, 0)):
    c.setFont(font, size)
    c.setFillColorRGB(*color)
    c.drawString(x, y, s)


def para(c, x, y, s, width, font='R', size=10, lead=14):
    """Rysuje zawinięty tekst od y w dół; zwraca y pod ostatnią linią."""
    c.setFont(font, size)
    c.setFillColorRGB(0, 0, 0)
    for chunk in s.split('\n'):
        for line in (simpleSplit(chunk, font, size, width) or ['']):
            c.drawString(x, y, line)
            y -= lead
    return y


def form_klasyczny(c, r):
    """Układ 1: tabela, etykiety po lewej, wartości po prawej."""
    text(c, M, H - 2.5 * cm, 'FORMULARZ ZGŁOSZENIA DO WSPARCIA', 'B', 16)
    text(c, M, H - 3.2 * cm, 'Northstar  |  Dział wsparcia  |  Dane fikcyjne', 'R', 9, (0.4, 0.4, 0.4))
    rows = [('Numer zgłoszenia', r['requestId']), ('Adres e-mail zgłaszającego', r['requesterEmail']),
            ('Usługa', r['service']), ('Temat', r['subject'])]
    y = H - 4.6 * cm
    lw, vw, rh = 6 * cm, W - 2 * M - 6 * cm, 1 * cm
    for label, val in rows:
        c.setStrokeColorRGB(0.5, 0.5, 0.5)
        c.rect(M, y - rh, lw, rh)
        c.rect(M + lw, y - rh, vw, rh)
        text(c, M + 0.2 * cm, y - 0.65 * cm, label, 'B', 9)
        text(c, M + lw + 0.2 * cm, y - 0.65 * cm, val, 'R', 10)
        y -= rh
    bh = 6 * cm
    c.rect(M, y - bh, lw, bh)
    c.rect(M + lw, y - bh, vw, bh)
    text(c, M + 0.2 * cm, y - 0.65 * cm, 'Opis problemu', 'B', 9)
    para(c, M + lw + 0.2 * cm, y - 0.65 * cm, r['body'], vw - 0.4 * cm)
    text(c, M, y - bh - 1.2 * cm, 'Data wypełnienia: 2026-10-05', 'R', 9, (0.4, 0.4, 0.4))
    text(c, M + 9 * cm, y - bh - 1.2 * cm, 'Podpis: ______________________', 'R', 9, (0.4, 0.4, 0.4))


def form_list(c, r):
    """Układ 2: pismo, dane w nagłówku i w tekście."""
    text(c, W - M - 6 * cm, H - 2.5 * cm, 'Warszawa, 5 października 2026', 'R', 9)
    text(c, M, H - 3.5 * cm, 'Od: ' + r['requesterEmail'], 'R', 10)
    text(c, M, H - 4.1 * cm, 'Do: Zespół Wsparcia Northstar', 'R', 10)
    text(c, M, H - 5.3 * cm, 'Dotyczy: zgłoszenia %s (usługa: %s)' % (r['requestId'], r['service']), 'B', 11)
    text(c, M, H - 6.0 * cm, 'Temat: ' + r['subject'], 'B', 11)
    y = para(c, M, H - 7.5 * cm, 'Szanowni Państwo,\n\n' + r['body'] + '\n\nZ poważaniem\n' + r['requesterEmail'], W - 2 * M, 'R', 11, 16)


def form_email(c, r):
    """Układ 3: wydruk wiadomości e-mail, numer i usługa w stopce systemowej."""
    c.setFillColorRGB(0.93, 0.95, 0.97)
    c.rect(M, H - 6 * cm, W - 2 * M, 4 * cm, fill=1, stroke=0)
    text(c, M + 0.4 * cm, H - 2.9 * cm, 'Od:', 'B', 10)
    text(c, M + 2.4 * cm, H - 2.9 * cm, r['requesterEmail'], 'R', 10)
    text(c, M + 0.4 * cm, H - 3.7 * cm, 'Do:', 'B', 10)
    text(c, M + 2.4 * cm, H - 3.7 * cm, 'wsparcie@northstar.example', 'R', 10)
    text(c, M + 0.4 * cm, H - 4.5 * cm, 'Data:', 'B', 10)
    text(c, M + 2.4 * cm, H - 4.5 * cm, 'poniedziałek, 5 października 2026, 08:42', 'R', 10)
    text(c, M + 0.4 * cm, H - 5.3 * cm, 'Temat:', 'B', 10)
    text(c, M + 2.4 * cm, H - 5.3 * cm, r['subject'], 'R', 10)
    y = para(c, M, H - 7.5 * cm, r['body'], W - 2 * M, 'R', 11, 16)
    text(c, M, 3 * cm, '[Zgłoszenie zarejestrowane automatycznie]', 'R', 8, (0.4, 0.4, 0.4))
    text(c, M, 2.5 * cm, 'Numer zgłoszenia: %s  |  Usługa: %s' % (r['requestId'], r['service']), 'R', 8, (0.4, 0.4, 0.4))


def form_pola(c, r):
    """Układ 4: etykiety nad polami, usługa jako pola wyboru."""
    text(c, M, H - 2.5 * cm, 'Karta zgłoszenia', 'B', 18)
    gray = (0.45, 0.45, 0.45)
    text(c, M, H - 4.0 * cm, 'NUMER ZGŁOSZENIA', 'R', 7, gray)
    text(c, M, H - 4.6 * cm, r['requestId'], 'B', 12)
    text(c, M + 8 * cm, H - 4.0 * cm, 'ZGŁASZAJĄCY (E-MAIL)', 'R', 7, gray)
    text(c, M + 8 * cm, H - 4.6 * cm, r['requesterEmail'], 'R', 11)
    text(c, M, H - 6.0 * cm, 'USŁUGA', 'R', 7, gray)
    x = M
    for name in ('portal', 'sales', 'billing', 'inna'):
        mark = '☒' if name == r['service'] else '☐'
        text(c, x, H - 6.7 * cm, mark + ' ' + name, 'R', 11)
        x += 3.2 * cm
    text(c, M, H - 8.0 * cm, 'TEMAT', 'R', 7, gray)
    text(c, M, H - 8.6 * cm, r['subject'], 'B', 12)
    text(c, M, H - 10.0 * cm, 'OPIS', 'R', 7, gray)
    para(c, M, H - 10.6 * cm, r['body'], W - 2 * M, 'R', 11, 16)


def form_en(c, r):
    """Układ 5: karta po angielsku (etykiety w innym języku)."""
    text(c, M, H - 2.5 * cm, 'SUPPORT REQUEST CARD', 'B', 16)
    text(c, M, H - 3.2 * cm, 'Northstar Service Desk  |  Fictional data', 'R', 9, (0.4, 0.4, 0.4))
    y = H - 5 * cm
    for label, val in (('Request ID', r['requestId']), ('Requester e-mail', r['requesterEmail']),
                       ('Service', r['service']), ('Subject', r['subject'])):
        text(c, M, y, label + ':', 'B', 10)
        text(c, M + 5 * cm, y, val, 'R', 10)
        y -= 0.9 * cm
    text(c, M, y - 0.4 * cm, 'Description:', 'B', 10)
    para(c, M + 5 * cm, y - 0.4 * cm, r['body'], W - 2 * M - 5 * cm)


JOBS = [
    ('formularze', 'REQ-001', form_klasyczny),
    ('formularze', 'REQ-002', form_list),
    ('formularze', 'REQ-005', form_email),
    ('formularze', 'REQ-004', form_pola),
    ('formularze', 'REQ-014', form_en),
    ('do_demo', 'REQ-009', form_list),
    ('do_demo', 'REQ-017', form_klasyczny),
]

for folder, rid, fn in JOBS:
    d = os.path.join(HERE, folder)
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, 'Zgloszenie_%s.pdf' % rid)
    c = canvas.Canvas(path, pagesize=A4, invariant=1)
    c.setTitle('Zgłoszenie %s' % rid)
    c.setAuthor('Northstar (dane fikcyjne)')
    fn(c, REQ[rid])
    c.showPage()
    c.save()
    print('ok', folder, os.path.basename(path), fn.__name__)
