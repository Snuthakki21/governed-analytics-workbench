# Domain and AI contracts — Governed Analytics Workbench

## Inputs

| Field | Behavior |
|---|---|
| `request` | 1–2,000 characters; exactly one supported metric, region/team/none grouping, and at most one explicit region. |
| `allowed_regions` | Nonempty unique subset of east, central and west. This is a caller-selected workspace scope, not authenticated identity. |
| `minimum_group_size` | Integer from 5 to 10,000; small groups can trigger complementary suppression of another group. |
| `records` | 1–10,000 records with unique id, region, team, resolution_minutes and Boolean breached. |

## Evidence and failure semantics

Unknown query terms, unsupported time windows, mixed metrics, multiple regions, scope widening, wrong planner groupings, malformed records, modified SQL aggregates and small groups are covered by executable negative tests. Invalid input raises a controlled validation error. Optional provider errors remain errors; the runtime does not claim that a failed model call succeeded. The raw report is the source for UI, JSON export and saved execution comparison.

## Interpretation boundaries

- The current semantic catalog contains three well-defined operational metrics. It does not silently approximate unsupported questions or accept arbitrary SQL.
- Caller-selected regions demonstrate enforcement of a scope contract; they are not a substitute for identity-backed authorization in a multi-user service.
- Small-group suppression does not prevent all inference or differencing attacks across query histories. No differential-privacy guarantee is claimed.
- The built-in language regression suite evaluates the deterministic interpreter. It is not a measured accuracy benchmark for a live provider. Original records are synthetic.

## Dataset origin

Committed examples are original synthetic data. Provider output snapshots in the examples are illustrative fixtures unless an individual execution explicitly records live mode. Synthetic examples demonstrate mechanisms; they are not measured employer, customer or production outcomes.
