"""S1-01 uses the existing scoped-review and feedback entry points."""

import copy
from pathlib import Path
import tempfile
import unittest

from feedback import prepare_feedback
from module_handoff import write_artifacts
from preparation_scope import review_preparation_scope
from scoped_review import build_scoped_review, render_review_batch
from test_feedback import confirm
from test_preparation_scope import source


def review_sample():
    full = source()
    full['cases'] = full['cases'][:4]
    ids = [case['id'] for case in full['cases']]
    for index, case in enumerate(full['cases']):
        case['priority'] = 'P2'
        case['business_group']['path'] = ['系统公告' if index < 3 else '首页弹窗公告']
        common = copy.deepcopy(case['common_preconditions'][0])
        case['common_preconditions'] = [
            dict(common, id='access', operation='核对访问配置'),
            dict(copy.deepcopy(common), id='enter', operation='打开创建页'),
        ]
        case['steps'][1]['expected'][0]['text'] = f'显示本例默认结果 {index}'
    full = review_preparation_scope(
        full, scope_kind='module', applicable_case_ids=ids, exception_case_ids=[],
        coverage='vast_majority_few_exceptions', basis='SIMULATED common preparation',
        actual_reply='SIMULATED exact scope reviewed', version='v1', frequency='每例重新进入',
    )
    empty = dict(full, cases=[], content_version='synthetic-full-v1')
    return build_scoped_review(
        empty, 'SIMULATED-creation-review',
        [{'case_id': case_id, 'action': 'add', 'reason': '检查创建页默认状态'} for case_id in ids],
        candidates=full['cases'], review_layout='incremental-v1',
    ), full


class IncrementalReviewTests(unittest.TestCase):
    def test_visible_outline_follows_the_confirmed_business_structure(self):
        result, _ = review_sample()
        markdown = result['xmind_markdown']
        self.assertTrue(markdown.startswith('# 增量用例评审｜Save\n- 评审范围\n'))
        self.assertIn('  - 稿件版本：' + result['batch']['content_version'], markdown)
        self.assertIn('  - 基线：synthetic-full-v1', markdown)
        self.assertIn('  - 本轮范围：Save，共 4 条', markdown)
        self.assertIn('\n- Example\n  - Workspace\n    - Web\n', markdown)
        self.assertIn('适用用例（本轮 4 条）', markdown)
        self.assertEqual(markdown.count('适用用例（'), 1)
        for index in range(4):
            self.assertIn(f'用例编号：SIM-{index}', markdown)
        self.assertIn('操作 1：核对访问配置', markdown)
        self.assertIn('操作 2：打开创建页', markdown)
        self.assertIn('预期：显示本例默认结果 1', markdown)
        self.assertNotIn('公共后置操作', markdown)
        self.assertNotIn('特殊前置操作', markdown)

    def test_same_file_then_one_expected_result_changes_only_its_own_case(self):
        result, _ = review_sample()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'review'
            output.mkdir()
            write_artifacts(result, output)
            returned = (output / 'xmind.md').read_text(encoding='utf-8')
            baseline = result['batch']
            pending = prepare_feedback(
                baseline, 'markdown', markdown=returned,
                actual_reply='SIMULATED no changes', companion_base=output,
            )
            self.assertEqual(pending['changes'], [])
            edited = returned.replace('预期：显示本例默认结果 1', '预期：展示本例默认渠道')
            pending = prepare_feedback(
                baseline, 'markdown', markdown=edited,
                actual_reply='SIMULATED one expected result changed', companion_base=output,
            )
            self.assertEqual(
                [(change['id'], change['path'], change['value']) for change in pending['changes']],
                [('SIM-1', ['steps', 1, 'expected', 0, 'text'], '展示本例默认渠道')],
            )
            updated = confirm(pending)['batch']
            self.assertEqual(updated['initial_copy_baseline'], baseline['initial_copy_baseline'])
            self.assertIn('预期：展示本例默认渠道', render_review_batch(updated)['xmind_markdown'])
            for before, after in zip(baseline['cases'], updated['cases']):
                if before['id'] != 'SIM-1':
                    self.assertEqual(after, before)


if __name__ == '__main__':
    unittest.main()
