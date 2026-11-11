"""Synthetic regressions through public render and persisted feedback boundaries."""
import copy  # Keep mutation baselines.
import tempfile  # Isolate task records.
import unittest  # Existing standard-library runner.
from pathlib import Path  # Workspace-local scratch files.
from authoring import render_batch  # Public rendering boundary.
from test_feedback import scope  # Existing synthetic catalog.
from qa_record import start_record, advance_record, read_record  # Sole persisted task API.


def question(identity, target=None, **extra):  # Complete synthetic focused question.
    return dict(id=identity, case_id='EDIT', field=identity, reason='模拟：如何处理？', affected_checks=['EDIT'], target_paths=target or [], depends_on=[], options=['确认', '搁置'], recommendation='核对', rationale='规则待核对', boundary='模拟范围', evidence='模拟来源', example_kind='hypothetical', example='模拟：明确标题', **extra)


def reply(identity, value=None, **extra):  # Actual synthetic test input, not dialogue acceptance.
    return dict(question_id=identity, decision='formal', actual_reply='SIMULATED answer', source_ref='synthetic', interpretation='synthetic', updates=[] if value is None else [dict(path=['cases', 0, 'title'], value=value)], **extra)


class ThreeRepairTests(unittest.TestCase):
    def test_literal_identity_tokens_survive_both_views(self):
        batch = scope()['batch']  # English IDs are also legitimate business values.
        batch['cases'][0]['steps'][0]['operation'] = '输入业务字面值 EDIT 和 用例编号：EDIT'  # Literal must remain exact.
        batch['cases'][0]['dependencies'] = [{'case_id': 'LINK', 'purpose': 'EDIT'}]  # Only identity field translates.
        for plain in (False, True):
            candidate = copy.deepcopy(batch)  # Exercise both public render routes.
            if plain:
                candidate.pop('kind', None)  # Ordinary authoring path.
            result = render_batch(candidate)  # Same version, different layouts.
            for view in ('human_view', 'xmind_markdown'):
                self.assertIn('输入业务字面值 EDIT 和 用例编号：EDIT', result[view])  # No global replacement.
            self.assertNotIn('用例编号：LINK', result['xmind_markdown'])  # Actual reference still hidden.

    def test_deferred_separate_impact_preserves_known_case_updates(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            path = Path(directory) / 'qa.md'  # Unique synthetic task.
            batch = scope()['batch']
            batch['questions'] = []  # No unrelated unknowns.
            start_record(path, 'synthetic-scope', batch, [question('TITLE', [['cases', 0, 'title']]), question('BRANCH', disposition_scope='separate_impact', scope_basis='Invalid-session branch is outside valid-account creation')])
            advance_record(path, 'respond', [reply('TITLE', 'Known title'), dict(reply('BRANCH'), decision='deferred', actual_reply='SIMULATED: defer invalid-session branch; retain valid-account precondition')])
            state = advance_record(path, 'summarize')
            self.assertEqual(state['summary']['blocked_cases'], [])  # Scope disposition is not a prerequisite rule.
            state = advance_record(path, 'apply_summary', dict(confirmed=True, actual_reply='SIMULATED agree', summary_id=state['summary']['id']))
            self.assertEqual(state['batch']['cases'][0]['title'], 'Known title')
            self.assertEqual(state['batch']['cases'][0]['rule_status'], 'formal')
            self.assertEqual(state['questions'][1]['history'][-1]['decision'], 'deferred')  # Unknown branch remains deferred.
            self.assertEqual(state['batch']['cases'][0]['context'], batch['cases'][0]['context'])  # Existing valid-account precondition is retained.

    def test_empty_targets_and_real_dependencies_still_block(self):
        from clarification import start_grill, respond, summarize  # Same public summary contract.
        batch = scope()['batch']
        batch['questions'] = []
        for separate in (False, True):
            premise = question('PREMISE', **(dict(disposition_scope='separate_impact', scope_basis='Separate invalid-session branch') if separate else {}))
            dependent = dict(question('DEPENDENT'), depends_on=['PREMISE'])  # Genuine dependent rule remains blocked.
            state = start_grill(batch, [premise, dependent])
            state = respond(state, [dict(reply('PREMISE'), decision='deferred')])
            summary = summarize(state)['summary']
            self.assertEqual(summary['blocked_cases'], ['EDIT'])  # Empty paths do not discharge unknown prerequisites.
            self.assertEqual(summary['blocked_questions'], ['DEPENDENT'])

    def test_feedback_conflicts_preserve_answers_and_candidate(self):
        for explicit in (False, True):
            with self.subTest(explicit=explicit), tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
                path = Path(directory) / 'qa.md'
                batch = scope()['batch']
                batch['questions'] = []
                start_record(path, 'synthetic-conflict', batch, [])
                qs = [question('Q1', [['cases', 0, 'title']])]
                if not explicit:
                    qs.append(question('Q2', [['cases', 0, 'title']]))
                changes = [dict(collection='cases', id='EDIT', path=['title'], value='A')] if explicit else []
                advance_record(path, 'start_feedback', dict(channel='chat', actual_reply='SIMULATED feedback', source_ref='synthetic', clear_changes=True, changes=changes, questions=qs))
                advance_record(path, 'respond', [reply('Q1', 'B')] + ([] if explicit else [reply('Q2', 'A')]))
                state = advance_record(path, 'summarize')
                before = path.read_bytes()  # Failed application must not erase actual answers.
                with self.assertRaisesRegex(ValueError, 'Conflicting confirmed updates'):
                    advance_record(path, 'apply_feedback', dict(confirmed=True, actual_reply='SIMULATED agree', summary_id=state['summary']['id']))
                self.assertEqual(path.read_bytes(), before)
                self.assertEqual(read_record(path)['batch'], state['batch'])

    def test_feedback_discovery_appends_question_and_requires_coverage_recheck(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            path = Path(directory) / 'qa.md'
            batch = scope()['batch']
            batch['questions'] = []
            start_record(path, 'synthetic-discovery', batch, [])
            coverage = dict(scope=dict(batch_cases=['EDIT', 'LINK'], direct_dependencies=[], p0_scope_ref='synthetic full approval'), sources=[dict(ref='synthetic source', finding='title and dependency')], history_basis='synthetic task history', branches=[dict(id='B', topic='title', source='synthetic source', dependencies=[], status='resolved', basis='supplied text', next_step='review')], conclusion='synthetic scope only')
            advance_record(path, 'record_coverage', coverage)  # Old closure must survive as stale evidence.
            advance_record(path, 'start_feedback', dict(channel='chat', actual_reply='SIMULATED feedback', source_ref='synthetic', clear_changes=True, questions=[]))
            with self.assertRaisesRegex(ValueError, 'Coverage recheck'):
                advance_record(path, 'summarize')  # Feedback requires a fresh source reread.
            advance_record(path, 'append_questions', [question('NEW', [['cases', 0, 'title']])])
            advance_record(path, 'respond', [reply('NEW', 'Discovered title')])
            advance_record(path, 'record_coverage', coverage)  # Synthetic observation after discovery and response.
            state = advance_record(path, 'summarize')
            self.assertIn('coverage', state['summary'])  # Coverage and proposal share one confirmed hash.
            self.assertIn('feedback_proposal', state['summary'])
            state = advance_record(path, 'apply_feedback', dict(confirmed=True, actual_reply='SIMULATED agree', summary_id=state['summary']['id']))
            self.assertEqual(state['batch']['cases'][0]['title'], 'Discovered title')
            self.assertEqual(read_record(path)['questions'][0]['id'], 'NEW')
