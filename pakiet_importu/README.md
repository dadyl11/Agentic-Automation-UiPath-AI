# Pakiet importu prowadzącego (Northstar)

Narzędzia, które uczestnicy importują wspólnie (FinalizeCase), oraz wersje zapasowe narzędzi budowanych w ćwiczeniach. Tylko dla prowadzącego: nie dołączaj tego folderu do zipa uczestników.

| Projekt | Rola | Kontrakt |
|---|---|---|
| `FinalizeCase` | Zapis wyniku procesu Northstar_Case (ćw. 6B) do `rejestr_spraw.csv`. Wywołuje go proces, nie agent | `kontrakty/narzedzia.md` § FinalizeCase |
| `GetTicketStatus_Zapas` | Zapas i wzorzec rozwiązania GetTicketStatus z ćw. 3A: czyta `sprawy.csv` z bucketu Northstar_Rejestr (Read Storage Text, pętla po wierszach) | § GetTicketStatus |
| `GetServiceStatus_Zapas` | Zapas dla GetServiceStatus z ćw. 3A (Studio Web) | § GetServiceStatus |
| `FindKnownIssue_Zapas` | Zapas dla FindKnownIssue z ćw. 2 (Studio Web). Semantic Similarity w pętli po znanych problemach, próg T=0,6 | § FindKnownIssue |
| `Intake_AI_Zapas` | Zapas ćwiczeń 1A i 1B (Studio Desktop): walidacja wejścia → Content Generation → Categorize → If kategoria z listy → Switch na zespół → Log. Wersja 1.0.0, bez argumentów Out (wynik w logu) | Instrukcja ćw. 1A, 1B |
| `Intake_AI_Zapas_Windows` | Ten sam workflow co Intake_AI_Zapas, projekt **Windows** (dla grupy przyzwyczajonej do Windows z kursu Studio Desktop). Nie działa na robocie serverless; uruchamiaj z Studio Desktop albo na robocie Windows | Instrukcja ćw. 1A, 1B |
| `Northstar_Agent/SupportAgent` | Referencyjny agent z ćw. 3B (low-code, Studio Web). Prompty 03/04, schemat wyniku z `kontrakty/agent_output.schema.json`, 3 narzędzia z folderu Shared | Instrukcja ćw. 3B |

Wszystkie projekty: Process, cross-platform (Portable), VB, `UiPath.System.Activities` 26.8.2. Studio 26 (Community) otworzy je i opublikuje bez konwersji. Wejścia mają nazwy bez prefiksów, bo agent widzi je jako parametry narzędzia. Wyjścia (wersja 2.0.0, 12.10.2026) to osobne argumenty Out z prefiksem `out_` (out_status, out_sourceId, pola danych), zgodnie z zaleceniem dokumentacji UiPath dla narzędzi agenta. Po zmianie argumentów uruchom `python -I narzedzia_argumenty.py <projekt>` przed `uip rpa pack`, a w Orchestratorze usuń i utwórz proces od nowa (update-version nie odświeża schematu). Zmienne wewnątrz workflow mają prefiks typu (`strX`, `boolX`), jak na kursie Studio Desktop.

## FinalizeCase: rejestr spraw w jednym pliku CSV

Wersja 2.0.1 (12.10.2026): ta sama logika co 2.0.0, ale kroki są ponumerowane (0–7) i każdy ma adnotację po polsku, żeby dało się omówić gotowiec bez tłumaczenia wyrażeń. Usunięte puste bloki Finally. Przetestowane na tenancie: INVALID_INPUT, SAVED, ALREADY_PROCESSED. Opis dla uczestników: instrukcja ćw. 3A, krok 8 „Jak działa FinalizeCase”.

Bucket **`Northstar_Rejestr`** (folder Shared) zawiera jeden plik **`rejestr_spraw.csv`**, w którym jeden wiersz to jedno zgłoszenie. Pobierz go w Orchestratorze (Shared → Storage Buckets → Northstar_Rejestr → plik → Download) i otwórz w Excelu. Separator to średnik, kodowanie UTF-8 z BOM, więc polskie znaki wyświetlają się poprawnie.

Kolumny: RequestId, FinalStatus, Category, NextAction, HumanReview, MatchedIssueId, Sources, Summary, DraftReply, ReviewOutcome, ReviewedDraft, ReviewerId, RunId, SavedAtUtc. Pola agenta pochodzą z `agentResultJson`; przy niepoprawnym JSON zostają puste (np. VALIDATION_FAILED).

Każdy przebieg robi trzy rzeczy:
1. Czyta plik (jeśli go nie ma, zaczyna od wiersza nagłówka).
2. Sprawdza, czy RequestId jest już w pierwszej kolumnie.
3. Jeśli nie ma: dopisuje wiersz i zwraca `SAVED`. Jeśli jest: nic nie zmienia i zwraca `ALREADY_PROCESSED`, `saved=false` (TECH-03).

`finalStatus` spoza listy albo pusty requestId zwraca `INVALID_INPUT` i niczego nie zapisuje. Błąd odczytu lub zapisu zwraca `ERROR` z komunikatem, a job kończy się poprawnie. Kolejne próby z tym samym RequestId widać w logach jobów (`FinalizeCase | ...`), nie w rejestrze.

Ograniczenie: plik jest odczytywany i zapisywany w całości, więc dwa równoległe przebiegi mogłyby nadpisać sobie wiersze. Na warsztacie jest jedna osoba na organizację i ręczny start, więc to nie występuje. Zaznacz to przy omawianiu przejścia do produkcji (tam: kolejka z Unique Reference albo Data Fabric).

Aby wyczyścić rejestr przed warsztatem, usuń plik `rejestr_spraw.csv`. Następny przebieg utworzy go od nowa.

## FindKnownIssue_Zapas: kalibracja progu T

Semantic Similarity (UiPath GenAI Activities, tryb String to string) porównuje query z description każdego kandydata. Kandydaci to wszystkie problemy przy service=unknown albo tylko problemy danej usługi. Po pętli najlepszy score porównywany jest z T. Lista znanych problemów jest wpisana jako wartość domyślna zmiennej `lstKnownIssues`, wygenerowana z `dane/known_issues.json`. Projekt chmurowy nie czyta plików z dysku.

| Para | Oczekiwane | Score (9.10.2026, 2 przebiegi) |
|---|---|---|
| SIM-05 identyczny tekst | MATCH | 1,00 |
| SIM-02 parafraza kwartał / Internal Server Error | MATCH | 0,86 |
| SIM-01 = REQ-001 | MATCH | 0,82 |
| SIM-06 = REQ-009 (faktury) | MATCH | 0,68–0,70 |
| SIM-03 / DEMO-02 CSV bez nagłówków | NO_MATCH | 0,38–0,42 |
| SIM-04 ciemny motyw | NO_MATCH | 0,08 |

**T=0,6** rozdziela obie grupy. Pierwsza próba z T=0,8 gubiła REQ-009. Najsłabszy MATCH ma ok. 0,08 zapasu, a score waha się między uruchomieniami o ok. 0,02. Model to domyślny model aktywności (w schemacie `gpt-5.1-2025-11-13`), więc po zmianie modelu skalibruj próg ponownie. Uczestnicy w ćw. 2 mogą dojść do innego T; to jest w porządku, liczy się uzasadnienie na parach.

Wymaga połączenia **UiPath GenAI Activities** w Integration Service. W kmisko jest w personal workspace; robot w Shared z niego korzysta. Uczestnik po imporcie wybiera w aktywności własne połączenie, bo ConnectionId jest per organizacja.

## Intake_AI_Zapas: ćwiczenia 1A i 1B

Gotowe rozwiązanie dokładnie według instrukcji, bez dodatków. Pięć argumentów In (wartości domyślne: REQ-001), zmienne summary, category, team, status. Prompt i kategorie z `Prompty_Northstar.txt`: prompt jako wyrażenie VB z `subject` i `body`, kategorie jako `Dictionary(Of String, String)` (nazwa → opis). Temperatura i model zostają domyślne (0, model domyślny aktywności).

Wariant `Intake_AI_Zapas_Windows` ma identyczną logikę (zbudowany i spakowany 12.10.2026, nietestowany na tenancie, bo serverless wymaga cross-platform).

Uczestnik, który utknął: rozpakuj folder i otwórz `project.json` w Studio Desktop. Wybierz własne połączenie **UiPath GenAI Activities** w obu aktywnościach, bo ConnectionId jest per organizacja.

| Test (`python -I testy_intake.py ../UiPath_AI_Warsztat`, 12.10.2026) | Wynik |
|---|---|
| REQ-001, 003, 004, 005, 006, DEMO-01 | Kategoria i zespół zgodne z tabelą kroku 5 (1B); REQ-001 zachowuje „500” i „60 dni” |
| TEST-EMPTY (pusty body) | NEEDS_DETAILS, „Brak treści zgłoszenia”, bez wywołania AI |
| REQ-007 („Nie działa. Pomocy.”) | **INCIDENT** zamiast OTHER, 3 z 3 przebiegów. Opis INCIDENT („niedziałającej funkcji”) pasuje dosłownie do treści. Dobry materiał do zdania z kroku 5: „doprecyzuj opis kategorii zamiast dodawać If” |

## SupportAgent (rozwiązanie Northstar_Agent)

Agent autonomiczny low-code: model `anthropic.claude-sonnet-4-6` (GA na tenancie kmisko), temperatura 0, maxIterations 8, maxTokens 8192. Prompt systemowy i użytkownika z `prompty/03_agent_system.txt` i `04_agent_user.txt` (tokeny `{{input.x}}`), wynik według `kontrakty/agent_output.schema.json`, opisy narzędzi z sekcji „Opis dla agenta” w `kontrakty/narzedzia.md`.

Narzędzia to procesy z folderu Shared (`location: external`): FindKnownIssue → FindKnownIssue_Zapas, GetServiceStatus → GetServiceStatus_Zapas, GetTicketStatus → GetTicketStatus_Zapas. Agent nie widzi `simulateFailure`, więc model nie decyduje o awarii; workflow przyjmuje wtedy wartość domyślną false. Awarię do testu TECH-01 włączasz na kopii narzędzia albo przez wejście procesu.

Wgrany do Studio Web przez `uip agent debug`. Pierwsze uruchomienie w Studio Web pokaże ten sam agent do edycji.

| Test (`python -I testy_agent.py REQ-002 REQ-003 REQ-001 REQ-007`) | Wynik |
|---|---|
| REQ-002 portal nie działa | INCIDENT / DRAFT_REPLY, wywołany GetServiceStatus, sources SERVICE:portal, bez terminu |
| REQ-003 status INC-104 | STATUS_REQUEST / DRAFT_REPLY, wywołany GetTicketStatus, sources TICKET:INC-104 |
| REQ-001 eksport 500 | INCIDENT / DRAFT_REPLY, wywołany FindKnownIssue, matchedIssueId KI-001, obejście z KI-001 |
| REQ-007 „nie działa” | OTHER / ASK_DETAILS, bez narzędzi, prośba o usługę, czynność i objawy |

4/4 zgodne z `testy/oczekiwane_wyniki.json` (kategoria, akcja, humanReview, matchedIssueId, wymagane narzędzia). Jeden run trwa ok. 12–20 s. Uwaga do ćw. 5: w REQ-001 szkic dodaje „pracujemy nad trwałym rozwiązaniem”, czego nie mówi żadne narzędzie. To dobry przykład dla oceny LLM-as-a-judge.

`uip agent debug` kończy się stanem Suspended, gdy agent czeka na job narzędzia. Agent dokańcza pracę, a wynik jest w trace (`uip traces spans get <TraceId>`, span agentOutput). Skrypt testowy odczytuje go stamtąd.

## Wiedza agenta (ćw. 4): indeks Northstar_KB

- Bucket **Northstar_KB** (Shared) zawiera tylko `Portal_Northstar.txt`.
- Indeks Context Grounding **Northstar_KB** (Shared) ze źródłem w tym buckecie i ekstrakcją **NativeV1**. Ingestia trwa ok. 10 s. Cały plik to jeden fragment, bo dokument jest krótki.
- **Community: zaawansowana ekstrakcja (domyślne `LLMV4` w CLI) daje HTTP 402 „Unavailable with current plan”.** Działa tylko ekstrakcja podstawowa. Ostrzeżenie dopisano do preflightu, ćw. 4 i diagnostyki.
- CLI: `uip context-grounding` wymaga Pythona z pakietem `uipath`. Zainstalowano go w `pakiet_importu/.venv` (aktywuj przed użyciem: `source .venv/Scripts/activate`), nie w globalnym Pythonie.
- W agencie: kontekst `resources/Northstar_KB` (semantic, 3 wyniki, opis z ćw. 4, krok 3).

| Test (`python -I testy_agent.py REQ-005 REQ-008 REQ-002 REQ-009`) | Wynik |
|---|---|
| REQ-005 pobieranie faktur | HOW_TO / DRAFT_REPLY, sources KB-001, kroki z procedury |
| REQ-008 zmiana rachunku dostawcy | HOW_TO / HUMAN_REVIEW, sources KB-004, bez wymyślonej instrukcji |
| REQ-002 portal | bez zmian: GetServiceStatus, bez wiedzy |
| REQ-009 brak faktur | FindKnownIssue → KI-002 i KB-001 |

Regresja REQ-001, REQ-003 i REQ-007 po dodaniu wiedzy: bez zmian. Uwaga do ćw. 5: szkic REQ-008 mówi „przekazujemy zgłoszenie do zespołu”, choć agent tylko rekomenduje przegląd (reguła 11). To przykład dla oceny LLM-as-a-judge.

## Ewaluacja (ćw. 5): v1 → v2

**Zestaw w agencie:** „Northstar DEVELOPMENT” (REQ-001…010) z `testy/oczekiwane_wyniki.json`. Evaluatory:
- Exact match osobno na category, nextAction i humanReview (`targetOutputKey`);
- Trajectory z opisem wymaganych narzędzi;
- LLM-as-a-judge na szkic według rubryki 05, karzący za niewykonane działania i wymyślone terminy.

Pliki: `SupportAgent/evals/`.

**Uruchomienie z interfejsu Studio Web działa** (9.10.2026: import `testy/import_Northstar_DEVELOPMENT.json` → Run → completed, 10/10 wykonanych, Default Evaluator 95,1). **Uruchomienie z CLI (`uip agent eval run start`) w kmisko nie działa:** każdy job kończy się `PrepareEnvironmentError` „Failed to resolve project … 403”. Na warsztacie uruchamiamy więc z Studio Web. Import przypisuje tylko Default Evaluator, bo `evaluatorRefs` jest puste; pozostałe evaluatory (3 × Exact match, Trajectory, LLM-judge szkicu) są w agencie i trzeba je przypisać do evaluation setu ręcznie.

**Ewaluacja wykonana zastępczo:** 10 × `uip agent debug`; pola porównane deterministycznie, narzędzia z trace, szkice przejrzane skanerem zdań z deklaracją działania (`dist/eval_v1_manual.txt`, `dist/eval_v2_manual.txt`).

| Miara | v1 (prompt z pakietu) | v2 (jedna poprawka) |
|---|---|---|
| category, nextAction, humanReview, matchedIssueId | 10/10 | 10/10 |
| Wymagane narzędzia wywołane | 10/10 | 10/10 |
| Zdania o działaniach, których nikt nie wykonał („przekazaliśmy”, „skontaktuje się”, „poinformujemy”) | 6 (REQ-001, 002, 004, 006×2, 008) | 2 (REQ-006, 008) |
| Wymyślone terminy, ujawnione dane | 0 | 0 |

Poprawka v2 (`prompty_v2/03_agent_system_v2.txt`, plik uczestników bez zmian): reguła 11 dopisuje zakaz deklarowania działań bez potwierdzenia narzędzia. Przykład wyniku w prompcie nie mówi już „Przekazaliśmy ją do analizy zespołu produktu”, bo to on uczył agenta tego zachowania w REQ-006. Agent ma teraz wgrany prompt v2.

Zostaje do v3 (celowo jedna zmiana naraz): REQ-010 wpisuje do `sources` `TICKET:INC-999`, choć narzędzie zwróciło NOT_FOUND z pustym sourceId (reguła 12). Wniosek dla grupy: prompt zmniejsza problem, ale go nie usuwa. Pewność daje dopiero kontrola poza modelem (evaluator, walidacja w procesie, guardrail).

Wyniki ewaluacji bez eksportu: `uip agent eval run list --set "Northstar DEVELOPMENT" --path ./SupportAgent`, potem `uip agent eval run results <runId> --set "Northstar DEVELOPMENT" --path ./SupportAgent --verbose` (uzasadnienia evaluatorów). Uruchamianie ewaluacji z CLI zwraca 403 na Community; odczyt działa.

## Wdrożenie na tenant (wykonane 9 października 2026, organizacja kmisko)

```bash
uip rpa pack "<projekt>" dist --output json
uip or packages upload dist/<projekt>.1.0.0.nupkg --output json
uip or processes create --name <projekt> --package-key <projekt> --package-version 1.0.0 --folder-path Shared --robot-size Small
uip or buckets create Northstar_Rejestr --folder-path Shared
```

Uczestnicy: import pakietu `.nupkg` z `dist/` do własnej organizacji (Orchestrator → Tenant → Packages → Upload), potem proces w folderze Shared i bucket `Northstar_Rejestr`. Alternatywnie: otwórz projekt w Studio 26 i Publish.

## Wyniki testów na tenancie (robot serverless, Shared)

`python -I testy_narzedzi.py ../UiPath_AI_Warsztat [GTS GSS FKI FIN]` uruchamia 24 przypadki (procesy wyszukuje po nazwie w Shared) i porównuje pola Out. Wynik 12.10.2026, wersja 2.0.0: 23/23 OK.

| Test | Wynik |
|---|---|
| GetTicketStatus: FOUND INC-104 i INC-105, normalizacja „ inc-104 ” + wielkie litery w e-mailu, NOT_FOUND, FORBIDDEN bez danych sprawy, ERROR | 6/6 OK |
| GetServiceStatus: portal DEGRADED, sales OPERATIONAL, unknown NOT_FOUND, ERROR | 4/4 OK |
| FindKnownIssue: 6 par SIM, REQ-001 → KI-001, REQ-009 → KI-002, REQ-006 i DEMO-02 → NO_MATCH, pusty query i awaria → ERROR | 12/12 OK |
| FinalizeCase (pełny cykl rejestru: `python -I testy_finalize.py`, od pustego rejestru; wynik z 9.10.2026, wersja 1.x): REQ-001 i REQ-004 → SAVED, REQ-001 ponownie → ALREADY_PROCESSED (TECH-03), zły finalStatus → INVALID_INPUT, niepoprawny JSON agenta → SAVED z pustymi polami agenta. W pliku 3 wiersze po 14 kolumn, szkic ze średnikiem, cudzysłowem i nową linią poprawnie zakodowany | 5/5 OK |

Lokalne `uip rpa run` na laptopie prowadzącego nie działa (Studio/Robot 24.10 nie uruchamia projektów 26). Dlatego testy runtime wykonano na tenancie.
