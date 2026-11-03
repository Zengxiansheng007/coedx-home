"""Synthetic feedback through the public batch and real Markdown boundaries."""
import unittest

from scoped_review import build_scoped_review
from test_scoped_review import catalog
from feedback import prepare_feedback, apply_feedback
from clarification import respond, summarize


def scope():
    full = catalog()
    for case in full['cases']:
        case['rule_status'] = 'formal'
        case['review_status'] = 'approved'
        case['final_review'] = {'synthetic': True}
    result = build_scoped_review(full, 'synthetic-feedback', [
        {'case_id': 'EDIT', 'action': 'reuse', 'reason': 'Synthetic review'},
        {'case_id': 'LINK', 'action': 'related', 'reason': 'Synthetic dependency'}])
    result['batch']['coverage'] = [{'check_id': 'CHECK-1', 'case_ids': ['EDIT'],
        'expected_summary': 'old', 'verification_summary': 'old', 'status': 'designed'}]
    return result


def confirm(pending):
    session = pending['grill']
    replies = [{'question_id': q['id'], 'decision': 'formal',
        'actual_reply': 'SIMULATED: confirm proposed business rule'}
        for q in session['round_questions']]
    pending['grill'] = summarize(respond(session, replies))
    return apply_feedback(pending, {'confirmed': True, 'actual_reply': 'SIMULATED: agreed',
        'summary_id': pending['grill']['summary']['id']})


class FeedbackTests(unittest.TestCase):
    def test_displayed_extension_before_final_review_accepts_only_business_scalar_edits(self):
        from test_extension import expansion
        from extension import build_extension, render_extension
        from clarification import start_grill, apply_summary, review
        import copy
        result = build_extension(*expansion(), mode='simulation')
        questions = [dict(q, id='R2-' + str(i), depends_on=[], options=['P1', 'P2'],
            recommendation='P1', rationale='SIMULATED risk', example='SIMULATED boundary',
            affected_checks=['LOW-CHECK', 'HIGH-CHECK'], target_paths=q['suggested_target_paths'])
            for i, q in enumerate(result['batch']['questions'])]
        session = start_grill(result['batch'], questions)
        session = summarize(respond(session, [{'question_id': q['id'], 'decision': 'formal',
            'actual_reply': 'SIMULATED: confirm priority', 'updates': []} for q in questions]))
        session = apply_summary(session, {'confirmed': True, 'summary_id': session['summary']['id'],
                                        'actual_reply': 'SIMULATED: summary agreed'})
        shown = render_extension(session['batch'])['xmind_markdown']
        session = review(session, {'approved': True, 'content_version': session['batch']['content_version'],
            'case_ids': ['LOW', 'HIGH'], 'actual_reply': 'SIMULATED: complete review approved'})
        batch = session['batch']
        frozen = copy.deepcopy(batch)
        old = batch['cases'][0]['steps'][1]['expected'][0]['text']
        for markdown in (shown, render_extension(batch)['xmind_markdown']):
            # This expectation appears in both cases; edit both deliberately.
            edited = markdown.replace(old, 'SIMULATED revised boundary expectation')
            pending = prepare_feedback(batch, 'markdown', markdown=edited,
                actual_reply='SIMULATED: edit expected result in the displayed file')
            self.assertEqual(len(pending['changes']), 2)
            updated = confirm(pending)['batch']
            self.assertEqual(updated['initial_copy_baseline'], frozen['initial_copy_baseline'])
            self.assertEqual(updated['cases'][0]['rule_decisions'], frozen['cases'][0]['rule_decisions'])
            self.assertEqual(updated['cases'][0]['review_history'][-1], frozen['cases'][0]['final_review'])
        self.assertEqual(batch, frozen)
        for broken in (shown + '  - unknown structure\n',
                       shown.replace('参数/数据', 'Unknown label', 1),
                       shown.replace(str(batch['data'][0]['value']), 'SIMULATED mismatching shared data', 1),
                       render_extension(batch)['xmind_markdown'].replace('SIMULATED: complete review approved', 'forged decision')):
            with self.assertRaises(ValueError):
                prepare_feedback(batch, 'markdown', markdown=broken, actual_reply='SIMULATED: malformed file')

    def test_agreed_rule_transitions_from_unconfirmed_provisional_and_deferred(self):
        from feedback import review_feedback
        for prior in ('unconfirmed', 'provisional', 'deferred'):
            for decision in ('formal', 'provisional', 'deferred'):
                with self.subTest(prior=prior, decision=decision):
                    full = catalog()
                    full['cases'][0]['rule_status'] = prior
                    full['cases'][0]['rule_decisions'] = [{'reply': {'decision': 'provisional',
                        'actual_reply': 'SIMULATED: historical provisional authorization',
                        'product_check': 'SIMULATED: historical product condition'}}]
                    batch = build_scoped_review(full, 'synthetic-new-candidate', [
                        {'case_id': 'EDIT', 'action': 'reuse', 'reason': 'Synthetic new candidate'}])['batch']
                    old_title = batch['cases'][0]['title']
                    pending = prepare_feedback(batch, 'chat', actual_reply='SIMULATED: use revised title', changes=[
                        {'collection': 'cases', 'id': 'EDIT', 'path': ['title'], 'value': 'New confirmed title'}])
                    replies = [{'question_id': q['id'], 'decision': decision,
                                'actual_reply': 'SIMULATED: ' + decision,
                                **({'product_check': 'SIMULATED: verify revised product rule'} if decision == 'provisional' else {})}
                               for q in pending['grill']['round_questions']]
                    pending['grill'] = respond(pending['grill'], replies)
                    self.assertEqual(pending['grill']['batch']['cases'][0]['rule_status'], prior)
                    self.assertEqual(pending['grill']['batch']['cases'][0]['title'], old_title)
                    pending['grill'] = summarize(pending['grill'])
                    result = apply_feedback(pending, {'confirmed': True, 'actual_reply': 'SIMULATED: agree to summary',
                        'summary_id': pending['grill']['summary']['id']})
                    case = result['batch']['cases'][0]
                    self.assertEqual(case['rule_status'], decision)
                    self.assertEqual(case['title'], old_title if decision == 'deferred' else 'New confirmed title')
                    self.assertEqual(case['rule_decisions'][0]['reply']['product_check'], 'SIMULATED: historical product condition')
                    final = {'approved': True, 'actual_reply': 'SIMULATED: reviewed complete updated case',
                             'case_ids': ['EDIT'], 'content_version': result['batch']['content_version']}
                    if decision == 'deferred':
                        with self.assertRaises(ValueError):
                            review_feedback(result, final)
                    else:
                        self.assertEqual(review_feedback(result, final)['batch']['cases'][0]['review_status'], 'approved')
                    if decision == 'provisional':
                        self.assertTrue(all(d['reply']['product_check'] == 'SIMULATED: verify revised product rule'
                                            for d in case['feedback_rule_history']))

    def test_new_final_review_is_required_against_updated_complete_content(self):
        from feedback import review_feedback
        batch = scope()['batch']
        result = confirm(prepare_feedback(batch, 'chat', actual_reply='SIMULATED: revise title', changes=[
            {'collection': 'cases', 'id': 'EDIT', 'path': ['title'], 'value': 'Revised title'}]))
        with self.assertRaises(ValueError):
            review_feedback(result, {'approved': True, 'actual_reply': 'SIMULATED: reviewed',
                'case_ids': ['EDIT'], 'content_version': batch['content_version']})
        reviewed = review_feedback(result, {'approved': True, 'actual_reply': 'SIMULATED: reviewed complete case',
            'case_ids': ['EDIT'], 'content_version': result['batch']['content_version']})
        self.assertEqual(reviewed['batch']['cases'][0]['review_status'], 'approved')
        self.assertEqual(reviewed['batch']['cases'][0]['merge_status'], batch['cases'][0]['merge_status'])
        self.assertEqual(reviewed['batch']['cases'][0]['execution_status'], batch['cases'][0]['execution_status'])
    def test_summary_is_bound_to_exact_proposal_and_deletion_reply(self):
        batch = scope()['batch']
        pending = prepare_feedback(batch, 'chat', actual_reply='SIMULATED: edit title', changes=[
            {'collection': 'cases', 'id': 'EDIT', 'path': ['title'], 'value': 'Proposed title'}])
        pending['changes'][0]['value'] = 'Unagreed title'
        with self.assertRaises(ValueError):
            confirm(pending)

    def test_initial_candidate_baseline_and_later_accepted_edits_are_distinct(self):
        original = scope()
        pending = prepare_feedback(original['batch'], 'chat', actual_reply='SIMULATED: title update', changes=[
            {'collection': 'cases', 'id': 'EDIT', 'path': ['title'], 'value': 'Accepted title'}])
        updated_result = confirm(pending)
        updated = updated_result['batch']
        changed = original['xmind_markdown'].replace('初始状态：signed in', '初始状态：authorized')
        next_pending = prepare_feedback(updated, 'markdown', markdown=changed,
            actual_reply='SIMULATED: change initial state only')
        newer = confirm(next_pending)['batch']
        self.assertEqual(newer['cases'][0]['title'], 'Accepted title')
        self.assertEqual(newer['cases'][0]['context']['initial_state'][0]['text'], 'authorized')
        latest_file = updated_result['xmind_markdown'].replace('初始状态：signed in', '初始状态：authorized')
        from_latest = confirm(prepare_feedback(updated, 'markdown', markdown=latest_file,
            actual_reply='SIMULATED: edit latest display'))['batch']
        self.assertEqual(from_latest['cases'][0]['context']['initial_state'][0]['text'], 'authorized')
        conflict = original['xmind_markdown'].replace(original['batch']['cases'][0]['title'], 'Conflicting title')
        with self.assertRaises(ValueError):
            prepare_feedback(updated, 'markdown', markdown=conflict, actual_reply='SIMULATED: conflict')

    def test_ambiguous_deletion_uses_grill_and_explicit_deactivation_retains_history(self):
        original = scope()
        # Delete a whole generated case subtree, including its hierarchy.
        lines = original['xmind_markdown'].splitlines()
        next_header = next(i for i, line in enumerate(lines) if '- LINK ' in line)
        edited = '\n'.join(lines[:3] + lines[next_header - 5:]) + '\n'
        pending = prepare_feedback(original['batch'], 'markdown', markdown=edited,
            actual_reply='SIMULATED: removed a case')
        question = next(q for q in pending['grill']['round_questions'] if q['field'] == 'deletion')
        self.assertEqual(question['options'], ['exclude this round', 'deactivate long term and retain record', 'restore'])
        replies = [{'question_id': q['id'], 'decision': 'formal',
                    'actual_reply': 'SIMULATED: deactivate long term', 'deletion_action': 'deactivate'}
                   for q in pending['grill']['round_questions']]
        pending['grill'] = summarize(respond(pending['grill'], replies))
        result = apply_feedback(pending, {'confirmed': True, 'actual_reply': 'SIMULATED: agreed',
            'summary_id': pending['grill']['summary']['id']})
        case = next(c for c in result['batch']['cases'] if c['id'] == 'EDIT')
        self.assertEqual(case['maintenance_action'], 'deactivate')
        self.assertIn('review_history', case)
        self.assertIn('OTHER', result['batch']['initial_copy_baseline']['not_displayed_case_ids'])
        again = prepare_feedback(result['batch'], 'chat', removed_case_ids=['EDIT'],
            actual_reply='SIMULATED: same deletion')
        self.assertFalse(any(q['field'] == 'deletion' for q in again['grill']['questions']))
        self.assertEqual(again['grill']['round_questions'], [])

    def test_unshown_and_workflow_edits_are_rejected_and_clear_exclusion_not_reasked(self):
        batch = scope()['batch']
        with self.assertRaises(ValueError):
            prepare_feedback(batch, 'chat', removed_case_ids=['OTHER'], actual_reply='SIMULATED: remove')
        with self.assertRaises(ValueError):
            prepare_feedback(batch, 'chat', actual_reply='SIMULATED: approve', changes=[
                {'collection': 'cases', 'id': 'EDIT', 'path': ['review_status'], 'value': 'approved'}])
        pending = prepare_feedback(batch, 'chat', removed_case_ids=['EDIT'], actual_reply='SIMULATED: exclude this round',
            deletion_decisions={'EDIT': {'action': 'exclude', 'actual_reply': 'SIMULATED: exclude this round'}})
        self.assertFalse(any(q['field'] == 'deletion' for q in pending['grill']['questions']))
        result = confirm(pending)
        self.assertEqual(len(result['batch']['cases']), 2)
        self.assertNotIn('EDIT ', result['human_view'])
        self.assertEqual(result['batch']['cases'][0]['feedback_disposition'], 'excluded_this_round')

    def test_chat_and_direct_markdown_edit_update_common_data_and_coverage(self):
        original = scope()
        batch = original['batch']
        value = batch['data'][0]['value']
        changes = [{'collection': 'data', 'id': batch['data'][0]['id'],
                    'path': ['value'], 'value': 'Synthetic revised value'}]
        chat = prepare_feedback(batch, 'chat', changes=changes,
            actual_reply='SIMULATED: use Synthetic revised value')
        edited = original['xmind_markdown'].replace(value, 'Synthetic revised value')
        markdown = prepare_feedback(batch, 'markdown', markdown=edited,
            actual_reply='SIMULATED: edited attached Markdown')
        self.assertEqual(chat['changes'], markdown['changes'])
        self.assertEqual(batch['data'][0]['value'], value)
        for pending in (chat, markdown):
            updated = confirm(pending)
            self.assertEqual(updated['batch']['data'][0]['value'], 'Synthetic revised value')
            self.assertEqual(updated['batch']['cases'][0]['review_status'], 'pending')
            self.assertIn('Synthetic revised value', updated['human_view'])
            self.assertIn('Synthetic revised value', updated['xmind_markdown'])
            self.assertEqual(updated['batch']['coverage'][0]['status'], 'pending_review')
            self.assertNotEqual(updated['batch']['coverage'][0]['expected_summary'], 'old')
            self.assertEqual(updated['batch']['initial_copy_baseline'], batch['initial_copy_baseline'])


if __name__ == '__main__':
    unittest.main()
