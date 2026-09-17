# Product requirements and verification map — Governed Analytics Workbench

| Requirement | Implementation | Verification |
|---|---|
| R-01: AI tool architecture | Optional model-generated semantic plan; generated SQL is never accepted and the plan must preserve the deterministic request interpretation. | Domain suites listed below; inspect current CI evidence. |
| R-02: Semantic governance | Versioned MetricDefinition entities and a MetricCatalog define expressions, units, ownership, grain and null policy. | Domain suites listed below; inspect current CI evidence. |
| R-03: Data access controls | Explicit region scope, fixed identifiers and parameter-bound values prevent the planner from widening the query. | Domain suites listed below; inspect current CI evidence. |
| R-04: Independent reconciliation | Every SQL aggregate is recomputed from authorized records before release. | Domain suites listed below; inspect current CI evidence. |
| R-05: Disclosure controls | Primary and complementary suppression withhold undersized groups and avoid publishing revealing totals. | Domain suites listed below; inspect current CI evidence. |
| R-06: Planner evaluation | Executable positive, ambiguity, temporal-filter, individual-data and unsupported-grouping regression cases. | Domain suites listed below; inspect current CI evidence. |

## Executable suites

- `tests/test_governed_analytics.py`
- `tests/test_semantic_product.py`
- `tests/test_operations_independent.py`

## Acceptance checks

- Default and alternate scenarios execute through the public adapter and ProductApplication.
- Invalid inputs are rejected before optional provider execution.
- New domain results are rendered in the product interface and exported completely.
- Saved scenario/run workflows use the common platform and preserve input revisions.
- Current CI tests, static build and browser execution succeed for this repository.
- A separate automated reviewer examines expanded source and records findings with validation evidence.



The product README defines user workflows and input boundaries. Architecture and domain contract documents specify calculations and assumptions; this acceptance map links those requirements to executable verification.
