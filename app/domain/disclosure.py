"""Primary and complementary suppression protect small output groups."""
from dataclasses import dataclass
from app.domain.catalog import METRICS

@dataclass(frozen=True)
class DisclosurePolicy:
    minimum: int

    def release(self, raw, grouping, plan):
        minimum = self.minimum
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
        return results, suppressed, secondary
