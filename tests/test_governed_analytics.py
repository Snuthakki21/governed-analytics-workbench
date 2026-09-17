import unittest
from copy import deepcopy
from projects.governed_analytics.project import META,default_input,run

class AnalyticsTests(unittest.TestCase):
    def test_expected_scoped_average_and_reconciliation(self):
        d=run(default_input())["details"]
        self.assertEqual({r["group"]:r["value"] for r in d["results"]},{"east":41.5,"central":44.5})
        self.assertTrue(d["reconciled"])
        self.assertEqual(d["bound_regions"],["east","central"])

    def test_changed_metric_changes_result(self):
        d=run(META["demo_inputs"][1]["payload"])["details"]
        self.assertEqual({r["group"]:r["value"] for r in d["results"]},{"east":18,"central":20})

    def test_changed_records_change_average(self):
        p=default_input();p["records"][0]["resolution_minutes"]+=18
        east=next(r for r in run(p)["details"]["results"] if r["group"]=="east")
        self.assertEqual(east["value"],42.5)

    def test_out_of_scope_region_rejected(self):
        p=default_input();p["request"]="What is case volume in west?"
        with self.assertRaisesRegex(ValueError,"scope"):run(p)

    def test_small_groups_and_complement_are_suppressed(self):
        p=default_input();p["request"]="What is case volume by team in east?"
        d=run(p)["details"]
        self.assertEqual(d["suppressed_group_count"],2)
        self.assertEqual(d["complementary_suppression_count"],1)
        self.assertEqual(len(d["results"]),1)
        self.assertNotIn("specialist",str(d["results"]))

    def test_all_small_groups_release_nothing(self):
        d=run(META["demo_inputs"][2]["payload"])["details"]
        self.assertEqual(d["results"],[])

    def test_exact_group_boundary_releases(self):
        p=default_input();p["minimum_group_size"]=18
        self.assertEqual(len(run(p)["details"]["results"]),2)
        p["minimum_group_size"]=19
        self.assertEqual(run(p)["details"]["results"],[])

    def test_unrecognized_ambiguous_or_sql_request_rejected(self):
        for text in ["DROP TABLE operations;", "What is salary by customer?", "What is case volume by month?", "What is case volume and breach rate?", "Tell me something", "Count cases in team", "Count cases;", "Count cases by resolution"]:
            with self.subTest(text=text):
                p=default_input();p["request"]=text
                with self.assertRaises(ValueError):run(p)

    def test_invalid_rows_and_disclosure_size_rejected(self):
        for mutation in [lambda p:p.update(minimum_group_size=4),lambda p:p["records"][0].update(resolution_minutes=float("nan")),lambda p:p["records"].append(deepcopy(p["records"][0])),lambda p:p.update(allowed_regions=[]),lambda p:p["records"][0].update(breached="false")]:
            with self.subTest(mutation=mutation):
                p=default_input();mutation(p)
                with self.assertRaises(ValueError):run(p)

    def test_live_plan_is_bounded_and_validated(self):
        class Context:
            def generate_json(self,**kw):return {"metric":"breach_rate","group_by":"region","region":"east","supported":True}
        p=default_input();p["request"]="What is the breach rate by region in east?"
        d=run(p,Context())["details"]
        self.assertEqual(d["plan"]["metric"],"breach_rate")
        self.assertEqual(d["bound_regions"],["east"])
        self.assertIn("live model",d["plan_source"])

    def test_malicious_live_plans_rejected(self):
        for plan in [{"metric":"COUNT(*); DROP TABLE operations","group_by":"region","region":"east","supported":True},{"metric":"case_volume","group_by":"region","region":"west","supported":True},{"metric":[],"group_by":"region","region":"east","supported":True},{"metric":"case_volume","group_by":"region","region":"east","supported":True,"sql":"DROP"}]:
            class Context:
                def generate_json(self,**kw):return plan
            with self.subTest(plan=plan),self.assertRaises(ValueError):run(default_input(),Context())

    def test_none_planner_uses_local_intent_and_preserves_input(self):
        class Context:
            def generate_json(self,**kw):return None
        p=default_input();original=deepcopy(p)
        self.assertEqual(run(p,Context())["details"]["plan_source"],"local intent baseline")
        self.assertEqual(p,original)

    def test_no_authorized_rows_releases_nothing(self):
        p=default_input();p["records"]=[r for r in p["records"] if r["region"]=="west"]
        self.assertEqual(run(p)["details"]["results"],[])

    def test_additional_boundary_and_grouping_cases(self):
        mutations=[lambda p:p.update(request=""),lambda p:p.update(records=[]),lambda p:p["records"][0].update(team="bad;name"),lambda p:p.update(request="Count cases by region and by team"),lambda p:p.update(request="Count cases in east and west")]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                p=default_input();mutation(p)
                with self.assertRaises(ValueError):run(p)
        with self.assertRaises(ValueError):run(None)
        p=default_input();p["request"]="What is the average resolution time?"
        self.assertEqual(len(run(p)["details"]["results"]),1)
        p["records"]=p["records"][:1];p["request"]="What is case volume by team?"
        self.assertEqual(run(p)["details"]["results"],[])
        self.assertEqual(run(p)["details"]["complementary_suppression_count"],0)

    def test_corrupt_query_result_fails_closed(self):
        from unittest.mock import patch
        import sqlite3
        real=sqlite3.connect(":memory:")
        class WrongCursor:
            def fetchall(self):return [("east",18,9999.0),("central",20,44.5)]
        class Connection:
            def execute(self,sql,*args):return WrongCursor() if sql.startswith("SELECT") else real.execute(sql,*args)
            def executemany(self,*args):return real.executemany(*args)
            def commit(self):return real.commit()
            def set_authorizer(self,*args):return real.set_authorizer(*args)
            def close(self):return real.close()
        with patch("projects.governed_analytics.project.sqlite3.connect",return_value=Connection()):
            with self.assertRaisesRegex(ValueError,"reconciliation"):run(default_input())
