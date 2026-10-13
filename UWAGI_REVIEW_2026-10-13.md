# Uwagi z przeglądu pakietu (13.10.2026)

Przegląd tylko do odczytu: instrukcja, prezentacja (`narzedzia_pakietu/deck_tresc.py`), projekty w `pakiet_importu`. Nic nie zostało jeszcze poprawione. Ścieżki względem `UiPath_AI_Warsztat/`, chyba że zaczynają się od `pakiet_importu`. Numery linii z dnia przeglądu.

Legenda: **[W]** wysoki priorytet, **[Ś]** średni, **[N]** niski, **(tenant)** do sprawdzenia na tenancie przed zmianą.

## Najpierw (może zepsuć warsztat)

- [ ] **[W] FinalizeCase, krok 4 „Czytaj rejestr”** (`pakiet_importu/FinalizeCase/Main.xaml`, Catch ok. l. 133–139): każdy błąd odczytu traktowany jak brak pliku → zapis nadpisuje `rejestr_spraw.csv` nagłówkiem + 1 wierszem (utrata danych); łamie kontrakt „błąd odczytu → ERROR”. Poprawka: nowy rejestr tylko przy braku pliku (List Storage Files albo konkretny błąd „not found”), inne błędy → ERROR.
- [ ] **[W] Ćw. 1A krok 2** (`instrukcje/Instrukcja_warsztatowa.md` ok. l. 286): gałąź pustego body przypisuje `summary`, `category`, `status` zanim zmienne powstaną; `status` nie jest tworzony nigdzie. Poprawka: na początku 1A krok „utwórz zmienne summary, category, status (String)” + jedno zdanie o If/Else wokół AI.
- [ ] **[W] Ćw. 6B krok 0** (ok. l. 1529–1535 vs uwaga ok. l. 1698): deploy rozwiązania KM01_Northstar_AI zawiera już Flow z 6A, czyli to de facto deploy Flow (kopie agenta bez narzędzi). Krok 0.3 („kopie jego narzędzi”) przeczy uwadze. (tenant) Ustalić, co dokładnie wdraża krok 0, i ujednolicić.
- [ ] **[W] SupportAgent ma prompt v2** (`pakiet_importu/Northstar_Agent/SupportAgent/agent.json` i `.agent-builder/agent.json`): przywrócić v1 (sekcja „SupportAgent: prompt systemowy” w `Prompty_Northstar.txt`). Prompt użytkownika jest już v1.
- [ ] **[Ś] Stare zasoby rozwiązania** (`pakiet_importu/Northstar_Agent/resources/solution_folder/package/*.json`, `process/Process/*.json`): wersje 1.0.x, `out_resultJson`. `uip solution resources refresh` albo usunąć przed pack/importem.
- [ ] **[Ś] simulateFailure w narzędziach agenta** (3B krok 5 ok. l. 1024; 5 krok 7 ok. l. 1322; TECH-01): brak kroku, żeby usunąć/ustawić statycznie `simulateFailure` w Tools; TECH-01 nie mówi, jak włączyć awarię.
- [ ] **[Ś] Prezentacja, slajd „Rozmowa uzupełnia brakujące dane”**: pokazuje FindKnownIssue, a NorthstarHelpdesk celowo go nie ma (ćw. 7 krok 4). Zmienić na CHAT-02 (GetServiceStatus, DEGRADED, brak terminu) albo CHAT-01 (KB-001).

## Czas

- [ ] **[W] Teoria poza planem dnia**: notatki prezentacji dają ok. 50–57 min teorii w dniu 2 i ok. 30 min w dniu 1 ponad plan (plan liczy same ćwiczenia). Albo napisać, że czas LAB zawiera wprowadzenie, albo dodać wiersze teorii i skrócić (najpierw blok wiedzy).
- [ ] **[Ś] Zamknięcie 15 min** (ok. l. 2006): karta agenta + prezentacje par po 5 min nie mieszczą się. 30 min albo prezentacje 2 min / tylko chętni.
- [ ] **[Ś] Karta Start 15+15 = 30 min** vs mapa i plan 25 min (l. 65 vs 20, 1988).
- [ ] **[Ś] 6B „75 min (+ demonstracja guardrails)”**: niejasne, czy demo 10–15 min jest w środku.
- [ ] **[Ś] Ćw. 5 przeładowane na 65 min** (ok. l. 1154–1326): oznaczyć 2a, JSON similarity, krok 7 i 8 jako opcjonalne; rdzeń = 2 Exact match (category, nextAction).

## Instrukcja: drobne błędy i pozostałości

- [ ] [Ś] l. 474: „dodaj cztery argumenty” → dziesięć (3 In, 7 Out).
- [ ] [Ś] l. 1764 i 2076: przykład folderu `Shared/Northstar_Agent` → `Shared/KM01_Northstar_AI`.
- [ ] [Ś] 6A (ok. l. 1453–1486) vs 6B krok 2 (ok. l. 1561, 1573): 6A mówi „dwie pierwsze reguły”, a buduje jedną (admin); zapowiedź rozszerzenia warunku niezgodna z 6B; fragment z gołym `subject`/`category` nie jest poprawnym wyrażeniem Flow.
- [ ] [Ś] (tenant) l. 1608: `agentResultJson` (String) ← `$vars.supportagent1.output` (obiekt) — sprawdzić, czy nie zapisuje „[object Object]”; ewentualnie `JSON.stringify(...)`.
- [ ] [Ś] (tenant) 6C wariant B (ok. l. 1784): czy trzeba włączyć Supports Persistence; czy Desktop publikuje do folderu rozwiązania.
- [ ] [N] l. 602: „połączone spacją” → subject + nowa linia + body.
- [ ] [N] l. 725: „GetTicketStatus_CSV” → GetTicketStatus_Zapas.
- [ ] [N] l. 1268: „Prompt 07” → sekcja „Evaluator Trajectory”.
- [ ] [N] l. 2080: „warunki bramki” (BPMN) → Decision.
- [ ] [N] nagłówek i tabela wersji (l. 3, 55–58): brak wiersza 1.3 (osobne Out, 12.10).
- [ ] [N] l. 878–882 (FinalizeCase): „otwórz projekt w Studio” — uczestnik ma tylko .nupkg → „na ekranie prowadzącego”; dystrybuować tylko 2.0.1; dodać ścieżkę uploadu pakietu.
- [ ] [N] ćw. 5 l. 1272/1286: wspomniany evaluator „Semantic Similarity”, którego nie ma; l. 1181: „Pliki JSON i CSV nie są potrzebne” przeczy wierszom importu.
- [ ] [N] l. 743: If „Sprawa istnieje?” ma warunek `arrSprawa Is Nothing` → nazwać „Brak sprawy?”.
- [ ] [N] l. 2013: ścieżka awaryjna „wspólne połączenie prowadzącego” nie działa między osobnymi organizacjami Community.
- [ ] [N] l. 1136 (ćw. 4): KB-003 dla REQ-002 oznaczyć jako opcjonalne (próba prowadzącego zwróciła tylko SERVICE:portal).
- [ ] [N] ćw. 7 krok 6: zdanie, że agent konwersacyjny ma tylko guardrails na narzędziach, może być nieaktualne (tenant / docs).

## Prezentacja

- [ ] [W] Rozgrzewka i blok Studio Web: plan dnia ma ćw. 0 przed 1A, a deck stawia teorię Studio Web po LAB 1; karta Start mówi „przed 1A”, uwaga w 1A „Studio Web poznasz w ćw. 2”. Ustalić jedną kolejność, ewentualnie dodać LAB 0.
- [ ] [Ś] Slajd „Maestro łączy agenta, regułę i człowieka” stoi po LAB 6A, a 6A to pierwszy Flow → przenieść przed LAB 6A.
- [ ] [Ś] Guardrails przed 6A, pokaz po 6B → przenieść slajd za LAB 6B.
- [ ] [Ś] „Kontrakt wyniku” (blok 1): humanReview/requestId dotyczą agenta → przenieść do bloku agenta albo przerobić pod ćw. 1.
- [ ] [Ś] LAB 6A: „sprawa bez prośby o dostęp” → „prośba o dostęp bez słowa admin omija przegląd” (test słabości reguły); dodać do „Gotowe, gdy”.
- [ ] [Ś] Blok wiedzy (8 slajdów) za długi względem prostego ćw. 4: połączyć „Jak agent szuka w wiedzy” z „Dwa pokrętła”, tabelę diagnozy przenieść do notatek/Diagnozy.
- [ ] [Ś] „Semantic Similarity = embeddingi / bliskie wektory” — dokumentacja nie opisuje mechanizmu → „ta sama idea: porównanie znaczenia”.
- [ ] [N] Dwie tabele Desktop vs Web nakładają się; „Git tylko w Desktop” może być nieaktualne (Studio Web ma Git dla rozwiązań lokalnych).
- [ ] [N] „Zakończenia procesu”: VALIDATION_FAILED tylko w rozszerzeniu → oznaczyć.
- [ ] [N] LAB 1 bez DEMO-01 (pierwszeństwo ACCESS_REQUEST); LAB 7 bez testu wieloturowego.
- [ ] [N] Slajd parametrów: „agent: Settings” → Properties; notatka Run Job: „ten sam mechanizm co Quick Form” → „ta sama idea (persistence)”; notatka ewaluacji: „na Community nie ma symulacji” → „nie używamy”.
- [ ] [N] Zakres: dodać jedną wzmiankę o konektorach Integration Service jako narzędziach agenta oraz API workflow / MCP / Maestro BPMN-Case.

## Projekty i pakiet prowadzącego

- [ ] [Ś] GetTicketStatus_Zapas (`Main.xaml` ok. l. 99): `Split(";"c)` bez kontroli liczby kolumn; średnik w polu przesuwa kolumny. Dodać `arrCols.Length = 6` → inaczej ERROR „Malformed row”; w 3A uwaga „bez średników w polach”.
- [ ] [Ś] `pakiet_importu/README.md`: liczby testów (skrypt ma 24: GTS 7, GSS 4, FKI 11, FIN 2); odwołania do `prompty/03…`, `04…`, „rubryka 05”; zdanie „wszystkie projekty Portable” (jest wariant Windows i agent); polecenia deployu z wersją 1.0.0.
- [ ] [N] FinalizeCase: pusty plik rejestru bez nagłówka → pierwszy wiersz traktowany jak nagłówek; `null` w `sources` → NullReference; wartości zaczynające się od = + - @ (CSV injection w Excelu).
- [ ] [N] Intake_AI_Zapas (oba warianty): temperatura nieustawiona jawnie (domyślnie może być 1) → ustawić 0.
- [ ] [N] SupportAgent: opis GetServiceStatus „Puste eta” → „Puste out_eta”; outputSchema bez `additionalProperties: false`.
- [ ] [N] Higiena: `hasDefault: false` w Intake mimo wartości domyślnych; GetServiceStatus_Zapas ma referencje UiAutomation/System.Drawing bez zależności; IntegrationService.Activities nieprzypięte „[1.34.0]”.
- [ ] [N] `testy/testy_techniczne.json`: TECH-02 („simulateInvalidOutput”) i TECH-03 („runId w historii”) opisują stary mechanizm; po zmianie `make_tables.py`.

## Co jest dobre (nie ruszać)

- Nazwy, statusy, formaty sourceId, bucket, próg T=0,6 i komunikaty spójne między instrukcją, kontraktem, XAML i agentem.
- Oczekiwane wyniki zgodne: Klucz_testow, oczekiwane_wyniki.json, evaluation sety, tabele ćwiczeń.
- Wszystkie dyrektywy `{{prompt|plik|tabela|diagram}}` się rozwiązują; plan dnia = 360 min (bez teorii, patrz wyżej).
- Zakres AI sensowny: robot wywołuje AI → agent używa robotów → proces kontroluje agenta; DU/IXP i Autopilot tylko wzmianka (świadomie).
