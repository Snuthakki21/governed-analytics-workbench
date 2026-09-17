"""Independent Staff Engineer regressions; author modules are not modified here.

Classes skip only when their project is absent from a standalone export.
"""

from copy import deepcopy

from decimal import Decimal

import importlib

import unittest

def load_project(project_id):
    try:
        return importlib.import_module(f"projects.{project_id}.project")
    except ModuleNotFoundError as exc:
        if exc.name in {f"projects.{project_id}", f"projects.{project_id}.project"}:
            raise unittest.SkipTest("This standalone repository does not contain that project") from exc
        raise

class IndependentAnalyticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project = load_project("governed_analytics")

    def test_unsupported_filter_does_not_become_all_records(self):
        questions = ["How many cases are there in north?", "How many cases were there last month?", "How many cases are there for north?", "How many open cases are there?", "How many cases for team specialist?"]
        for question in questions:
            with self.subTest(question=question):
                data = self.project.default_input()
                data["request"] = question
                with self.assertRaises(ValueError):
                    self.project.run(data)

    def test_disallowed_explicit_region_is_checked_before_model(self):
        class MustNotCall:
            def generate_json(self, **kwargs):
                raise AssertionError("An explicitly disallowed region should be rejected before model invocation")
        data = self.project.default_input()
        data["request"] = "How many cases are there in west?"
        with self.assertRaises(ValueError):
            self.project.run(data, MustNotCall())

    def test_live_plan_cannot_replace_east_with_all(self):
        class WrongPlan:
            def generate_json(self, **kwargs):
                return {"metric": "case_volume", "group_by": "none", "region": "all", "supported": True}
        data = self.project.default_input()
        data["request"] = "How many cases are there in east?"
        with self.assertRaises(ValueError):
            self.project.run(data, WrongPlan())

    def test_live_plan_preserves_explicit_metric_and_grouping(self):
        class WrongPlan:
            def generate_json(self, **kwargs):
                return {"metric": "avg_resolution_minutes", "group_by": "none", "region": "all", "supported": True}
        data = self.project.default_input()
        data["request"] = "How many cases are there by region?"
        with self.assertRaises(ValueError):
            self.project.run(data, WrongPlan())

    def test_huge_duration_is_a_controlled_input_error(self):
        data = self.project.default_input()
        data["records"][0]["resolution_minutes"] = 10**400
        with self.assertRaises(ValueError):
            self.project.run(data)

    def test_released_breach_rates_match_raw_authorized_records(self):
        data = self.project.default_input()
        data["request"] = "What is the breach rate by region?"
        result = self.project.run(data)["details"]
        for group in result["results"]:
            rows = [row for row in data["records"] if row["region"] == group["group"]]
            expected = round(100 * sum(row["breached"] for row in rows) / len(rows), 4)
            self.assertEqual(group["value"], expected)
        self.assertEqual({r["group"] for r in result["results"]}, {"east", "central"})

if __name__ == "__main__":
    unittest.main()
