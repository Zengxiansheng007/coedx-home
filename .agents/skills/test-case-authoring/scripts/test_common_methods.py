"""Public projection and reassessment of shared business methods."""
import copy
import unittest

from source_preparation import assess_preparations, render_selection
from test_preparation_scope import source


class CommonMethodTests(unittest.TestCase):
    def test_fixed_operation_keeps_case_inputs_and_assertions_in_selected_review(self):
        batch = source()
        cases = batch['cases']
        first, second = cases[:2]
        definition = dict(module_path=first['module_path'], kind='operation', name='登记业务单',
                          instruction='在登记页提交本次业务单并核实实参', timing='每次提交时',
                          source='业务约定第2节', pending={}, excluded={c['id']: '只读' for c in cases[2:]},
                          applicable={c['id']: ['steps/' + c['steps'][0]['id']] for c in cases[:2]})
        candidate = assess_preparations(batch, [definition])
        self.assertEqual(candidate['cases'], batch['cases'])
        self.assertEqual(candidate['data'], batch['data'])
        tree = render_selection(candidate, [second['id']])['xmind_markdown']
        self.assertEqual(tree.count('在登记页提交本次业务单并核实实参'), 1)
        self.assertIn('- 公共操作与数据', tree)
        self.assertIn('适用用例：' + second['id'], tree)
        self.assertNotIn('登记业务单', render_selection(candidate, [cases[-1]['id']])['xmind_markdown'])
        with self.assertRaises(ValueError):
            bad = copy.deepcopy(definition)
            bad['applicable'][first['id']] = ['steps/unknown']
            assess_preparations(batch, [bad])
    def test_definition_change_selects_only_same_version_references(self):
        from source_preparation import affected_case_ids
        batch = source()
        cases = batch['cases']
        method = dict(kind='evidence', module_path=cases[0]['module_path'], name='查回执',
                      instruction='定位本次回执', timing='每例结束前', source='业务约定',
                      applicable={c['id']: ['steps/' + c['steps'][-1]['id']] for c in cases[:3]},
                      pending={cases[3]['id']: '入口待核'}, excluded={c['id']: '仅看页面' for c in cases[4:]})
        candidate = assess_preparations(batch, [method])
        self.assertEqual(affected_case_ids(candidate, method['module_path'], '查回执', candidate['content_version']),
                         [c['id'] for c in cases[:3]])
        with self.assertRaises(ValueError):
            affected_case_ids(candidate, method['module_path'], '查回执', 'old-version')
        candidate['cases'][1]['steps'][-1]['operation'] += '变更'
        tree = render_selection(candidate, [cases[0]['id'], cases[1]['id']])['xmind_markdown']
        self.assertIn('公共取证方法', tree)
        self.assertIn('适用范围待核对：查回执', tree)
        self.assertNotIn('适用用例：' + cases[0]['id'] + '、' + cases[1]['id'], tree)
