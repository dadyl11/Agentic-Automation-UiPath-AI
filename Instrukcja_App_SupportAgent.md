# App (low-code) uruchamiająca SupportAgenta

Prosta aplikacja w Studio Web: formularz z inputami agenta, przycisk uruchamiający, wynik na ekranie.

**Wymagania:** agent wdrożony w folderze **Academy**. Uprawnienia: *Apps → Create* w folderze, *App Versions → Create* na tenancie.

> **Do sprawdzenia w kroku 3:** dokumentacja Apps opisuje regułę *Start process* tylko dla procesów z Orchestratora i nie potwierdza wprost, że agent pojawi się na liście zasobów. Jeśli go nie ma, użyj wariantu B na końcu.

## Kroki

1. **Studio Web → Create New → App.** Nazwa: `SupportAgent_App`.
2. **Kontrolki na `MainPage`:**
   - Text input: `requestId`, `requesterEmail`, `subject`, `body` (`body` wielolinijkowe).
   - Dropdown lub Text input: `service`.
   - Button: `btnRun` ("Uruchom").
   - Label: `lblCategory`, `lblNextAction`, `lblHumanReview`, `lblSources`, `lblStatus`.
3. **Dodaj proces:** lista rozwijana obok **Add control** → **Process** → tenant → **Next** → agent z folderu **Academy** → **Add**.
4. **Reguła na przycisku:** `btnRun` → **Events** → **Create rule** → **Start process**.
   - **What process to start:** SupportAgent.
   - **Type:** Unattended (szablon **Any machine** lub **Production machine**; **Testing** nie działa: "No unattended runtimes configured on the machine").
   - **Run Asynchronous:** odznaczone (kolejne reguły czekają na wynik).
5. **Input Override** (argument z panelu **Resources**, składnia `Processes.<proces>.<argument>`):

   | Argument | Wartość |
   |---|---|
   | `requestId` | `MainPage.requestId.Value` |
   | `requesterEmail` | `MainPage.requesterEmail.Value` |
   | `subject` | `MainPage.subject.Value` |
   | `body` | `MainPage.body.Value` |
   | `service` | `MainPage.service.Value` |

6. **When started:** ustaw `lblStatus` na "Trwa przetwarzanie…" (lub pokaż spinner).
7. **When completed:** ustaw teksty etykiet z argumentów wyjściowych, np. `lblCategory` ← `Processes.<proces>.category`; tak samo `nextAction`, `humanReview`, `sources`. Na końcu `lblStatus` ← "Gotowe".
   - Nazwy argumentów wyjściowych weź z panelu **Resources**. Mogą różnić się od `agent_output.schema.json`.
   - `JobStatus` jest dostępne jako właściwość wyjściowa reguły.
8. **Errors:** reguła **Show Message** (typ Error) z treścią `Error` (komunikat błędu zadania).
9. **Test:** **Preview**, wpisz dane REQ-001 z `dane/zgloszenia.json`, porównaj kategorię i akcję z `testy/oczekiwane_wyniki.json`.
10. **Publish i wdrożenie:**
    - **Publish** → opis → potwierdź (nowa wersja na tenancie).
    - Orchestrator → folder **Academy** → **Automations → Apps → Deploy app** → App i wersja → **Deploy**.

## Wariant B: agent niewidoczny w Apps

W Studio Desktop zbuduj proces z argumentami `in_*` / `out_*`, który woła agenta aktywnością **Run Job** (jak w ćwiczeniu 6C). Opublikuj do folderu Academy i w kroku 3 dodaj ten proces zamiast agenta. Pozostałe kroki bez zmian.

## Uwagi

- Status pośredni (*When state changes*) działa tylko w trybie Attended. Przy Unattended używaj *When started* i *When completed*.
- Unattended wymaga robota; na Community użyj Serverless, jeśli folder go ma.

## Źródła (docs.uipath.com)

- [Rule: Start process](https://docs.uipath.com/apps/automation-cloud/latest/user-guide/rule-start-process)
- [Connecting your app to an Orchestrator tenant](https://docs.uipath.com/apps/automation-cloud/latest/user-guide/connecting-your-app-to-an-orchestrator-tenant)
- [Publishing, deploying, and upgrading app projects](https://docs.uipath.com/studio-web/automation-cloud/latest/user-guide/publishing-deploying-upgrading-app-projects)
- [About Apps (uprawnienia)](https://docs.uipath.com/orchestrator/automation-cloud/latest/user-guide/about-apps)

Sprawdzone przez `uip docsai` 2026-10-13. Funkcje potwierdź na docelowym tenancie.
