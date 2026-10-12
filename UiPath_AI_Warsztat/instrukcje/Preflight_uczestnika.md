# Preflight uczestnika | UiPath AI / Northstar

| | |
|---|---|
| **Cel** | Sprawdzić przed warsztatem, że Twoja organizacja UiPath Community ma wszystko, czego użyjemy. |
| **Kiedy** | Najpóźniej 5 dni roboczych przed warsztatem |
| **Czas** | 45–60 min |
| **Wynik** | Zrzuty ekranu z punktu 8 wysłane prowadzącemu |

> **Zasada danych:** używaj wyłącznie plików z pakietu. Nie wgrywaj firmowych dokumentów, danych klientów ani pracowników, haseł, danych płatniczych ani medycznych.

## 1. Organizacja Community

- [ ] Mam własną organizację UiPath Community i zapisałem/am jej adres.
- [ ] Nie zużywam puli consumables na własne eksperymenty z AI w miesiącu szkolenia.

## 2. Licencje i zużycie

- [ ] Plan pokazuje Community.
- [ ] Widzę przydzielone licencje użytkownika i robota oraz pulę consumables.

## 3. Usługi

| Usługa | Sprawdzenie | OK? |
|---|---|---|
| Studio Web | Otwiera się | ☐ |
| Agents | Mogę utworzyć agenta | ☐ |
| Orchestrator | Otwiera się | ☐ |
| Maestro | Otwiera się i pozwala utworzyć proces | ☐ |
| Apps, Action Center | Otwierają się | ☐ |
| UiPath Assistant (lokalnie) | Wersja 2026.0.190+, zalogowany do mojej organizacji Community. RPA workflow z Log Message uruchamia się w Studio Web w trybie Debug | ☐ |
| Studio Desktop (lokalnie) | Wersja **2026.x** (najnowsza Community), zalogowane do mojej organizacji Community. Nowy projekt Process **cross-platform** z aktywnością **Content Generation** (połączenie UiPath GenAI Activities, prompt „Napisz OK”) zwraca wynik. Ten projekt publikuję (Publish) do folderu Shared i widzę go w Orchestratorze jako proces | ☐ |

> **Brakuje usługi?** Sprawdź Admin → Tenant → Services. Jeśli nadal jej nie ma, zgłoś to prowadzącemu.

## 4. Test agenta

1. Utwórz agenta autonomicznego **PreflightAgent**.
2. Argumenty:

   | Argument | Kierunek | Typ |
   |---|---|---|
   | message | wejście | String |
   | summary | wyjście | String |

3. Prompt użytkownika (argument wstaw przez edytor):

```text
Podsumuj w jednym zdaniu: {{input.message}}
```

4. Uruchom z tekstem: „Portal nie otwiera się u nikogo w zespole.”
5. Otwórz **Execution Trail**.

- [ ] Widzę niepusty wynik summary i otwarty trace.

## 5. Test wiedzy

1. W Orchestratorze utwórz Storage Bucket **Northstar_KB** i wgraj do niego `baza_wiedzy/Portal_Northstar.txt`.
2. Utwórz indeks **Context Grounding** ze źródłem Storage Bucket, z podstawową ekstrakcją tekstu (Basic).
3. Uruchom synchronizację (ingestion) i poczekaj na status zakończony powodzeniem.
4. Wyszukaj „Jak pobrać faktury?”.

- [ ] Wynik zawiera fragment z KB-001.

> **Uwaga (Community):** przy tworzeniu indeksu wybierz podstawową ekstrakcję tekstu (**Basic** / NativeV1). Zaawansowana ekstrakcja (Advanced / LLM) nie jest dostępna w Community: tworzenie kończy się błędem „Unavailable with current plan. Please upgrade your license” (HTTP 402). Dla pliku TXT podstawowa ekstrakcja w zupełności wystarcza. Nazwy opcji w interfejsie sprawdź na swoim tenantcie.

> **Uwaga:** indeks zostaw. Przyda się w ćwiczeniu 4.

## 6. Test zadania człowieka (potrzebny w dniu 2)

1. W Studio Web: **Create New → Flow**, nazwa **PreflightReview**. Flow: **Manual trigger → Human task → Quick Form → End**.
2. W węźle Quick Form:

   | Sekcja w Properties | Wartość |
   |---|---|
   | Schema → pole | message, kierunek Input, tekst „Test” |
   | Schema → outcomes | Approve (primary), Reject |
   | Assignment criteria | Twój użytkownik |

3. Kliknij **Debug**, poczekaj na zadanie i zakończ je, wybierając Approve.

- [ ] Zadanie dało się zakończyć, a flow zakończył się po decyzji. Jeśli nie, zapisz komunikat błędu.

## 7. Test agenta konwersacyjnego (potrzebny w dniu 2)

1. W Studio Web: **Create New → Agent → Conversational → Start fresh**. Nazwa: **PreflightChat**.
2. Prompt systemowy:

```text
Jesteś uprzejmym asystentem. Odpowiadaj po polsku, w jednym lub dwóch zdaniach.
```

3. Kliknij **Debug** i wyślij dwie wiadomości: „Cześć, mam na imię Ola.”, a potem „Jak mam na imię?”.

- [ ] Agent odpowiedział na obie wiadomości i w drugiej pamiętał imię. Jeśli pojawił się komunikat o licencji lub braku dostępu, zapisz go dosłownie.

> **Uwaga:** według dokumentacji licencji miesięczna pula dla agentów konwersacyjnych nie jest dostępna w Community. Wynik tego punktu decyduje, czy ćwiczenie 7 robisz samodzielnie, w parze czy jako pokaz.

## 8. Odeślij prowadzącemu

| Co wysłać | OK? |
|---|---|
| Zrzut: plan, licencje i pula consumables | ☐ |
| Zrzut: widoczne usługi | ☐ |
| Zrzut: wynik Content Generation w Studio Desktop i proces w Orchestratorze | ☐ |
| Zrzut: wynik PreflightAgent i Execution Trail | ☐ |
| Zrzut: zakończony indeks z wynikiem KB-001 | ☐ |
| Wynik testu zadania człowieka (działa / komunikat błędu) | ☐ |
| Wynik testu agenta konwersacyjnego (działa / dosłowny komunikat) | ☐ |
| Który krok się nie powiódł i jaki komunikat się pojawił | ☐ |

Po wysłaniu zrzutów możesz usunąć PreflightAgent i PreflightChat.
