# Independent automated Staff Engineer review — expanded application

Review date: 2026-09-17. A separate automated reviewer, independent of the product author, examined the current expanded source. This is an automated engineering review, not an external human audit or production certification.

## Scope and method

Read the current product diff, product requirements, actual domain/application/AI services, compatibility adapter, product UI template and author tests. Independently designed adverse-input tests in `tests/test_product_review.py` and rendering tests in `tests/product-review-ui.test.mjs`. The product author corrected implementation findings; the reviewer retested those changes.

This domain review excludes an independent audit of shared persistence/HTTP code, distribution packaging, hosted CI and live-browser visual quality. The whole existing Python suite was executed for regression evidence; that execution does not expand the source-review scope. Live provider accuracy and real financial outcomes were not measured.

## Verdict

**Pass for the documented product scope after independent verification. No unresolved implementation finding was reproduced in this review.** The verdict applies to the attached source snapshot and executed checks. It does not assert a defect-free or production-certified system.

## Requirements and architecture assessment

R-01 through R-06: constrained model plans; versioned metric definitions; scope-preserving access; independent reconciliation; disclosure controls; executable planner evaluation and safe clarification.

MetricDefinition and MetricCatalog define the semantic contract. Authorization validates the interpreted request before any optional model call; VerifiedQueryEngine owns allowlisted SQL and a separate recomputation. DisclosurePolicy applies primary/complementary suppression, and PlanEvaluation adds executable language-regression and result-quality evidence. ProductApplication composes these policies without granting model-generated SQL authority.

New results are calculated by the domain services, rendered in the product-specific template and included in full downloadable reports. Independent UI checks confirm all published scenarios render without undefined or NaN values, preserve result evidence and escape hostile labels. Common workspace actions are assessed separately.

## Findings and resolution

### GA-1 — P2: Coordinated groupings silently lost part of the request.

Reproduction: "How many cases by region and team?" returned only region, and the reversed phrase returned only team. Both were accepted as supported even though the contract permits only one grouping.

Resolution and retest: The parser detects coordinated grouping names and rejects the ambiguity before calling a model. Independent tests cover both orders, validation order, malicious generated grouping replacement, region scope and complementary suppression.

Status: closed by an author implementation change and independent regression verification.

## Executed verification

- Full Python suite: 138 tests, zero failures, 2 explicit skips.
- Independent domain regressions: 5 passed as part of that run.
- Static build: the standalone product and all declared examples built successfully.
- Frontend and independent product UI tests: 34 total, 28 passed, 6 explicit absent-project skips, zero failures. Three checks specifically exercise the expanded UI.

```sh
python3 -m unittest discover -s tests
python3 -m portfolio build --output dist
node --test --test-timeout=20000 tests/frontend.test.mjs tests/product-review-ui.test.mjs
```

## Source snapshot

[Machine-readable SHA-256 snapshot](STAFF_REVIEW_V2_SOURCE.json) identifies every reviewed domain module, compatibility adapter, template, independent test and current requirement document. Future material edits require renewed review of changed behavior.

| File | SHA-256 |
|---|---|
| `app/ai/__init__.py` | `3b3a14d073c138b40d988b4b8190df8e8a9260df4a601bc5f4a01bc3e5eed029` |
| `app/ai/evaluation.py` | `a171cd21374eff255f1a7d9b251bcdb4ef668e519daab4e5c806da117c11b22a` |
| `app/ai/planner.py` | `6b5698332cfd57e2440b432714f075f4f8a7eca4979c7d737315e49d23458182` |
| `app/application/__init__.py` | `4ca85bbc1f8ce81b55960e4222fee1429279e38bef72bf3070d2b1ee65bf17d7` |
| `app/application/product.py` | `e0acfd80a8924cac541f200b8c62b533a36eee7ae9545c5455f032c943dd0621` |
| `app/domain/__init__.py` | `2a0b1d756023f313f1d4280a19ba351434ebdbaafc2a3a6e3cde02992dcfe982` |
| `app/domain/authorization.py` | `84acf3608d01684233f5456a380d1851e65e4d65260b0a8f5f364b426b2dabbc` |
| `app/domain/catalog.py` | `56bb753f42bfa11bf0781bff229ed1903df63f9450901f9160232626afca1d1a` |
| `app/domain/disclosure.py` | `f249d01dced664bfe5dbeea45d7fb1a7af30355ee6fb63f09a45ef15a77b985d` |
| `app/domain/query.py` | `18a0ec2a1af0377371024643b085daef603108aea046abe93924bdecc7bfb5e4` |
| `app/domain/records.py` | `aceebb74ed18f4c6bc3c4772172e5cb4cdf3559d8ae232522687363dc8a93e10` |
| `docs/PRODUCT.md` | `83c4eb73028d71f6641e9cb507c8390e4151eaeecd454cbf1b7abee4aebb6106` |
| `docs/REQUIREMENTS.md` | `f404788f3883d320e4c32fe6aea1c2b744da001ed4e824ec03b1ee14f87acc13` |
| `projects/governed_analytics/project.py` | `82bbb529e84f5255cfe2b10d4b33b8eb259b36d5004fa1335a5ef789aec171f7` |
| `tests/product-review-ui.test.mjs` | `d6949802163b9b56e718118d544c8a9b211150b348d0d5769ac9fb5ffe9a73ce` |
| `tests/test_product_review.py` | `843d9f3ad37da20e5f85cdd24f6ddaeba7db26991faf40bac1ccc21d5ac0fbb1` |
| `web/templates/governed_analytics.js` | `e0129e3eb5aab5b1760ee084aa3fa1a3c30ca1acb164cde2612f3bc78caf7e20` |
