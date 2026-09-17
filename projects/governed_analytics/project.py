"""Public entry point; product behavior lives in the app package."""
from copy import deepcopy
import json
from pathlib import Path
import sqlite3
from app.domain.catalog import METRICS, REGIONS
from app.ai.planner import PLAN_SCHEMA, _request_constraints, local_plan
from app.domain.records import _records
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

def default_input():
    return {"request": "What is the average resolution time by region?", "allowed_regions": ["east", "central"],
            "minimum_group_size": 5, "records": json.loads(Path(__file__).with_name("fixtures.json").read_text())}

from app.application.product import ProductApplication

def run(payload, context=None):
    return ProductApplication().run(payload, context)

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

_semantic = default_input()
_semantic["allowed_regions"] = ["east", "central", "west"]
_semantic["request"] = "How many cases by team in west?"
META["demo_inputs"].append({"label": "Inspect a scoped semantic plan", "payload": _semantic})
