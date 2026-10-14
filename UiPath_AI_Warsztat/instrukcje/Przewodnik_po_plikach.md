# Przewodnik po plikach | Co do czego służy

Ściąga dla prowadzącego: który plik pakietu jest potrzebny w którym ćwiczeniu. Źródłem danych są pliki JSON; Excel, CSV i pliki „do wklejenia” są z nich generowane (`narzedzia_pakietu/make_tables.py`), więc po zmianie edytuj JSON i uruchom skrypt.

## Najkrócej: po którą rzecz sięgnąć

| Potrzebuję… | Plik |
|---|---|
| treści zgłoszenia do wpisania w argumenty | `dane/Northstar_dane.xlsx`, arkusz *Zgloszenia* (albo tabela w instrukcji) |
| promptu do skopiowania | `Prompty_Northstar.txt` (sekcje `##### nazwa`) |
| pliku do wgrania do Orchestratora | `dane/sprawy.csv` → bucket Northstar_Rejestr (ćw. 3A) |
| dokumentu wiedzy dla agenta | `baza_wiedzy/Portal_Northstar.txt` → indeks Context Grounding (ćw. 4) |
| evaluation setu do importu | `testy/import_Northstar_DEVELOPMENT.json` i `import_Northstar_HOLDOUT.json` (ćw. 5) |
| oczekiwanych wyników do sprawdzenia | `testy/Northstar_testy.xlsx`, arkusz *Oczekiwane_wyniki* |
| kontraktu narzędzia (wejścia, wyjścia, statusy) | `kontrakty/narzedzia.md` |

## Pliki według ćwiczeń

| Ćwiczenie | Plik | Do czego |
|---|---|---|
| 1A | arkusz *Zgloszenia* | REQ-001, REQ-005, REQ-007 do argumentów |
| 1A | `Prompty_Northstar.txt` → „Podsumowanie zgłoszenia” | prompt Content Generation |
| 1B | `Prompty_Northstar.txt` → „Kategorie”, arkusz *Kategorie* | 6 kategorii z opisami do Categorize |
| 1B | arkusz *Przyklady_cwiczeniowe* | DEMO-01 (kilka próśb w jednej wiadomości) |
| 1A, 1B | `zapas/Intake_AI_Zapas` (cross-platform), `zapas/Intake_AI_Zapas_Windows` | gotowe rozwiązanie, gdy ćwiczenie nie wychodzi; w obu aktywnościach GenAI wybierz własne połączenie |
| 2 | `dane/known_issues_do_wklejenia.txt` | wartość domyślna zmiennej lstKnownIssues (4 znane problemy jako wyrażenie VB) |
| 2 | arkusz *Znane_problemy* | te same problemy w czytelnej tabeli |
| 2 | arkusz *Pary_podobienstwa* | 6 par SIM do kalibracji progu T (kolumna na wynik score) |
| 3A | `dane/sprawy.csv` | wgrać do bucketu Northstar_Rejestr; GetTicketStatus czyta go przez Read Storage Text |
| 3A | arkusze *Sprawy* i *Statusy_uslug* | te same dane w Excelu: 3 sprawy, 3 statusy usług |
| 3A | `kontrakty/narzedzia.md` | wejścia, wyjścia `out_…`, statusy i opisy narzędzi dla agenta |
| 3B | `Prompty_Northstar.txt` → „SupportAgent: prompt systemowy” i „prompt użytkownika” | prompty agenta |
| 3B | `kontrakty/agent_output.schema.json` | schemat wyniku agenta (Output w Definition) |
| 4 | `baza_wiedzy/Portal_Northstar.txt` | jedyny dokument wiedzy agenta, 6 procedur KB |
| 5 | `testy/import_Northstar_DEVELOPMENT.json`, `import_Northstar_HOLDOUT.json` | import evaluation setów w Studio Web |
| 5 | `testy/ewaluacja_do_wklejenia.txt` | te same przypadki DEVELOPMENT do ręcznego wklejenia (krok 2a i zapas) |
| 5 | `testy/import_Northstar_DEVELOPMENT.csv` | ten sam set w CSV, tylko do porównania formatów |
| 5 | `Prompty_Northstar.txt` → „Rubryka oceny szkicu”, „Evaluator Trajectory” | prompty evaluatorów LLM |
| 5 | `testy/Northstar_testy.xlsx` | *Oczekiwane_wyniki* (kolumny na wynik v1 i v2), *Testy_techniczne* |
| 6B | arkusz *Testy_techniczne*, *Przyklady_cwiczeniowe* | TECH-01…06 (awaria, zły JSON, powtórzenie, odrzucenie) i DEMO-03 |
| 7 | `Prompty_Northstar.txt` → „NorthstarHelpdesk: prompt systemowy” | prompt agenta konwersacyjnego |
| 7 | `testy/Northstar_testy.xlsx`, arkusz *Rozmowy_testowe* | 11 rozmów CHAT-01…11 (CHAT-09…11 dla rozszerzenia z regulaminem i katalogiem) |
| 7 (rozszerzenie) | `baza_wiedzy/helpdesk/Regulamin_wsparcia.pdf`, `Katalog_uslug.csv` | dwa dodatkowe źródła wiedzy NorthstarHelpdesk, osobne buckety i indeksy (generuje je `narzedzia_pakietu/make_wiedza.py`) |
| 7 | `testy/rubryka_zadania_koncowego.md` | ocena prezentacji zespołów na koniec dnia 2 |

## Pliki prowadzącego (nie dla uczestników w trakcie ćwiczeń)

| Plik | Do czego |
|---|---|
| `testy/oczekiwane_wyniki.json` | źródło oczekiwanych wyników (kategoria, akcja, KI, wymagane narzędzia, split DEVELOPMENT/HOLDOUT) |
| `testy/Klucz_testow.md` | te same oczekiwania jako tabela do wydruku |
| `testy/karta_oceny.md` | szablon notatki z jednego przebiegu (runId, kategoria oczekiwana/otrzymana…) |
| `testy/pary_podobienstwa.json`, `testy_techniczne.json`, `rozmowy_testowe.json` | źródła arkuszy testowych |
| `UiPath_AI_Warsztaty.pptx` | prezentacja z notatkami (generowana z `narzedzia_pakietu/deck_tresc.py`) |
| `Przyklady_promptow.html` | teoria prompt engineeringu do slajdów |
| `UiPath_AI_Trust_Layer_przewodnik.html` | materiał uzupełniający o LLM Gateway, guardrails, własnych modelach |
| `Preflight_uczestnika.html` | do wysłania uczestnikom przed szkoleniem |

> **Uwaga:** oczekiwanych wyników i testów nie wklejaj do promptu ani do wiedzy agenta. To kryteria oceny, nie dane.

## Źródła danych (edytujesz tylko je)

| Plik JSON | Z niego powstaje |
|---|---|
| `dane/zgloszenia.json` (18 zgłoszeń) | arkusz *Zgloszenia*, evaluation sety |
| `dane/przyklady_cwiczeniowe.json` (DEMO-01…03) | arkusz *Przyklady_cwiczeniowe* |
| `dane/known_issues.json` (4) | arkusz *Znane_problemy*, `known_issues_do_wklejenia.txt` |
| `dane/service_status.json` (3) | arkusz *Statusy_uslug* |
| `dane/tickets.json` (3 sprawy) | arkusz *Sprawy*, `dane/sprawy.csv` |
| `dane/categories.json` (6) | arkusz *Kategorie* |
| `dane/przyklad_wyniku.json` | przykład poprawnego wyniku agenta (REQ-001), do porównania ze schematem |

Pozostałe pliki pochodne: `dane/csv/` i `testy/csv/` to każdy arkusz Excela jako CSV. `diagramy/*.svg` i `diagramy/png/` są generowane z `diagramy/diagramy.json` (`make_diagrams.py`). Pliki HTML są generowane z `instrukcje/*.md` (`make_html.py`).

## Sprawy w sprawy.csv

| Sprawa | Właściciel | Po co jest |
|---|---|---|
| INC-104 | celina@example.com | REQ-003 (właścicielka → FOUND) i REQ-016 (ktoś inny → FORBIDDEN); rozmowa CHAT-04 |
| INC-105 | anna@example.com | drugi przypadek FOUND (RESOLVED) w testach narzędzia |
| INC-106 | bartek@example.com | jedyna sprawa z potwierdzonym terminem (`eta` 2026-11-20): pokazuje, kiedy agent może podać termin |
| INC-999 | (brak w pliku) | REQ-010 sprawdza NOT_FOUND |
