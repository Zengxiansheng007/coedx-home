"""Synthetic public journal regression; replies below are simulated."""
import tempfile  # Keep test artifacts isolated.
import unittest  # Exercise the public boundary.
from pathlib import Path  # Use actual Markdown persistence.
from test_clarification import fixture  # Reuse the established candidate seam.
from qa_record import start_record, advance_record, read_record  # Public task journal API.


class RecordTests(unittest.TestCase):  # Verify disk-backed decisions, not private helpers.
    def test_provisional_and_deferred_preserve_conditions_and_history(self):  # Exercise the other real choices.
        for choice in ('provisional', 'deferred'):  # Decisions come from simulated explicit replies.
            batch, questions = fixture()  # Same public candidate boundary.
            questions = questions[:2]  # Independent questions only in this ticket.
            for q in questions:  # Complete presentation inputs.
                q.update(boundary='影响当前用例', evidence=['模拟来源第1行'], example_kind='hypothetical')  # Honest provenance.
            with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:  # Keep atomic replacement inside authorized workspace.
                path = Path(directory) / 'qa.md'  # Sole answer source.
                start_record(path, 'simulated-task', batch, questions)  # Persist questions first.
                advance_record(path, 'record_note', dict(actual_reply='[模拟]不知道', source_ref='模拟第2轮'))  # Unknown stays open.
                self.assertTrue(all(not q['history'] for q in read_record(path)['questions']))  # No automatic deferral.
                for q in questions:  # Actual explicit disposition after the unknown reply.
                    reply = dict(question_id=q['id'], decision=choice, actual_reply='[模拟]明确选择' + choice, source_ref='模拟第3轮', interpretation='本轮规则处置', updates=[])  # Preserve real choice.
                    if choice == 'provisional':  # Both expectation and condition are required.
                        with self.assertRaises(ValueError):  # Missing expected behavior cannot authorize.
                            advance_record(path, 'respond', [reply])  # Public boundary rejection.
                        reply.update(authorized_expectation='保存为草稿', product_check='发布前由产品核对草稿规则')  # Explicit temporary meaning.
                    advance_record(path, 'respond', [reply])  # Saved actual decision.
                state = advance_record(path, 'summarize')  # Candidate still unchanged.
                self.assertEqual(state['batch'], batch)  # Summary is not application.
                state = advance_record(path, 'apply_summary', dict(confirmed=True, summary_id=state['summary']['id'], actual_reply='[模拟]汇总准确'))  # Separate confirmation.
                self.assertEqual(state['batch']['cases'][0]['rule_status'], choice)  # Preserve each route.
                self.assertEqual(state['batch']['cases'][0]['review_status'], 'pending')  # Still not full-case approval.

    def test_question_saved_before_answer_and_summary_before_candidate_update(self):  # One end-to-end tracer.
        batch, questions = fixture()  # Genuine converter candidate with unknown rules.
        questions = questions[:2]  # Keep this ticket independent of dependent-round additions.
        for q in questions:  # Supply actual presentation inputs.
            q.update(boundary='搁置将阻塞相关用例', evidence=['模拟录制第1行'], example_kind='hypothetical')  # Mark provenance.
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:  # No public artifacts contain private inputs.
            path = Path(directory) / 'qa.md'  # One task, one answer record.
            current = start_record(path, 'simulated-task', batch, questions)  # Must save and read before chat.
            self.assertEqual(read_record(path)['batch'], batch)  # No answer means no candidate mutation.
            self.assertTrue(all(not q['history'] for q in current['questions']))  # Recommendations never become answers.
            for q in questions:  # Simulate actual replies only after questions exist.
                current = advance_record(path, 'respond', [dict(question_id=q['id'], decision='formal', actual_reply='[模拟]确认该规则', source_ref='模拟对话第2轮', interpretation='确认现有规则', updates=[])])  # Preserve original and interpretation.
            self.assertEqual(current['batch'], batch)  # Answers alone cannot update candidates.
            current = advance_record(path, 'summarize', None)  # Separate understanding confirmation.
            current = advance_record(path, 'apply_summary', dict(confirmed=True, summary_id=current['summary']['id'], actual_reply='[模拟]汇总准确'))  # Explicit current summary.
            self.assertEqual(current['batch']['cases'][0]['rule_status'], 'formal')  # Business decision applied.
            self.assertEqual(current['batch']['cases'][0]['review_status'], 'pending')  # Whole-case review remains separate.
            self.assertIn('#Q1-A1', current['questions'][0]['history'][0]['qa_ref'])  # Derived state cites sole answer source.
            self.assertEqual(read_record(path), current)  # Disk is authoritative.
