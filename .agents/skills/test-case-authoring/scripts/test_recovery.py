"""Public recovery checks using isolated simulated records."""
import json  # Read actual candidate files.
import tempfile  # Keep all fixtures disposable.
import unittest  # Existing regression runner.
from pathlib import Path  # Explicit artifact paths.
from test_clarification import fixture  # Existing public authoring fixture.
from qa_record import start_record, checkpoint_record, resume_record, advance_record  # Public persistence boundary.


class RecoveryTests(unittest.TestCase):  # Verify observable persistence and recovery.
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
