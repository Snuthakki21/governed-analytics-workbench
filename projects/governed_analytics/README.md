# Governed Operations Analytics

An operations manager asks a data question and receives an answer that has a defined metric, an explicit region scope and an independent reconciliation. The application translates supported language into a small semantic plan, executes a read-only query and withholds undersized groups.

## Two-minute demonstration

```sh
python -m portfolio run governed_analytics
python -m unittest tests.test_governed_analytics -v
```

The original synthetic fixture contains 62 records. The default scope permits east and central, covering 38 records. Average resolution time is 41.5 minutes in east and 44.5 minutes in central. Change the request to “How many cases are there by region?” to obtain 18 and 20. Request the breach rate by team in east with a minimum group size of ten to see all results withheld.

`default_input()` supplies a full editable request, scope, disclosure threshold and record set. Local language supports case volume, average resolution time or breach rate; optional region and team grouping; and one named region or all allowed regions. Unknown metrics and ambiguous questions raise a clear error.

## Principal-level engineering evidence

The model can select only a metric, grouping and region. SQL identifiers and aggregate expressions come from code-owned allowlists; region values use parameters. SQLite query-only mode and an authorizer provide additional write denial. A separate Python calculation reconciles each SQL aggregate before any answer is released.

Minimum groups are suppressed, and a second group is suppressed when exactly one small group would otherwise be hidden. Suppressed group values and all-record totals are absent from the answer. Tests include malicious model plans, arbitrary SQL text, scope violations, invalid records and threshold boundaries.

## Director-level delivery evidence

The demonstration makes self-service analytics easier to assess: one question, one metric definition, one visible scope and an evidence trail. It surfaces the boundary between convenient language access and accountable data access. It demonstrates a delivery decision to support a useful bounded vocabulary rather than promising unrestricted text-to-SQL.

## Architecture

```mermaid
flowchart LR
    A[Manager question] --> B[Local intent matcher or live planner]
    B --> C[Validate semantic plan and scope]
    C --> D[Fixed parameterized SQL]
    D --> E[Read-only SQLite]
    E --> F[Independent reconciliation]
    F --> G[Group disclosure controls]
    G --> H[Result with definition and scope]
```

The local matcher is a useful baseline. Live mode interprets word order and supported metric synonyms while preserving the same documented vocabulary and bounded execution path. Unsupported substantive words are rejected before either planner runs. No model-generated SQL is executed. In-memory SQLite gives a real relational calculation with no database service or external dependencies.

## Evaluation and limitations

The unit suite verifies exact arithmetic outcomes, changes to records and questions, region denial, duplicate record rejection, malformed planner output, complementary suppression, fully withheld results and local fallback. Scope is supplied by the demo caller and therefore **is not authenticated authorization**. A production service must derive it from identity.

Small-group suppression does not establish differential privacy or prevent repeated-query inference. The demo has no query-history budget, user identity, access logging service or production data connector. Resolution time is a synthetic per-record value; this is not a statistical claim about real operations. Every fixture is original and includes no customer, employer or personal data.

## Live AI status and production roadmap

A configured `context.generate_json` can interpret requests into the documented JSON schema; its result is independently checked against the requested metric, grouping and region; a schema-valid interpretation that changes the question is rejected. Unit tests cover the provider seam with doubles, not live vendor performance. Local mode is entirely offline. Before production, add identity-derived scopes, policy-managed metric versions, query-history protection, approved database views and monitored data freshness. Evaluate live interpretation against business-authored questions, including unsupported requests.

Choosing a constrained workflow for a structured problem is consistent with [Google Cloud’s architecture guidance](https://docs.cloud.google.com/architecture/choose-design-pattern-agentic-ai-system). This implementation claims no regulatory certification.

## Input/output and operating contract

| Input | Supported behavior |
|---|---|
| `request` | 1–2,000 characters, one supported aggregate question |
| `allowed_regions` | Nonempty unique list drawn from `east`, `central`, `west`; supplied demo scope |
| `minimum_group_size` | Integer 5–10,000; applies to all released groups |
| `records` | 1–10,000 records with unique string `id`, supported `region`, simple team identifier, finite nonnegative `resolution_minutes` and Boolean `breached` |
| Bounded plan | Metric `case_volume`, `avg_resolution_minutes` or `breach_rate`; group by region/team/none; one region or all scoped regions |

The result includes released group values, counts, unit, SQL template, bound regions, the semantic plan and suppression counts. It excludes record-level data, hidden group values and all-record totals. A suppressed answer is a normal result. Malformed input, unsupported language, rejected model plans, unauthorized regions and reconciliation failures raise `ValueError`.

Each run creates and closes an isolated in-memory database. No persistent tables or external systems are changed. Mean calculations use SQLite/Python floating-point arithmetic and reconcile within `1e-8`; results display four decimals. This is appropriate for synthetic operational durations and rates, not money or a regulated ledger. A direct database service or arbitrary-SQL agent would add unnecessary permissions and operating cost for this bounded demonstration.
