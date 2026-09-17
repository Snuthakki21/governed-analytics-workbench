"""Record-level trust boundary for imported operations snapshots."""
import math
import re
from app.domain.catalog import REGIONS
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
