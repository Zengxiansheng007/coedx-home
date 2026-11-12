"""Public recovery checks using isolated simulated records."""
import json  # Read actual candidate files.
import tempfile  # Keep all fixtures disposable.
import unittest  # Existing regression runner.
from pathlib import Path  # Explicit artifact paths.
from test_clarification import fixture  # Existing public authoring fixture.
from qa_record import start_record, checkpoint_record, resume_record, advance_record  # Public persistence boundary.


class RecoveryTests(unittest.TestCase):  # Verify observable persistence and recovery.
    def test_feedback_reserves_prior_stage_ids_and_keeps_current_answer_history(self):  # Public persisted admission and answer provenance.
        from test_extension import expansion  # Reuse simulated full P0 evidence.
        from extension import build_extension  # Existing phase builder.
        from qa_record import read_record  # Fresh disk replay.
        reply = dict(question_id='Q1', decision='formal', actual_reply='SIMULATED original answer', interpretation='Original rule', source_ref='SIMULATED turn 1')  # Explicit fixture answer.
        original = advance_record(self.qa, 'respond', [reply])  # Reserve the original Q1-A1 anchor.
        args = expansion()  # Existing complete simulated envelope.
        batch = build_extension(*args, mode='simulation')['batch']  # Public extension behavior.
        questions = [dict(q, id='EXT' + str(i), depends_on=[], options=['P1', 'P2'], recommendation='P1', rationale='SIMULATED risk', example='SIMULATED boundary', affected_checks=['LOW-CHECK'], target_paths=q['suggested_target_paths'], evidence=['SIMULATED design'], boundary='Current extension', example_kind='hypothetical') for i, q in enumerate(batch['questions'])]  # Unique presented questions.
        extension = dict(envelope=dict(zip(('catalog', 'baseline', 'reports', 'entry_request', 'design'), args)), mode='simulation', questions=questions, source_ref='SIMULATED extension')  # Actual supplied fixture materials.
        state = advance_record(self.qa, 'start_extension', extension)  # Retain the answered P0 stage.
        collision = dict(id='Q1', case_id='LOW', field='title', reason='SIMULATED title rule?', affected_checks=['LOW-CHECK'], target_paths=[['cases', 0, 'title']], depends_on=[], options=['A', 'B'], recommendation='A', rationale='SIMULATED rationale', boundary='LOW only', evidence=['SIMULATED feedback'], example_kind='hypothetical', example='SIMULATED example')  # Different new rule cannot reuse P0 identity.
        feedback = dict(channel='chat', actual_reply='SIMULATED clarify title', source_ref='SIMULATED turn 2', clear_changes=True, questions=state['questions'] + [collision])  # Preserve existing current-stage questions.
        before = self.qa.read_bytes()  # Failed admission must leave the sole record unchanged.
        with self.assertRaisesRegex(ValueError, 'Question ID already used in an earlier stage'):  # Confirm the precise cross-stage rejection.
            advance_record(self.qa, 'start_feedback', feedback)  # Reproduce the reviewed public entry.
        self.assertEqual(self.qa.read_bytes(), before)  # No duplicate event or anchor is published.
        for action, payload in [('append_questions', [collision]), ('start_extension', dict(extension, questions=questions + [collision]))]:  # Other admission entries keep the same reservation contract.
            with self.subTest(action=action), self.assertRaises(ValueError):  # Both public paths must reject the prior-stage identity.
                advance_record(self.qa, action, payload)  # No private transition inspection.
            self.assertEqual(self.qa.read_bytes(), before)  # Rejections preserve the original MD bytes.
        feedback['questions'][-1] = dict(collision, id='NEW-TITLE')  # A genuinely new ID is admissible.
        state = advance_record(self.qa, 'start_feedback', feedback)  # Preserve current-stage graph and add only this new rule.
        for version in (1, 2, 3):  # Ordinary same-question corrections increment permanent answer versions.
            state = advance_record(self.qa, 'respond', [dict(reply, question_id='NEW-TITLE', actual_reply='SIMULATED correction ' + str(version), source_ref='SIMULATED title turn ' + str(version))])  # Public persistent answer entry.
        history = next(q['history'] for q in state['questions'] if q['id'] == 'NEW-TITLE')  # Read observable history.
        self.assertEqual([h['qa_ref'] for h in history], [str(self.qa.resolve()) + '#NEW-TITLE-A' + str(v) for v in (1, 2, 3)])  # Stable unique answer anchors.
        self.assertEqual(state['prior_stages'][0]['questions'], original['questions'])  # New feedback cannot rewrite old stage answers.
        self.assertEqual(read_record(self.qa), state)  # Fresh replay agrees with the saved result.
        self.assertEqual(self.qa.read_text(encoding='utf-8').count('<a id="Q1-A1"></a>'), 1)  # Original permanent anchor remains unique.

    def test_feedback_reopens_current_question_and_preserves_answer_versions(self):  # Existing same-stage IDs are valid review questions.
        from qa_record import read_record  # Fresh replay is the observable recovery seam.
        from test_feedback import scope  # Feedback requires a scoped candidate baseline.
        batch = scope()['batch']  # Existing simulated eligible review fixture.
        batch['questions'] = []  # Start with a supplied candidate and one explicit rule question.
        question = dict(self.state['questions'][0], case_id='EDIT', field='title', target_paths=[['cases', 0, 'title']], depends_on=[])  # Bind the rule to this candidate's actual identity.
        self.qa = self.root / 'feedback-qa.md'  # Independent simulated task, preserving the setup record.
        start_record(self.qa, 'simulated-current-feedback', batch, [question])  # Public fixture setup with the required scope.
        reply = dict(question_id='Q1', decision='formal', actual_reply='SIMULATED original', interpretation='Original rule', source_ref='SIMULATED turn 1')  # Actual synthetic answer.
        state = advance_record(self.qa, 'respond', [reply])  # Record Q1-A1 before feedback.
        state = advance_record(self.qa, 'start_feedback', dict(channel='chat', actual_reply='SIMULATED premise changed', source_ref='SIMULATED turn 2', clear_changes=True, questions=state['questions'], reopen_question_ids=['Q1']))  # Explicit current identity reuse must stay legal.
        self.assertEqual(state['questions'][0]['history'][0]['qa_ref'], str(self.qa.resolve()) + '#Q1-A1')  # Feedback preserves the saved answer.
        for version in (2, 3):  # Reopened answers continue rather than restart history.
            state = advance_record(self.qa, 'respond', [dict(reply, actual_reply='SIMULATED correction ' + str(version), source_ref='SIMULATED turn ' + str(version + 1))])  # Normal public answer correction.
        self.assertEqual([h['answer_version'] for h in state['questions'][0]['history']], [1, 2, 3])  # Exact source versions survive review.
        self.assertEqual(read_record(self.qa), state)  # The sole MD remains fully replayable.

    def test_extension_reuses_record_and_preserves_prior_questions(self):  # Actual existing P0 gate remains in the transition.
        from test_extension import expansion  # Existing explicitly simulated public inputs.
        from extension import build_extension  # Derive questions from real candidate doubts.
        from qa_record import read_record  # Fresh replay after transition.
        args = expansion()  # Includes complete simulated scope and evidence.
        batch = build_extension(*args, mode='simulation')['batch']  # Existing entry, never bypass its gate.
        questions = []  # Only new stage questions use new stable identities.
        for index, doubt in enumerate(batch['questions']):  # Enrich public candidate doubts.
            questions.append(dict(doubt, id='EXT' + str(index), depends_on=[], options=['P1', 'P2'], recommendation='P1', rationale='SIMULATED risk', example='SIMULATED boundary', affected_checks=['LOW-CHECK'], target_paths=doubt['suggested_target_paths'], evidence=['SIMULATED design'], boundary='Current extension', example_kind='hypothetical'))  # Full presentation.
        payload = dict(envelope=dict(zip(('catalog', 'baseline', 'reports', 'entry_request', 'design'), args)), mode='simulation', questions=questions, source_ref='SIMULATED supplied extension materials')  # Actual supplied evidence.
        state = advance_record(self.qa, 'start_extension', payload)  # Same MD receives the new candidate stage.
        self.assertEqual(read_record(self.qa), state)  # Disk replay includes both stages.
        self.assertEqual(state['prior_stages'][0]['questions'], self.state['questions'])  # Old unanswered and history retained.
        self.assertEqual([c['id'] for c in state['batch']['cases']], ['LOW', 'HIGH'])  # Real extension result.
        self.candidate.write_text(json.dumps(state['batch']), encoding='utf-8')  # Persist actual new-stage candidate.
        checkpoint_record(self.qa, 'p1-p2', self.candidate, [{'path': str(self.source), 'question_ids': ['Q1']}], 'Continue extension')  # Earlier-stage source decisions remain valid bindings.
        payload['envelope']['reports'] = []  # Missing full P0 evidence must still reject.
        before = self.qa.read_bytes()  # Rejection cannot erase prior stage.
        with self.assertRaises(ValueError):  # Existing public evidence gate.
            advance_record(self.qa, 'start_extension', payload)  # No alternate permissive path.
        self.assertEqual(self.qa.read_bytes(), before)  # All earlier events remain intact.

    def setUp(self):  # Build a fresh simulated task for each test.
        self.temp = tempfile.TemporaryDirectory(dir=Path.cwd())  # Workspace-only writes.
        self.addCleanup(self.temp.cleanup)  # Remove only this test's directory.
        self.root = Path(self.temp.name)  # Actual disk artifacts.
        self.qa = self.root / 'qa.md'  # Sole business record.
        batch, questions = fixture()  # Public converter output.
        for q in questions:  # Fully presented simulated questions.
            q.update(evidence=['SIMULATED source'], boundary='Related case only', example_kind='hypothetical')  # Honest provenance.
        self.state = start_record(self.qa, 'simulated-recovery', batch, questions)  # Save before any answers.
        self.candidate = self.root / 'candidate.json'  # Technical projection.
        self.candidate.write_text(json.dumps(batch), encoding='utf-8')  # Actual candidate to compare.
        self.source = self.root / 'source.md'  # Actual simulated source.
        self.source.write_text('SIMULATED original condition', encoding='utf-8')  # No invented answers.

    def checkpoint(self):  # Persist the minimum handoff through the public seam.
        return checkpoint_record(self.qa, 'p0', self.candidate, [{'path': str(self.source), 'question_ids': ['Q1']}], 'Await actual answers')  # Scoped source dependency.

    def test_fresh_read_uses_saved_sources_and_pending_questions(self):  # No cached state is passed to recovery.
        self.checkpoint()  # Save exact actual versions.
        result = resume_record(self.qa)  # Read only disk-backed materials.
        self.assertEqual(result['conflicts'], [])  # Verified candidate and source agree.
        self.assertEqual(result['state']['batch'], self.state['batch'])  # Recovery cannot advance business state.
        self.assertEqual(result['recovery']['stage'], 'p0')  # Actual checkpoint governs continuation.
        self.assertTrue(result['state']['round_questions'])  # Real unanswered questions remain.

    def test_changed_source_only_identifies_declared_questions(self):  # Independent questions stay available.
        self.checkpoint()  # Bind original source bytes.
        self.source.write_text('SIMULATED changed condition', encoding='utf-8')  # One genuine source change.
        result = resume_record(self.qa)  # Re-read actual files.
        self.assertEqual(result['conflicts'][0]['question_ids'], ['Q1'])  # Exact source-linked impact.
        self.assertEqual(result['state']['batch'], self.state['batch'])  # Never silently replace candidate.

    def test_candidate_same_version_content_tamper_is_detected(self):  # Version labels alone do not prove identity.
        self.checkpoint()  # Bind actual candidate contents.
        value = json.loads(self.candidate.read_text(encoding='utf-8'))  # Independently change one business field.
        value['cases'][0]['title'] = 'SIMULATED conflicting title'  # Keep old version label deliberately.
        self.candidate.write_text(json.dumps(value), encoding='utf-8')  # Technical source now conflicts.
        result = resume_record(self.qa)  # Inspect without overwriting either source.
        self.assertTrue(any(c['kind'] == 'candidate' for c in result['conflicts']))  # Conflict is visible.
        self.assertNotEqual(result['state']['batch']['cases'][0]['title'], value['cases'][0]['title'])  # MD remains authoritative.

    def test_failed_save_reports_payload_and_preserves_history(self):  # Actual filesystem replacement failure.
        from unittest.mock import patch  # Inject only the documented OS write failure.
        before = self.qa.read_bytes()  # Preserve known persisted event bytes.
        payload = {'actual_reply': 'SIMULATED not yet saved', 'source_ref': 'simulated turn'}  # Real attempted input.
        with patch('os.replace', side_effect=PermissionError('SIMULATED locked record')):  # Filesystem boundary, not business logic.
            with self.assertRaises(OSError) as caught:  # Failure must propagate honestly.
                advance_record(self.qa, 'record_note', payload)  # Public write attempt.
        self.assertEqual(caught.exception.pending_payload, payload)  # Recovery retains exact unsaved content.
        self.assertEqual(caught.exception.record_path, str(self.qa.resolve()))  # Concrete recovery location.
        self.assertEqual(self.qa.read_bytes(), before)  # Old source was never overwritten.
