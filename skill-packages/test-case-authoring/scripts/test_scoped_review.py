"""Synthetic full-catalog samples, never a formal ui-test integration claim."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from authoring import build_batch
from test_authoring import sample
from scoped_review import build_scoped_review


def catalog():
    recording, draft = sample()
    batch = build_batch(recording, draft)['batch']
    original = batch['cases'][0]
    cases = []
    for name, module in [('EDIT', 'Notes'), ('LINK', 'Accounts'), ('OTHER', 'Archive')]:
        case = copy.deepcopy(original)
        case.update(id=name, module_path=['Example', 'Workspace', 'Web', module, 'Save'])
        cases.append(case)
    return {'schema_version': 1, 'kind': 'authoring_full_catalog',
            'content_version': 'synthetic-full-v1', 'source_ref': 'synthetic://catalog',
            'cases': cases, 'data': batch['data']}


class ScopedReviewTests(unittest.TestCase):
    def test_business_extensions_conditions_and_data_are_readable_in_both_views(self):
        full = catalog()
        case = full['cases'][0]
        case['dependencies'] = [{'case_id': 'ACCOUNT-1', 'module_path': ['Example', 'Workspace', 'Web', 'Accounts', 'Prepare'],
                                 'purpose': 'Prepare the same account', 'required_state': 'active'}]
        for group in ('steps', 'common_preconditions', 'special_preconditions', 'special_postconditions'):
            if not case.get(group):
                case[group] = [copy.deepcopy(case['steps'][0])]
            case[group][0]['object_binding'] = 'Use the account returned by ACCOUNT-1'
            case[group][0]['extra_condition'] = {'required_state': 'account is active'}
            case[group][0]['assertion_id'] = 'INTERNAL-ASSERTION-ONLY'
        full['data'][0].update(object_ref='same account', validity='until account disabled',
                              reuse_policy='shared within validity', invalidation_action='ask for approval')
        result = build_scoped_review(full, 'business-display', [
            {'case_id': 'EDIT', 'action': 'reuse', 'reason': 'Necessary preparation'}])
        for view in (result['human_view'], result['xmind_markdown']):
            for text in ('Use the account returned by ACCOUNT-1', 'account is active',
                         '角色：editor', '初始状态：signed in', 'Prepare the same account',
                         '所需状态：active', '业务对象：same account', '有效性：until account disabled',
                         '复用策略：shared within validity', '失效处理：ask for approval'):
                self.assertIn(text, view)
            for technical in ('"source"', '"lines"', '"id"', 'INTERNAL-ASSERTION-ONLY', '{', '}'):
                self.assertNotIn(technical, view)
        self.assertEqual(result['human_view'].count('Use the account returned by ACCOUNT-1'), 4)
        self.assertEqual(result['xmind_markdown'].count('Use the account returned by ACCOUNT-1'), 4)
        self.assertEqual(result['batch']['cases'][0], case)

    def test_complete_related_cases_and_baseline_are_read_only_and_scope_is_separate(self):
        full = catalog()
        original = copy.deepcopy(full)
        result = build_scoped_review(full, 'scope-1', [
            {'case_id': 'EDIT', 'action': 'reuse', 'reason': 'Reuse prepared note'},
            {'case_id': 'LINK', 'action': 'related', 'reason': 'Review account dependency'}],
            approved_validation_scope=['EDIT'])
        batch = result['batch']
        self.assertEqual(full, original)
        self.assertEqual([c['id'] for c in batch['cases']], ['EDIT', 'LINK'])
        self.assertEqual(batch['cases'][1], original['cases'][1])
        self.assertEqual(batch['initial_copy_baseline']['cases'], original['cases'][:2])
        self.assertEqual(batch['approved_validation_scope'], ['EDIT'])
        self.assertEqual(result['changes'], [])
        self.assertIn('OTHER', batch['initial_copy_baseline']['not_displayed_case_ids'])
        self.assertIn('未展示不表示删除', result['review_notes'])
        self.assertIn('Accounts', result['xmind_markdown'])

    def test_actual_fields_and_data_changes_only_with_complete_new_and_modified_cases(self):
        full = catalog()
        for group in ('steps', 'common_preconditions'):
            for step in full['cases'][1][group]:
                step['data_refs'] = []
        changed = copy.deepcopy(full['cases'][0])
        changed['title'] = 'Revised synthetic title'
        added = copy.deepcopy(changed)
        added['id'] = 'NEW'
        data = copy.deepcopy(full['data'])
        data[0]['value'] = 'Revised synthetic value'
        result = build_scoped_review(full, 'scope-2', [
            {'case_id': 'EDIT', 'action': 'modify', 'reason': 'Confirmed title rule',
             'basis': 'synthetic decision', 'coverage_impact': 'CHECK-1 revised'},
            {'case_id': 'LINK', 'action': 'deactivate', 'reason': 'Retired account flow'},
            {'case_id': 'NEW', 'action': 'add', 'reason': 'New boundary'}],
            candidates=[changed, added], candidate_data=data)
        self.assertEqual(result['batch']['cases'][0], changed)
        self.assertEqual(result['batch']['initial_copy_baseline']['cases'], [changed, full['cases'][1], added])
        self.assertEqual(result['batch']['initial_copy_baseline']['catalog_cases'], full['cases'][:2])
        self.assertEqual(result['batch']['initial_copy_baseline']['catalog_data'], full['data'])
        self.assertEqual(result['batch']['initial_copy_baseline']['data'], data)
        changes = result['changes']
        self.assertEqual([(d['case_id'], d['field']) for d in changes],
                         [('EDIT', '/title'), ('EDIT', '/data/' + data[0]['id'] + '/value')])
        self.assertEqual(changes[0]['before'], full['cases'][0]['title'])
        self.assertEqual(changes[0]['after'], 'Revised synthetic title')
        self.assertEqual(changes[0]['coverage_impact'], 'CHECK-1 revised')
        self.assertEqual(result['xmind_markdown'].count('- Revised synthetic title\n'), 2)  # Same-name independent candidates both remain visible.
        self.assertIn('Revised synthetic value', result['xmind_markdown'])

    def test_shared_data_change_cannot_silently_modify_a_related_record(self):
        full = catalog()
        data = copy.deepcopy(full['data'])
        data[0]['value'] = 'Changed value'
        with self.assertRaises(ValueError):
            build_scoped_review(full, 'scope-3', [
                {'case_id': 'EDIT', 'action': 'modify', 'reason': 'Change data',
                 'basis': 'synthetic decision', 'coverage_impact': 'CHECK-1'},
                {'case_id': 'LINK', 'action': 'related', 'reason': 'Display only'}],
                candidates=[full['cases'][0]], candidate_data=data)

    def test_missing_fields_are_pending_and_special_groups_and_references_remain_visible(self):
        full = catalog()
        case = full['cases'][0]
        case.pop('priority_basis')
        case['special_preconditions'] = [copy.deepcopy(case['steps'][0])]
        case['special_preconditions'][0]['operation'] = 'Bind synthetic account'
        case['special_postconditions'] = [copy.deepcopy(case['steps'][0])]
        case['special_postconditions'][0]['operation'] = 'Restore synthetic account'
        case['dependencies'] = [{'case_id': 'LINK', 'module_path': full['cases'][1]['module_path'],
                                 'purpose': 'Same synthetic object', 'required_state': 'active'}]
        result = build_scoped_review(full, 'scope-4', [
            {'case_id': 'EDIT', 'action': 'reuse', 'reason': 'Necessary preparation'}])
        self.assertNotIn('priority_basis', result['batch']['cases'][0])
        self.assertTrue(any(q['field'] == 'priority_basis' for q in result['batch']['questions']))
        for text in ('特殊前置操作', '特殊后置操作', 'Bind synthetic account',
                     'Restore synthetic account', 'Same synthetic object', '关联用例（名称待核对）', '待核对'):
            self.assertIn(text, result['xmind_markdown'])
        self.assertIn('| 序号 | 操作 | 参数/数据 | 预期结果 |', result['human_view'])

    def test_rejects_candidate_masquerading_as_full_and_ambiguous_scope(self):
        for broken in [dict(catalog(), kind='candidate'),
                       dict(catalog(), content_version='')]:
            with self.assertRaises(ValueError):
                build_scoped_review(broken, 'scope-5', [])
        with self.assertRaises(ValueError):
            build_scoped_review(catalog(), 'scope-5', [
                {'case_id': 'EDIT', 'action': 'reuse', 'reason': 'Reuse'}], ['UNKNOWN'])  # Undisplayed known IDs remain approved; unknown IDs remain invalid.

    def test_file_entry_preserves_full_input_and_writes_distinct_review_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'full.json'
            source.write_text(json.dumps(catalog()), encoding='utf-8')
            before = source.read_bytes()
            request = root / 'request.json'
            request.write_text(json.dumps({'batch_id': 'CLI-synthetic', 'selection': [
                {'case_id': 'EDIT', 'action': 'reuse', 'reason': 'Review supplied full record'}],
                'approved_validation_scope': []}), encoding='utf-8')
            command = [sys.executable, '-B', str(Path(__file__).with_name('scoped_review.py')),
                       '--catalog', str(source), '--request', str(request), '--output-dir', str(root / 'review')]
            done = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(done.returncode, 0, done.stderr)
            self.assertEqual(source.read_bytes(), before)
            files = {p.name for p in (root / 'review').iterdir()}
            self.assertEqual(files, {'candidate.json', 'initial-copy-baseline.json', 'changes.json',
                                     'human-view.md', 'xmind.md', 'review-notes.md'})
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)


if __name__ == '__main__':
    unittest.main()
