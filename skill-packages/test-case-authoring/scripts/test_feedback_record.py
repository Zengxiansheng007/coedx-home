"""Simulated feedback at the persisted public task boundary."""
import copy  # Preserve comparison baselines.
import tempfile  # Isolate the sole task Markdown.
import unittest  # Standard-library regression runner.
from pathlib import Path  # Portable test paths.
from qa_record import start_record, advance_record, read_record  # User-facing persistence seam.
from test_feedback import scope  # Existing simulated review catalog.


class FeedbackRecordTests(unittest.TestCase):
    def test_clear_feedback_waits_for_summary_and_preserves_other_cases(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:  # Authorized workspace avoids restricted system TEMP.
            path = Path(directory) / 'qa.md'  # One record through review.
            batch = scope()['batch']  # Two selected cases and retained baseline.
            batch['questions'] = []  # This scenario begins with rules already clear.
            original = copy.deepcopy(batch)  # Detect accidental eager mutation.
            start_record(path, 'simulated-feedback', batch, [])  # Existing task entry.
            state = advance_record(path, 'start_feedback', dict(channel='chat', actual_reply='SIMULATED: rename EDIT', source_ref='simulated chat', changes=[dict(collection='cases', id='EDIT', path=['title'], value='Revised title')], clear_changes=True))  # Record proposal only.
            self.assertEqual(state['batch'], original)  # No eager candidate update.
            self.assertEqual(state['round_questions'], [])  # Clear edits need no redundant rule questionnaire.
            state = advance_record(path, 'summarize')  # Existing summary boundary.
            self.assertIn('Revised title', path.read_text(encoding='utf-8'))  # Proposal is durable.
            state = advance_record(path, 'apply_feedback', dict(confirmed=True, actual_reply='SIMULATED: summary agreed', summary_id=state['summary']['id']))  # Explicit centralized update.
            self.assertEqual(state['batch']['cases'][0]['title'], 'Revised title')  # Only agreed proposal applied.
            self.assertEqual(state['batch']['cases'][1], original['cases'][1])  # Unrelated selection untouched.
            self.assertEqual(state['batch']['cases'][0]['review_status'], 'pending')  # Old approval never migrates.
            self.assertEqual(read_record(path)['batch'], state['batch'])  # Replay exact candidate.
            with self.assertRaises(ValueError):  # Reject approval of old content.
                advance_record(path, 'review_feedback', dict(approved=True, actual_reply='SIMULATED: old review', case_ids=['EDIT'], content_version=original['content_version']))  # Version-bound review.

    def test_partial_feedback_preserves_unrelated_rule_and_reopens_dependency(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:  # Isolated simulated task.
            path = Path(directory) / 'qa.md'  # Same record for every phase.
            batch = scope()['batch']  # Current review copy.
            batch['questions'] = []  # Begin with a clear candidate.
            start_record(path, 'simulated-partial', batch, [])  # Persist initial version.
            question = dict(id='Q-LIMIT', case_id='EDIT', field='title', reason='标题条件和超限如何处理？', affected_checks=['EDIT'], target_paths=[['cases', 0, 'title']], depends_on=[], options=['提交拒绝', '阻止输入'], recommendation='核对约定', rationale='两种行为预期不同', boundary='只改标题用例', evidence='模拟反馈', example_kind='hypothetical', example='输入第101字时拒绝或阻止', answer_parts={'condition': '长度条件', 'behavior': '超限行为'})  # Complete focused Chinese prompt.
            dependency = dict(question, id='Q-DEPENDENT', field='dependent', depends_on=['Q-LIMIT'], answer_parts={}, target_paths=[])  # Only direct dependent reopens.
            independent = dict(question, id='Q-OTHER', case_id='LINK', field='independent', answer_parts={}, target_paths=[])  # Unrelated decision remains reusable.
            advance_record(path, 'start_feedback', dict(channel='chat', actual_reply='SIMULATED: clarify title rule', source_ref='simulated chat', clear_changes=True, questions=[question, dependency, independent]))  # Record full graph before questions.
            def reply(qid, decision='formal', **extra):  # Deterministic simulated responses through public boundary.
                return dict(question_id=qid, decision=decision, actual_reply='SIMULATED: actual answer', source_ref='simulated chat', interpretation='模拟规则答复', **extra)  # Provenance stays in sole record.
            state = advance_record(path, 'respond', [reply('Q-LIMIT', 'partial', answered_parts={'condition': '100字'}), reply('Q-OTHER')])  # Do not guess omitted behavior.
            self.assertIn('超限行为', state['chat'])  # Remaining aspect is actually asked.
            with self.assertRaises(ValueError):  # Partial answers block closure.
                advance_record(path, 'summarize')  # Existing summary gate.
            state = advance_record(path, 'respond', [reply('Q-LIMIT', 'provisional', answered_parts={'behavior': '提交拒绝'}, authorized_expectation='提交拒绝', product_check='待产品核对', updates=[dict(path=['cases', 0, 'title'], value='暂定标题')])])  # Explicit conditional authorization.
            state = advance_record(path, 'respond', [reply('Q-DEPENDENT')])  # Ask after premise only.
            other = copy.deepcopy(state['questions'][2])  # Freeze unrelated answer history.
            state = advance_record(path, 'summarize')  # Aggregate actual answers.
            state = advance_record(path, 'apply_feedback', dict(confirmed=True, actual_reply='SIMULATED: agree', summary_id=state['summary']['id']))  # Centralized update.
            self.assertEqual(state['batch']['cases'][0]['title'], '暂定标题')  # Actual answered update applied.
            self.assertEqual(state['batch']['cases'][0]['rule_status'], 'provisional')  # Temporary condition not formalized.
            state = advance_record(path, 'start_feedback', dict(channel='chat', actual_reply='SIMULATED: condition changed', source_ref='simulated chat', clear_changes=True, reopen_question_ids=['Q-LIMIT']))  # Reopen one premise and its dependencies.
            self.assertEqual([q['id'] for q in state['round_questions']], ['Q-LIMIT'])  # Unrelated question stays closed.
            self.assertEqual(state['questions'][2], other)  # Original unrelated evidence unchanged.
            self.assertEqual(state['questions'][0]['history'][-1]['product_check'], '待产品核对')  # Old provisional condition survives.


if __name__ == '__main__':
    unittest.main()  # Direct standard-library invocation.
