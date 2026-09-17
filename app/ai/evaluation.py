"""Semantic-plan explanation and a deterministic interpretation regression suite."""
from dataclasses import dataclass
from app.domain.catalog import MetricCatalog
from app.ai.planner import local_plan


@dataclass(frozen=True)
class PlanContract:
    metric: str
    grouping: str
    region: str

    def matches(self, plan):
        return plan["metric"] == self.metric and plan["group_by"] == self.grouping and plan["region"] == self.region


class PlanEvaluation:
    """Never evaluates by issuing extra live calls or exposing suppressed records."""
    CASES = (
        ("How many cases are there by region?", PlanContract("case_volume", "region", "all")),
        ("Average resolution time by team in east", PlanContract("avg_resolution_minutes", "team", "east")),
        ("What is the breach rate in west?", PlanContract("breach_rate", "none", "west")),
        ("What is the average resolution time and breach rate?", None),
        ("How many cases were resolved yesterday?", None),
        ("Show customer email", None),
        ("How many cases by employee?", None),
        ("How many cases in east and west?", None),
    )

    def evaluate(self):
        rows = []
        for request, expected in self.CASES:
            try:
                plan = local_plan(request)
                actual = "accepted"
                passed = expected is not None and expected.matches(plan)
                reason = "Matched the registered semantic plan."
            except ValueError as exc:
                actual = "rejected"
                passed = expected is None
                reason = str(exc)
            rows.append({"request": request, "expected": "rejected" if expected is None else "accepted",
                         "actual": actual, "passed": passed, "explanation": reason})
        return rows

    def diagnose(self, request):
        """Return a clarification path without converting ambiguity into a query."""
        if not isinstance(request, str) or not 1 <= len(request.strip()) <= 2000:
            raise ValueError("Provide a question of 1 to 2,000 characters.")
        try:
            plan = local_plan(request)
            return {"status": "ready", "plan": plan, "clarification": None}
        except ValueError as exc:
            return {"status": "clarification_required", "plan": None, "clarification": str(exc),
                    "supported_questions": [row[0] for row in self.CASES[:3]]}

    def analyze(self, plan, selected, results, minimum, source):
        catalog = MetricCatalog()
        metric = catalog.resolve(plan["metric"])
        checks = [
            {"control": "Semantic metric exists", "passed": True, "evidence": f"{metric.identifier}@{metric.version}"},
            {"control": "Scope is explicit", "passed": bool(selected), "evidence": ", ".join(selected)},
            {"control": "Released groups satisfy threshold", "passed": all(r["records"] >= minimum for r in results), "evidence": f"Every released group has at least {minimum} records."},
            {"control": "Released values are nonnegative", "passed": all(r["value"] >= 0 for r in results), "evidence": "Evaluated after independent reconciliation and suppression."},
            {"control": "Rate is bounded", "passed": all(0 <= r["value"] <= 100 for r in results) if metric.unit == "%" else True, "evidence": "Percentage bounds enforced for rate metrics; otherwise not applicable."},
        ]
        evaluation = self.evaluate()
        return {"semantic_catalog": catalog.describe(),
                "query_explanation": {"business_measure": metric.label, "formula": metric.expression,
                    "metric_version": metric.version, "grain": metric.grain, "group_by": plan["group_by"],
                    "filters": {"region_in": selected}, "null_policy": metric.null_policy,
                    "authorization_source": "caller-selected workspace scope; not authenticated identity",
                    "query_limits": {"maximum_input_records": 10000, "minimum_released_group": minimum,
                                     "allowed_groupings": ["region", "team", "none"]},
                    "steps": ["Parse exactly one metric and grouping", "Validate plan preserves the request", "Bind selected regions as SQL parameters", "Reconcile every aggregate independently", "Apply primary and complementary suppression"]},
                "result_quality": {"passed": all(c["passed"] for c in checks), "checks": checks,
                    "released_groups": len(results), "disclosure_note": "Quality diagnostics contain only released output groups; no suppressed values, counts or global totals are added."},
                "planner_evaluation": {"passed": sum(r["passed"] for r in evaluation), "cases": len(evaluation),
                    "mode": "built-in deterministic interpretation regression; no live model benchmark", "results": evaluation},
                "clarification_workflow": {"ambiguous_requests": "Rejected before data access. Choose one metric, one grouping, and at most one explicit region.",
                    "unsupported_filters": "Time windows and per-person requests are rejected; import the desired complete snapshot first.",
                    "examples": [row[0] for row in self.CASES[:3]]}}
