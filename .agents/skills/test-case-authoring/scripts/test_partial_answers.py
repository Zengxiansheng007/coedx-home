"""Synthetic replies through the persisted public conversation boundary."""
import tempfile  # Isolate task records.
import unittest  # Public behavior assertions.
from pathlib import Path  # Sole Markdown source.
from test_clarification import fixture  # Real converter fixture.
from qa_record import start_record, advance_record, read_record  # Public interfaces.


class PartialAnswers(unittest.TestCase):  # Test actual saved state and follow-up text.
    def test_reopened_partial_premise_holds_already_presented_dependency(self):  # Correction while a dependent is awaiting a reply.
        batch, questions = fixture()  # Public seed.
        for q in questions:  # Complete saved presentation.
            q.update(evidence='模拟材料', boundary='相关用例', example_kind='hypothetical')  # Synthetic only.
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:  # Authorized temporary state.
            path = Path(directory) / 'qa.md'  # One source.
            start_record(path, 'simulation', batch, questions)  # Initial frontier.
            def answer(qid, decision):  # Test-only natural reply metadata.
                return dict(question_id=qid, decision=decision, actual_reply='[模拟]规则待补充' if decision == 'unknown' else '[模拟]确认规则', source_ref='模拟轮次', interpretation='当前实际答复', updates=[])  # Explicit choices.
            state = advance_record(path, 'respond', [answer('Q1', 'formal'), answer('Q2', 'formal')])  # Dependency becomes visible.
            self.assertEqual([q['id'] for q in state['round_questions']], ['FOLLOW'])  # Awaiting dependent reply.
            state = advance_record(path, 'respond', [answer('Q1', 'unknown')])  # Premise reopened first.
            self.assertEqual([q['id'] for q in state['round_questions']], ['Q1'])  # Do not keep asking invalid dependent.
            with self.assertRaises(ValueError):  # Previously displayed dependency is no longer eligible.
                advance_record(path, 'respond', [answer('FOLLOW', 'formal')])  # Public boundary must reject.

    def test_unknown_asks_disposition_then_correction_reopens_only_dependency(self):  # Second vertical slice.
        batch, questions = fixture()  # Public candidate seed.
        for q in questions:  # Record complete questions.
            q.update(evidence='模拟材料', boundary='仅影响相关检查', example_kind='hypothetical')  # Synthetic provenance.
        def reply(qid, choice, words):  # Explicit test-only responses after start.
            return dict(question_id=qid, decision=choice, actual_reply='[模拟]' + words, source_ref='模拟对话', interpretation=words, updates=[])  # Never product evidence.
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:  # Isolated persistence.
            path = Path(directory) / 'qa.md'  # Sole source.
            start_record(path, 'simulation', batch, questions)  # Ask independent questions.
            state = advance_record(path, 'respond', [reply('Q1', 'unknown', '不知道')])  # Unknown is not deferral.
            self.assertIn('如何处置', state['chat'])  # Actual full disposition question.
            self.assertIn('也可自定义回答', state['chat'])  # User remains free to answer.
            self.assertNotIn('FOLLOW：', state['chat'])  # Premise still unknown.
            self.assertEqual(state['questions'][0]['history'][-1]['decision'], 'unknown')  # Preserve actual uncertainty.
            state = advance_record(path, 'respond', [reply('Q2', 'formal', '明确独立规则')])  # Unrelated answer can proceed.
            independent = state['questions'][1]['history']  # Save unchanged evidence.
            state = advance_record(path, 'respond', [reply('Q1', 'formal', '已查明原规则')])  # Premise arrives later.
            self.assertEqual([q['id'] for q in state['round_questions']], ['FOLLOW'])  # Dependent now eligible.
            state = advance_record(path, 'respond', [reply('FOLLOW', 'formal', '确认依赖规则')])  # Actual next round.
            state = advance_record(path, 'respond', [reply('Q1', 'formal', '改为新规则')])  # Correction keeps old history.
            self.assertEqual([q['id'] for q in state['round_questions']], ['FOLLOW'])  # Only dependent reopened.
            self.assertEqual(state['questions'][1]['history'], independent)  # Independent decision preserved.
            self.assertEqual(len(state['questions'][0]['history']), 3)  # Unknown and both actual rule replies remain.
            self.assertEqual(read_record(path), state)  # Replay follows actual rounds.

    def test_partial_answer_retains_parts_and_asks_remaining_behavior(self):  # First vertical slice.
        batch, questions = fixture()  # Includes two independent questions and one dependent.
        for q in questions:  # Complete persisted presentation contract.
            q.update(evidence='模拟材料', boundary='仅影响相关检查', example_kind='hypothetical')  # Explicit simulation.
        questions[0]['answer_parts'] = {'object': '标题对象', 'condition': '是否必填和长度', 'behavior': '超限处理'}  # Independent checks.
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:  # Authorized temporary space.
            path = Path(directory) / 'qa.md'  # One task source.
            state = start_record(path, 'simulation', batch, questions)  # Save before question display.
            self.assertEqual([q['id'] for q in state['round_questions']], ['Q1', 'Q2'])  # Independent frontier.
            state = advance_record(path, 'respond', [dict(question_id='Q1', decision='partial', actual_reply='[模拟]标题必填、最多100字', source_ref='模拟第2轮', interpretation='对象与条件已答，超限未知', answered_parts={'object': '标题', 'condition': '必填、最多100字'}, updates=[])])  # Partial real response.
            self.assertEqual(state['questions'][0]['remaining_parts'], ['behavior'])  # Cannot close whole question.
            self.assertIn('超限处理', state['chat'])  # Actual remaining prompt returned.
            self.assertEqual(state['batch'], batch)  # No premature candidate writes.
            self.assertEqual(read_record(path), state)  # Disk replay retains partial answer.
            with self.assertRaises(ValueError):  # Missing behavior blocks summary.
                advance_record(path, 'summarize')  # Public gate.
            complete = dict(question_id='Q1', decision='formal', actual_reply='[模拟]允许输入，提交拒绝', source_ref='模拟第3轮', interpretation='补足超限行为', answered_parts={'behavior': '允许输入，提交拒绝'}, updates=[])  # Actual later answer only.
            state = advance_record(path, 'respond', [complete])  # Accumulate prior explicit aspects.
            self.assertEqual(state['questions'][0]['remaining_parts'], [])  # Whole question now complete.
            self.assertEqual(state['questions'][0]['answered_parts']['condition'], '必填、最多100字')  # No lost earlier answer.
            self.assertEqual([q['id'] for q in state['round_questions']], ['Q2'])  # Omitted independent answer still pending.
            state = advance_record(path, 'respond', [dict(complete, question_id='Q2', answered_parts={})])  # Next actual simulated reply.
            state = advance_record(path, 'respond', [dict(complete, question_id='FOLLOW', answered_parts={})])  # Real premise now met.
            state = advance_record(path, 'summarize')  # Snapshot includes all actual aspects.
            self.assertEqual(state['summary']['decisions'][0]['answered_parts']['behavior'], '允许输入，提交拒绝')  # Earlier and later answers are both reviewable.
