# Własny klucz OpenAI w UiPath (demo)

Dwie ścieżki. **Ścieżka A** jest prosta i według dokumentacji nie wymaga planu płatnego. **Ścieżka B** podmienia model dla całych produktów UiPath, ale nie jest dostępna na Community.

| | A. Konektor OpenAI | B. LLM configurations (AI Trust Layer) |
|---|---|---|
| Co robi | Daje aktywności i narzędzia OpenAI, które wywołujesz świadomie | Podmienia model, z którego korzystają Agents, GenAI Activities, Autopilot |
| Gdzie | Orchestrator → Connections | Admin → AI Trust Layer → LLM configurations |
| Plan | Dokumentacja nie ogranicza do planu płatnego | Brak Community na liście planów |
| Klucz | `sk-…` z platform.openai.com | Ten sam klucz, przez to samo połączenie |

> **Uwaga:** klucz OpenAI to płatne konto po stronie OpenAI (koszt według jego cennika). Nie wklejaj klucza do promptów, plików pakietu ani czatu. Do pokazu użyj klucza z niskim limitem i usuń go po demo.

## A. Konektor OpenAI (działa na Community)

1. Na [platform.openai.com/api-keys](https://platform.openai.com/api-keys) utwórz klucz (zaczyna się od `sk-`).
2. Automation Cloud → **Orchestrator** → wybierz folder (np. Shared) → zakładka **Connections**.
3. **Add connection** → wyszukaj **OpenAI**.
4. Wklej klucz w polu API key. Opcjonalnie wybierz **Use credential asset**, żeby klucz był w zasobie poświadczeń, a nie wpisany ręcznie.
5. **Connect**. Połączenie pojawia się na liście.
6. Użycie:
   - **Studio Desktop lub Web:** dodaj aktywność OpenAI i wybierz to połączenie z listy **Connection**.
   - **Agent (Studio Web):** **Definition → Tools → Add tool → Activities**, wyszukaj aktywność OpenAI i wybierz połączenie. Nie sprawdzałem, czy aktywności OpenAI są widoczne jako narzędzia agenta na Twoim tenancie.

Kto widzi połączenie, zależy od folderu, w którym je utworzono.

## B. Własny model dla Agents i GenAI Activities (tylko plany z AI Trust Layer)

1. Najpierw wykonaj kroki 1–5 ścieżki A (połączenie w folderze).
2. **Admin → AI Trust Layer → LLM configurations** → wybierz **Tenant** → **Add configuration**.
3. Wybierz **Product** (np. Agents albo Gen AI Activities) i **Feature**.
4. W **Connections Folder** wskaż folder z połączeniem.
5. Uzupełnij dane modelu: konektor **Open AI**, połączenie, identyfikator modelu (nazwa modelu u OpenAI).
6. **Test configuration**, potem **Save**.

Dla zgodnej z OpenAI bramki (np. własny serwer) użyj konektora **Open AI V1 Compliant LLM**.

## Do pokazu

- Pokaż ścieżkę A na żywo (krok 3–5 zajmują kilka minut) i omów B jako to, co robi firma z planem Enterprise.
- Jeśli menu **LLM configurations** nie jest widoczne, to potwierdza ograniczenie planu.
- Pokaż w śladzie wykonania (trace), który model odpowiedział.

## Źródła (docs.uipath.com)

- [Configuring LLMs](https://docs.uipath.com/automation-cloud/automation-cloud/latest/admin-guide/configuring-llms)
- [About AI Trust Layer](https://docs.uipath.com/automation-cloud/automation-cloud/latest/admin-guide/about-ai-trust-layer)
- [OpenAI connector: authentication](https://docs.uipath.com/integration-service/automation-cloud/latest/user-guide/uipath-openai-openai-authentication)
- [OpenAI connector](https://docs.uipath.com/integration-service/automation-cloud/latest/user-guide/uipath-openai-openai)

Sprawdzone przez `uip docsai` 2026-10-14. Dostępność na planie Community wynika z listy planów w dokumentacji, nie z testu na koncie.
