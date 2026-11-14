"""Synthetic public authoring tests for whole-step P0 reuse."""
import unittest
import copy
from test_extension import expansion
from extension import build_extension, render_extension


def reuse_design():
    args = expansion()
    target, source = args[4]['candidates'][0], args[0]['cases'][0]
    target['reuse_assessments'] = [dict(group='steps', step_id=target['steps'][0]['id'],
        p0_case_id=source['id'], p0_step_id=source['steps'][0]['id'],
        applicability='SIMULATED: identical editor role, saved note and fixed input',
        endpoint='SIMULATED: target sequence is complete and stops at its last assertion',
        source_basis='synthetic://complete-design', comparison={key: 'SIMULATED: identical supplied business condition; independently checked against source'
            for key in ('operation', 'data', 'expected', 'verification')})]
    return args


class StepReuseTests(unittest.TestCase):
    def test_missing_stale_inapplicable_and_override_references_block(self):
        base = build_extension(*reuse_design(), mode='simulation')['batch']
        for failure in ('missing', 'version', 'group', 'override', 'context', 'data'):
            with self.subTest(failure=failure):
                batch = copy.deepcopy(base)
                step = batch['cases'][0]['steps'][0]
                if failure == 'missing':
                    batch['step_definitions'] = []
                elif failure in ('version', 'group'):
                    step['step_reference']['semantic_version' if failure == 'version' else 'group'] = 'invalid'
                elif failure == 'override':
                    step['expected'] = [{'text': 'override', 'source': 'synthetic'}]
                elif failure == 'context':
                    batch['cases'][0]['context']['role'] = 'different role'
                else:
                    batch['data'][0]['validity'] = 'expired'
                with self.assertRaisesRegex(ValueError, 'step reference'):
                    render_extension(batch)

    def test_public_clarification_review_merge_and_selected_chat(self):
        from clarification import start_grill, respond, summarize, apply_summary, review
        from partial_merge import merge_reviewed
        from presentation import render_chat
        args = reuse_design()
        batch = build_extension(*args, mode='simulation')['batch']
        questions = [dict(q, id='RR03-' + str(i), depends_on=[], options=['P1', 'P2'], recommendation='P1',
            rationale='SIMULATED: high impact', example='SIMULATED: fixed note', affected_checks=['LOW-CHECK'],
            target_paths=q['suggested_target_paths']) for i, q in enumerate(batch['questions'])]
        session = start_grill(batch, questions)
        session = summarize(respond(session, [dict(question_id=q['id'], decision='formal', actual_reply='SIMULATED: confirm proposed priority', updates=[]) for q in questions]))
        session = apply_summary(session, dict(confirmed=True, actual_reply='SIMULATED: agree summary', summary_id=session['summary']['id']))
        batch = session['batch']
        session = review(session, dict(approved=True, actual_reply='SIMULATED: reviewed complete source and restored target endpoint', content_version=batch['content_version'], case_ids=['LOW']))
        batch = session['batch']
        self.assertIn('整步引用', render_chat(batch, ['LOW'])['human_view'])
        result = merge_reviewed(args[0], batch, dict(kind='merge_instruction', actual_reply='SIMULATED: merge only LOW', content_version=batch['content_version'], baseline_version=args[0]['content_version'], case_ids=['LOW']), target_kind='isolated')
        self.assertEqual(result['cases'][0]['status'], 'applied')
        self.assertTrue(result['catalog']['step_definitions'])
        changed = copy.deepcopy(batch)
        changed['cases'][0]['steps'].reverse()
        with self.assertRaisesRegex(ValueError, 'endpoint'):
            render_extension(changed)

    def test_every_different_dimension_remains_complete(self):
        for field in ('operation', 'data', 'expected', 'verification'):
            with self.subTest(field=field):
                args = reuse_design()
                step = args[4]['candidates'][0]['steps'][0]
                if field == 'operation':
                    step[field] = 'SIMULATED: perform a different operation'
                elif field == 'data':
                    item = copy.deepcopy(args[0]['data'][0])
                    item['validity'] = 'SIMULATED: different business validity'
                    args[4]['candidate_data'] = [item]
                else:
                    step[field][0]['text'] = 'SIMULATED: a different business result'
                result = build_extension(*args, mode='simulation')
                self.assertNotIn('step_reference', result['batch']['cases'][0]['steps'][0])

    def test_negative_endpoint_and_scope_round_trip(self):
        from scoped_review import build_scoped_review
        from feedback import prepare_feedback
        args = reuse_design()
        args[4]['candidates'][0]['steps'] = args[4]['candidates'][0]['steps'][:1]
        result = build_extension(*args, mode='simulation')
        self.assertEqual(len(result['batch']['cases'][0]['steps']), 1)
        pending = prepare_feedback(result['batch'], 'markdown', markdown=result['xmind_markdown'], actual_reply='SIMULATED: unchanged return')
        self.assertEqual(pending['changes'], [])
        full = dict(args[0], cases=args[0]['cases'] + result['batch']['cases'], step_definitions=result['batch']['step_definitions'])
        scoped = build_scoped_review(full, 'second-scope', [{'case_id': 'LOW', 'action': 'reuse', 'reason': 'SIMULATED: selected negative case'}])
        self.assertEqual(len(scoped['batch']['cases'][0]['steps']), 1)
        self.assertEqual(scoped['batch']['step_definitions'], result['batch']['step_definitions'])
        self.assertFalse(any('/expected' in q['field'] for q in scoped['batch']['questions']))

    def test_native_archive_unchanged_return_is_not_a_client_acceptance(self):
        import json
        import tempfile
        import zipfile
        from pathlib import Path
        from xmind_feedback import prepare_xmind_feedback
        result = build_extension(*reuse_design(), mode='simulation')
        lines = result['xmind_markdown'].splitlines()
        root = {'title': lines[0][2:], 'children': {'attached': []}}
        stack = [(-1, root)]
        for line in lines[1:]:
            level = (len(line) - len(line.lstrip())) // 2
            topic = {'title': line.strip()[2:]}
            while stack[-1][0] >= level:
                stack.pop()
            stack[-1][1].setdefault('children', {}).setdefault('attached', []).append(topic)
            stack.append((level, topic))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'synthetic.xmind'
            with zipfile.ZipFile(path, 'w') as archive:
                archive.writestr('content.json', json.dumps([{'rootTopic': root}]))
            pending = prepare_xmind_feedback(result['batch'], path, actual_reply='SIMULATED: unchanged native return')
        self.assertEqual(pending['changes'], [])

    def test_review_checks_reference_even_if_version_string_was_not_changed(self):
        from clarification import review
        args = expansion()
        result = build_extension(*args, mode='simulation')
        batch = result['batch']
        batch['cases'][0]['steps'][0] = {'id': 'broken', 'step_reference': {'definition_digest': 'missing'}}
        session = {'batch': batch}
        with self.assertRaisesRegex(ValueError, 'step reference'):
            review(session, {})

    def test_authoring_selects_whole_step_and_rechecks_snapshot(self):
        args = expansion()  # Complete source design, never a fabricated reference.
        case = args[4]['candidates'][0]
        source = args[0]['cases'][0]
        case['reuse_assessments'] = [{  # Explicit synthetic agent interpretation of the supplied source.
            'group': 'steps', 'step_id': case['steps'][0]['id'],
            'p0_case_id': source['id'], 'p0_step_id': source['steps'][0]['id'],
            'applicability': 'SIMULATED: same editor role and initial note state',
            'endpoint': 'SIMULATED: stop after the declared target steps',
            'comparison': {key: 'SIMULATED: source design retained without business changes'
                           for key in ('operation', 'data', 'expected', 'verification')},
            'source_basis': 'synthetic://complete-design'}]
        result = build_extension(*args, mode='simulation')
        step = result['batch']['cases'][0]['steps'][0]
        self.assertEqual(set(step), {'id', 'step_reference'})
        self.assertIn(source['title'], result['xmind_markdown'])
        self.assertTrue(result['batch']['step_definitions'])
        result['batch']['step_definitions'][0]['step']['operation'] = 'corrupted'
        with self.assertRaisesRegex(ValueError, 'reference'):
            render_extension(result['batch'])


if __name__ == '__main__':
    unittest.main()
