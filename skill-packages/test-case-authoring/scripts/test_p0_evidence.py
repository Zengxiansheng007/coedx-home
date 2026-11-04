"""Synthetic reports and simulated decisions; never business execution evidence."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_scoped_review import catalog
from p0_evidence import approve_p0_scope, check_extension


def fixture():
    full = catalog()
    for case in full['cases']:
        case.update(rule_status='formal', review_status='approved')
        for group in ('steps', 'common_preconditions'):
            for step in case[group]:
                for field in ('expected', 'verification'):
                    if not step[field]:
                        step[field] = [{'text': 'SIMULATED: action completed', 'source': 'inference'}]
    baseline = approve_p0_scope(full, 'synthetic-round', ['EDIT', 'LINK'],
                               'SIMULATED: validate both P0 cases')
    reports = []
    for case in full['cases'][:2]:
        checks = baseline['cases'][case['id']]['required_checks']
        text = 'SIMULATED: saved synthetic note visible'
        reports.append({'kind': 'p0_execution_report', 'synthetic': True,
            'report_ref': 'synthetic://' + case['id'], 'round_id': 'synthetic-round',
            'case_id': case['id'], 'module_path': case['module_path'],
            'semantic_version': case['semantic_version'], 'data_version': case['data_version'],
            'tested_version': 'synthetic-app-v1', 'purpose': 'functional_validation',
            'result': 'passed', 'evidence': [{'check_id': check, 'ref': 'synthetic://proof',
                'content': text, 'sha256': hashlib.sha256(text.encode()).hexdigest()}
                for check in checks]})
    request = {'manual_start': {'actual_reply': 'SIMULATED: start P1/P2',
                               'baseline_id': baseline['id']},
               'tested_version': 'synthetic-app-v1',
               'gap_review': {'completed': True, 'basis': ['synthetic://manual-points'],
                              'summary': 'SIMULATED: checked all supplied points'}}
    return full, baseline, reports, request


class P0EvidenceTests(unittest.TestCase):
    def test_matching_full_scope_and_manual_request_allow_only_simulated_extension(self):
        full, baseline, reports, request = fixture()
        before = copy.deepcopy((full, baseline, reports, request))
        result = check_extension(full, baseline, reports, request, mode='simulation')
        self.assertTrue(result['can_extend'])
        self.assertEqual([r['execution_status'] for r in result['cases']], ['passed', 'passed'])
        self.assertEqual(result['evidence_nature'], 'simulated')
        self.assertEqual((full, baseline, reports, request), before)

    def test_report_matrix_and_preparation_reuse_never_imply_pass(self):
        full, baseline, reports, request = fixture()
        for change, expected in [({'result': 'failed'}, 'failed'),
                                 ({'result': 'not_run'}, 'not_run'),
                                 ({'semantic_version': 'old'}, 'pending_check'),
                                 ({'data_version': 'old'}, 'pending_check'),
                                 ({'tested_version': 'old-app'}, 'pending_check'),
                                 ({'round_id': 'old-round'}, 'pending_check'),
                                 ({'module_path': ['wrong-module']}, 'pending_check'),
                                 ({'evidence': []}, 'pending_check'),
                                 ({'purpose': 'preparation_reuse'}, 'pending_check'),
                                 ({'case_id': 'same-title-wrong-id'}, 'pending_check')]:
            with self.subTest(change=change):
                changed = copy.deepcopy(reports)
                changed[0].update(change)
                result = check_extension(full, baseline, changed, request, mode='simulation')
                self.assertEqual(result['cases'][0]['execution_status'], expected)
                self.assertFalse(result['can_extend'])
        result = check_extension(full, baseline, [], request, mode='simulation')
        self.assertEqual([r['execution_status'] for r in result['cases']], ['pending_check'] * 2)

    def test_attachment_tampering_and_partial_checks_are_pending(self):
        full, baseline, reports, request = fixture()
        reports[0]['evidence'][0]['content'] = 'changed after hashing'
        result = check_extension(full, baseline, reports, request, mode='simulation')
        self.assertEqual(result['cases'][0]['execution_status'], 'pending_check')

    def test_unreviewed_p0_and_changed_catalog_source_do_not_enable_extension(self):
        full, baseline, reports, request = fixture()
        full['cases'][0]['review_status'] = 'pending'
        result = check_extension(full, baseline, reports, request, mode='simulation')
        self.assertFalse(result['can_extend'])
        full, baseline, reports, request = fixture()
        full['source_ref'] = 'synthetic://different-project'
        result = check_extension(full, baseline, reports, request, mode='simulation')
        self.assertFalse(result['can_extend'])
        full, baseline, reports, request = fixture()
        reports[0]['evidence'] = reports[0]['evidence'][:1]
        result = check_extension(full, baseline, reports, request, mode='simulation')
        self.assertEqual(result['cases'][0]['execution_status'], 'pending_check')

    def test_real_use_rejects_synthetic_reports_even_with_matching_results(self):
        full, baseline, reports, request = fixture()
        with self.assertRaises(ValueError):
            check_extension(full, baseline, reports, request)

    def test_relabeling_sample_or_dropping_required_checks_cannot_open_real_gate(self):
        full, baseline, reports, request = fixture()
        for report in reports:
            report['synthetic'] = False
        with self.assertRaises(ValueError):
            check_extension(full, baseline, reports, request)
        full['cases'][0]['steps'][0]['verification'] = []
        with self.assertRaises(ValueError):
            approve_p0_scope(full, 'synthetic-round', ['EDIT'], 'SIMULATED: approve')

    def test_changed_content_and_duplicate_reports_remain_pending(self):
        full, baseline, reports, request = fixture()
        full['data'][0]['value'] = 'different input even if version was not updated'
        result = check_extension(full, baseline, reports, request, mode='simulation')
        self.assertEqual(result['cases'][0]['execution_status'], 'pending_check')
        full, baseline, reports, request = fixture()
        reports.append(copy.deepcopy(reports[0]))
        result = check_extension(full, baseline, reports, request, mode='simulation')
        self.assertEqual(result['cases'][0]['execution_status'], 'pending_check')

    def test_public_file_entry_writes_new_read_only_check_without_execution(self):
        full, baseline, reports, request = fixture()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, value in [('catalog', full), ('baseline', baseline),
                                ('reports', reports), ('request', request)]:
                (root / (name + '.json')).write_text(json.dumps(value), encoding='utf-8')
            before = (root / 'catalog.json').read_bytes()
            command = [sys.executable, '-B', str(Path(__file__).with_name('p0_evidence.py')),
                       '--catalog', str(root / 'catalog.json'), '--baseline', str(root / 'baseline.json'),
                       '--reports', str(root / 'reports.json'), '--request', str(root / 'request.json'),
                       '--mode', 'simulation', '--output-dir', str(root / 'result')]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            checked = json.loads((root / 'result/extension-check.json').read_text(encoding='utf-8'))
            self.assertTrue(checked['can_extend'])
            self.assertEqual(checked['evidence_nature'], 'simulated')
            self.assertEqual((root / 'catalog.json').read_bytes(), before)
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)

    def test_partial_merge_cannot_shrink_whole_scope_and_manual_is_independent(self):
        full, baseline, reports, request = fixture()
        full['cases'][0]['merge_status'] = 'merged'
        result = check_extension(full, baseline, reports[:1], request, mode='simulation')
        self.assertEqual(len(result['cases']), 2)
        self.assertFalse(result['can_extend'])
        request.pop('manual_start')
        result = check_extension(full, baseline, reports, request, mode='simulation')
        self.assertIn('manual_start_required', result['blockers'])
        self.assertEqual([r['execution_status'] for r in result['cases']], ['passed'] * 2)

    def test_provisional_continue_is_distinct_and_preserves_conditions(self):
        full, _, _, _ = fixture()
        full['cases'][0]['rule_status'] = 'provisional'
        full['cases'][0]['rule_decisions'] = [{'reply': {'decision': 'provisional',
                                                     'product_check': 'Confirm save limit'}}]
        baseline = approve_p0_scope(full, 'synthetic-round', ['EDIT', 'LINK'], 'SIMULATED: approve')
        _, _, reports, request = fixture()
        request['manual_start']['baseline_id'] = baseline['id']
        result = check_extension(full, baseline, reports, request, mode='simulation')
        self.assertIn('provisional_continue_required', result['blockers'])
        request['provisional_continue'] = {'continue': True, 'baseline_id': baseline['id'],
                                           'actual_reply': 'SIMULATED: proceed pending product'}
        result = check_extension(full, baseline, reports, request, mode='simulation')
        self.assertTrue(result['can_extend'])
        self.assertIn('Confirm save limit', str(result['cases'][0]['provisional_conditions']))

    def test_gap_routes_require_user_decision_and_supplement_returns_to_p0_flow(self):
        full, baseline, reports, request = fixture()
        gap = {'id': 'G1', 'proposal': 'Missing save permission core path',
               'basis': ['synthetic://manual-points#permission']}
        request['gaps'] = [gap]
        result = check_extension(full, baseline, reports, request, mode='simulation')
        self.assertFalse(result['can_extend'])
        for route, allowed in [('supplement_p0', False), ('extension', True), ('exclude', True)]:
            gap['decision'] = {'route': route, 'actual_reply': 'SIMULATED: ' + route}
            result = check_extension(full, baseline, reports, request, mode='simulation')
            self.assertEqual(result['can_extend'], allowed)
            self.assertEqual(result['gaps'][0]['decision'], gap['decision'])
            if route == 'supplement_p0':
                self.assertEqual(result['gaps'][0]['next_step'], 'clarify_review_ui_test_validate_user_merge')


if __name__ == '__main__':
    unittest.main()
