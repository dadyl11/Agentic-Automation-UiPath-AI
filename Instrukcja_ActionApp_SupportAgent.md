# Action App zamiast Quick Form w Northstar_Case

Zamiana węzła **Quick Form** („Przegląd szkicu” z ćwiczeń 6A/6B) na **Human task → Action App**. Kontrakt pól i wyników zostaje ten sam, więc FinalizeCase zmienia się tylko w odwołaniach do węzła.

**Wymagania:** Northstar_Case z 6A/6B (SupportAgent, Decision, FinalizeCase) oraz uprawnienia do publikacji i wdrożenia aplikacji w folderze.

## 1. Zbuduj Action App

**Studio Web → New project → App** (szablon Blank page). Nazwa: `Northstar_Przeglad`.

1. **Project Explorer → + → Action → Continue.** Otworzy się edytor schematu (domyślnie: wynik Submit i jedna właściwość wejściowa).
2. Domyślną właściwość wejściową zmień na `requestId`, resztę dodaj przez **Add property** (typ String):

   | Właściwość | Kierunek | Obowiązkowa |
   |---|---|---|
   | requestId | Input | tak |
   | category | Input | tak |
   | summary | Input | tak |
   | rationale | Input | tak |
   | draftReply | Input | tak |
   | reviewedDraft | Output | nie |
   | reviewerComment | Output | nie |

3. **Outcomes:** zmień nazwę Submit na `Approve`, kliknij **+** i dodaj `Reject`.
4. Na stronie aplikacji dodaj:
   - 5 kontrolek **Label** z tekstem w stylu `"Kategoria: " + ActionProperties.category` (po jednej na każdą właściwość Input),
   - 2 pola **Text input**: `txtReviewedDraft` (wielolinijkowe) i `txtComment`,
   - 2 przyciski: `Approve` i `Reject`.
5. Dla każdego przycisku: **Events → Clicked on → Define automation** → dodaj **Submit Action**:
   - **Outcome:** `Approve` (dla drugiego przycisku `Reject`).
   - **Add Properties Override:** `reviewedDraft` ← `Controls.<NazwaStrony>.txtReviewedDraft.Value`, `reviewerComment` ← `Controls.<NazwaStrony>.txtComment.Value`.
   - Właściwości Output bez override wracają z wartościami domyślnymi. Zmiana nazwy właściwości usuwa jej override, więc nazwij je przed tym krokiem.
6. **Publish** → nazwa `Northstar_Przeglad` → **Publish**.
7. **Wdrożenie:** Orchestrator → **Automations → Apps → Deploy app** → wybierz aplikację → **Deploy**. Jeśli aplikacja jest częścią rozwiązania Studio Web: zakładka **Solutions**, runtime serverless.
8. Po wdrożeniu: **Edit the process details → Next → Cloud Robot - Serverless: Medium → Update**.

## 2. Zamień węzeł w Northstar_Case

1. Zapisz wyrażenia z węzła Quick Form (mapowania pól), potem go usuń.
2. Na wyjściu **Przegląd** z Decision „Wymaga przeglądu?”: **+ → Human task → Action App**. Nazwa: **Przegląd szkicu**.
3. Wybierz wdrożoną aplikację `Northstar_Przeglad`.
4. Zmapuj pola przez **{} Insert**:

   | Pole aplikacji | Wartość |
   |---|---|
   | requestId | z Manual trigger (`$vars.manualTrigger1.output.requestId`) |
   | category, summary, rationale, draftReply | z SupportAgent (`$vars.supportagent1.output.<pole>`) |

5. **Assignment criteria:** Single User i Twój użytkownik (jeśli węzeł oferuje to pole).
6. Połącz wyjścia **Approve** i **Reject** z tymi samymi węzłami co wcześniej. Jeśli węzeł nie pokazuje osobnych wyjść, dodaj **Decision** z warunkiem `$vars.<id węzła>.status === "Approve"`.
7. W FinalizeCase zamień `$vars.quickForm1.output.reviewedDraft` na `$vars.<id nowego węzła>.output.reviewedDraft`. Pozostałe argumenty bez zmian (tabela ścieżek w 6B).

## 3. Test

Action App nie ma podglądu na canvasie: cykl to build, deploy, run.

1. **Debug** z danymi REQ-004. Zadanie pojawi się w **Action Center → Tasks**. Wpisz `reviewedDraft` i komentarz, wybierz **Approve**. Powtórz z **Reject**.

   | Sprawdzenie | OK? |
   |---|---|
   | Zadanie pokazuje category, summary, rationale i draftReply tylko do odczytu | ☐ |
   | Approve i Reject idą osobnymi ścieżkami | ☐ |
   | reviewedDraft i reviewerComment są w output węzła | ☐ |
   | FinalizeCase zapisuje reviewedDraft z nowego węzła | ☐ |
   | Bez decyzji flow czeka | ☐ |

## Do sprawdzenia na tenancie

- Dokumentacja Maestro opisuje szczegółowo tylko Quick Form. Panel węzła Action App (wybór aplikacji, mapowanie pól, wyjścia dla outcomes) może wyglądać inaczej niż w punkcie 2.
- `sources` jest poza kontraktem: dodaj opcjonalną właściwość String i zmapuj `sourcesText` z rozszerzenia 6B.

## Źródła (docs.uipath.com)

- [Human (Maestro)](https://docs.uipath.com/maestro/automation-cloud/latest/user-guide/node-human)
- [Designing an action app](https://docs.uipath.com/studio-web/automation-cloud/latest/user-guide/designing-an-action-app)
- [Submit Action](https://docs.uipath.com/activities/other/latest/workflow/submit-action)
- [Creating agent escalations with Action apps](https://docs.uipath.com/action-center/automation-cloud/latest/user-guide/quick-start-guide-for-app-actions-and-agents)

Sprawdzone przez `uip docsai` 2026-10-14. Funkcje potwierdź na docelowym tenancie.
