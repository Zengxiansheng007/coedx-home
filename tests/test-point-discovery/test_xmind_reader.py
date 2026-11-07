"""Synthetic archives prove format handling only, never client compatibility."""
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

SCRIPT = Path(__file__).parents[2] / 'skills/test-point-discovery/scripts/read_xmind.py'


class NativeRead(unittest.TestCase):
    def read(self, sheets, extra=None):
        spec = importlib.util.spec_from_file_location('reader', SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'returned.xmind'
            with zipfile.ZipFile(path, 'w') as archive:
                archive.writestr('content.json', json.dumps(sheets, ensure_ascii=False))
                archive.writestr('content.xml', '<compatibility/>')
                if extra:
                    archive.writestr(*extra)
            return module.read_xmind(path)

    def test_ordered_chinese_hierarchy_without_writing_or_interpreting(self):
        result = self.read([{'rootTopic': {'id': 'root', 'title': '待评审', 'children': {'attached': [
            {'id': 'chart', 'title': '设备图', 'children': {'attached': [
                {'id': 'date', 'title': '首尾均纳入'}]}},
            {'id': 'question', 'title': '【待产品确认】'}]}}}])
        self.assertEqual(result['status'], 'read_for_agent_review')
        self.assertEqual([t['title'] for t in result['topics']], ['待评审', '设备图', '首尾均纳入', '【待产品确认】'])
        self.assertEqual(result['topics'][2]['path'], ['待评审', '设备图', '首尾均纳入'])
        self.assertEqual(result['topics'][2]['id'], 'date')
        self.assertEqual(len(result['source']['sha256']), 64)

    def test_unsupported_semantics_remain_pending(self):
        for sheet in [
            {'rootTopic': {'title': '主题', 'notes': {'plain': {'content': '不能丢'}}}},
            {'rootTopic': {'title': '主题', 'children': {'detached': [{'title': '自由主题'}]}}},
            {'rootTopic': {'title': '主题'}, 'relationships': [{}]},
        ]:
            result = self.read([sheet])
            self.assertEqual(result['status'], 'pending_verification')
            self.assertNotIn('topics', result)

    def test_duplicate_identity_and_multiple_sheets_are_pending(self):
        sheet = {'rootTopic': {'id': 'r', 'title': '根', 'children': {'attached': [{'id': 'r', 'title': '重复'}]}}}
        self.assertEqual(self.read([sheet])['status'], 'pending_verification')
        self.assertEqual(self.read([{'rootTopic': {'title': '根'}}] * 2)['status'], 'pending_verification')


if __name__ == '__main__':
    unittest.main()
