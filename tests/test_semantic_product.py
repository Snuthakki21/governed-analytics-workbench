"""Semantic catalog, language ambiguity and released-output assessment."""
import unittest
from app.application.product import ProductApplication
from app.ai.evaluation import PlanContract, PlanEvaluation
from app.domain.catalog import MetricCatalog
from app.domain.query import VerifiedQueryEngine
from app.domain.disclosure import DisclosurePolicy
from projects.governed_analytics.project import default_input, run

class SemanticProductTests(unittest.TestCase):
    def test_application_uses_same_public_contract(self):
        self.assertEqual(ProductApplication().run(default_input()),run(default_input()))

    def test_catalog_resolves_versioned_metric_and_rejects_sql(self):
        catalog=MetricCatalog()
        self.assertEqual(catalog.resolve("case_volume").expression,"COUNT(*)")
        self.assertEqual(len(catalog.describe()),3)
        with self.assertRaises(ValueError):catalog.resolve("COUNT(*); DROP TABLE operations")

    def test_ambiguity_requires_clarification_without_query(self):
        result=PlanEvaluation().diagnose("What is the average resolution time and breach rate?")
        self.assertEqual(result["status"],"clarification_required")
        self.assertIsNone(result["plan"])
        self.assertIn("exactly one",result["clarification"])
        self.assertEqual(len(result["supported_questions"]),3)

    def test_coordinated_grouping_is_not_silently_dropped(self):
        for request in ['How many cases by region and team?', 'How many cases by team and region?', 'How many cases by region and by team?', 'How many cases by region and every team?']:
            with self.subTest(request=request):
                self.assertEqual(PlanEvaluation().diagnose(request)['status'],'clarification_required')
        self.assertEqual(PlanEvaluation().diagnose('How many cases by team for all authorized regions?')['status'],'ready')

    def test_supported_question_has_explicit_metric_scope(self):
        result=PlanEvaluation().diagnose("What is the breach rate by team in east?")
        self.assertEqual(result["status"],"ready")
        self.assertTrue(PlanContract("breach_rate","team","east").matches(result["plan"]))
        self.assertFalse(PlanContract("case_volume","team","east").matches(result["plan"]))

    def test_bad_diagnostic_input_rejected(self):
        for request in [None,5,""," "*8,"x"*2001]:
            with self.subTest(request=request),self.assertRaises(ValueError):PlanEvaluation().diagnose(request)

    def test_builtin_regression_cases_are_executed(self):
        result=PlanEvaluation().evaluate()
        self.assertEqual(len(result),8)
        self.assertTrue(all(row["passed"] for row in result))
        self.assertEqual(sum(row["actual"]=="rejected" for row in result),5)

    def test_quality_assessment_does_not_disclose_hidden_counts(self):
        data=default_input();data["minimum_group_size"]=10000
        result=run(data)["details"]
        self.assertEqual(result["results"],[])
        self.assertEqual(result["result_quality"]["released_groups"],0)
        self.assertNotIn("total_records",result["result_quality"])
        self.assertNotIn("suppressed_records",result["result_quality"])
        self.assertTrue(result["result_quality"]["passed"])

    def test_explanation_matches_bound_query(self):
        data=default_input();data["request"]="How many cases by team in east?"
        result=run(data)["details"];explanation=result["query_explanation"]
        self.assertEqual(explanation["filters"]["region_in"],result["bound_regions"])
        self.assertEqual(explanation["group_by"],result["plan"]["group_by"])
        self.assertEqual(explanation["formula"],"COUNT(*)")
        self.assertEqual(len(explanation["steps"]),5)

    def test_complementary_suppression_policy_releases_neither_group(self):
        rows=[("east",2,10.0),("central",8,20.0)]
        released,suppressed,secondary=DisclosurePolicy(5).release(rows,"region",{"metric":"avg_resolution_minutes"})
        self.assertEqual(released,[])
        self.assertEqual(suppressed,{"east","central"})
        self.assertEqual(secondary,["central"])

    def test_rate_quality_control_flags_invalid_external_result(self):
        plan={"metric":"breach_rate","group_by":"region","region":"all","supported":True}
        result=PlanEvaluation().analyze(plan,["east"],[{"records":5,"value":101}],5,"local")
        self.assertFalse(result["result_quality"]["passed"])

if __name__=="__main__":unittest.main()
