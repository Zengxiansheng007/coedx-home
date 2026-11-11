"""Synthetic public coverage regressions; no semantic or business acceptance."""
import copy  # Preserve the candidate baseline.
import tempfile  # Isolate the single task record.
import unittest  # Exercise public transitions.
from pathlib import Path  # Keep persistence in the worktree.
from test_clarification import fixture  # Reuse real candidate conversion.
from qa_record import start_record, advance_record, read_record  # Sole journal API.
from scoped_review import build_scoped_review  # Display selection remains a separate public boundary.
from p0_evidence import check_extension  # Full approved validation scope authority.
from test_p0_evidence import fixture as p0_fixture  # Synthetic complete P0 evidence.
from test_partial_merge import fixture as merge_fixture  # Existing isolated P1 candidate source.
from clarification import start_grill, summarize, apply_summary, review  # Public review gates.
from partial_merge import merge_reviewed  # Isolated catalog merge only.


class CoverageTests(unittest.TestCase):  # Test effects instead of private helpers.
    def test_local_merge_preserves_undisplayed_validation_scope(self):  # Merge selection cannot shrink approval.
        full, _, _ = merge_fixture()  # Synthetic P1 catalog.
        changed = dict(copy.deepcopy(full['cases'][0]), title='Synthetic scoped revision')  # Only one authorized edit.
        batch = build_scoped_review(full, 'synthetic-scope-merge', [dict(case_id='EDIT', action='modify', reason='Current batch', basis='simulated decision', coverage_impact='one title')], approved_validation_scope=['EDIT', 'OTHER'], candidates=[changed])['batch']  # Preserve undisplayed approval.
        state = summarize(start_grill(batch, []))  # Pure supplied-content seam.
        state = apply_summary(state, dict(confirmed=True, actual_reply='SIMULATED agree', summary_id=state['summary']['id']))  # Explicit understanding.
        state = review(state, dict(approved=True, actual_reply='SIMULATED approve', content_version=state['batch']['content_version'], case_ids=['EDIT']))  # Exact scoped review.
        instruction = dict(kind='merge_instruction', actual_reply='SIMULATED merge EDIT', content_version=state['batch']['content_version'], baseline_version=full['content_version'], case_ids=['EDIT'])  # Isolated merge authorization.
        merged = merge_reviewed(full, state['batch'], instruction, target_kind='isolated')  # No real assets.
        self.assertEqual(merged['approved_validation_scope'], ['EDIT', 'OTHER'])  # Scope survives local merge.
        self.assertEqual(merged['catalog']['cases'][2], full['cases'][2])  # Undisplayed content is untouched.

    def test_display_subset_cannot_replace_full_approved_p0_scope(self):  # Editing scope and validation scope remain distinct.
        full, baseline, reports, request = p0_fixture()  # Two approved P0 cases.
        original = copy.deepcopy(baseline)  # Approval stays immutable.
        displayed = build_scoped_review(full, 'synthetic-local-edit', [dict(case_id='EDIT', action='reuse', reason='Only this case needs review')], approved_validation_scope=['EDIT', 'LINK'])  # One displayed case.
        self.assertEqual([c['id'] for c in displayed['batch']['cases']], ['EDIT'])  # No full-module re-review.
        checked = check_extension(full, baseline, reports[:1], request, mode='simulation')  # The hidden approved case lacks proof.
        self.assertFalse(checked['can_extend'])  # Partial display cannot grant P1/P2 entry.
        self.assertEqual(baseline, original)  # No implicit scope rewrite.

    def test_fact_gap_and_stale_recheck_block_summary_without_fabricating_questions(self):  # Empty frontier is not complete coverage.
        batch, _ = fixture()  # Use supplied candidate content.
        batch['questions'] = []  # No question is currently askable.
        review = dict(scope={'batch_cases': [c['id'] for c in batch['cases']], 'direct_dependencies': [], 'p0_scope_ref': 'simulated full approved P0'}, sources=[{'ref': 'simulated PRD section 2', 'finding': 'Missing empty-state rule'}], history_basis='Read entire task MD', branches=[dict(id='B1', topic='Empty state', source='simulated PRD section 2', dependencies=[], status='fact_pending', basis='Attachment unavailable', next_step='Obtain attachment')], conclusion='Only empty-state facts blocked')  # Agent observation, not machine semantic proof.
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:  # Real single-file replay.
            path = Path(directory) / 'qa.md'  # Preserve sole authority.
            start_record(path, 'synthetic-facts', batch, [])  # No invented business questions.
            advance_record(path, 'record_coverage', review)  # Persist explicit gap.
            with self.assertRaises(ValueError):  # No questions cannot erase a fact blocker.
                advance_record(path, 'summarize')  # Must report missing facts.
            review['branches'][0].update(status='resolved', basis='simulated supplied attachment section 2: show empty list')  # Actual source finding in the test scenario.
            advance_record(path, 'record_coverage', review)  # Recheck after available evidence.
            state = advance_record(path, 'summarize')  # Resolved source permits summary only.
            self.assertEqual(state['summary']['coverage']['branches'][0]['status'], 'resolved')  # Limitations travel with snapshot.
            self.assertEqual(state['batch'], batch)  # No candidate writes or business execution.
            discovered = dict(fixture()[1][0], id='Q8', evidence='simulated source', boundary='same batch', example_kind='hypothetical')  # New source finding after review.
            advance_record(path, 'append_questions', [discovered])  # Invalidate recorded coverage revision.
            advance_record(path, 'respond', [dict(question_id='Q8', decision='deferred', actual_reply='SIMULATED defer this rule', source_ref='simulated turn 2', interpretation='explicit deferral', updates=[])])  # User decides, unknown remains.
            with self.assertRaises(ValueError):  # Old review cannot cover the newly answered theme.
                advance_record(path, 'summarize')  # Requires a fresh source reread.
            review['branches'][0]['status'] = 'deferred'  # Agent alone cannot decide deferral.
            with self.assertRaises(ValueError):  # Require actual answered Q reference.
                advance_record(path, 'record_coverage', review)  # Reject invented user disposition.
            review['branches'][0]['question_id'] = 'Q8'  # Actual matching simulated disposition.
            advance_record(path, 'record_coverage', review)  # Refresh after rereading affected sources.
            state = advance_record(path, 'summarize')  # Only disposition is settled.
            self.assertEqual(state['summary']['coverage']['branches'][0]['status'], 'deferred')  # Never convert unknown to resolved.
            self.assertTrue(state['summary']['blocked_cases'])  # Deferred cases cannot pass review.

    def test_discovered_question_keeps_history_and_blocks_early_summary(self):  # Source discovery reopens the conversation.
        batch, questions = fixture()  # Existing candidate doubts.
        questions = questions[:2]  # Independent initial frontier.
        for question in questions:  # Supply complete source-aware presentation.
            question.update(evidence='SIMULATED source section 1', boundary='Current batch only', example_kind='hypothetical')  # No real facts.
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:  # Authorized local writes.
            path = Path(directory) / 'qa.md'  # One answer authority.
            start_record(path, 'synthetic-coverage', batch, questions)  # Save before asking.
            for question in questions:  # Simulated replies to already presented questions.
                advance_record(path, 'respond', [dict(question_id=question['id'], decision='formal', actual_reply='SIMULATED confirmed', source_ref='simulated turn', interpretation='known rule', updates=[])])  # Actual-source contract.
            history = read_record(path)['questions'][0]['history']  # Preserve prior decisions.
            discovered = dict(copy.deepcopy(questions[0]), id='Q9', reason='新发现的空值规则如何处置？')  # Independent newly found rule.
            state = advance_record(path, 'append_questions', [discovered])  # Public discovery seam.
            self.assertIn('Q9', state['chat'])  # New complete question becomes visible.
            self.assertEqual(state['questions'][0]['history'], history)  # Old answers remain valid.
            self.assertEqual(state['batch'], batch)  # Discovery grants no edit authority.
            with self.assertRaises(ValueError):  # Answered initial list is insufficient.
                advance_record(path, 'summarize')  # Unanswered discovery blocks.
            with self.assertRaises(ValueError):  # Stable IDs cannot be reused.
                advance_record(path, 'append_questions', [discovered])  # Preserve original question identity.


if __name__ == '__main__':  # Standalone public regression entry.
    unittest.main()  # Standard runner.
