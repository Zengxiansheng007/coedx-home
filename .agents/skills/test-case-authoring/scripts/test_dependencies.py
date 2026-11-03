"""Synthetic dependency cases and simulated user decisions; no business execution."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_p0_evidence import fixture as evidence_fixture
from dependencies import review_dependencies
from p0_evidence import check_extension
from authoring import render_batch
from clarification import start_grill, summarize, apply_summary, review


def fixture():
    full, _, _, _ = evidence_fixture()
    proposal = {'id': 'DEP-1', 'current_case_id': 'EDIT', 'case_id': 'LINK',
        'module_path': full['cases'][1]['module_path'], 'direction': 'pre',
        'basis': ['synthetic://manual-points#link'], 'purpose': 'prepare linked object',
        'required_state': 'enabled', 'inputs': {'record': 'sample'},
        'outputs': {'object_id': 'linked record'}, 'object_binding': {'object_id': 'D1'},
        'data_refs': ['D1'], 'complete_case': True, 'final_state_matches': True,
        'applicability_basis': ['synthetic://complete-case-review'],
        'decision': {'include': True, 'actual_reply': 'SIMULATED: include complete LINK'}}
    full['data'][0].update(reuse_policy='long_term', object_ref='object_id',
        validity='check enabled before use', invalidation_action='ask_user',
        identity_ref='synthetic://data/object-id', validity_check='lookup exact object_id',
        policy_decision={'actual_reply': 'SIMULATED: long term after check'})
    # Use the real data ID from the existing public fixture.
    proposal['data_refs'] = [full['data'][0]['id']]
    proposal['object_binding'] = {'object_id': full['data'][0]['id']}
    return full, proposal


class DependencyTests(unittest.TestCase):
    def test_complete_independent_reference_and_conditions_are_in_both_views(self):
        full, proposal = fixture()
        before = copy.deepcopy(full)
        result = review_dependencies(full, 'synthetic-deps', ['EDIT'], [proposal])
        self.assertFalse(result['blockers'])
        self.assertEqual(full, before)
        current = result['batch']['cases'][0]
        self.assertEqual(current['dependencies'][0]['case_id'], 'LINK')
        self.assertEqual(result['batch']['cases'][1], full['cases'][1])
        self.assertEqual(result['batch']['approved_validation_scope'], [])
        for view in ('human_view', 'xmind_markdown'):
            for word in ('LINK', 'prepare linked object', 'enabled', 'object_id', 'long_term'):
                self.assertIn(word, result[view])
        self.assertNotIn('特殊后置操作', result['human_view'])

    def test_scope_is_user_decision_and_inapplicable_final_state_suggests_split(self):
        full, p = fixture()
        for decision, expected in [({}, 'scope_decision_required'),
                ({'include': False, 'actual_reply': 'SIMULATED: exclude'}, 'excluded_by_user')]:
            p['decision'] = decision
            r = review_dependencies(full, 'batch', ['EDIT'], [p])
            self.assertEqual(r['findings'][0]['status'], expected)
            self.assertNotIn('dependencies', r['batch']['cases'][0])
        full, p = fixture()
        p['final_state_matches'] = False
        r = review_dependencies(full, 'batch', ['EDIT'], [p])
        self.assertEqual(r['findings'][0]['status'], 'propose_add_or_split')
        p['step_range'] = [0, 1]
        with self.assertRaises(ValueError):
            review_dependencies(full, 'batch', ['EDIT'], [p])

    def test_missing_and_unmanaged_scripts_return_to_both_P0_inputs(self):
        for variant in ('missing', 'unmanaged', 'managed'):
            full, p = fixture()
            if variant == 'missing':
                p['case_id'] = 'NEW'
            else:
                p['script_asset'] = dict(managed_by='ui-test' if variant == 'managed' else 'other',
                    applicable=True, ref='synthetic://script', basis=['synthetic://asset-review'])
            r = review_dependencies(full, 'batch', ['EDIT'], [p])
            if variant == 'managed':
                self.assertFalse(r['blockers'])
            else:
                self.assertEqual(r['findings'][0]['routes'], ['recording', 'handwritten'])
                self.assertTrue(r['blockers'])

    def test_postconditions_bind_same_object_and_have_one_data_node_per_step(self):
        full, p = fixture()
        p['direction'] = 'post'
        r = review_dependencies(full, 'batch', ['EDIT'], [p])
        self.assertIn('特殊后置操作', r['human_view'])
        case = r['batch']['cases'][0]
        self.assertEqual(case['special_postconditions'][0]['dependency']['object_binding'], p['object_binding'])
        tree = r['xmind_markdown'].split('特殊后置操作')[1]
        self.assertEqual(tree.split('\n- Example')[0].count('- 参数/数据'), 1)
        self.assertIn('- 预期', tree)
        p['object_binding'] = {'object_id': 'DIFFERENT-NOT-IN-DATA'}
        with self.assertRaises(ValueError):
            review_dependencies(full, 'batch', ['EDIT'], [p])

    def test_three_policies_and_invalidation_require_actual_user_decisions(self):
        for policy in ('long_term', 'time_limited', 'exclusive'):
            full, p = fixture()
            d = full['data'][0]
            d['reuse_policy'] = policy
            if policy == 'time_limited':
                d.update(valid_until='synthetic-end', downstream_window='synthetic-run', covers_downstream_window=True)
            if policy == 'exclusive':
                d.update(exclusive_case_id='EDIT', subsequent_use={'choice': 'reuse_if_valid', 'actual_reply': 'SIMULATED: same case may reuse'})
            d.update(invalidation_action='rebuild_complete_precondition', rebuild_decision={'actual_reply': 'SIMULATED: allow complete prepare before run'})
            r = review_dependencies(full, 'batch', ['EDIT'], [p])
            self.assertFalse(r['blockers'])
            for view in ('human_view', 'xmind_markdown'):
                self.assertIn(policy, r[view])
                self.assertIn('rebuild_complete_precondition', r[view])
            if policy == 'exclusive':
                d.pop('subsequent_use')
            elif policy == 'time_limited':
                d['covers_downstream_window'] = False
            else:
                d.pop('rebuild_decision')
            r = review_dependencies(full, 'batch', ['EDIT'], [p])
            self.assertTrue(r['blockers'])

    def test_reused_preparation_cannot_pass_functional_scope(self):
        full, baseline, reports, request = evidence_fixture()
        reports[1]['purpose'] = 'preparation_reuse'
        r = check_extension(full, baseline, reports, request, mode='simulation')
        self.assertFalse(r['can_extend'])
        self.assertEqual(r['cases'][1]['execution_status'], 'pending_check')
        self.assertEqual(len(r['cases']), 2)

    def test_rerender_retains_P0_special_references_and_incomplete_target_is_blocked(self):
        full, p = fixture()
        p['direction'] = 'post'
        r = review_dependencies(full, 'batch', ['EDIT'], [p])
        self.assertEqual(r['batch']['stage'], 'P0')
        rendered = render_batch(r['batch'])
        self.assertIn('特殊后置操作', rendered['human_view'])
        self.assertIn('prepare linked object', rendered['human_view'])
        full['cases'][1]['context']['role'] = []
        r = review_dependencies(full, 'batch', ['EDIT'], [p])
        self.assertTrue(r['blockers'])

    def test_common_clarification_and_final_review_preserve_references(self):
        full, p = fixture()
        p['direction'] = 'post'
        r = review_dependencies(full, 'batch', ['EDIT'], [p])
        session = summarize(start_grill(r['batch'], []))
        session = apply_summary(session, {'confirmed': True, 'summary_id': session['summary']['id'],
                                         'actual_reply': 'SIMULATED: supplied complete conditions confirmed'})
        session = review(session, {'approved': True, 'content_version': session['batch']['content_version'],
                                  'case_ids': ['EDIT'], 'actual_reply': 'SIMULATED: final complete case approved'})
        self.assertIn('特殊后置操作', session['human_view'])
        self.assertIn('object_id', session['xmind_markdown'])
        self.assertEqual(session['batch']['cases'][0]['merge_status'], 'not_merged')

    def test_public_file_entry_and_source_immutability(self):
        full, p = fixture()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'catalog.json').write_text(json.dumps(full), encoding='utf-8')
            (root / 'request.json').write_text(json.dumps(dict(batch_id='synthetic', current_case_ids=['EDIT'], proposals=[p])), encoding='utf-8')
            before = (root / 'catalog.json').read_bytes()
            command = [sys.executable, '-B', str(Path(__file__).with_name('dependencies.py')),
                '--catalog', str(root / 'catalog.json'), '--request', str(root / 'request.json'), '--output-dir', str(root / 'output')]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((root / 'catalog.json').read_bytes(), before)
            self.assertTrue((root / 'output/xmind.md').is_file())
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)


if __name__ == '__main__':
    unittest.main()
