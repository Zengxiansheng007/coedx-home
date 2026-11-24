"""SIMULATED public preparation review behavior; no preparation execution."""
import copy
import unittest
from scoped_review import build_scoped_review
from authoring import render_batch
from test_scoped_review import catalog


def source():
    full = catalog()
    template = copy.deepcopy(full['cases'][0])
    full['cases'] = []
    for index in range(8):
        case = copy.deepcopy(template)
        case['id'] = 'SIM-' + str(index)
        case['title'] = '模拟用例' + str(index)
        case['business_group'] = {'path': ['既有订单审批'], 'source': 'SIMULATED existing requirement section'}
        case['common_preconditions'] = [dict(copy.deepcopy(case['steps'][1]), operation='准备模拟订单')]
        full['cases'].append(case)
    full['cases'][-1]['common_preconditions'] = []
    full['cases'][-1]['common_preconditions_note'] = {'text': '明确无需准备'}
    return full


def show(full):
    return build_scoped_review(full, 'SIMULATED-preparation', [
        {'case_id': c['id'], 'action': 'related', 'reason': 'SIMULATED review'} for c in full['cases']])


class PreparationScopeTests(unittest.TestCase):
    def test_equivalent_preparation_without_review_stays_inside_cases(self):
        shown = show(source())
        self.assertEqual(shown['xmind_markdown'].count('步骤 1：准备模拟订单'), 7)
        self.assertNotIn('适用：公共前置操作', shown['xmind_markdown'])


def approved(full=None):
    from preparation_scope import review_preparation_scope
    full = full or source()
    return review_preparation_scope(full, applicable_case_ids=[c['id'] for c in full['cases'][:-1]],
        exception_case_ids=[full['cases'][-1]['id']], coverage='vast_majority_few_exceptions',
        basis='SIMULATED: existing business group; all approval scenarios except viewing history require preparation',
        actual_reply='SIMULATED reviewer: assessed scope and sole exception approved', version='模拟范围v1',
        frequency='长期数据先验有效；当日数据到期重建；独占数据每例准备')


class ReviewedScopeTests(unittest.TestCase):
    def test_reviewed_scope_survives_selection_and_serialized_resume(self):
        import json
        full = approved()
        before = copy.deepcopy(full)
        result = show(full)
        tree = result['xmind_markdown']
        self.assertEqual(tree.count('步骤 1：准备模拟订单'), 1)
        for text in ('范围版本：模拟范围v1', '例外用例：模拟用例7', '既有订单审批', '独占数据每例准备'):
            self.assertIn(text, tree)
        self.assertEqual(render_batch(json.loads(json.dumps(result['batch'])))['xmind_markdown'], tree)
        self.assertEqual(before, full)

    def test_partial_selection_and_structural_deletion_do_not_remove_obligations(self):
        from feedback import prepare_feedback
        full = approved()
        partial = build_scoped_review(full, 'SIMULATED-partial', [
            {'case_id': 'SIM-0', 'action': 'related', 'reason': 'SIMULATED selected case'}])
        self.assertIn('步骤 1：准备模拟订单', partial['xmind_markdown'])
        self.assertNotIn('适用：公共前置操作', partial['xmind_markdown'])
        result = show(full)
        changed = result['xmind_markdown'].replace('准备模拟订单', '')
        with self.assertRaises(ValueError):  # Removal needs explicit dependency and impact review in chat.
            prepare_feedback(result['batch'], 'markdown', markdown=changed, actual_reply='SIMULATED delete proposed')
        self.assertEqual(result['batch']['cases'][0]['common_preconditions'][0]['operation'], '准备模拟订单')

    def test_new_move_delete_and_semantic_change_never_inherit_old_scope(self):
        for change in ('new', 'move', 'delete', 'preparation', 'exception'):
            full = approved()
            if change == 'new':
                new = copy.deepcopy(full['cases'][0])
                new['id'] = 'NEW'
                full['cases'].append(new)
            elif change == 'move':
                full['cases'][0]['business_group']['path'] = ['其他真实业务分组']
            elif change == 'delete':
                full['cases'].pop()
            elif change == 'exception':
                full['cases'][-1]['common_preconditions_note']['text'] = '需要重新核对'
            else:
                full['cases'][0]['common_preconditions'][0]['operation'] = '修改准备操作'
            self.assertNotIn('适用：公共前置操作', show(full)['xmind_markdown'], change)

    def test_only_some_and_artificial_subset_are_rejected(self):
        from preparation_scope import review_preparation_scope
        full = source()
        for coverage, exceptions in [('some_only', ['SIM-7']), ('vast_majority_few_exceptions', [])]:
            with self.assertRaises(ValueError):
                review_preparation_scope(full, applicable_case_ids=['SIM-0'], exception_case_ids=exceptions,
                    coverage=coverage, basis='SIMULATED', actual_reply='SIMULATED', version='v1', frequency='每例')

    def test_data_lifecycles_remain_complete_and_drift_invalidates_scope(self):
        for policy in ('long_term', 'time_limited', 'exclusive'):
            full = source()
            data = full['data'][0]
            data.update(reuse_policy=policy, validity='模拟有效条件', invalidation_action='失效重新准备')
            for case in full['cases'][:-1]:
                case['common_preconditions'][0]['data_refs'] = [data['id']]
            full = approved(full)
            tree = show(full)['xmind_markdown']
            for text in (policy, '模拟有效条件', '失效重新准备'):
                self.assertIn(text, tree)
            full['data'][0]['validity'] = '新有效条件'
            self.assertNotIn('适用：公共前置操作', show(full)['xmind_markdown'])

    def test_shared_edit_is_a_proposal_and_obligations_stay_unchanged(self):
        from feedback import prepare_feedback
        result = show(approved())
        original = copy.deepcopy(result['batch'])
        proposal = prepare_feedback(result['batch'], 'markdown',
            markdown=result['xmind_markdown'].replace('准备模拟订单', '准备新的模拟订单'), actual_reply='SIMULATED request change')
        self.assertEqual({c['id'] for c in proposal['changes']}, {'SIM-' + str(i) for i in range(7)})
        self.assertEqual(original, result['batch'])


if __name__ == '__main__':
    unittest.main()
