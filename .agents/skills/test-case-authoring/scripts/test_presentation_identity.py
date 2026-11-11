"""SIMULATED Chinese presentation and stable feedback identity."""
import copy
import unittest
from authoring import render_batch
from test_aggregation import synthetic_scope
from feedback import prepare_feedback


class PresentationIdentityTests(unittest.TestCase):
    def test_legacy_displayed_ids_keep_scalar_feedback_compatible(self):
        from test_feedback import scope
        original = scope()
        legacy = original['xmind_markdown'].replace('- Save a notice\n', '- EDIT Save a notice\n', 1)
        offset = legacy.index('- Accounts')
        legacy = legacy[:offset] + legacy[offset:].replace('- Save a notice\n', '- LINK Save a notice\n', 1)
        edited = legacy.replace('Saved message is visible', '模拟：保存成功')
        pending = prepare_feedback(original['batch'], 'markdown', markdown=edited, actual_reply='模拟：修改历史英文编号稿的预期')
        self.assertEqual({c['id'] for c in pending['changes']}, {'EDIT', 'LINK'})

    def test_same_title_reordered_cases_need_business_binding_not_position(self):
        from scoped_review import build_scoped_review
        from test_scoped_review import catalog
        from aggregation import feedback_topics
        full = catalog()
        for case in full['cases'][:2]:
            case['title'] = '保存资料'
            case['module_path'] = full['cases'][0]['module_path']
        full['cases'][1]['context']['role'][0]['text'] = '审核员'
        result = build_scoped_review(full, 'SIMULATED-same-name', [{'case_id': cid, 'action': 'related', 'reason': '模拟评审'} for cid in ('EDIT', 'LINK')])
        changed = result['xmind_markdown'].replace('初始状态：signed in', '初始状态：已授权', 1)
        with self.assertRaises(ValueError):
            prepare_feedback(result['batch'], 'markdown', markdown=changed, actual_reply='模拟：修改保存资料')
        topics = [t for t in feedback_topics(changed) if t['title'] == '保存资料']
        bindings = {'EDIT': dict(topics[0], source_version=result['batch']['content_version'], actual_reply='模拟：修改编辑员的初始状态，审核员不变')}
        lines = changed.splitlines()
        starts = [i for i, line in enumerate(lines) if line == '          - 保存资料']  # Move complete known fixture subtrees after explicit binding.
        changed = '\n'.join(lines[:starts[0]] + lines[starts[1]:] + lines[starts[0]:starts[1]]) + '\n'
        pending = prepare_feedback(result['batch'], 'markdown', markdown=changed, actual_reply='模拟：编辑员已授权', case_bindings=bindings)
        self.assertEqual(pending['affected_case_ids'], ['EDIT'])
        from test_feedback import confirm
        forged = copy.deepcopy(pending)
        forged['case_bindings']['EDIT']['actual_reply'] = '伪造身份答复'
        with self.assertRaises(ValueError):
            confirm(forged)
        stale = copy.deepcopy(bindings)
        stale['EDIT']['source_version'] = 'stale'
        with self.assertRaises(ValueError):
            prepare_feedback(result['batch'], 'markdown', markdown=changed, actual_reply='模拟：旧版本', case_bindings=stale)

    def test_rename_requires_explicit_business_binding_and_preserves_identity(self):
        from aggregation import feedback_topics
        from test_feedback import confirm
        original = synthetic_scope()
        edited = original['xmind_markdown'].replace('- Save a notice\n', '- 保存修订资料\n', 1)
        with self.assertRaises(ValueError):
            prepare_feedback(original['batch'], 'markdown', markdown=edited, actual_reply='模拟：已改名')
        topics = feedback_topics(edited)
        target = next(t for t in topics if t['title'] == '保存修订资料')
        bindings = {'EDIT': dict(target, source_version=original['batch']['content_version'], actual_reply='模拟：修改资料目录下准备模拟资料的创建用例名称，关联用例保持不变')}
        pending = prepare_feedback(original['batch'], 'markdown', markdown=edited, actual_reply='模拟：已改名', case_bindings=bindings)
        updated = confirm(pending)
        self.assertEqual(updated['batch']['cases'][0]['id'], 'EDIT')
        self.assertEqual(updated['batch']['cases'][0]['title'], '保存修订资料')
        self.assertEqual(updated['batch']['cases'][1], original['batch']['cases'][1])
        self.assertEqual(updated['batch']['feedback_history'][-1]['case_bindings'], bindings)

    def test_same_named_cases_keep_internal_ids_and_chinese_views(self):
        batch = synthetic_scope()['batch']  # Same-name cases are still independent records.
        for case in batch['cases']:
            case['title'] = '保存模拟资料'
        batch['cases'][0]['dependencies'] = [{'case_id': 'LINK', 'purpose': '准备模拟资料'}]
        before = copy.deepcopy(batch)
        for plain in (False, True):
            displayed = copy.deepcopy(batch)
            if plain:
                displayed.pop('kind')
            result = render_batch(displayed)
            for view in ('human_view', 'xmind_markdown'):
                self.assertNotIn('EDIT', result[view])
                self.assertNotIn('LINK', result[view])
                self.assertNotIn('用例编号', result[view])
                self.assertIn('保存模拟资料', result[view])
                self.assertIn('P0', result[view])
                self.assertIn(batch['content_version'], result[view])
        self.assertEqual(batch, before)


if __name__ == '__main__':
    unittest.main()
