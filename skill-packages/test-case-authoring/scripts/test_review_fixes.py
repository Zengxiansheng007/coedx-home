"""Synthetic regression examples from final review, through public APIs."""
import copy
import unittest

from test_p0_evidence import fixture
from test_feedback import scope, confirm
from scoped_review import build_scoped_review
from clarification import start_grill, summarize, apply_summary, respond
from feedback import prepare_feedback, review_feedback
from p0_evidence import approve_p0_scope, check_extension


class ReviewFixTests(unittest.TestCase):
    def test_explicit_product_change_resolves_only_its_rule_and_preserves_history(self):
        from test_product_reconciliation import sample
        from product_reconciliation import reconcile_product, prepare_product_change
        for unrelated in (False, True):
            full, _, reports, conclusion = sample()
            case = full['cases'][0]
            case['rule_decisions'][0].update(rule_id='RULE-SAVE', question_id='save-policy',
                                             field='steps/0/expected')
            if unrelated:
                case['rule_refs'].append('OTHER-RULE')
                case['rule_decisions'].append(dict(rule_id='OTHER-RULE', field='context/role',
                    reply=dict(decision='provisional', actual_reply='SIMULATED tentative role',
                               product_check='SIMULATED product must confirm role')))
            historical = copy.deepcopy(case['rule_decisions'])
            baseline = approve_p0_scope(full, 'synthetic-round', ['EDIT', 'LINK'], 'SIMULATED scope')
            conclusion['relation'] = 'changed'
            reconciliation = reconcile_product(full, baseline, reports, conclusion, mode='simulation')
            pending = prepare_product_change(full, reconciliation, [dict(collection='cases', id='EDIT',
                path=['title'], value='SIMULATED revised save rule')])
            result = confirm(pending)
            updated = result['batch']['cases'][0]
            self.assertEqual(updated['rule_status'], 'provisional' if unrelated else 'formal')
            self.assertEqual(updated['rule_decisions'], historical)
            self.assertEqual(reconciliation['historical_results']['reports'], reports)
            self.assertEqual([d['reply']['product_check'] for d in updated['active_rule_decisions']
                              if d['reply']['decision'] == 'provisional'],
                             ['SIMULATED product must confirm role'] if unrelated else [])

    def test_unrelated_formal_answer_preserves_active_product_condition_in_both_paths_and_gate(self):
        full, _, reports, request = fixture()
        case = full['cases'][0]
        case['rule_status'] = 'provisional'
        case['rule_decisions'] = [dict(question_id='save-policy', case_id='EDIT',
            field='steps/0/expected', reply=dict(decision='provisional', actual_reply='SIMULATED tentative save',
                product_check='SIMULATED product must confirm save policy'))]
        batch = build_scoped_review(full, 'synthetic-rules', [
            dict(case_id='EDIT', action='reuse', reason='SIMULATED correct title')])['batch']
        pending = prepare_feedback(batch, 'chat', actual_reply='SIMULATED title only', changes=[
            dict(collection='cases', id='EDIT', path=['title'], value='Corrected title')])
        feedback_result = confirm(pending)
        q = dict(id='title-rule', case_id='EDIT', field='title', reason='SIMULATED title check',
            affected_checks=['CHECK-1'], target_paths=[], depends_on=[], options=['formal', 'provisional'],
            recommendation='formal', rationale='SIMULATED explicit title', example='SIMULATED title')
        session = summarize(respond(start_grill(batch, [q]), [dict(question_id='title-rule',
            decision='formal', actual_reply='SIMULATED title confirmed')]))
        common_result = apply_summary(session, dict(confirmed=True, actual_reply='SIMULATED agree',
                                                   summary_id=session['summary']['id']))
        for result in (feedback_result, common_result):
            updated = result['batch']['cases'][0]
            self.assertEqual(updated['rule_status'], 'provisional')
            self.assertIn('product must confirm save policy', str(updated['active_rule_decisions']))
            self.assertEqual(updated['rule_decisions'], case['rule_decisions'])
        reviewed = review_feedback(feedback_result, dict(approved=True, case_ids=['EDIT'],
            content_version=feedback_result['batch']['content_version'], actual_reply='SIMULATED whole case review'))
        full['cases'][0] = reviewed['batch']['cases'][0]
        baseline = approve_p0_scope(full, 'synthetic-round', ['EDIT', 'LINK'], 'SIMULATED whole P0')
        for report in reports:
            c = next(c for c in full['cases'] if c['id'] == report['case_id'])
            report.update({k: c[k] for k in ('semantic_version', 'data_version')})
        request['manual_start']['baseline_id'] = baseline['id']
        gate = check_extension(full, baseline, reports, request, mode='simulation')
        self.assertFalse(gate['can_extend'])
        self.assertEqual(gate['blockers'], ['provisional_continue_required'])
        request['provisional_continue'] = {'continue': True, 'actual_reply': 'SIMULATED continue', 'baseline_id': baseline['id']}
        self.assertTrue(check_extension(full, baseline, reports, request, mode='simulation')['can_extend'])

    def test_current_markdown_and_bound_chat_allow_second_edit_but_stale_conflicts_do_not(self):
        original = scope()
        first = confirm(prepare_feedback(original['batch'], 'chat', actual_reply='SIMULATED A to B',
            changes=[dict(collection='cases', id='EDIT', path=['title'], value='B')]))
        for channel in ('markdown', 'chat'):
            kwargs = (dict(markdown=first['xmind_markdown'].replace('- EDIT B', '- EDIT C'))
                      if channel == 'markdown' else dict(changes=[dict(collection='cases', id='EDIT',
                          path=['title'], value='C', before='B')], source_version=first['batch']['content_version']))
            pending = prepare_feedback(first['batch'], channel, actual_reply='SIMULATED current B to C', **kwargs)
            second = confirm(pending)['batch']
            self.assertEqual(second['cases'][0]['title'], 'C')
            self.assertEqual(second['initial_copy_baseline'], original['batch']['initial_copy_baseline'])
            self.assertEqual(second['feedback_history'][0]['changes'][0]['value'], 'B')
            self.assertEqual(second['cases'][0]['review_status'], 'pending')
        stale = original['xmind_markdown'].replace(original['batch']['cases'][0]['title'], 'C')
        with self.assertRaises(ValueError):
            prepare_feedback(first['batch'], 'markdown', markdown=stale, actual_reply='SIMULATED stale conflict')
        for extra in ({}, dict(source_version='stale')):
            with self.assertRaises(ValueError):
                prepare_feedback(first['batch'], 'chat', actual_reply='SIMULATED unbound overwrite',
                    changes=[dict(collection='cases', id='EDIT', path=['title'], value='C')], **extra)

    def test_nested_catalog_path_survives_common_clarification(self):
        full, _, _, _ = fixture()
        full['cases'][0]['module_path'].append('Nested')
        batch = build_scoped_review(full, 'synthetic-deep', [
            dict(case_id='EDIT', action='reuse', reason='SIMULATED nested review')])['batch']
        self.assertEqual(batch['questions'], [])
        session = summarize(start_grill(batch, []))
        result = apply_summary(session, dict(confirmed=True, actual_reply='SIMULATED agree',
                                            summary_id=session['summary']['id']))
        self.assertEqual(result['batch']['cases'][0]['module_path'],
                         ['Example', 'Workspace', 'Web', 'Notes', 'Save', 'Nested'])
        changed = confirm(prepare_feedback(result['batch'], 'chat', actual_reply='SIMULATED nested title edit',
            changes=[dict(collection='cases', id='EDIT', path=['title'], value='Nested title')]))
        self.assertEqual(changed['batch']['cases'][0]['module_path'],
                         ['Example', 'Workspace', 'Web', 'Notes', 'Save', 'Nested'])


if __name__ == '__main__':
    unittest.main()
