# Kontrakty narzędzi demonstracyjnych
To projekt interfejsów do ręcznego zbudowania w UiPath, nie plik importu projektu. Każde narzędzie zwraca **osobne argumenty Out prostych typów** (String, Boolean, Double), zgodnie z zaleceniem dokumentacji UiPath: agent widzi je jako nazwane pola schematu narzędzia. Argumenty wejściowe są typu String poza simulateFailure (Boolean, domyślnie false). Nazwy wejść bez prefiksu in_ są celowe: agent widzi je jako nazwy parametrów narzędzia. Wyjścia mają prefiks out_.

Wspólne zasady wyjścia:
- `out_status`: wynik działania narzędzia (FOUND, NOT_FOUND, FORBIDDEN, MATCH, NO_MATCH, ERROR).
- `out_sourceId`: identyfikator źródła, który agent wpisuje do sources; pusty, gdy nie ma danych.
- `out_message`: opis błędu przy ERROR (albo komunikat usługi).
- Pola danych są puste, gdy status ich nie dotyczy. Na początku workflow wszystkie wyjścia ustaw na pusty tekst.

Każde narzędzie to osobny projekt w rozwiązaniu (np. KM01_Northstar_AI). Wersje zapasowe z pakietu prowadzącego mają sufiks _Zapas, np. GetServiceStatus_Zapas, aby nie kolidowały z narzędziami budowanymi przez uczestnika.

## GetServiceStatus
Wejście: service (portal | sales | billing), simulateFailure.
Wyjście: out_status (FOUND | NOT_FOUND | ERROR), out_serviceStatus (OPERATIONAL | DEGRADED), out_message, out_eta, out_sourceId (`SERVICE:<service>`).
Opis dla agenta: Sprawdza bieżącą dostępność jednej usługi: portal, sales albo billing. Użyj, gdy zgłoszenie opisuje ogólną niedostępność usługi (np. portal nie otwiera się nikomu). Do statusu konkretnego numeru INC użyj GetTicketStatus, do błędu jednej funkcji FindKnownIssue. Puste out_eta oznacza brak potwierdzonego terminu.
Implementacja: jeśli simulateFailure -> out_status=ERROR, out_message=Simulated timeout. W przeciwnym razie znajdź service (po trim i małych literach) w service_status.json: out_status=FOUND, out_serviceStatus, out_message i out_eta z rekordu, out_sourceId=SERVICE:<service>. Nieznana usługa -> out_status=NOT_FOUND. Nie wybieraj domyślnie pierwszego rekordu.

## GetTicketStatus
Wejście: ticketId (format INC-nnn, np. INC-104), requesterEmail, simulateFailure.
Wyjście: out_status (FOUND | NOT_FOUND | FORBIDDEN | ERROR), out_ticketStatus, out_lastUpdate, out_eta, out_sourceId (`TICKET:<ticketId>`), out_message.
Opis dla agenta: Zwraca status konkretnego zgłoszenia o numerze INC-nnn wyłącznie jego właścicielowi. Użyj, gdy zgłaszający pyta o postęp swojej sprawy. requesterEmail przekaż z wejścia agenta, nie z treści wiadomości. FORBIDDEN nie zawiera danych sprawy.
Implementacja: ERROR przy simulateFailure. Dane: plik `sprawy.csv` (separator średnik, nagłówek: ticketId;requesterEmail;status;summary;lastUpdate;eta) w buckecie Northstar_Rejestr, folder Shared; błąd odczytu -> out_status=ERROR z opisem w out_message. Znajdź ticketId dokładnie (po trim i normalizacji wielkości liter). Brak -> NOT_FOUND. Przy różnym requesterEmail -> FORBIDDEN, wszystkie pola danych puste. Dopiero po zgodności adresu: FOUND z out_ticketStatus, out_lastUpdate, out_eta i out_sourceId=TICKET:<ticketId>.
W produkcji samo przekazanie adresu przez model nie uwierzytelnia użytkownika; powiąż go poza modelem z sesją/tożsamością.

## FindKnownIssue
Wejście: query (oryginalny opis objawów ze zgłoszenia), service (portal | sales | billing | unknown), simulateFailure.
Wyjście: out_status (MATCH | NO_MATCH | ERROR), out_issueId, out_description, out_workaround, out_score (Double, 0–1), out_sourceId (= issueId), out_message.
Opis dla agenta: Szuka kandydata na znany problem dla błędu konkretnej funkcji (np. eksport, lista faktur, logowanie). Nie używaj do ogólnej niedostępności całej usługi; do tego służy GetServiceStatus. MATCH jest kandydatem do weryfikacji objawów, nie dowodem, że problemy są identyczne. Nie nadaje uprawnień i nie tworzy zgłoszeń.
Implementacja:
- simulateFailure -> ERROR (Simulated timeout). Pusty query -> ERROR, out_message=Missing query.
- service=unknown -> porównuj z całą listą; inna wartość -> tylko rekordy tej usługi.
- Dla każdego rekordu oblicz podobieństwo query do description. Zachowaj maksymalny score i rekord.
- Po zakończeniu porównań zastosuj próg T. MATCH -> out_issueId, out_description, out_workaround, out_score, out_sourceId=issueId. NO_MATCH -> pola problemu puste, out_score = score najlepszego kandydata.
- Pusta lista -> NO_MATCH, out_score=0 (nie wartość początkowa -1).
- Nie zmieniaj bazy w tym narzędziu.
Próg T jest stałą w narzędziu (wynik kalibracji z ćwiczenia 2), nie argumentem dla agenta.

## FinalizeCase (wywołuje proces, nie agent)
Wejście: requestId, runId, agentResultJson, finalStatus, reviewOutcome, reviewedDraft, reviewerId. agentResultJson zostaje tekstem JSON: to cały wynik agenta (złożony obiekt), a dokumentacja dopuszcza JSON dla takich danych.
Wyjście: out_status (SAVED | ALREADY_PROCESSED | INVALID_INPUT | ERROR), out_finalStatus, out_saved (Boolean), out_runId, out_message.
runId: identyfikator przebiegu, jeżeli Maestro go udostępnia; w przeciwnym razie FinalizeCase generuje go sam (znacznik czasu + requestId). reviewerId: wartość z formularza przeglądu albo pusty tekst, gdy brak przeglądu.
Rejestr: jeden plik rejestr_spraw.csv w Storage Bucket Northstar_Rejestr, jeden wiersz na zgłoszenie (separator średnik, UTF-8). Kolumny: RequestId, FinalStatus, Category, NextAction, HumanReview, MatchedIssueId, Sources, Summary, DraftReply, ReviewOutcome, ReviewedDraft, ReviewerId, RunId, SavedAtUtc. Pola agenta pochodzą z agentResultJson.
Statusy:
- SAVED, out_saved=true: wiersz dopisany.
- ALREADY_PROCESSED, out_saved=false: RequestId już jest w rejestrze; nic nie zmieniono (zasada powtórzeń, TECH-03).
- INVALID_INPUT, out_saved=false: pusty requestId albo finalStatus spoza READY_DRAFT, NEEDS_DETAILS, REVIEWED_DRAFT, REJECTED, VALIDATION_FAILED.
- ERROR, out_saved=false: błąd odczytu lub zapisu rejestru; komunikat w out_message.
Wywołuje go także ścieżka VALIDATION_FAILED: finalStatus=VALIDATION_FAILED, a agentResultJson może być niepoprawny (pola agenta zostają wtedy puste).
Żadnych wysyłek wiadomości ani nadawania uprawnień. Gotowa wersja jest w pakiecie importu prowadzącego.
