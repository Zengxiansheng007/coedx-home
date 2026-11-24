"""Hypothetical mixed selection and isolated merge through public entries."""

import copy
from pathlib import Path
import re
import tempfile
import unittest
from urllib.parse import urlsplit
from urllib.request import url2pathname

from clarification import apply_summary, review, start_grill, summarize
from feedback import prepare_feedback
from module_handoff import write_artifacts
from partial_merge import merge_reviewed
from preparation_scope import review_preparation_scope
from scoped_review import build_scoped_review
from test_partial_merge import fixture
from test_preparation_scope import source


def mixed(detail=None):
    full, previous, _ = fixture()
    full['data'][0]['value'] = ''
    related = dict(copy.deepcopy(full['cases'][2]), id='CONTEXT', title='来源详情')
    full['cases'].append(related)
    candidates = [case for case in previous['cases'] if case['id'] in ('EDIT', 'NEW')]
    requests = [
        {'case_id': 'NEW', 'action': 'add', 'reason': '验证留空字段'},
        {'case_id': 'EDIT', 'action': 'modify', 'reason': '更新读取后的检查',
         'basis': 'hypothetical design', 'coverage_impact': '操作 2 的预期'},
        {'case_id': 'OTHER', 'action': 'reuse', 'reason': '旧定义仍适用'},
        {'case_id': 'CONTEXT', 'action': 'related', 'reason': '检查操作的结果'},
        {'case_id': 'LINK', 'action': 'deactivate', 'reason': '旧入口移除',
         'replacement_case_id': 'EDIT'},
    ]
    if detail is not None:
        requests[3]['detail_ref'] = str(detail)
    result = build_scoped_review(
        full, 'hypothetical-appointment', requests, candidates=candidates,
        review_layout='incremental-v1', hypothetical=True,
    )
    return full, result


class IncrementalMixedTests(unittest.TestCase):
    def test_source_only_relationship_keeps_id_and_actual_detail(self):
        with tempfile.TemporaryDirectory() as directory:
            detail = Path(directory) / '示例 详情.md'
            detail.write_text('# 假设详情\n', encoding='utf-8')
            _, result = mixed(detail)
            view = result['xmind_markdown']
            related = view.partition('「关联查看」P1 来源详情')[2].split('资料与 Agent 交接说明')[0]
            self.assertIn('用例编号：CONTEXT', related)
            self.assertIn('[查看关联用例详情](' + detail.resolve().as_uri() + ')', related)  # Match the resolved path casing used in the exported link.
            self.assertNotIn('操作 1', related)

    def test_distinct_pre_scopes_and_shared_post_scope_keep_exact_owners(self):
        full = source()
        full['cases'] = full['cases'][:4]
        ids = [case['id'] for case in full['cases']]
        for case in full['cases']:
            base = case['common_preconditions'][0]
            case['common_preconditions'] = [dict(base, id='entry', operation='打开假设预约页')]
            if case['id'] in ids[:3]:
                case['common_preconditions'].append(dict(base, id='prepare', operation='准备预约场次'))
                case['common_postconditions'] = [
                    dict(base, id='delete', operation='删除本例草稿', trigger_condition='本例已取得草稿编号'),
                    dict(base, id='check', operation='按草稿编号核对', trigger_condition='删除已成功'),
                ]
        for operation, direction, count in (('entry', 'pre', 4), ('prepare', 'pre', 3),
                                             ('delete', 'post', 3), ('check', 'post', 3)):
            owners = ids[:count]
            full = review_preparation_scope(
                full, scope_kind='module', operation_id=operation, direction=direction,
                step_ids_by_case={cid: [operation] for cid in owners},
                applicable_case_ids=owners, exception_case_ids=ids[count:],
                coverage='vast_majority_few_exceptions', basis='SIMULATED specific completeness',
                actual_reply='SIMULATED exact scope reviewed', version='demo', frequency='每例确认',
            )
        result = build_scoped_review(
            full, 'hypothetical-common', [
                dict(case_id=cid, action='reuse', reason='假设复用') for cid in ids
            ], review_layout='incremental-v1', hypothetical=True,
        )
        view = result['xmind_markdown']
        self.assertEqual(view.count('适用用例（本轮 4 条）'), 1)
        self.assertEqual(view.count('适用用例（本轮 3 条）'), 2)
        self.assertEqual(view.count('公共后置操作'), 1)
        self.assertIn('触发条件：本例已取得草稿编号', view)
        self.assertLess(view.index('用例编号：SIM-3'), view.index('公共后置操作'))
        proposed = prepare_feedback(result['batch'], 'markdown', actual_reply='SIMULATED edit',
            markdown=view.replace('准备预约场次', '准备可选预约场次'), source_catalog=full)
        self.assertEqual(set(proposed['affected_case_ids']), set(ids[:3]))
        self.assertEqual({item['id'] for item in proposed['changes']}, set(ids[:3]))

    def test_mixed_status_notes_and_modules_with_actual_materials(self):
        full, result = mixed()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'review'
            output.mkdir()
            write_artifacts(result, output, source_catalog=full)
            markdown = (output / 'xmind.md').read_text(encoding='utf-8')
            self.assertIn('假设样稿', markdown)
            self.assertIn('新增 1 条、修改 1 条、沿用 1 条、关联查看 1 条、拟停用 1 条', markdown)
            self.assertIn('本次修改：更新读取后的检查。操作 2 的预期', markdown)
            self.assertIn('沿用依据：旧定义仍适用', markdown)
            self.assertIn('关联原因：检查操作的结果', markdown)
            self.assertIn('停用原因：旧入口移除', markdown)
            self.assertIn('替代用例：EDIT', markdown)
            self.assertIn('：留空', markdown)
            self.assertNotIn('「新增」', markdown)
            self.assertEqual(markdown.count('资料与 Agent 交接说明'), 3)
            self.assertNotIn('资料与 Agent 交接说明', markdown.partition('\n- Example')[0])
            for link in re.findall(r'\]\((file://[^)]+)\)', markdown):
                self.assertTrue(Path(url2pathname(urlsplit(link).path)).is_file())
            unchanged = prepare_feedback(result['batch'], 'markdown', markdown=markdown,
                actual_reply='SIMULATED unchanged', companion_base=output, source_catalog=full)
            self.assertEqual(unchanged['changes'], [])

    def test_only_reviewed_selection_is_applied_with_formal_titles(self):
        full, result = mixed()
        batch = result['batch']
        before = copy.deepcopy(full)
        state = summarize(start_grill(batch, []))
        state = apply_summary(state, dict(confirmed=True, actual_reply='SIMULATED summary approved',
                                          summary_id=state['summary']['id']))
        chosen = ['EDIT', 'NEW']
        state = review(state, dict(approved=True, actual_reply='SIMULATED selected cases reviewed',
                                  case_ids=chosen, content_version=state['batch']['content_version']))
        merged = merge_reviewed(full, state['batch'], dict(
            kind='merge_instruction', actual_reply='SIMULATED explicit isolated merge', case_ids=chosen,
            content_version=state['batch']['content_version'], baseline_version=full['content_version'],
        ), target_kind='isolated')
        written = {case['case_id'] for case in merged['cases'] if case['status'] == 'applied'}
        self.assertEqual(written, set(chosen))
        self.assertEqual(full, before)
        records = {case['id']: case for case in merged['catalog']['cases']}
        for case in full['cases']:
            if case['id'] not in chosen:
                self.assertEqual(case, records[case['id']])
        self.assertTrue(all('「' not in records[case_id]['title'] for case_id in chosen))
        self.assertEqual(merged['catalog']['data'][0]['value'], '')


if __name__ == '__main__':
    unittest.main()
