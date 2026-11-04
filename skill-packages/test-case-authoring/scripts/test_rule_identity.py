"""Synthetic independent rules sharing one field; public authoring boundaries."""
import copy
import unittest

from test_p0_evidence import fixture
from scoped_review import build_scoped_review
from clarification import start_grill, respond, summarize, apply_summary
from feedback import prepare_feedback, apply_feedback
from test_feedback import confirm


def question(qid, rule=None):
    q = dict(id=qid, case_id='EDIT', field='steps/0/expected', reason='SIMULATED ' + qid,
             affected_checks=[qid], target_paths=[], depends_on=[], options=['formal', 'provisional'],
             recommendation='provisional', rationale='SIMULATED independent rules', example='SIMULATED')
    if rule:
        q['rule_id'] = rule
    return q


def apply(batch, questions, decisions):
    replies = [dict(question_id=q['id'], decision=d, actual_reply='SIMULATED ' + q['id'],
                    **({'product_check': 'SIMULATED confirm ' + q['id']} if d == 'provisional' else {}))
               for q, d in zip(questions, decisions)]
    session = summarize(respond(start_grill(batch, questions), replies))
    return apply_summary(session, dict(confirmed=True, actual_reply='SIMULATED agree exact summary',
                                      summary_id=session['summary']['id']))['batch']


class RuleIdentityTests(unittest.TestCase):
    def test_enriched_known_rule_can_be_formally_resolved_without_repeating_identity(self):
        for other_pending in (False, True):
            full, _, _, _ = fixture()
            batch = build_scoped_review(full, 'synthetic-known-rule', [
                dict(case_id='EDIT', action='reuse', reason='SIMULATED named confirmation')])['batch']
            qs = [question('VALIDATE', 'VALIDATION')]
            if other_pending:
                qs.append(question('MESSAGE', 'MESSAGE'))
            updated = apply(batch, qs, ['provisional'] * len(qs))
            history = copy.deepcopy(updated['cases'][0]['rule_decisions'])
            pending = prepare_feedback(updated, 'chat', actual_reply='SIMULATED validation finally formal; title corrected',
                changes=[dict(collection='cases', id='EDIT', path=['title'], value='Validated save')])
            existing = [q for q in pending['grill']['round_questions'] if q['id'].startswith('existing-')]
            self.assertEqual({q.get('rule_id') for q in existing}, {'VALIDATION', 'MESSAGE'} if other_pending else {'VALIDATION'})
            origins = {q['rule_id']: q['feedback_origin'] for q in existing}
            replies = [dict(question_id=q['id'], decision='provisional' if q.get('rule_id') == 'MESSAGE' else 'formal',
                actual_reply='SIMULATED message still pending' if q.get('rule_id') == 'MESSAGE' else 'SIMULATED formal confirmation',
                **({'product_check': 'SIMULATED message condition still pending'} if q.get('rule_id') == 'MESSAGE' else {}))
                for q in pending['grill']['round_questions']]
            pending['grill'] = summarize(respond(pending['grill'], replies))
            self.assertEqual({d.get('rule_id') for d in pending['grill']['summary']['decisions'] if d.get('rule_id')}, set(origins))
            result = apply_feedback(pending, dict(confirmed=True, actual_reply='SIMULATED agree current summary',
                summary_id=pending['grill']['summary']['id']))['batch']
            case = result['cases'][0]
            self.assertEqual(case['rule_status'], 'provisional' if other_pending else 'formal')
            self.assertEqual(case['rule_decisions'], history)
            self.assertEqual({d['rule_id']: d['reply']['decision'] for d in case['active_rule_decisions'] if d.get('rule_id')},
                             {'VALIDATION': 'formal', 'MESSAGE': 'provisional'} if other_pending else {'VALIDATION': 'formal'})
            self.assertEqual({q['rule_id']: q['feedback_origin'] for q in result['questions']}, origins)

    def test_automatic_question_ids_do_not_alias_different_source_doubts(self):
        full, _, _, _ = fixture()
        def scoped(round_id, field, reason):
            batch = build_scoped_review(full, round_id, [
                dict(case_id='EDIT', action='reuse', reason='SIMULATED source scope')])['batch']
            batch['questions'] = [dict(case_id='EDIT', field=field, reason=reason)]
            return batch
        first = prepare_feedback(scoped('first-source', 'steps/0/expected', 'SIMULATED validation uncertain'),
            'chat', actual_reply='SIMULATED title B and provisional validation', changes=[
                dict(collection='cases', id='EDIT', path=['title'], value='B')])
        q = next(q for q in first['grill']['round_questions'] if q['id'].startswith('existing-'))
        replies = [dict(question_id=item['id'], decision='provisional' if item['id'] == q['id'] else 'formal',
            actual_reply='SIMULATED reply', **({'product_check': 'SIMULATED validation pending'}
                                             if item['id'] == q['id'] else {}))
                   for item in first['grill']['round_questions']]
        first['grill'] = summarize(respond(first['grill'], replies))
        first = apply_feedback(first, dict(confirmed=True, actual_reply='SIMULATED agree',
                                          summary_id=first['grill']['summary']['id']))
        full['cases'][0] = first['batch']['cases'][0]
        second = prepare_feedback(scoped('second-source', 'steps/0/expected', 'SIMULATED success message uncertain'),
            'chat', actual_reply='SIMULATED title C and formal message only', changes=[
                dict(collection='cases', id='EDIT', path=['title'], value='C')])
        new_q = next(q for q in second['grill']['round_questions'] if q['id'].startswith('existing-'))
        self.assertNotEqual(q['id'], new_q['id'])
        result = confirm(second)['batch']['cases'][0]
        self.assertEqual(result['rule_status'], 'provisional')
        self.assertIn('validation pending', str(result['active_rule_decisions']))

    def test_only_explicit_same_rule_revision_resolves_that_condition(self):
        full, _, _, _ = fixture()
        batch = build_scoped_review(full, 'synthetic-explicit-rule', [
            dict(case_id='EDIT', action='reuse', reason='SIMULATED rules')])['batch']
        qs = [question('VALIDATE', 'VALIDATION'), question('MESSAGE', 'MESSAGE')]
        updated = apply(batch, qs, ['provisional', 'formal'])
        # A new question for the same explicitly identified rule can resolve it.
        resolved = apply(updated, [question('FINAL-VALIDATE', 'VALIDATION')], ['formal'])
        self.assertEqual(resolved['cases'][0]['rule_status'], 'formal')
        self.assertEqual(len(resolved['cases'][0]['active_rule_decisions']), 2)
        self.assertEqual(resolved['cases'][0]['rule_decisions'], updated['cases'][0]['rule_decisions'])
        # Feedback must explicitly bind the rule too; changing a field alone
        # is not evidence that every condition in that field was resolved.
        result = confirm(prepare_feedback(updated, 'chat', actual_reply='SIMULATED product confirms VALIDATION only',
            changes=[dict(collection='cases', id='EDIT', path=['title'], value='Validated save',
                          rule_id='VALIDATION')]))['batch']
        self.assertEqual(result['cases'][0]['rule_status'], 'formal')
        self.assertEqual({d['rule_id']: d['reply']['decision'] for d in result['cases'][0]['active_rule_decisions']
                          if d.get('rule_id')}, {'VALIDATION': 'formal', 'MESSAGE': 'formal'})

    def test_product_subset_and_ambiguous_legacy_conditions_are_preserved(self):
        from p0_evidence import approve_p0_scope
        from product_reconciliation import reconcile_product, prepare_product_change
        for legacy in (False, True):
            full, _, reports, request = fixture()
            c = full['cases'][0]
            c.update(rule_status='provisional', rule_refs=['VALIDATION'])
            c['rule_decisions'] = [dict(field='steps/0/expected', reply=dict(decision='provisional',
                actual_reply='SIMULATED ' + name, product_check='SIMULATED product confirm ' + name),
                **({} if legacy else dict(rule_id=name))) for name in ('VALIDATION', 'MESSAGE')]
            historical = copy.deepcopy(c['rule_decisions'])
            baseline = approve_p0_scope(full, 'synthetic-round', ['EDIT', 'LINK'], 'SIMULATED scope')
            conclusion = dict(rule_id='VALIDATION', relation='changed', actual_reply='SIMULATED validation only final',
                              source_ref='synthetic://product', tested_version=request['tested_version'])
            rec = reconcile_product(full, baseline, reports, conclusion, mode='simulation')
            result = confirm(prepare_product_change(full, rec, [dict(collection='cases', id='EDIT',
                path=['title'], value='Validated title')]))
            case = result['batch']['cases'][0]
            self.assertEqual(case['rule_status'], 'provisional')
            remaining = [d['reply']['product_check'] for d in case['active_rule_decisions']
                         if d['reply']['decision'] == 'provisional']
            self.assertEqual(remaining, ['SIMULATED product confirm VALIDATION', 'SIMULATED product confirm MESSAGE']
                             if legacy else ['SIMULATED product confirm MESSAGE'])
            self.assertEqual(case['rule_decisions'], historical)
            self.assertIn('product confirm MESSAGE', result['human_view'])

    def test_same_field_independent_questions_and_rules_remain_active(self):
        for named in (False, True):
            full, _, _, _ = fixture()
            batch = build_scoped_review(full, 'synthetic-rule-identity', [
                dict(case_id='EDIT', action='reuse', reason='SIMULATED rules')])['batch']
            qs = [question('SAVE-VALIDATION', 'VALIDATION' if named else None),
                  question('SAVE-MESSAGE', 'MESSAGE' if named else None)]
            updated = apply(batch, qs, ['provisional', 'formal'])
            self.assertEqual(updated['cases'][0]['rule_status'], 'provisional')
            self.assertEqual(len(updated['cases'][0]['active_rule_decisions']), 2)
            historical = copy.deepcopy(updated['cases'][0]['rule_decisions'])
            pending = prepare_feedback(updated, 'chat', actual_reply='SIMULATED title only; validation remains provisional', changes=[
                dict(collection='cases', id='EDIT', path=['title'], value='Corrected title')])
            # Explicitly retain the unresolved validation when answering its
            # known rule question, rather than blanket-confirming every rule.
            replies = [dict(question_id=q['id'], decision='provisional' if q['reason'] == 'SIMULATED SAVE-VALIDATION' else 'formal',
                actual_reply='SIMULATED validation remains provisional' if q['reason'] == 'SIMULATED SAVE-VALIDATION' else 'SIMULATED formal',
                **({'product_check': 'SIMULATED confirm SAVE-VALIDATION'} if q['reason'] == 'SIMULATED SAVE-VALIDATION' else {}))
                for q in pending['grill']['round_questions']]
            pending['grill'] = summarize(respond(pending['grill'], replies))
            result = apply_feedback(pending, dict(confirmed=True, actual_reply='SIMULATED agree title and retained condition',
                summary_id=pending['grill']['summary']['id']))['batch']
            self.assertEqual(result['cases'][0]['rule_status'], 'provisional')
            self.assertEqual(result['cases'][0]['rule_decisions'], historical)
            self.assertIn('confirm SAVE-VALIDATION', str(result['cases'][0]['active_rule_decisions']))
            resolved = apply(updated, [qs[0]], ['formal'])
            self.assertEqual(resolved['cases'][0]['rule_status'], 'formal')
            self.assertEqual(len(resolved['cases'][0]['active_rule_decisions']), 2)


if __name__ == '__main__':
    unittest.main()
