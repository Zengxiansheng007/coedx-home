"""Synthetic public projection regression for issue 114."""
import copy
import unittest
from test_scoped_review import catalog
from scoped_review import build_scoped_review
from presentation import render_chat
from feedback import prepare_feedback


class ReviewExpressionTests(unittest.TestCase):
    def test_titles_and_duplicate_expectations_roundtrip(self):
        full = catalog()  # Synthetic source; no business approval.
        for priority, case in zip(('P0', 'P1', 'P2'), full['cases']):
            case.update(priority=priority, title='创建系统公告')  # Keep stable IDs.
            case['steps'][0]['expected'] = [{'text': '保存成功'}]
            case['steps'][0]['verification'] = [{'text': '保存成功'}, {'text': '列表显示本次记录且状态正确'}]
        before = copy.deepcopy(full)
        result = build_scoped_review(full, 'synthetic-114', [{'case_id': c['id'], 'action': 'related', 'reason': '模拟评审'} for c in full['cases']])
        for priority, case in zip(('P0', 'P1', 'P2'), full['cases']):
            chat = render_chat(result['batch'], [case['id']])['human_view']
            self.assertIn('# ' + priority + ' 创建系统公告', chat)
            self.assertIn('- ' + priority + ' 创建系统公告', result['xmind_markdown'])
            self.assertEqual(chat.count('保存成功'), 1)
            self.assertIn('列表显示本次记录且状态正确', chat)
        pending = prepare_feedback(result['batch'], 'markdown', markdown=result['xmind_markdown'], actual_reply='模拟：原样回传')
        self.assertEqual(pending['changes'], [])
        self.assertEqual(full, before)


if __name__ == '__main__':
    unittest.main()
