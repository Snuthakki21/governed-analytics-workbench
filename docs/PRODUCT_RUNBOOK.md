# Product runbook — Governed Analytics Workbench

## Normal operation

1. Start the native app or open the static browser app. Confirm the scenario and execution mode.
2. Load an example or import a validated input. Save a scenario revision before changing assumptions.
3. Execute the domain workflow. Read the summary, failed controls and full evidence before recording a review.
4. Compare saved runs with the same question and scenario scope. Export input and report together for reproduction.
5. Use the native workspace backup/export controls before moving or deleting local storage. Browser-local storage must be exported before clearing browser data.

## Product-specific review

- **Ask an operational question:** Choose one metric—case volume, average resolution time or breach rate—and optionally group by region or team. Scope the query to allowed regions. Supported vocabulary is deliberately bounded and unsupported filters are rejected.
- **Inspect the semantic contract:** Review the registered metric expression, version, unit, grain and null policy. The query explanation shows the selected region parameters and every validation, reconciliation and disclosure step.
- **Resolve ambiguity safely:** A request containing multiple metrics, unsupported dates, individual records or unknown groupings receives an explicit clarification error before data access. The planner evaluation exposes accepted and refused examples.
- **Validate released results:** Inspect read-only parameterized SQL, independent Python reconciliation, minimum group size and complementary suppression. Quality diagnostics operate only on released groups and do not add hidden counts.

## Fault handling

| Symptom | Resolution |
|---|---|
| Input rejected | Match the bounded schema in DOMAIN_CONTRACTS; do not weaken validation to fit malformed data. |
| Unexpected calculation | Export the exact input and full report, then reproduce through the CLI and inspect the named domain service. |
| Optional provider failure | Check model/endpoint settings and schema; retain the failed result as a failure, not an approval. |
| Old UI/source | Rebuild the site and restart the native process after Python changes. |
| Workspace conflict | Reload the latest revision before applying changes; preserve conflicting edits in a separate scenario. |
| Browser storage missing | Check origin and browser profile. Static and native workspaces do not share a database. |

## Change and recovery procedure

Run domain and full application tests after a rule change. Regenerate example outputs, inspect affected decisions and request an independent review of changed boundaries. Keep source/version evidence with exported reports. Do not relabel historical validation as a review of later source.

## Deployment scope

Native service is a local single-operator workspace unless an authenticated deployment is explicitly implemented. Public Pages is a client-side application. No multi-user authorization, production SLA, compliance certification or real financial transaction execution is implied by a passing test suite.
