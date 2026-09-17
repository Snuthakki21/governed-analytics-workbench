"""Versioned metric definitions are the only source of SQL aggregates."""
from dataclasses import dataclass, asdict
METRICS = {
    "case_volume": {"sql": "COUNT(*)", "label": "Case volume", "unit": "cases"},
    "avg_resolution_minutes": {"sql": "AVG(resolution_minutes)", "label": "Average resolution time", "unit": "minutes"},
    "breach_rate": {"sql": "100.0 * AVG(breached)", "label": "Service-level breach rate", "unit": "%"},
}
REGIONS = ["east", "central", "west"]

@dataclass(frozen=True)
class MetricDefinition:
    identifier: str
    label: str
    unit: str
    expression: str
    grain: str = "operation"
    version: str = "1.0.0"
    null_policy: str = "reject missing inputs"
    owner: str = "Operations data steward"

class MetricCatalog:
    def __init__(self):
        self.metrics = {key: MetricDefinition(key, value["label"], value["unit"], value["sql"])
                        for key, value in METRICS.items()}

    def describe(self):
        return [asdict(metric) for metric in self.metrics.values()]

    def resolve(self, identifier):
        if identifier not in self.metrics:
            raise ValueError("Metric is not registered in the semantic catalog.")
        return self.metrics[identifier]
