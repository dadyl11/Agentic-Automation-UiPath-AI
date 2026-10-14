"""Generuje dodatkowe źródła wiedzy dla NorthstarHelpdesk (rozszerzenie ćwiczenia 7), do baza_wiedzy/helpdesk/:
  Regulamin_wsparcia.pdf  (sekcje REG-1 ... REG-6; sam tekst, bez tabel i obrazów, bo ingestia Basic czyta tylko tekst cyfrowy)
  Katalog_uslug.csv       (przecinek, nagłówek w pierwszym wierszu, UTF-8 bez BOM, LF)

Użycie (z katalogu UiPath_AI_Warsztat): python narzedzia_pakietu/make_wiedza.py
Treść obu plików jest w tym skrypcie; po zmianie uruchom go ponownie (wymaga reportlab).
Zgodność z danymi pakietu: usługi portal, sales, billing jak w dane/service_status.json; okno serwisowe billing w piątek,
jak termin sprawy INC-106 (2026-11-20 to piątek). Regulamin nie podaje terminów napraw (zasada KB-003).
"""
import os, sys, glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'baza_wiedzy', 'helpdesk')

TITLE = 'Regulamin wsparcia Northstar'
META = 'Wersja 1.0 | 2026-10-14 | Dane fikcyjne'

# Każda sekcja: (identyfikator | tytuł, [akapity]). Identyfikator stoi w tym samym fragmencie co treść, żeby dało się go zacytować.
SECTIONS = [
    ('REG-1 | Zakres i godziny pracy', [
        'Wsparcie Northstar obsługuje zgłoszenia dotyczące usług z katalogu usług, w tym portalu (portal), usługi raportowej (sales) '
        'i rozliczeń (billing). Wsparcie pracuje od poniedziałku do piątku w godzinach 8:00–18:00 czasu polskiego, z wyjątkiem dni '
        'ustawowo wolnych od pracy. Zgłoszenia przesłane poza godzinami pracy są przyjmowane, a ich obsługa zaczyna się o 8:00 '
        'następnego dnia roboczego.']),
    ('REG-2 | Priorytety i czas pierwszej reakcji', [
        'Priorytet krytyczny: usługa jest niedostępna dla wszystkich użytkowników. Pierwsza reakcja wsparcia nastąpi w ciągu 30 minut '
        'w godzinach pracy.',
        'Priorytet wysoki: usługa działa częściowo albo problem dotyczy całego zespołu. Pierwsza reakcja nastąpi w ciągu 2 godzin '
        'w godzinach pracy.',
        'Priorytet normalny: problem dotyczy jednej osoby albo funkcji pomocniczej. Pierwsza reakcja nastąpi w ciągu 1 dnia roboczego.',
        'Priorytet niski: pytania, prośby o informacje i propozycje zmian. Pierwsza reakcja nastąpi w ciągu 3 dni roboczych.',
        'Czas pierwszej reakcji to czas do pierwszej odpowiedzi zespołu wsparcia. Nie jest terminem naprawy. Termin naprawy konkretnej '
        'awarii podaje wyłącznie bieżący status usługi (zob. KB-003); gdy go brak, termin nie jest potwierdzony.']),
    ('REG-3 | Ustalanie priorytetu', [
        'Priorytet zgłoszenia ustala zespół wsparcia na podstawie opisu problemu. Zgłaszający może zaproponować priorytet, ale go nie nadaje.']),
    ('REG-4 | Eskalacja', [
        'Jeśli czas pierwszej reakcji minął, a zgłaszający nie otrzymał odpowiedzi, może przekazać sprawę kierownikowi wsparcia pod '
        'adresem kierownik.wsparcia@example.com. W wiadomości należy podać numer zgłoszenia i nazwę usługi. Eskalacja nie zmienia '
        'priorytetu zgłoszenia.']),
    ('REG-5 | Awarie krytyczne', [
        'Awarię krytyczną należy zgłosić jednocześnie do zespołu wsparcia i do zespołu będącego właścicielem usługi. Dane kontaktowe '
        'właściciela znajdują się w katalogu usług, w kolumnie kontakt. Awaria krytyczna zgłoszona poza godzinami pracy zostanie '
        'obsłużona od 8:00 następnego dnia roboczego.']),
    ('REG-6 | Okna serwisowe i granice wsparcia', [
        'Planowe prace serwisowe odbywają się w oknach podanych w katalogu usług. Okno serwisowe jest stałym harmonogramem prac '
        'planowych i nie jest terminem naprawy awarii. Wsparcie nie nadaje uprawnień bez weryfikacji (zob. KB-002), nie przyjmuje '
        'numerów rachunków, haseł ani danych kart i nie gwarantuje terminów napraw.']),
]

# Bez przecinków wewnątrz wartości (separator to przecinek).
CATALOG_HEADER = ['usluga', 'nazwa', 'zespol', 'kontakt', 'okno_serwisowe']
CATALOG = [
    ['portal', 'Portal Northstar', 'Zespół Portal', 'portal@example.com', 'wtorek 20:00-22:00'],
    ['sales', 'Usługa raportowa', 'Zespół Raportowanie', 'raporty@example.com', 'środa 20:00-22:00'],
    ['billing', 'Rozliczenia', 'Zespół Rozliczenia', 'rozliczenia@example.com', 'piątek 20:00-22:00'],
    ['archiwum', 'Archiwum dokumentów', 'Zespół Archiwum', 'archiwum@example.com', 'sobota 06:00-08:00'],
    ['kadry', 'Kadry i płace', 'Zespół HR Systems', 'hr-systems@example.com', 'sobota 08:00-10:00'],
    ['poczta', 'Poczta i kalendarz', 'Zespół Infrastruktura', 'infrastruktura@example.com', 'niedziela 02:00-04:00'],
    ['vpn', 'Dostęp zdalny (VPN)', 'Zespół Infrastruktura', 'infrastruktura@example.com', 'niedziela 04:00-06:00'],
    ['drukarki', 'Drukarki i skanery', 'Zespół Stanowiska', 'stanowiska@example.com', 'czwartek 18:00-19:00'],
]


def find_fonts():
    """Font z polskimi znakami: DejaVu z matplotlib, potem DejaVu/Arial z Windows."""
    cands = []
    try:
        import matplotlib
        d = os.path.join(os.path.dirname(matplotlib.__file__), 'mpl-data', 'fonts', 'ttf')
        cands.append((os.path.join(d, 'DejaVuSans.ttf'), os.path.join(d, 'DejaVuSans-Bold.ttf')))
    except ImportError:
        pass
    cands += [('C:/Windows/Fonts/DejaVuSans.ttf', 'C:/Windows/Fonts/DejaVuSans-Bold.ttf'),
              ('C:/Windows/Fonts/arial.ttf', 'C:/Windows/Fonts/arialbd.ttf')]
    for reg, bold in cands:
        if os.path.exists(reg) and os.path.exists(bold):
            return reg, bold
    sys.exit('Brak fontu z polskimi znakami (DejaVu Sans albo Arial).')


def build_pdf(path):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from xml.sax.saxutils import escape

    reg, bold = find_fonts()
    pdfmetrics.registerFont(TTFont('Body', reg))
    pdfmetrics.registerFont(TTFont('BodyBold', bold))
    h1 = ParagraphStyle('h1', fontName='BodyBold', fontSize=18, leading=22, spaceAfter=4)
    meta = ParagraphStyle('meta', fontName='Body', fontSize=9, leading=12, spaceAfter=14)
    h2 = ParagraphStyle('h2', fontName='BodyBold', fontSize=12, leading=15, spaceBefore=10, spaceAfter=4)
    body = ParagraphStyle('body', fontName='Body', fontSize=10.5, leading=15, spaceAfter=5)

    story = [Paragraph(escape(TITLE), h1), Paragraph(escape(META), meta)]
    for head, paras in SECTIONS:
        story.append(Paragraph(escape(head), h2))
        story += [Paragraph(escape(p), body) for p in paras]
    # invariant=1: ten sam plik przy każdym uruchomieniu (bez znacznika czasu), więc czysty diff w gicie
    doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=2.2 * cm, rightMargin=2.2 * cm, topMargin=2.2 * cm, bottomMargin=2.2 * cm,
                            title=TITLE, author='Northstar (dane fikcyjne)', invariant=1)
    doc.build(story)


def build_csv(path):
    lines = [','.join(CATALOG_HEADER)] + [','.join(r) for r in CATALOG]
    for r in CATALOG:
        assert len(r) == len(CATALOG_HEADER) and not any(',' in c for c in r), r
    open(path, 'w', encoding='utf8', newline='\n').write('\n'.join(lines) + '\n')


os.makedirs(OUT, exist_ok=True)
build_pdf(os.path.join(OUT, 'Regulamin_wsparcia.pdf'))
build_csv(os.path.join(OUT, 'Katalog_uslug.csv'))
print('ok', OUT, [os.path.basename(p) for p in sorted(glob.glob(os.path.join(OUT, '*')))])
