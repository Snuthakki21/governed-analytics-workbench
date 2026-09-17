# Independent Staff Engineer review

Reviewed on 2026-09-17.

Reviewer: independent automated agent operating in a Staff Engineer review role. The reviewer did not author or change this project's implementation. Author fixes were requested with concrete reproductions and independently rechecked. This is not a human sign-off or a claim that all possible failures were tested.

Scope: project requirements in CONTRIBUTING.md, this project's README, project.py, original fixture data, its author unit suite and the independent regressions. Shared provider/network handling, browser UI, deployment configuration and real production data are outside this review.

## Findings and resolution

**GOV-01 · P2 · Resolved — Unsupported qualifiers and model plan changes could produce an answer to a different question.** Requests for cases `in north`, `last month`, `for north`, `open cases` and `for team specialist` originally returned all 38 authorized records. A schema-valid model plan could replace an explicit region with `all`, or answer a case-count-by-region question using a single average-duration result. Safe SQL execution did not make those interpretations correct.

The author now applies a documented bounded vocabulary and deterministic intent parse before model calls, rejects unsupported qualifiers, checks explicit region scope before invoking a model, and requires generated metric/grouping/region to match the requested plan. Independent tests exercise all five qualifiers, disallowed west, east-to-all rewriting and count-to-average/grouping rewriting.

**GOV-02 · P2 · Resolved — A huge JSON integer escaped the input-error contract.** Setting a duration to `10**400` originally raised `OverflowError` while converting it inside `math.isfinite`. The author now checks the supported numeric range before conversion; the independent test observes `ValueError`.

## Domain and security checks

The independent suite recalculates released breach rates directly from the authorized fixture records and verifies that only east and central are returned. The author suite covers independent reconciliation failure, complementary suppression, fully withheld groups, invalid SQL-like plans and record errors. Source review confirmed that aggregate/identifier expressions are code-owned, region values are parameterized and the in-memory database is closed after use.

## Verdict and remaining limits

**PASS for the reviewed bounded analytics contract at the source hash below.** The reproduced intent and numeric-boundary defects are fixed. Local and live interpretation now share a deliberately limited vocabulary; live generation proposes an independently checked plan. Caller-provided regions are not authenticated identity. Suppression is not differential privacy and does not address repeated-query inference. Browser rendering and transport controls remain separate review scope.

## Reproducible verification

```sh
python -m unittest discover -s tests -p 'test_governed_analytics.py' -v
python -m unittest discover -s tests -p 'test_operations_independent.py' -v
```

The final local run passed 15 author tests for this project and 6 independent project-specific tests. The complete independent file passed all 18 tests across four review scopes. When copied to a single-project repository, tests for absent projects are explicitly skipped, not counted as that project's validation.

Final reviewed `project.py` SHA-256: `06c758cdb068871df88be8b101e83aa0f99537a99cab66af0f8b90f760c79ae4`.

Independent regression file SHA-256: `28392166c7fc198d671c9cb78fc143810e23600e76d0b3b0cbf9e94e911fa7ca`.

The verdict applies to the identified source. Any later implementation change requires rechecking the affected behavior. No live paid call, production write, external account action or destructive security payload was performed during this review.
