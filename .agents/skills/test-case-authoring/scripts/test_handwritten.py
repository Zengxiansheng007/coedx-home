"""Synthetic hand-authored P0 through the shared public conversion/review seam."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import authoring
from clarification import start_grill, respond, summarize, apply_summary, review


def handwritten_sample():
    text = ('Role: editor; state: signed in.\n'
            'Save the notice. Expect Saved visible; verify the saved message.\n')
    draft = dict(batch_id='hand-demo', case_id='DEMO-P0-001', title='Save a notice',
        module_path=['Example team', 'Example product', 'Web', 'Notices', 'Create'],
        context={key: [dict(text=value, source='handwritten', lines=[1, 1])]
                 for key, value in [('role', 'editor'), ('initial_state', 'signed in')]},
        data=[], common_preconditions=[],
        steps=[dict(operation='Save the notice', data_refs=[], source='handwritten', lines=[2, 2],
            expected=[dict(text='Saved message is visible', source='handwritten', lines=[2, 2])],
            verification=[dict(text='Read the visible saved message', source='handwritten', lines=[2, 2])])],
        handwritten_coverage=[dict(lines=[1, 2], reason='Supplied context, action and checks')])
    return text, draft


class HandwrittenTests(unittest.TestCase):
    def test_complete_handwritten_with_or_without_prd_uses_shared_review_and_views(self):
        text, draft = handwritten_sample()
        original = copy.deepcopy(draft)
        for prd in (None, 'Synthetic PRD: editor saves a notice.'):
            result = authoring.build_handwritten_batch(text, draft, prd)
            batch = result['batch']
            self.assertEqual(batch['questions'], [])
            self.assertEqual(batch['sources'][0]['kind'], 'handwritten')
            self.assertEqual(batch['cases'][0]['steps'][0]['basis'], 'material_statement')
            self.assertEqual(batch['cases'][0]['rule_status'], 'unconfirmed')
            session = summarize(start_grill(batch, []))
            session = apply_summary(session, dict(confirmed=True, summary_id=session['summary']['id'],
                actual_reply='[SIMULATED] understanding agrees'))
            reviewed = review(session, dict(approved=True, content_version=session['batch']['content_version'],
                case_ids=['DEMO-P0-001'], actual_reply='[SIMULATED] complete case approved'))
            case = reviewed['batch']['cases'][0]
            self.assertEqual(case['supplied_content_confirmation']['actual_reply'], '[SIMULATED] understanding agrees')
            self.assertEqual((case['rule_status'], case['review_status'], case['merge_status'], case['execution_status']),
                             ('formal', 'approved', 'not_merged', 'not_run'))
            for view in ('human_view', 'xmind_markdown'):
                self.assertIn('Saved message is visible', reviewed[view])
                self.assertIn('Read the visible saved message', reviewed[view])
                self.assertIn(reviewed['batch']['content_version'], reviewed[view])
        self.assertEqual(draft, original)

    def test_explicit_no_preparation_is_preserved_and_answered_doubts_are_not_pending(self):
        text, draft = handwritten_sample()
        draft['common_preconditions_note'] = dict(text='No extra preparation is needed', source='handwritten', lines=[1, 1])
        result = authoring.build_handwritten_batch(text, draft)
        for view in ('human_view', 'xmind_markdown'):
            self.assertIn('No extra preparation is needed', result[view])
            self.assertNotIn('输入未提供，待核对', result[view])
        draft['context']['role'] = []
        batch = authoring.build_handwritten_batch(text, draft)['batch']
        question = dict(batch['questions'][0], id='ROLE', depends_on=[], options=['Editor', 'Defer'],
            recommendation='Editor', rationale='Confirm missing role', example='Editor can save',
            affected_checks=['SAVE'], target_paths=[['cases', 0, 'context', 'role']])
        session = start_grill(batch, [question])
        session = respond(session, [dict(question_id='ROLE', decision='formal', actual_reply='[SIMULATED] editor',
            updates=[dict(path=question['target_paths'][0], value=[dict(text='editor', source='user_decision')])])])
        self.assertIn('缺少依据，待澄清', authoring.render_batch(session['batch'])['human_view'])
        session = summarize(session)
        session = apply_summary(session, dict(confirmed=True, summary_id=session['summary']['id'], actual_reply='[SIMULATED] accurate summary'))
        self.assertEqual(len(session['batch']['questions'][0]['history']), 1)
        for view in ('human_view', 'xmind_markdown'):
            self.assertNotIn('缺少依据，待澄清', session[view])

    def test_equivalent_recording_and_handwriting_have_same_business_review_result(self):
        text, hand = handwritten_sample()
        recorded = copy.deepcopy(hand)
        def sources(value):
            if isinstance(value, dict):
                if value.get('source') == 'handwritten':
                    value['source'] = 'recording'
                for child in value.values():
                    sources(child)
            elif isinstance(value, list):
                for child in value:
                    sources(child)
        sources(recorded)
        recorded['recording_coverage'] = recorded.pop('handwritten_coverage')
        recording = '// editor signed in\nawait saveNotice(); // Saved message visible\n'
        outcomes = []
        for result in (authoring.build_batch(recording, recorded), authoring.build_handwritten_batch(text, hand)):
            self.assertEqual(result['batch']['questions'], [])
            session = start_grill(result['batch'], [])
            with self.assertRaises(ValueError):
                review(session, dict(approved=True, content_version=result['batch']['content_version'],
                    case_ids=['DEMO-P0-001'], actual_reply='[SIMULATED] final review only'))
            session = summarize(session)
            session = apply_summary(session, dict(confirmed=True, summary_id=session['summary']['id'],
                actual_reply='[SIMULATED] supplied content accurately expresses the rules'))
            session = review(session, dict(approved=True, content_version=session['batch']['content_version'],
                case_ids=['DEMO-P0-001'], actual_reply='[SIMULATED] full case approved'))
            # Compare displayed business semantics; versions/provenance properly differ.
            outcomes.append(tuple('\n'.join(line for line in session[v].splitlines() if '版本：' not in line)
                                  for v in ('human_view', 'xmind_markdown')))
        self.assertEqual(outcomes[0], outcomes[1])

    def test_missing_context_and_prd_conflict_ask_only_missing_or_doubtful_fields(self):
        text, draft = handwritten_sample()
        draft['context']['initial_state'] = []
        draft['steps'][0]['expected'].append(dict(text='Notice waits for approval', source='prd', lines=[1, 1]))
        batch = authoring.build_handwritten_batch(text, draft, 'Synthetic PRD: notice waits for approval.')['batch']
        self.assertEqual({q['field'] for q in batch['questions']}, {'initial_state', 'steps/0/expected'})
        conflict = next(q for q in batch['questions'] if q['field'] == 'steps/0/expected')
        self.assertEqual({e['source'] for e in conflict['evidence']}, {'handwritten', 'prd'})
        questions = [dict(q, id=f'Q{i}', depends_on=[], options=['Use supplied P0', 'Use PRD', 'Defer'],
            recommendation='Use PRD', rationale='Confirm conflicting business rules with user',
            example='Saved versus awaiting approval', affected_checks=['SAVE'], target_paths=[])
            for i, q in enumerate(batch['questions'])]
        session = start_grill(batch, questions)
        self.assertEqual(len(session['round_questions']), 2)
        session = respond(session, [dict(question_id=questions[0]['id'], decision='formal',
            actual_reply='[SIMULATED] signed in', updates=[])])
        self.assertEqual(len(session['round_questions']), 1)
        self.assertEqual(session['batch'], batch)
        with self.assertRaises(ValueError):
            summarize(session)

    def test_handwritten_cli_uses_same_outputs_and_rejects_unaccounted_or_unsafe_input(self):
        text, draft = handwritten_sample()
        with self.assertRaisesRegex(ValueError, 'unaccounted'):
            authoring.build_handwritten_batch(text + 'Additional verification\n', draft)
        with self.assertRaisesRegex(ValueError, 'credential'):
            authoring.build_handwritten_batch(text + "password='synthetic-only'\n", draft)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'p0.md').write_text(text, encoding='utf-8')
            (root / 'draft.json').write_text(json.dumps(draft), encoding='utf-8')
            cmd = [sys.executable, '-B', str(Path(__file__).with_name('authoring.py')),
                   '--handwritten', str(root / 'p0.md'), '--interpretation', str(root / 'draft.json'),
                   '--output-dir', str(root / 'output')]
            result = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            batch = json.loads((root / 'output/candidate.json').read_text(encoding='utf-8'))
            self.assertEqual(batch['sources'][0]['kind'], 'handwritten')
            self.assertEqual(batch['cases'][0]['review_status'], 'pending')
            self.assertFalse((root / 'output/human-view.md').exists())  # Human tables stay in chat.
            for name in ('xmind.md',):  # XMind remains the persisted business view.
                self.assertIn('Saved message is visible', (root / 'output' / name).read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
