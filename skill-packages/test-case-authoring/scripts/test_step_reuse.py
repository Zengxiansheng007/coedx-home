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
    def test_nested_business_identity_is_not_erased_as_metadata(self):
        from p0_evidence import approve_p0_scope
        from step_reuse import expanded
        for location in ('step', 'data', 'assertion'):
            with self.subTest(location=location):
                args = list(reuse_design())
                source = args[0]['cases'][0]['steps'][0]
                target = args[4]['candidates'][0]['steps'][0]
                if location == 'data':
                    source = args[0]['data'][0]
                    args[4]['candidate_data'] = [copy.deepcopy(source)]
                    target = args[4]['candidate_data'][0]
                elif location == 'assertion':
                    source, target = source['verification'][0], target['verification'][0]
                source['business_object'] = {'id': 'ORDER-A', 'source': 'warehouse-A'}  # Business identities, not trace metadata.
                target['business_object'] = {'id': 'ORDER-B', 'source': 'warehouse-A'}
                args[1] = approve_p0_scope(args[0], 'synthetic-round', ['EDIT', 'LINK'], 'SIMULATED: distinct order objects')
                args[3]['manual_start']['baseline_id'] = args[1]['id']
                result = build_extension(*args, mode='simulation')
                self.assertNotIn('step_reference', result['batch']['cases'][0]['steps'][0])
                self.assertEqual(expanded(result['batch'])['cases'][0]['steps'], args[4]['candidates'][0]['steps'])  # Full target and order survive.

    def test_conflicting_current_data_is_not_silently_selected(self):
        args = reuse_design()  # Conflicting authored values must return to source clarification.
        item = copy.deepcopy(args[0]['data'][0])
        args[4]['candidate_data'] = [item, dict(item, value='contradictory value')]
        with self.assertRaisesRegex(ValueError, 'Duplicate candidate data identity'):
            build_extension(*args, mode='simulation')

    def test_dynamic_values_bind_current_case(self):
        from step_reuse import expanded  # Public reconstruction of the authored batch.
        args = list(reuse_design())  # Start with full source and target designs.
        source = args[0]['data'][0]
        source['generation_rule'] = 'unique title per case, maximum 20 characters'
        from p0_evidence import approve_p0_scope
        args[1] = approve_p0_scope(args[0], 'synthetic-round', ['EDIT', 'LINK'], 'SIMULATED: approve dynamic baseline')
        args[3]['manual_start']['baseline_id'] = args[1]['id']
        for index, case in enumerate(args[4]['candidates']):
            item = copy.deepcopy(source)
            item.update(id='current-' + str(index), value='Current ' + str(index))
            args[4]['candidate_data'].append(item)
            case['steps'][0]['data_refs'] = [item['id']]
            case['reuse_assessments'] = copy.deepcopy(args[4]['candidates'][0]['reuse_assessments'])
        result = build_extension(*args, mode='simulation')
        self.assertTrue(all('step_reference' in case['steps'][0] for case in result['batch']['cases']))
        restored = expanded(result['batch'])
        self.assertEqual([case['steps'][0]['data_refs'] for case in restored['cases']], [['current-0'], ['current-1']])
        self.assertIn('Current 0', result['xmind_markdown'])
        self.assertIn('Current 1', result['xmind_markdown'])
        for field in ('validity', 'object_ref'):
            conflicting = copy.deepcopy(args)
            conflicting[4]['candidate_data'][1][field] = 'different business condition'
            output = build_extension(*conflicting, mode='simulation')
            self.assertNotIn('step_reference', output['batch']['cases'][1]['steps'][0])
        tampered = copy.deepcopy(result['batch'])
        next(item for item in tampered['data'] if item['id'] == 'current-1')['value'] = 'neighbor value'
        blocked = render_extension(tampered)
        self.assertIn('HIGH', blocked['blocked_case_ids'])
        self.assertIn('LOW', blocked['ready_case_ids'])
        self.assertIn('binding changed', str(blocked['blockers']))
        args[4]['candidate_data'][1]['generation_rule'] = 'exactly 20 characters'
        changed = build_extension(*args, mode='simulation')
        self.assertNotIn('step_reference', changed['batch']['cases'][1]['steps'][0])

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
                blocked = render_extension(batch)
                self.assertIn('LOW', blocked['blocked_case_ids'])
                self.assertIn('step reference', str(blocked['blockers']))
                self.assertTrue(any(row['status'] != 'complete' for row in blocked['coverage']['checks']))

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
        session = review(session, dict(approved=True, actual_reply='SIMULATED: reviewed complete source and restored target endpoint', content_version=batch['content_version'], case_ids=['LOW']), source_catalog=args[0])
        batch = session['batch']
        human = render_chat(batch, ['LOW'])['human_view']
        self.assertIn('整步引用', human)
        self.assertIn(args[0]['cases'][0]['title'], human)
        row = next(line for line in human.splitlines() if '| Enter notice title |' in line)
        self.assertIn(args[0]['cases'][0]['steps'][0]['expected'][0]['text'], row)
        self.assertIn(args[0]['data'][0]['value'], row)
        self.assertNotIn('见引用步骤', human)
        result = merge_reviewed(args[0], batch, dict(kind='merge_instruction', actual_reply='SIMULATED: merge only LOW', content_version=batch['content_version'], baseline_version=args[0]['content_version'], case_ids=['LOW']), target_kind='isolated')
        self.assertEqual(result['cases'][0]['status'], 'applied')
        self.assertTrue(result['catalog']['step_definitions'])
        changed = copy.deepcopy(batch)
        changed['cases'][0]['steps'].reverse()
        blocked = render_extension(changed)
        self.assertIn('LOW', blocked['blocked_case_ids'])
        self.assertIn('endpoint', str(blocked['blockers']))

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
            review(session, {'case_ids': [batch['cases'][0]['id']]})  # Check the explicitly requested dependent scope.

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
        blocked = render_extension(result['batch'])
        self.assertIn('LOW', blocked['blocked_case_ids'])
        self.assertIn('reference', str(blocked['blockers']))


if __name__ == '__main__':
    unittest.main()
