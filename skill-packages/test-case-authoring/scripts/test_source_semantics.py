"""Synthetic source semantics through conversion and scoped-review public APIs."""
import copy  # Verify callers' source remains unchanged.
import unittest  # Use the existing standard-library test runner.

from authoring import build_handwritten_batch  # Test the actual authoring entry.
from scoped_review import build_scoped_review  # Test the second presentation entry.


def synthetic_case():  # Explicitly authored semantics; never infer actions from prose.
    source = '\n'.join(['editor; fresh form', 'choose type A', 'query unique title',
                        'fill title and body', 'set dates', 'preview', 'permission remains required'])  # Synthetic evidence.
    def claim(text, line):  # Preserve source evidence for each result.
        return {'text': text, 'source': 'handwritten', 'lines': [line, line]}
    def step(operation, refs, expected, line):  # Each independent checkpoint is explicit.
        return dict(claim('', line), operation=operation, data_refs=refs,
                    expected=[claim(expected, line)], verification=[claim(expected, line)])
    values = [('类型', 'A', 2), ('标题', '{MMDD}{case}{HHmmss}; maximum 20 characters', 3),
              ('正文', '内容引用 {本次标题}', 4), ('有效期', 'start=day+1 10:00; end=day+1 10:00; target overrides default +1 day', 5)]  # One effective date pair.
    data = [dict(claim('', line), id=name, value=value, object_ref='synthetic notice',
                 validity='this scenario', reuse_policy='reference only', invalidation_action='clarify')
            for name, value, line in values]  # Business rules remain visible.
    return source, {'batch_id': 'synthetic-semantic', 'case_id': 'SYN-P0', 'title': '合成预览',
        'module_path': ['合成组', '合成产品', '合成系统', '通知', '预览'],
        'context': {'role': [claim('editor', 1)], 'initial_state': [claim('fresh form', 1)]},
        'data': data, 'common_preconditions': [step('查询本次标题', ['标题'], '同名记录为零', 3)],
        'steps': [step('选择类型', ['类型'], '类型为 A', 2),
                  step('填写标题和正文', ['标题', '正文'], '标题与正文分别等于指定值', 4),
                  step('设置生效与结束时间', ['有效期'], '两端时间完全相等', 5),
                  step('预览', [], '预览显示已填写内容', 6)],
        'technical_handoff': [claim('TECHNICAL-PERMIT: downstream allocation requires authorization', 7)],
        'handwritten_coverage': [{'lines': [1, 7], 'reason': 'synthetic scenario and execution constraint'}]}


def scoped(result):  # Reuse exactly the converted case and data in the other entry.
    batch = result['batch']  # Keep the original content as catalog authority.
    full = {'kind': 'authoring_full_catalog', 'schema_version': 1, 'source_ref': 'synthetic://semantics',
            'content_version': batch['content_version'], 'cases': batch['cases'], 'data': batch['data']}
    return build_scoped_review(full, 'synthetic-review', [{'case_id': 'SYN-P0', 'action': 'reuse', 'reason': 'review'}])


class SourceSemanticsTests(unittest.TestCase):
    def test_corrected_source_keeps_data_rules_and_independent_checkpoints_in_both_views(self):
        source, draft = synthetic_case()  # Source meaning is resolved before rendering.
        converted = build_handwritten_batch(source, draft)  # First public presentation entry.
        for result in (converted, scoped(converted)):  # The scoped entry must preserve the same case.
            case = result['batch']['cases'][0]  # Inspect public output rather than renderer internals.
            self.assertEqual(case['steps'][0]['data_refs'], ['类型'])  # Selection must not consume the full form.
            self.assertEqual([step['operation'] for step in case['steps']],
                             ['选择类型', '填写标题和正文', '设置生效与结束时间', '预览'])  # Combined ordinary entry and separate checkpoints survive.
            for key in ('human_view', 'xmind_markdown'):  # Both outputs preserve all necessary business meaning.
                for text in ('查询本次标题', '同名记录为零', '填写标题和正文', '标题与正文分别等于指定值',
                             '{MMDD}{case}{HHmmss}', 'maximum 20 characters', '内容引用 {本次标题}',
                             'target overrides default +1 day', '两端时间完全相等', '预览显示已填写内容'):
                    self.assertIn(text, result[key])  # Literal expectations are independent of renderer implementation.
                self.assertIn(result['batch']['content_version'], result[key])  # Views bind their own batch version.

    def test_negative_case_does_not_gain_form_filling_and_unknown_result_stays_pending(self):
        source, draft = synthetic_case()  # Reuse only the fixture shape, not successful-path steps.
        draft['common_preconditions'] = []  # No lookup needed for this goal.
        draft['data'] = draft['data'][:1]  # Only type data is used.
        draft['steps'] = draft['steps'][:1] + [{'operation': '清空标题并移开焦点', 'data_refs': [],
            'source': 'handwritten', 'lines': [4, 4], 'expected': [], 'verification': []}]  # Trigger outcome is unknown.
        result = build_handwritten_batch(source, draft)  # Conversion must not fabricate a result.
        self.assertEqual(len(result['batch']['cases'][0]['steps']), 2)  # No automatic full-form expansion.
        self.assertTrue(any(q['field'] == 'steps/1' for q in result['batch']['questions']))  # Unknown remains locatable for actual questioning.
        for key in ('human_view', 'xmind_markdown'):  # Both views stay honest about missing rules.
            self.assertNotIn('填写标题和正文', result[key])  # No invented action.
            self.assertNotIn('预览显示已填写内容', result[key])  # No copied successful result.
            self.assertIn('待澄清', result[key])  # Pending content is not approved behavior.

    def test_technical_constraints_survive_both_entries_outside_business_views(self):
        source, draft = synthetic_case()  # The constraint is source-authored, not renderer-derived.
        before = copy.deepcopy(draft)  # Detect source mutation.
        converted = build_handwritten_batch(source, draft)  # Public conversion seam.
        self.assertEqual(converted['batch']['cases'][0]['technical_handoff'][0]['text'], draft['technical_handoff'][0]['text'])  # No silent constraint loss.
        for result in (converted, scoped(converted)):  # Both presentation paths keep technical handoff.
            self.assertIn('TECHNICAL-PERMIT', str(result['batch']['cases'][0]['technical_handoff']))  # Still locatable internally.
            for key in ('human_view', 'xmind_markdown'):  # Business readers see business conditions only.
                self.assertNotIn('TECHNICAL-PERMIT', result[key])  # No governance as data or action.
                self.assertIn('editor', result[key])  # Required role is not hidden with governance.
        self.assertEqual(draft, before)  # The input remains immutable.


if __name__ == '__main__':
    unittest.main()  # Allow the existing standalone test convention.
