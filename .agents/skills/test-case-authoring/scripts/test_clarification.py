"""Synthetic batch and explicitly simulated user replies; no business execution."""
import copy
import unittest

from authoring import build_batch
from test_authoring import sample
from clarification import start_grill, respond, summarize, apply_summary, review, record_actions


def fixture():
    recording, draft = sample()
    batch = build_batch(recording, draft)['batch']
    questions = []
    for i, original in enumerate(batch['questions']):
        questions.append(dict(original, id=f'Q{i+1}', depends_on=[],
            options=['Use supplied proposal', 'Supply another rule', 'Defer'],
            recommendation='Supply another rule', rationale='Observation alone is not a business rule',
            example='A save message alone does not prove recipient delivery',
            affected_checks=['CHECK-1'], target_paths=[]))
    questions.append(dict(questions[0], id='FOLLOW', depends_on=['Q1'], field='follow-up'))
    return batch, questions


class ClarificationTests(unittest.TestCase):
    def test_partial_simulated_reply_keeps_unanswered_and_dependency_for_later_round(self):
        batch, questions = fixture()
        session = start_grill(batch, questions)
        self.assertEqual([q['id'] for q in session['round_questions']], ['Q1', 'Q2'])
        self.assertIn('推荐：', session['chat'])  # Public chat now uses Chinese labels.
        self.assertIn('recipient delivery', session['chat'])
        reply = {'question_id': 'Q1', 'decision': 'formal', 'actual_reply': '[SIMULATED] use proposed rule', 'updates': []}
        updated = respond(session, [reply])
        self.assertEqual(updated['batch'], batch)
        self.assertEqual([q['id'] for q in updated['round_questions']], ['Q2'])
        self.assertEqual(updated['questions'][1]['history'], [])
        updated = respond(updated, [dict(reply, question_id='Q2')])
        self.assertEqual([q['id'] for q in updated['round_questions']], ['FOLLOW'])

    def test_three_way_history_summary_gates_atomic_update_and_blocks_only_affected_case(self):
        batch, questions = fixture()
        another = copy.deepcopy(batch['cases'][0])
        another['id'] = 'INDEPENDENT-P0'
        batch['cases'].append(another)
        questions[1]['case_id'] = another['id']
        # The original data question still belongs to the first case.
        batch['questions'][1]['case_id'] = another['id']
        path = ['cases', 1, 'title']
        questions[1]['target_paths'] = [path]
        session = start_grill(batch, questions)
        session = respond(session, [dict(question_id='Q1', decision='deferred',
            actual_reply='[SIMULATED] ask product next week', updates=[])])
        session = respond(session, [dict(question_id='Q2', decision='formal',
            actual_reply='[SIMULATED] use Draft title', updates=[{'path': path, 'value': 'Save draft'}])])
        session = respond(session, [dict(question_id='Q2', decision='provisional',
            actual_reply='[SIMULATED] use Tentative title until product confirms',
            product_check='Confirm title with product before next release',
            updates=[{'path': path, 'value': 'Save tentative draft'}])])
        self.assertEqual(session['batch'], batch)
        self.assertEqual(len(session['questions'][1]['history']), 2)
        summary = summarize(session)
        self.assertEqual(summary['summary']['blocked_questions'], ['FOLLOW'])
        with self.assertRaises(ValueError):
            apply_summary(summary, {'confirmed': True, 'summary_id': 'stale', 'actual_reply': '[SIMULATED] agree'})
        result = apply_summary(summary, {'confirmed': True, 'summary_id': summary['summary']['id'],
            'actual_reply': '[SIMULATED] summary matches my understanding'})
        self.assertEqual(result['batch']['cases'][0]['rule_status'], 'deferred')
        self.assertEqual(result['batch']['cases'][1]['rule_status'], 'provisional')
        self.assertEqual(result['batch']['cases'][1]['title'], 'Save tentative draft')
        self.assertEqual(result['batch']['cases'][1]['review_status'], 'pending')
        self.assertEqual(result['batch']['clarification_history'][-1]['confirmation']['actual_reply'],
                         '[SIMULATED] summary matches my understanding')
        for view in ('human_view', 'xmind_markdown'):
            self.assertIn('Save tentative draft', result[view])
            self.assertIn('INDEPENDENT-P0', result[view])
            self.assertIn(result['batch']['content_version'], result[view])
            self.assertIn('Confirm title with product before next release', result[view])
        self.assertNotEqual(result['batch']['content_version'], batch['content_version'])

    def test_unanswered_or_stale_summary_never_revises_candidates(self):
        batch, questions = fixture()
        session = start_grill(batch, questions)
        with self.assertRaises(ValueError):
            summarize(session)
        replies = [dict(question_id=q['id'], decision='formal',
                        actual_reply='[SIMULATED] rule confirmed', updates=[]) for q in questions[:2]]
        session = respond(session, replies)
        session = respond(session, [dict(replies[0], question_id='FOLLOW')])
        session = summarize(session)
        confirmation = dict(confirmed=True, summary_id=session['summary']['id'], actual_reply='[SIMULATED] agree')
        changed = respond(session, [dict(replies[0], actual_reply='[SIMULATED] changed rule')])
        with self.assertRaises(ValueError):
            apply_summary(changed, confirmation)
        self.assertIn('FOLLOW', [q['id'] for q in changed['round_questions']])

    def test_final_review_and_explicit_actions_are_separate_and_new_content_requires_review(self):
        batch, questions = fixture()
        session = start_grill(batch, questions)
        actual = '[SIMULATED] rule confirmed; no execution or merge requested'
        session = respond(session, [dict(question_id=q['id'], decision='formal', actual_reply=actual, updates=[]) for q in questions[:2]])
        session = respond(session, [dict(question_id='FOLLOW', decision='formal', actual_reply=actual, updates=[])])
        session = summarize(session)
        session = apply_summary(session, dict(confirmed=True, summary_id=session['summary']['id'], actual_reply='[SIMULATED] summary correct'))
        self.assertEqual(session['batch']['cases'][0]['review_status'], 'pending')
        final = dict(approved=True, content_version=session['batch']['content_version'],
                     case_ids=['DEMO-P0-001'], actual_reply='[SIMULATED] full case approved')
        result = review(session, final)
        case = result['batch']['cases'][0]
        self.assertEqual(case['review_status'], 'approved')
        self.assertEqual(case['merge_status'], 'not_merged')
        self.assertEqual(case['execution_status'], 'not_run')
        self.assertEqual(result['actions'], [])
        self.assertIn('ui-test', result['next_step'])
        self.assertIn('approved', result['human_view'])
        actions = [dict(kind=kind, content_version=final['content_version'], case_ids=final['case_ids'],
                        actual_reply='[SIMULATED] start execution and merge requested explicitly')
                   for kind in ('execution_start', 'merge_instruction')]
        result = record_actions(result, actions)
        self.assertEqual(len(result['actions']), 2)
        self.assertEqual(result['batch']['cases'][0]['merge_status'], 'not_merged')
        # Changed answers invalidate descendants, and changed content loses final approval.
        path = ['cases', 0, 'title']
        result['questions'][1]['target_paths'] = [path]
        result = respond(result, [dict(question_id='Q2', decision='formal',
            actual_reply='[SIMULATED] revise title', updates=[dict(path=path, value='New title')])])
        result = summarize(result)
        result = apply_summary(result, dict(confirmed=True, summary_id=result['summary']['id'], actual_reply='[SIMULATED] corrected summary agrees'))
        self.assertEqual(result['batch']['cases'][0]['review_status'], 'pending')
        self.assertTrue(result['batch']['cases'][0]['review_history'])
        with self.assertRaises(ValueError):
            review(result, final)

    def test_review_requires_summary_and_cannot_approve_deferred_content(self):
        batch, questions = fixture()
        session = start_grill(batch, questions)
        final = dict(approved=True, content_version=batch['content_version'], case_ids=['DEMO-P0-001'], actual_reply='[SIMULATED] approve')
        with self.assertRaises(ValueError):
            review(session, final)

        session = respond(session, [dict(question_id=q['id'], decision='deferred', actual_reply='[SIMULATED] defer', updates=[]) for q in questions[:2]])
        session = summarize(session)
        session = apply_summary(session, dict(confirmed=True, summary_id=session['summary']['id'], actual_reply='[SIMULATED] agree to defer'))
        final['content_version'] = session['batch']['content_version']
        with self.assertRaises(ValueError):
            review(session, final)

    def test_declared_business_field_updates_are_generic_but_workflow_and_secrets_are_protected(self):
        batch, questions = fixture()
        fields = [(['cases', 0, 'context', 'role'], [{'text': 'approver', 'source': 'user_decision'}]),
                  (['cases', 0, 'steps', 0, 'verification'], [{'text': 'Read entered title', 'source': 'user_decision'}]),
                  (['data', 0, 'validity'], 'Until release closes')]
        questions[0]['target_paths'] = [p for p, _ in fields]
        session = start_grill(batch, questions)
        answer = dict(question_id='Q1', decision='formal', actual_reply='[SIMULATED] accept business changes',
                      updates=[dict(path=p, value=v) for p, v in fields])
        session = respond(session, [answer, dict(answer, question_id='Q2', updates=[])])
        session = respond(session, [dict(answer, question_id='FOLLOW', updates=[])])
        session = summarize(session)
        result = apply_summary(session, dict(confirmed=True, summary_id=session['summary']['id'], actual_reply='[SIMULATED] agree'))
        self.assertIn('approver', result['human_view'])
        self.assertIn('Read entered title', result['xmind_markdown'])
        self.assertIn('Until release closes', result['human_view'])
        # Explicit same-content answers remain reusable in a later invocation.
        resumed = start_grill(result['batch'], result['questions'])
        self.assertEqual(resumed['round_questions'], [])
        invalid = copy.deepcopy(session)
        invalid['questions'][0]['history'][-1]['updates'] = [dict(path=['cases', 0, 'execution_status'], value='passed')]
        invalid = summarize(invalid)
        with self.assertRaises(ValueError):
            apply_summary(invalid, dict(confirmed=True, summary_id=invalid['summary']['id'], actual_reply='[SIMULATED] agree'))
        with self.assertRaisesRegex(ValueError, 'credential'):
            respond(resumed, [dict(answer, actual_reply='Bearer synthetic-private-value')])


if __name__ == '__main__':
    unittest.main()
