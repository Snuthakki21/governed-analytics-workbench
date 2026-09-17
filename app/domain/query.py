"""Read-only SQL engine with independent Python reconciliation."""
import sqlite3
from app.domain.catalog import METRICS

class VerifiedQueryEngine:
    def execute(self, rows, scope, plan):
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
        return raw, sql, selected, grouping, reconciled
