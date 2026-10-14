# UiPath Solution Workspace

> **A `.uipx` file in this directory marks a UiPath solution. Drive every solution operation through the `uip` CLI — packing, publishing, deploying, and deployment configuration.** Do not hand-edit `.uipx`; manage projects via `uip solution projects ...` so the manifest stays internally consistent. Load the `uipath-solution` skill before running `uip solution` commands or editing `.uipx` (`uip skills install`).

This file was trimmed from the CLI-scaffolded reference (uip `1.202.1`). Everything removed is available from `uip <group> --help` and the uipath skills; look commands up there instead of relying on a static copy.

## Essentials

- `<solution>.uipx` at the solution root lists every project. Membership changes only via the CLI: `uip solution init <name>`, `uip solution projects add|import|remove|list`.
- `uip ... init` scaffolders auto-register new projects inside a solution directory (`--skip-solution-registration` opts out).
- Library projects are not registered as solution projects; publish them separately (`uip rpa pack`, `uip or libraries upload`).
- Lifecycle: `uip login` -> `uip solution pack . ./out` (`--dry-run` to validate) -> `uip solution publish <zip>` -> `uip solution deploy config get|set` -> `uip solution deploy run`.
- Project-type scaffolding and skills: `uipath-rpa`, `uipath-maestro-flow`, `uipath-maestro-case`, `uipath-maestro-bpmn`, `uipath-agents`, `uipath-coded-apps`, `uipath-functions`, `uipath-api-workflow`.
- Per-project resource declarations live in `bindings_v2.json`; use `uip solution resources ...` rather than editing by hand.
