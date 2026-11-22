"""Fresh handoff checks use actual supplied artifacts, never cached success."""
import copy  # Preserve the seed evidence.
import json  # Existing technical material.
import test_recovery  # Exercise the established public record seam without duplicate module test discovery.
from test_step_reuse import reuse_design  # Explicit synthetic source material.
from extension import build_extension  # Existing authoring entry.
from qa_record import start_record, checkpoint_record, resume_record  # Existing handoff entry.


class HandoffRevalidationTests(test_recovery.RecoveryTests):
    def test_checkpoint_becomes_stale_after_new_answer_but_not_notes(self):
        from qa_record import advance_record  # Public event transition.
        self.checkpoint()  # Original event position.
        advance_record(self.qa, 'record_note', dict(actual_reply='SIMULATED context only', source_ref='synthetic://note'))  # Nonsemantic note remains safe.
        self.assertEqual(resume_record(self.qa)['conflicts'], [])  # Notes do not invalidate recovery.
        state = advance_record(self.qa, 'respond', [dict(question_id='Q1', decision='formal', actual_reply='SIMULATED answer', interpretation='SIMULATED rule', source_ref='synthetic://turn')])  # New decisions need a new checkpoint.
        self.candidate.write_text(json.dumps(state['batch']), encoding='utf-8')  # Matching candidate alone is insufficient.
        self.assertTrue(any(c['kind'] == 'checkpoint' for c in resume_record(self.qa)['conflicts']))  # Do not return stale next action silently.

    def test_unqualified_definition_cannot_borrow_unrelated_p0_pass(self):
        from p0_evidence import approve_p0_scope  # Explicit unrelated approved scope.
        args = list(reuse_design())  # Reference points at EDIT.
        batch = build_extension(*args, mode='simulation')['batch']  # Retain original active definition.
        args[1] = approve_p0_scope(args[0], 'synthetic-round', ['LINK'], 'SIMULATED unrelated scope')  # Only LINK qualifies.
        args[2] = [r for r in args[2] if r['case_id'] == 'LINK']  # Valid but unrelated report.
        args[3]['manual_start']['baseline_id'] = args[1]['id']  # Match the explicitly narrower baseline.
        evidence = self.root / 'unrelated.json'  # Actual supplied artifact.
        evidence.write_text(json.dumps(dict(zip(('catalog', 'baseline', 'reports', 'request'), args[:4]), mode='simulation')), encoding='utf-8')  # No qualification for EDIT.
        questions = [dict(q, id='RR07-' + str(i), depends_on=[], options=['P1', 'P2'], recommendation='P1', rationale='SIMULATED risk', example='SIMULATED boundary', affected_checks=['LOW-CHECK'], target_paths=q['suggested_target_paths'], evidence=['synthetic://design'], boundary='Current case', example_kind='hypothetical') for i, q in enumerate(batch['questions'])]  # Public question admission.
        qa = self.root / 'unqualified.md'  # Isolated actual task.
        start_record(qa, 'unqualified-source', batch, questions)  # Save complete doubts.
        self.candidate.write_text(json.dumps(batch), encoding='utf-8')  # Exact supplied candidate.
        with self.assertRaisesRegex(ValueError, 'qualified scope'):
            checkpoint_record(qa, 'p1-p2', self.candidate, [{'path': str(self.source)}], 'Continue review', extension_evidence=evidence)  # Unrelated success must never qualify EDIT.

    def test_extension_handoff_rechecks_live_evidence_and_definition_closure(self):
        args = reuse_design()  # No real business evidence.
        batch = build_extension(*args, mode='simulation')['batch']  # Actual authoring result.
        qa = self.root / 'extension.md'  # Isolated task record.
        questions = [dict(q, id='RR07-' + str(i), depends_on=[], options=['P1', 'P2'], recommendation='P1', rationale='SIMULATED risk', example='SIMULATED boundary', affected_checks=['LOW-CHECK'], target_paths=q['suggested_target_paths'], evidence=['synthetic://design'], boundary='Current case', example_kind='hypothetical') for i, q in enumerate(batch['questions'])]  # Preserve actual candidate doubts.
        start_record(qa, 'simulated-extension', batch, questions)  # Pending review remains pending.
        self.candidate.write_text(json.dumps(batch), encoding='utf-8')  # Same candidate.
        evidence = self.root / 'entry.json'  # Technical source already required for extension.
        envelope = dict(zip(('catalog', 'baseline', 'reports', 'request'), args[:4]))  # Explicit existing gate inputs.
        envelope['mode'] = 'simulation'  # Never represent simulation as execution.
        evidence.write_text(json.dumps(envelope), encoding='utf-8')  # Supplied actual file.
        checkpoint_record(qa, 'p1-p2', self.candidate, [{'path': str(self.source)}], 'Continue review', extension_evidence=evidence)  # Revalidate at handoff.
        restored = resume_record(qa)  # Receiver has only disk-backed materials.
        self.assertEqual(restored['conflicts'], [])  # Same sources remain valid.
        self.assertNotIn('step_reference', restored['complete_batch']['cases'][0]['steps'][0])  # Complete meaning is transient.
        self.assertEqual(restored['complete_batch']['content_version'], batch['content_version'])  # Same reviewed candidate version.
        changed = copy.deepcopy(envelope)  # Invalidate P0 after the successful checkpoint.
        changed['reports'] = []  # Missing current evidence must override old success.
        evidence.write_text(json.dumps(changed), encoding='utf-8')  # Actual changed source.
        self.assertTrue(resume_record(qa)['conflicts'])  # Old success cannot hide invalidation.
        with self.assertRaisesRegex(ValueError, 'P0'):
            checkpoint_record(qa, 'p1-p2', self.candidate, [{'path': str(self.source)}], 'Continue', extension_evidence=evidence)  # No new permissive checkpoint.
