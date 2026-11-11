"""Synthetic expansion at the public batch seam; no business execution."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_p0_evidence import fixture
from p0_evidence import approve_p0_scope
from extension import build_extension, render_extension
from clarification import start_grill, respond, summarize, apply_summary, review
from scoped_review import build_scoped_review


def expansion():
    full, baseline, reports, entry = fixture()
    for item in full['data']:
        item.update(object_ref='synthetic note', validity='during isolated run',
                    reuse_policy='shared while valid', invalidation_action='ask user')
    baseline = approve_p0_scope(full, 'synthetic-round', ['EDIT', 'LINK'], 'SIMULATED: validate both P0 cases')
    entry['manual_start']['baseline_id'] = baseline['id']
    cases = []
    for identity in ('LOW', 'HIGH'):
        case = copy.deepcopy(full['cases'][0])
        case.update(id=identity, title='模拟下界' if identity == 'LOW' else '模拟上界', priority='P1',  # Business titles are independent of stable codes.
                    priority_basis='SIMULATED: high impact, corruption risk, rare use',
                    priority_factors={'importance': 'high', 'risk': 'corruption', 'frequency': 'rare'},
                    data_preparation='SIMULATED: use isolated prepared note')
        cases.append(case)
    design = {'batch_id': 'synthetic-extension', 'manual_points': [
        {'id': 'M1', 'basis': 'synthetic://manual#1', 'checks': [
            {'id': 'LOW-CHECK', 'description': 'lower bound', 'aspects': ['save', 'display'], 'boundary_group': 'length', 'input': 'lower'},
            {'id': 'HIGH-CHECK', 'description': 'upper bound', 'aspects': ['save'], 'boundary_group': 'length', 'input': 'upper'},
            {'id': 'GAP', 'description': 'permission', 'aspects': ['deny']}]}],
        'coverage': [
            {'check_id': 'LOW-CHECK', 'links': [{'case_id': 'LOW', 'aspects': ['save']}], 'pending': 'SIMULATED: display path unknown'},
            {'check_id': 'HIGH-CHECK', 'links': [{'case_id': 'HIGH', 'aspects': ['save']}]},
            {'check_id': 'GAP', 'links': [], 'pending': 'SIMULATED: permission behavior unknown'}],
        'candidates': cases, 'candidate_data': [], 'ui_gaps': [], 'ai_suggestions': [],
        'uncovered_combinations': ['SIMULATED: role x bounds not selected']}
    return full, baseline, reports, entry, design


class ExtensionTests(unittest.TestCase):
    def test_partial_check_never_marks_whole_manual_point_complete(self):
        args = expansion()
        before = copy.deepcopy(args)
        result = build_extension(*args, mode='simulation')
        self.assertEqual([c['status'] for c in result['coverage']['checks']], ['partial', 'complete', 'gap'])
        self.assertEqual(result['coverage']['points'][0]['status'], 'partial')
        self.assertIn('display', result['coverage_notes'])
        self.assertEqual(args, before)
        self.assertEqual([c['review_status'] for c in result['batch']['cases']], ['pending', 'pending'])
        self.assertEqual([c['execution_status'] for c in result['batch']['cases']], ['not_run', 'not_run'])
        self.assertEqual(len(result['batch']['questions']), 2)

    def test_gate_recomputed_and_manual_checks_cannot_disappear(self):
        args = list(expansion())
        args[2] = []
        with self.assertRaises(ValueError):
            build_extension(*args, mode='simulation')
        args = list(expansion())
        args[4]['coverage'].pop()
        with self.assertRaises(ValueError):
            build_extension(*args, mode='simulation')

    def test_boundaries_are_independent_and_dispositions_keep_actual_user_basis(self):
        args = list(expansion())
        args[4]['coverage'][1]['links'][0]['case_id'] = 'LOW'
        with self.assertRaises(ValueError):
            build_extension(*args, mode='simulation')
        for route in ('deferred', 'excluded'):
            args = list(expansion())
            args[4]['coverage'][2]['decision'] = {'route': route, 'basis': 'synthetic://reply#1',
                'actual_reply': 'SIMULATED: permission ' + route}
            result = build_extension(*args, mode='simulation')
            self.assertEqual(result['coverage']['checks'][2]['status'], route)
            self.assertIn('SIMULATED: permission ' + route, result['coverage_notes'])
            args[4]['coverage'][2]['decision'].pop('actual_reply')
            with self.assertRaises(ValueError):
                build_extension(*args, mode='simulation')

    def test_ai_extra_combinations_and_ui_gaps_need_user_decisions(self):
        args = list(expansion())
        args[4]['ai_suggestions'] = [{'id': 'AI1', 'proposal': 'SIMULATED: editor x upper',
            'basis': 'synthetic://risk', 'risk': 'wrong permissions', 'uncovered_scope': 'other roles'}]
        with self.assertRaises(ValueError):
            build_extension(*args, mode='simulation')
        args[4]['ai_suggestions'][0]['decision'] = {'route': 'exclude', 'actual_reply': 'SIMULATED: exclude extra pair'}
        args[4]['ui_gaps'] = [{'description': 'SIMULATED: no permission dialog observed',
            'basis': 'synthetic://ui#missing', 'recommendation': 'supply exploration', 'case_ids': ['LOW']}]
        with self.assertRaises(ValueError):
            build_extension(*args, mode='simulation')
        args[4]['ui_gaps'][0]['decision'] = {'route': 'explore_first', 'actual_reply': 'SIMULATED: explore first'}
        with self.assertRaises(ValueError):
            build_extension(*args, mode='simulation')
        args[4]['ui_gaps'][0]['decision'] = {'route': 'write_first', 'actual_reply': 'SIMULATED: write first using known path'}
        result = build_extension(*args, mode='simulation')
        self.assertEqual(len(result['coverage']['checks']), 3)
        self.assertEqual(len(result['coverage']['ai_suggestions']), 1)

    def test_one_batch_grill_priority_confirmation_then_same_version_scoped_review(self):
        result = build_extension(*expansion(), mode='simulation')
        self.assertNotIn('human_view', result)
        questions = []
        for i, doubt in enumerate(result['batch']['questions']):
            questions.append(dict(doubt, id='Q' + str(i), depends_on=[],
                options=['P1', 'P2'], recommendation='P1', rationale='SIMULATED: corruption risk',
                example='SIMULATED: high boundary', affected_checks=['LOW-CHECK', 'HIGH-CHECK'],
                target_paths=doubt['suggested_target_paths']))
        session = start_grill(result['batch'], questions)
        self.assertEqual(len(session['round_questions']), 2)
        session = respond(session, [{'question_id': 'Q0', 'decision': 'formal',
            'actual_reply': 'SIMULATED: lower should be P2',
            'updates': [{'path': ['cases', 0, 'priority'], 'value': 'P2'}]}])
        self.assertEqual(session['batch']['cases'][0]['priority'], 'P1')
        self.assertEqual(len(session['round_questions']), 1)
        session = respond(session, [{'question_id': 'Q1', 'decision': 'formal',
            'actual_reply': 'SIMULATED: upper P1 confirmed', 'updates': []}])
        session = summarize(session)
        session = apply_summary(session, {'confirmed': True, 'summary_id': session['summary']['id'],
                                         'actual_reply': 'SIMULATED: summary correct'})
        self.assertEqual(session['batch']['cases'][0]['priority'], 'P2')
        self.assertEqual(session['batch']['cases'][0]['rule_status'], 'formal')
        self.assertEqual(session['batch']['cases'][0]['review_status'], 'pending')
        rendered = render_extension(session['batch'], case_id='LOW')
        self.assertIn('模拟下界', rendered['human_view'])
        self.assertNotIn('# HIGH ', rendered['human_view'])
        self.assertEqual(rendered['coverage']['content_version'], session['batch']['content_version'])
        self.assertIn(session['batch']['content_version'], rendered['xmind_markdown'])
        session = review(session, {'approved': True, 'content_version': session['batch']['content_version'],
            'case_ids': ['LOW', 'HIGH'], 'actual_reply': 'SIMULATED: final review approved'})
        self.assertIn('user-started authoring merge', session['next_step'])
        self.assertTrue(all(c['review_status'] == 'approved' for c in session['batch']['cases']))
        self.assertTrue(all(c['execution_status'] == 'not_run' for c in session['batch']['cases']))

    def test_public_file_entry_emits_scope_not_full_human_view_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            args = expansion()
            envelope = dict(zip(('catalog', 'baseline', 'reports', 'entry_request', 'design'), args))
            source = root / 'input.json'
            source.write_text(json.dumps(envelope), encoding='utf-8')
            before = source.read_bytes()
            command = [sys.executable, '-B', str(Path(__file__).with_name('extension.py')),
                '--input', str(source), '--mode', 'simulation', '--output-dir', str(root / 'result')]
            done = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(done.returncode, 0, done.stderr)
            self.assertEqual(source.read_bytes(), before)
            self.assertFalse((root / 'result/human-view.md').exists())
            self.assertIn('partial', (root / 'result/review-notes.md').read_text(encoding='utf-8'))
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)

    def test_incomplete_business_claims_and_duplicate_manual_points_are_rejected(self):
        for mutation in ('claim', 'point'):
            args = list(expansion())
            if mutation == 'claim':
                args[4]['candidates'][0]['steps'][0]['verification'] = [{'text': '', 'source': 'inference'}]
            else:
                extra = copy.deepcopy(args[4]['manual_points'][0])
                extra['checks'] = [{'id': 'EXTRA', 'description': 'another check', 'aspects': ['a']}]
                args[4]['manual_points'].append(extra)
                args[4]['coverage'].append({'check_id': 'EXTRA', 'links': [], 'pending': 'SIMULATED: unknown'})
            with self.assertRaises(ValueError):
                build_extension(*args, mode='simulation')

    def test_zero_is_a_valid_boundary_input(self):
        args = list(expansion())
        args[4]['manual_points'][0]['checks'][0]['input'] = 0
        self.assertEqual(build_extension(*args, mode='simulation')['coverage']['checks'][0]['status'], 'partial')

    def test_initial_copy_baseline_matches_public_scope_version(self):
        args = expansion()
        result = build_extension(*args, mode='simulation')
        batch = result['batch']
        expected = build_scoped_review(args[0], batch['id'], batch['selection'],
            candidates=batch['cases'], candidate_data=batch['data'])['batch']['initial_copy_baseline']
        self.assertEqual(batch['initial_copy_baseline'], expected)

    def test_accepted_feedback_recomputes_extension_coverage_at_new_version(self):
        from feedback import prepare_feedback, apply_feedback
        original = build_extension(*expansion(), mode='simulation')
        pending = prepare_feedback(original['batch'], 'chat', actual_reply='SIMULATED: revise save expectation',
            changes=[{'collection': 'cases', 'id': 'LOW', 'path': ['steps', 1, 'expected', 0, 'text'],
                      'value': 'SIMULATED: revised expected save result'}])
        replies = [{'question_id': q['id'], 'decision': 'formal',
                    'actual_reply': 'SIMULATED: confirm this proposed change'}
                   for q in pending['grill']['round_questions']]
        pending['grill'] = summarize(respond(pending['grill'], replies))
        updated = apply_feedback(pending, {'confirmed': True, 'summary_id': pending['grill']['summary']['id'],
            'actual_reply': 'SIMULATED: summary accurate'})
        result = render_extension(updated['batch'])
        self.assertNotEqual(result['coverage']['content_version'], original['coverage']['content_version'])
        self.assertIn('SIMULATED: revised expected save result', result['coverage_notes'])
        self.assertEqual(result['batch']['initial_copy_baseline'], original['batch']['initial_copy_baseline'])
        self.assertEqual([p['status'] for p in result['coverage']['points']], ['partial'])
        self.assertEqual(result['batch']['cases'][0]['review_status'], 'pending')


if __name__ == '__main__':
    unittest.main()
