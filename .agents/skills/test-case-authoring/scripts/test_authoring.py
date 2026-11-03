"""Synthetic recordings only; exercise the public batch conversion seam."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from authoring import build_batch


def sample():
    recording = "// role: editor; state: signed in\nawait page.getByLabel('Title').fill('Sample notice');\nawait page.getByRole('button', {name: 'Save'}).click();\nawait expect(page.getByText('Saved')).toBeVisible();\n"
    draft = {
        'batch_id': 'demo-batch', 'case_id': 'DEMO-P0-001',
        'module_path': ['Example team', 'Example product', 'Web', 'Notices', 'Create'],
        'title': 'Save a notice',
        'context': {'role': [{'text': 'editor', 'source': 'recording', 'lines': [1, 1]}],
                    'initial_state': [{'text': 'signed in', 'source': 'recording', 'lines': [1, 1]}]},
        'data': [{'id': 'title', 'value': 'Sample notice', 'source': 'recording', 'lines': [2, 2]}],
        'steps': [
            {'operation': 'Enter notice title', 'data_refs': ['title'], 'source': 'recording', 'lines': [2, 2],
             'expected': [], 'verification': []},
            {'operation': 'Save the notice', 'data_refs': [], 'source': 'recording', 'lines': [3, 3],
             'expected': [{'text': 'Saved message is visible', 'source': 'recording', 'lines': [4, 4]}],
             'verification': [{'text': 'Read the visible saved message', 'source': 'recording', 'lines': [4, 4]}]},
        ],
        'common_preconditions': [],
        'recording_coverage': [{'lines': [1, 1], 'reason': 'context'},
                               {'lines': [2, 4], 'reason': 'steps and observation'}],
    }
    return recording, draft


class BatchTests(unittest.TestCase):
    def test_business_conditions_and_data_versions_are_preserved_in_both_views(self):
        recording, draft = sample()
        draft['data'][0].update({'object_ref': 'this notice', 'validity': 'today only', 'reuse_policy': 'per case', 'invalidation_action': 'ask user'})
        result = build_batch(recording, draft)
        for view in ('human_view', 'xmind_markdown'):
            self.assertIn('today only', result[view])
            self.assertIn('per case', result[view])
        tree = result['xmind_markdown']
        self.assertEqual(tree.count('- 参数/数据\n'), 2)
        self.assertEqual(tree.count('- 预期\n'), 2)
        changed = copy.deepcopy(draft)
        changed['data'][0]['value'] = 'Another title'
        updated = build_batch(recording, changed)
        self.assertNotEqual(result['batch']['content_version'], updated['batch']['content_version'])
        self.assertNotEqual(result['batch']['data_version'], updated['batch']['data_version'])
        self.assertEqual(result['batch']['cases'][0]['id'], updated['batch']['cases'][0]['id'])

    def test_credentials_rejected_everywhere_and_reference_only_is_rendered(self):
        recording, draft = sample()
        with self.assertRaisesRegex(ValueError, 'credential'):
            build_batch(recording + "await page.getByLabel('Password').fill('synthetic-secret');", draft)
        draft['title'] = 'Bearer synthetic-access-token'
        with self.assertRaisesRegex(ValueError, 'credential'):
            build_batch(recording, draft)
        recording, draft = sample()
        draft['data'].append({'id': 'login', 'credential_ref': 'credential://demo/editor', 'source': 'inference'})
        draft['steps'][0]['data_refs'].append('login')
        result = build_batch(recording, draft)
        self.assertIn('credential://demo/editor', result['human_view'])
        self.assertNotIn('value', result['batch']['data'][1])

    def test_cli_reads_code_without_executing_and_refuses_existing_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sentinel = root / 'executed'
            recording, draft = sample()
            recording += f"require('fs').writeFileSync({json.dumps(str(sentinel))}, 'bad');\n"
            draft['recording_coverage'].append({'lines': [5, 5], 'reason': 'untrusted non-business code, never execute'})
            (root / 'recording.js').write_text(recording, encoding='utf-8')
            (root / 'draft.json').write_text(json.dumps(draft), encoding='utf-8')
            command = [sys.executable, '-B', str(Path(__file__).with_name('authoring.py')), '--recording', str(root / 'recording.js'), '--interpretation', str(root / 'draft.json'), '--output-dir', str(root / 'output')]
            process = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertFalse(sentinel.exists())
            batch = json.loads((root / 'output/candidate.json').read_text(encoding='utf-8'))
            self.assertEqual(batch['cases'][0]['execution_status'], 'not_run')
            original = (root / 'output/human-view.md').read_bytes()
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
            self.assertEqual((root / 'output/human-view.md').read_bytes(), original)
            self.assertEqual((root / 'recording.js').read_text(encoding='utf-8'), recording)

    def test_prd_conflict_and_missing_context_remain_locatable_and_unconfirmed(self):
        recording, draft = sample()
        draft['context']['role'] = []
        draft['steps'][1]['expected'].append({'text': 'Notice waits for approval', 'source': 'prd', 'lines': [1, 1]})
        result = build_batch(recording, draft, 'Saving a notice must wait for approval.')
        questions = result['batch']['questions']
        self.assertTrue(any(q['field'] == 'role' for q in questions))
        conflict = next(q for q in questions if q['reason'] == '资料或观察不一致，待用户裁决')
        self.assertEqual({s['source'] for s in conflict['evidence']}, {'recording', 'prd'})
        self.assertIn('Notice waits for approval', result['human_view'])
        self.assertIn('Saved message is visible', result['human_view'])
        self.assertEqual(result['batch']['cases'][0]['rule_status'], 'unconfirmed')
        self.assertEqual(result['batch']['sources'][1]['kind'], 'prd')

    def test_unaccounted_recording_and_invalid_provenance_are_rejected(self):
        recording, draft = sample()
        with self.assertRaisesRegex(ValueError, 'unaccounted'):
            build_batch(recording + 'await page.reload();\n', draft)
        draft['steps'][0]['lines'] = [2, 999]
        with self.assertRaisesRegex(ValueError, 'source range'):
            build_batch(recording, draft)

    def test_recording_becomes_unreviewed_p0_with_shared_version_and_business_data(self):
        recording, draft = sample()
        original = copy.deepcopy(draft)
        result = build_batch(recording, draft)
        self.assertEqual(draft, original)
        case = result['batch']['cases'][0]
        self.assertEqual(case['id'], 'DEMO-P0-001')
        self.assertEqual(case['priority'], 'P0')
        self.assertEqual(case['review_status'], 'pending')
        self.assertEqual(case['execution_status'], 'not_run')
        self.assertEqual(case['steps'][0]['data_refs'], ['title'])
        self.assertNotIn('Sample notice', str(case))
        self.assertEqual(result['batch']['data'][0]['value'], 'Sample notice')
        for view in ('human_view', 'xmind_markdown'):
            self.assertIn(result['batch']['content_version'], result[view])
            self.assertIn('Sample notice', result[view])
            self.assertIn('Save the notice', result[view])
            self.assertIn('Saved message is visible', result[view])
            self.assertIn('Read the visible saved message', result[view])
        self.assertIn('| 序号 | 操作 | 参数/数据 | 预期结果 |', result['human_view'])
        self.assertEqual(result['batch']['sources'][0]['kind'], 'recording')
        self.assertTrue(result['batch']['questions'])  # first step lacks an expectation


if __name__ == '__main__':
    unittest.main()
