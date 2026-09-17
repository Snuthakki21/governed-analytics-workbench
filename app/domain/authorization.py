"""Planner results cannot widen scope or change the requested metric."""
from app.domain.catalog import METRICS, REGIONS
from app.domain.records import _records
from app.ai.planner import PLAN_SCHEMA, local_plan, _request_constraints
def prepare(payload, context=None):
    if not isinstance(payload, dict):
        raise ValueError("Input must be an object.")
    request = payload.get("request")
    if not isinstance(request, str) or not 1 <= len(request.strip()) <= 2000:
        raise ValueError("Provide a question of 1 to 2,000 characters.")
    scope = payload.get("allowed_regions")
    if not isinstance(scope, list) or not scope or any(r not in REGIONS for r in scope) or len(set(scope)) != len(scope):
        raise ValueError("allowed_regions must be a nonempty unique list of supported regions.")
    minimum = payload.get("minimum_group_size", 5)
    if type(minimum) is not int or not 5 <= minimum <= 10000:
        raise ValueError("Minimum group size must be an integer of at least 5.")
    requested_region = _request_constraints(request)
    if requested_region != "all" and requested_region not in scope:
        raise ValueError("The requested region is outside this demo's allowed scope.")
    expected_plan = local_plan(request)
    rows = _records(payload.get("records"))
    source = "local intent baseline"
    plan = None
    if context is not None:
        plan = context.generate_json(task="Translate the operations question into the bounded metric plan. Do not return SQL. Mark supported false for requests outside the supported metrics, filters or groupings. Do not reinterpret a disallowed region as all regions.", data={"request": request, "metrics": {k: v["label"] for k,v in METRICS.items()}, "regions": REGIONS, "groupings": ["region", "team", "none"]}, schema=PLAN_SCHEMA)
        if plan is not None:
            source = "live model interpretation, independently validated"
    if plan is None:
        plan = expected_plan
    if not isinstance(plan, dict) or set(plan) != {"metric", "group_by", "region", "supported"}:
        raise ValueError("Planner returned an invalid semantic plan.")
    if any(not isinstance(plan[field], str) for field in ("metric", "group_by", "region")):
        raise ValueError("Plan metric, grouping and region must be strings.")
    if plan["supported"] is not True or plan["metric"] not in METRICS or plan["group_by"] not in ["region", "team", "none"] or plan["region"] not in REGIONS + ["all"]:
        raise ValueError("The requested metric, grouping or filter is not supported.")
    if any(plan[field] != expected_plan[field] for field in ("metric", "group_by")):
        raise ValueError("The generated plan does not preserve the request's metric or grouping.")
    if plan["region"] != requested_region:
        raise ValueError("The generated plan does not preserve the request's explicit region scope.")
    if plan["region"] != "all" and plan["region"] not in scope:
        raise ValueError("The requested region is outside this demo's allowed scope.")
    return request, scope, minimum, rows, source, plan
