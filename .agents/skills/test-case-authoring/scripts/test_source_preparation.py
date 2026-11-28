"""Source-backed module preparation is selected from the complete authored batch."""
import unittest

from scoped_review import build_scoped_review
from test_preparation_scope import source
from source_preparation import assess_preparations, render_selection


class SourcePreparationTests(unittest.TestCase):
    def test_confirmed_input_is_enough_for_draft_without_creating_approval(self):
        full = source()
        cases = full['cases']
        definition = dict(name='订单准备', timing='每例开始前', instruction='检查订单', source='需求 §2',
                          module_path=cases[0]['module_path'],
                          applicable={c['id']: [c['common_preconditions'][0]['id']] for c in cases[:3]},
                          pending={c['id']: '旧准备未对应本例步骤' for c in cases[3:7]},
                          excluded={cases[7]['id']: '仅浏览'})
        candidate = assess_preparations(full, [definition])
        selection = [dict(case_id=c['id'], action='related', reason='选择') for c in (cases[1], cases[5])]
        selected = build_scoped_review(candidate, '节选', selection)['xmind_markdown']
        self.assertEqual(selected.count('检查订单'), 1)
        self.assertIn('适用范围待核对', selected)
        self.assertIn('准备模拟订单', selected)
        self.assertNotIn('模拟用例0', selected)
        self.assertNotIn('检查订单', render_selection(candidate, [cases[7]['id']])['xmind_markdown'])
        self.assertEqual(candidate['cases'], full['cases'])
        self.assertEqual(render_selection(candidate)['xmind_markdown'].count('检查订单'), 1)
