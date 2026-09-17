"""Independent Staff review: ambiguous grouping, scope and disclosure invariants."""
import unittest
from app.ai.planner import local_plan
from projects.governed_analytics.project import default_input, run

class IndependentProductReview(unittest.TestCase):
    def test_compound_groupings_require_clarification(self):
        for question in ('How many cases by region and team?', 'How many cases by team and region?'):
            with self.subTest(question=question), self.assertRaises(ValueError):local_plan(question)

    def test_ambiguous_grouping_is_rejected_before_model_use(self):
        class Context:
            def generate_json(self,**kwargs):raise AssertionError('provider called')
        p=default_input();p['request']='How many cases by region and team?'
        with self.assertRaises(ValueError):run(p,Context())

    def test_generated_grouping_cannot_replace_requested_grouping(self):
        class Context:
            def generate_json(self,**kwargs):return dict(metric='case_volume',group_by='team',region='all',supported=True)
        p=default_input();p['request']='How many cases by region?'
        with self.assertRaisesRegex(ValueError,'metric or grouping'):run(p,Context())

    def test_scope_narrowing_reconciles_only_authorized_rows(self):
        p=default_input();p.update(request='How many cases?',allowed_regions=['east'])
        d=run(p)['details']; expected=sum(row['region']=='east' for row in p['records'])
        self.assertEqual(d['bound_regions'],['east'])
        self.assertEqual(d['results'][0]['value'],expected)
        self.assertTrue(d['reconciled'])

    def test_one_primary_suppression_does_not_leave_reconstructable_total(self):
        p=default_input();p.update(request='How many cases by region?',allowed_regions=['east','west','central'])
        template=p['records'][0];p['records']=[dict(template,id=f'{region}-{i}',region=region) for region,count in [('east',2),('west',6),('central',8)] for i in range(count)]
        d=run(p)['details']
        self.assertEqual(d['suppressed_group_count'],2)
        self.assertEqual(d['complementary_suppression_count'],1)
        self.assertEqual(len(d['results']),1)
        self.assertNotIn('raw_results',d)
