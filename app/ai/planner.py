"""Bounded language interpretation; generated SQL is never accepted."""
import re
from app.domain.catalog import METRICS, REGIONS
PLAN_SCHEMA = {"type": "object", "properties": {
    "metric": {"type": "string", "enum": list(METRICS)},
    "group_by": {"type": "string", "enum": ["region", "team", "none"]},
    "region": {"type": "string", "enum": REGIONS + ["all"]},
    "supported": {"type": "boolean"},
}, "required": ["metric", "group_by", "region", "supported"], "additionalProperties": False}
def _request_constraints(request):
    query = request.lower()
    # ponytail: reject unknown qualifiers instead of silently discarding filters.
    vocabulary = set("what is are there the a an of by in for from to and please show me give report tell get calculate how many number count counts case cases volume average avg mean resolution resolutions handling duration time minutes breach breaches rate rates late sla service level region regions team teams all each every authorized allowed scope total overall operations operational snapshot grouped grouping east central west".split())
    unknown = set(re.findall(r"[a-z0-9_]+", query)) - vocabulary
    if unknown:
        raise ValueError("Unsupported request terms or filters: " + ", ".join(sorted(unknown)) + ". Use the documented metric and region/grouping vocabulary.")
    if re.search(r"\b(last|previous|this|next)\s+(day|week|month|quarter|year)\b|\b(today|yesterday|tomorrow|since|before|after|between|during|where|excluding|except|greater|less|over|under)\b|\b20\d\d\b", query):
        raise ValueError("Time windows and additional record filters are unsupported; ask about the supplied complete snapshot.")
    for place in re.findall(r"\b(?:in|from)\s+(?:the\s+)?([a-z_]+)\b", query):
        if place not in REGIONS + ["all", "each", "every", "authorized", "scope", "minutes", "total"]:
            raise ValueError("Only east, central and west region filters are supported.")
    regions = [region for region in REGIONS if re.search(r"\b" + region + r"\b", query)]
    if len(regions) > 1:
        raise ValueError("Specify one region or ask for all authorized regions.")
    return regions[0] if regions else "all"
def local_plan(request):
    # ponytail: bounded vocabulary; use the existing live planner for broader language.
    _request_constraints(request)
    query = request.lower()
    if re.search(r"\b(drop|delete|insert|update|alter|attach|pragma|password|salary|email|individual|customer)\b|;|--", query):
        raise ValueError("Only aggregate operations questions are supported; executable commands and individual records are rejected.")
    matches = []
    if re.search(r"\b(average|avg|mean)\b", query) and re.search(r"\b(resolution|handling|duration|time)\b", query):
        matches.append("avg_resolution_minutes")
    if re.search(r"\b(breach|breaches|late|sla)\b", query):
        matches.append("breach_rate")
    if re.search(r"\b(volume|count|how many|number of)\b", query):
        matches.append("case_volume")
    if len(matches) != 1:
        raise ValueError("Ask for exactly one supported metric: case volume, average resolution time, or breach rate.")
    grouping_clauses = re.findall(r"\bby\s+((?:region|team)(?:\s+(?:and|by|each|every|the|region|team))*)\b", query)
    requested_groups = {name for clause in grouping_clauses for name in re.findall(r"\b(region|team)\b", clause)}
    if len(requested_groups) > 1:
        raise ValueError("Choose one grouping: region or team.")
    grouping = "region" if "by region" in query else "team" if "by team" in query else "none"
    # Reject unknown grouping rather than silently returning a different result.
    if re.search(r"\bby\s+(?!region\b|team\b)\w+", query):
        raise ValueError("Grouping is limited to region or team.")
    regions = [region for region in REGIONS if re.search(r"\b" + region + r"\b", query)]
    if len(regions) > 1:
        raise ValueError("Specify one region or ask for all authorized regions.")
    return {"metric": matches[0], "group_by": grouping, "region": regions[0] if regions else "all", "supported": True}
