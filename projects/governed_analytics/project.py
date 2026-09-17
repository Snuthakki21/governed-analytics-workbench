"""Bounded natural-language analytics over original synthetic operations data."""
from __future__ import annotations
from copy import deepcopy
import json
from pathlib import Path
import re
import sqlite3
import math

METRICS = {
    "case_volume": {"sql": "COUNT(*)", "label": "Case volume", "unit": "cases"},
    "avg_resolution_minutes": {"sql": "AVG(resolution_minutes)", "label": "Average resolution time", "unit": "minutes"},
    "breach_rate": {"sql": "100.0 * AVG(breached)", "label": "Service-level breach rate", "unit": "%"},
}
REGIONS = ["east", "central", "west"]
META = {
    "id": "governed_analytics", "title": "Governed Operations Analytics", "order": 8,
    "flagship": False, "category": "Data & decisions", "buyer": "Operations and data leaders",
    "question": "Can a manager ask a data question and trust the answer?",
    "promise": "Answer supported operations questions with scoped, reconciled metrics.",
    "description": "Translate a natural-language request into an allowlisted semantic plan, execute read-only SQL and suppress undersized groups.",
    "principal": "Separate probabilistic interpretation from authorized query planning, metric definitions and deterministic reconciliation.",
    "director": "Give managers consistent metrics while making data access boundaries and unsupported questions explicit.",
    "patterns": ["Semantic metrics", "Bounded LLM planning", "Read-only tools", "Data reconciliation"],
    "architecture": ["Operations question", "Local intent matcher or live bounded planner", "Allowlist and scope validation", "Parameterized read-only SQLite", "Group suppression and reconciliation", "Manager-ready answer"],
    "risks": ["Demo scopes are caller-provided, not identity-backed authorization.", "Small-group suppression alone does not prevent all inference attacks."],
    "limits": ["Only three metrics and three regions are supported.", "Local interpretation supports a documented vocabulary, not general natural language.", "All records are original synthetic data; no employer or customer records are included."],
}
PLAN_SCHEMA = {"type": "object", "properties": {
    "metric": {"type": "string", "enum": list(METRICS)},
    "group_by": {"type": "string", "enum": ["region", "team", "none"]},
    "region": {"type": "string", "enum": REGIONS + ["all"]},
    "supported": {"type": "boolean"},
}, "required": ["metric", "group_by", "region", "supported"], "additionalProperties": False}

def default_input():
    return {"request": "What is the average resolution time by region?", "allowed_regions": ["east", "central"],
            "minimum_group_size": 5, "records": json.loads(Path(__file__).with_name("fixtures.json").read_text())}

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
    if "by region" in query and "by team" in query:
        raise ValueError("Choose one grouping: region or team.")
    grouping = "region" if "by region" in query else "team" if "by team" in query else "none"
    # Reject unknown grouping rather than silently returning a different result.
    if re.search(r"\bby\s+(?!region\b|team\b)\w+", query):
        raise ValueError("Grouping is limited to region or team.")
    regions = [region for region in REGIONS if re.search(r"\b" + region + r"\b", query)]
    if len(regions) > 1:
        raise ValueError("Specify one region or ask for all authorized regions.")
    return {"metric": matches[0], "group_by": grouping, "region": regions[0] if regions else "all", "supported": True}

def _records(records):
    if not isinstance(records, list) or not 1 <= len(records) <= 10000:
        raise ValueError("Provide 1 to 10,000 synthetic operation records.")
    ids = set()
    result = []
    for row in records:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str) or row["id"] in ids:
            raise ValueError("Each record needs a unique string id.")
        ids.add(row["id"])
        if row.get("region") not in REGIONS or not isinstance(row.get("team"), str) or not re.fullmatch(r"[a-z][a-z_]{0,39}", row["team"]):
            raise ValueError("Record region or team is invalid.")
        minutes = row.get("resolution_minutes")
        if isinstance(minutes, bool) or not isinstance(minutes, (int, float)) or not 0 <= minutes <= 100000 or not math.isfinite(minutes):
            raise ValueError("Resolution minutes must be a finite nonnegative number.")
        if type(row.get("breached")) is not bool:
            raise ValueError("breached must be a Boolean.")
        result.append((row["id"], row["region"], row["team"], float(minutes), int(row["breached"])))
    return result

def run(payload, context=None):
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
    selected = scope if plan["region"] == "all" else [plan["region"]]
    placeholders = ",".join("?" for _ in selected)
    grouping = plan["group_by"]
    label_sql = "'all authorized records'" if grouping == "none" else grouping
    aggregate = METRICS[plan["metric"]]["sql"]
    sql = f"SELECT {label_sql} AS group_name, COUNT(*) AS n, {aggregate} AS metric_value FROM operations WHERE region IN ({placeholders})"
    if grouping != "none":
        sql += f" GROUP BY {grouping}"
    sql += " ORDER BY group_name"
    connection = sqlite3.connect(":memory:")
    try:
        connection.execute("CREATE TABLE operations (id TEXT PRIMARY KEY, region TEXT, team TEXT, resolution_minutes REAL, breached INTEGER)")
        connection.executemany("INSERT INTO operations VALUES (?, ?, ?, ?, ?)", rows)
        connection.commit()
        connection.execute("PRAGMA query_only = ON")
        allowed_actions = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION}
        connection.set_authorizer(lambda action, *_: sqlite3.SQLITE_OK if action in allowed_actions else sqlite3.SQLITE_DENY)
        raw = connection.execute(sql, selected).fetchall()
    finally:
        connection.close()
    authorized = [row for row in rows if row[1] in selected]
    expected = {}
    for row in authorized:
        group = row[1] if grouping == "region" else row[2] if grouping == "team" else "all authorized records"
        expected.setdefault(group, []).append(row)
    reconciled = True
    for group, n, value in raw:
        data = expected.get(group, [])
        expected_value = len(data) if plan["metric"] == "case_volume" else (sum(r[3] for r in data) / len(data) if plan["metric"] == "avg_resolution_minutes" and data else sum(r[4] for r in data) * 100 / len(data) if data else None)
        reconciled &= len(data) == n and ((value is None and expected_value is None) or (value is not None and expected_value is not None and abs(value - expected_value) < 1e-8))
    reconciled &= sum(n for _, n, _ in raw) == len(authorized)
    if not reconciled:
        raise ValueError("Query result failed independent reconciliation; no answer was released.")
    suppressed = {group for group, n, _ in raw if n < minimum}
    # If only one small group is hidden, also hide the smallest other group.
    # We never publish unfiltered totals that could reveal suppressed groups.
    secondary = []
    if len(suppressed) == 1 and grouping != "none":
        releasable = [(n, group) for group, n, _ in raw if group not in suppressed]
        if releasable:
            secondary = [min(releasable)[1]]
            suppressed.update(secondary)
    results = [{"group": group, "records": n, "value": round(value, 4), "unit": METRICS[plan["metric"]]["unit"]} for group, n, value in raw if group not in suppressed and n >= minimum]
    label = METRICS[plan["metric"]]["label"]
    statement = "; ".join(f"{r['group']}: {r['value']:g} {r['unit']}" for r in results)
    return {
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

def _demos():
    average = default_input()
    volume = deepcopy(average)
    volume["request"] = "How many cases are there by region?"
    privacy = deepcopy(average)
    privacy["request"] = "What is the breach rate by team in east?"
    privacy["minimum_group_size"] = 10
    return [{"label": "Average resolution by authorized region", "payload": average},
            {"label": "Change the business metric", "payload": volume},
            {"label": "Withhold undersized teams", "payload": privacy}]

META["demo_inputs"] = _demos()
