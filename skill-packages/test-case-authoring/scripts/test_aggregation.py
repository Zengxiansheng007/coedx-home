"""SIMULATED public projection checks; no business execution."""
import copy
import unittest
import json
from pathlib import Path
import tempfile
import zipfile

from authoring import render_batch
from scoped_review import build_scoped_review
from test_scoped_review import catalog
from feedback import prepare_feedback  # Public return boundary retains shared owners.
from xmind_feedback import prepare_xmind_feedback  # Synthetic native files exercise supported return format.


def synthetic_scope():
    full = catalog()  # Reuse a source-traced synthetic catalog.
    for case in full['cases'][:2]:
        case['module_path'] = ['模拟项目', '同名平台', '同名平台', '资料', '保存']  # Semantic levels remain separate.
        case['common_preconditions'] = [copy.deepcopy(case['steps'][1])]  # Identical complete preparation.
        case['common_preconditions'][0]['operation'] = '准备模拟资料'  # Distinct from case steps.
    return build_scoped_review(full, 'SIMULATED-aggregation', [
        {'case_id': cid, 'action': 'related', 'reason': 'SIMULATED review'}
        for cid in ('EDIT', 'LINK')])  # Unselected OTHER stays outside the copy.


class AggregationTests(unittest.TestCase):
    def test_batch_and_scope_share_one_semantic_path_and_preparation(self):
        result = synthetic_scope()  # Exercise the scoped entry first.
        batch = copy.deepcopy(result['batch'])  # Rendering must preserve source content.
        plain = copy.deepcopy(batch)
        plain.pop('kind')  # Exercise the ordinary multi-case batch entry too.
        for rendered in (result, render_batch(plain)):
            tree = rendered['xmind_markdown']
            self.assertEqual(tree.count('- 模拟项目\n'), 1)
            self.assertEqual(tree.count('- 同名平台\n'), 2)
            self.assertEqual(tree.count('步骤 1：准备模拟资料'), 1)
            self.assertIn('适用用例：EDIT、LINK', tree)
            self.assertNotIn('OTHER ', tree)
        self.assertEqual(result['batch'], batch)

    def test_context_order_data_expectation_and_path_differences_remain_separate(self):
        for difference in ('role', 'state', 'order', 'data', 'expected', 'path', 'object'):
            batch = synthetic_scope()['batch']  # Each variation starts with identical preparation.
            first, second = batch['cases']
            if difference == 'role':
                second['context']['role'][0]['text'] = '模拟审核员'
            elif difference == 'state':
                second['context']['initial_state'][0]['text'] = '模拟已锁定'
            elif difference == 'order':
                first['common_preconditions'].append(copy.deepcopy(first['steps'][0]))
                second['common_preconditions'] = list(reversed(copy.deepcopy(first['common_preconditions'])))
            elif difference == 'data':
                second['common_preconditions'][0]['data_refs'] = ['title']
            elif difference == 'expected':
                second['common_preconditions'][0]['expected'][0]['text'] = '模拟其他结果'
            elif difference == 'object':
                first['common_preconditions'][0]['object_binding'] = {'id': 'SIMULATED-A'}
                second['common_preconditions'][0]['object_binding'] = {'id': 'SIMULATED-B'}
            else:
                second['module_path'][1] = '另一产品'
            tree = render_batch(batch)['xmind_markdown']
            self.assertEqual(tree.count('准备模拟资料'), 2, difference)
            self.assertNotIn('适用用例：EDIT、LINK', tree, difference)

    def test_shared_feedback_targets_both_cases_and_single_case_keeps_preparation(self):
        result = synthetic_scope()
        edited = result['xmind_markdown'].replace('准备模拟资料', '准备修订模拟资料')
        pending = prepare_feedback(result['batch'], 'markdown', markdown=edited, actual_reply='SIMULATED: revise shared preparation')
        self.assertEqual({c['id'] for c in pending['changes']}, {'EDIT', 'LINK'})
        self.assertTrue(all(c['path'] == ['common_preconditions', 0, 'operation'] for c in pending['changes']))
        single = copy.deepcopy(result['batch'])
        single['cases'] = single['cases'][:1]
        tree = render_batch(single)['xmind_markdown']
        self.assertEqual(tree.count('准备模拟资料'), 1)
        self.assertIn('适用用例：EDIT', tree)
        self.assertIn('执行时仍须完成', tree)

    def test_special_groups_and_case_data_are_preserved_after_shared_projection(self):
        batch = synthetic_scope()['batch']
        batch['cases'][0]['special_preconditions'] = [dict(copy.deepcopy(batch['cases'][0]['steps'][0]), operation='特殊模拟准备')]
        batch['cases'][0]['special_postconditions'] = [dict(copy.deepcopy(batch['cases'][0]['steps'][1]), operation='特殊模拟清理')]
        before = copy.deepcopy(batch)
        result = render_batch(batch)
        for view in ('human_view', 'xmind_markdown'):
            for text in ('特殊模拟准备', '特殊模拟清理', 'Sample notice', 'Saved message is visible'):
                self.assertIn(text, result[view])
        self.assertEqual(batch, before)

    def test_native_shared_edit_preserves_all_case_owners(self):
        result = synthetic_scope()
        lines = result['xmind_markdown'].replace('准备模拟资料', '准备修订模拟资料').splitlines()
        root = {'title': lines[0][2:], 'children': {'attached': []}}
        stack = [(-1, root)]  # Encode the actual public output as the supported native topic tree.
        for line in lines[1:]:
            depth = (len(line) - len(line.lstrip())) // 2
            node = {'title': line.strip()[2:]}
            while stack[-1][0] >= depth:
                stack.pop()
            stack[-1][1].setdefault('children', {}).setdefault('attached', []).append(node)
            stack.append((depth, node))
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'SIMULATED.xmind'
            with zipfile.ZipFile(path, 'w') as archive:
                archive.writestr('content.json', json.dumps([{'rootTopic': root}]))
            pending = prepare_xmind_feedback(result['batch'], path, actual_reply='SIMULATED: shared preparation edit')
        self.assertEqual(pending['status'], 'ready_for_clarification')
        self.assertEqual({c['id'] for c in pending['changes']}, {'EDIT', 'LINK'})


if __name__ == '__main__':
    unittest.main()
