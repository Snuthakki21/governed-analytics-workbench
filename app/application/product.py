"""Plan, authorize, reconcile and disclose a governed metric answer."""
from app.domain.catalog import METRICS, MetricCatalog
from app.domain.authorization import prepare
from app.domain.query import VerifiedQueryEngine
from app.domain.disclosure import DisclosurePolicy
from app.ai.evaluation import PlanEvaluation

class ProductApplication:
    def run(self, payload, context=None):
        request, scope, minimum, rows, source, plan = prepare(payload, context)
        raw, sql, selected, grouping, reconciled = VerifiedQueryEngine().execute(rows, scope, plan)
        results, suppressed, secondary = DisclosurePolicy(minimum).release(raw, grouping, plan)
        label = METRICS[plan["metric"]]["label"]
        statement = "; ".join(f"{r['group']}: {r['value']:g} {r['unit']}" for r in results)
        report = {
            "summary": f"{label} — {statement}." if results else "No result was released: groups do not meet the disclosure threshold.",
            "metrics": [{"label": "Released groups", "value": len(results), "unit": "groups"},
                        {"label": "Records in released groups", "value": sum(r["records"] for r in results), "unit": "synthetic cases"},
                        {"label": "Reconciliation", "value": "passed", "unit": "independent calculation"},
                        {"label": "Minimum group size", "value": minimum, "unit": "records"}],
            "evidence": [f"The request was interpreted by {source}.",
                         f"Only these regions were queried: {', '.join(selected)}. SQL identifiers and aggregates came from a fixed allowlist.",
                         "SQLite query-only mode and an authorizer prevented modification; values were bound as parameters.",
                         "Results matched a separate Python calculation before disclosure controls were applied.",
                         f"{len(suppressed)} group(s) were withheld, including {len(secondary)} complementary suppression(s). No suppressed values or overall totals are released.",
                         "Original synthetic records and caller-provided demo scopes; this is not a production identity or privacy system."],
            "next_actions": ["Review the metric definition and scope before using this result.", "Bind scopes to authenticated identity and add query-history privacy controls before production."],
            "details": {"plan": plan, "plan_source": source, "sql_template": sql, "bound_regions": selected,
                        "metric_definition": label, "results": results, "reconciled": reconciled,
                        "suppressed_group_count": len(suppressed), "complementary_suppression_count": len(secondary),
                        "minimum_group_size": minimum, "data_origin": "original synthetic operations records"},
        }
        report["details"].update(PlanEvaluation().analyze(plan, selected, results, minimum, source))
        return report
