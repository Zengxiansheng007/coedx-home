"""Synthetic shared-source changes through the existing feedback boundary."""
import copy
import unittest
from extension import build_extension
from test_local_step_feedback import shared_design
from feedback import prepare_feedback
from test_feedback import confirm
from step_reuse import expanded
from authoring import _digest


class SharedFeedbackTests(unittest.TestCase):
    def test_three_review_cycles_keep_flat_lossless_history(self):
        args = shared_design()  # Exercise public extension and confirmed feedback.
        batch = build_extension(*args, mode='simulation')['batch']
        source = copy.deepcopy(args[0]['cases'][0])
        batch['cases'].append(source)
        batch['selection'].append(dict(case_id=source['id'], action='related', reason='SIMULATED source'))
        base = batch['initial_copy_baseline']
        base['cases'].append(copy.deepcopy(source))
        base['copy_version'] = _digest({k: base[k] for k in ('cases', 'data', 'selection', 'step_definitions')})
        expected = []  # Preserve each prior complete source exactly once.
        for index in range(3):
            current = batch['cases'][-1]
            expected.append(copy.deepcopy({k: v for k, v in current.items() if k != 'shared_definition_history'}))
            old = batch['step_definitions'][-1]
            new = dict(copy.deepcopy(old), title='SIMULATED title ' + str(index))
            request = dict(explicit_request='SIMULATED formatting', definition_digest=_digest(old), replacement=new)
            batch = confirm(prepare_feedback(batch, 'chat', actual_reply=request['explicit_request'], shared_change=request))['batch']
        self.assertEqual(batch['cases'][-1]['shared_definition_history'], expected)  # Linear and lossless.

    def test_referenced_handoff_preserves_current_owner_and_step_scope(self):
        from p0_evidence import approve_p0_scope
        from module_handoff import module_notes
        from scoped_review import _render
        args = list(shared_design())  # Author identical full source and target instructions before compaction.
        instruction = '必须重新核对输入约束'
        args[0]['cases'][0]['steps'][0]['technical_handoff'] = dict(reuse_policy=instruction)
        for case in args[4]['candidates']:
            case['steps'][0]['technical_handoff'] = dict(reuse_policy=instruction)
        args[1] = approve_p0_scope(args[0], 'synthetic-round', ['EDIT', 'LINK'], 'SIMULATED: handoff baseline')
        args[3]['manual_start']['baseline_id'] = args[1]['id']
        batch = build_extension(*args, mode='simulation')['batch']
        self.assertIn('step_reference', batch['cases'][0]['steps'][0])
        frozen = copy.deepcopy(batch)
        notes = module_notes(batch)
        for case in batch['cases']:
            owner = next(lines for title, lines in notes[tuple(case['module_path'])] if title == case['title'])
            self.assertTrue(any('测试步骤 1（' in line and instruction in line for line in owner))
            self.assertTrue(any('测试步骤 1：' in line and '修改须重新核对' in line for line in owner))
        rendered = _render(batch)
        self.assertIn(instruction, str(rendered['human_view']))
        self.assertIn(instruction, rendered['xmind_markdown'])
        self.assertEqual(batch, frozen)  # Projection never rewrites compact candidates.

    def test_changed_data_is_version_bound(self):
        for shown in (False, True):  # Both review projections must preserve data semantics.
            for choice in ('reference', 'independent', 'mixed'):
                with self.subTest(shown=shown, choice=choice):
                    args = shared_design()
                    batch = build_extension(*args, mode='simulation')['batch']
                    if shown:
                        source = copy.deepcopy(args[0]['cases'][0])
                        batch['cases'].append(source)
                        batch['selection'].append(dict(case_id=source['id'], action='related', reason='SIMULATED source'))
                        base = batch['initial_copy_baseline']
                        base['cases'].append(copy.deepcopy(source))
                        base['copy_version'] = _digest({k: base[k] for k in ('cases', 'data', 'selection', 'step_definitions')})
                    old = copy.deepcopy(batch)
                    new = copy.deepcopy(batch['step_definitions'][0])
                    new['data'][0]['value'] = 'SIMULATED revised input'
                    new['data'][0]['generation_rule'] = 'SIMULATED revised generation rule'
                    extra = dict(copy.deepcopy(new['data'][0]), id='extra-input', value='SIMULATED second input')
                    new['data'].append(extra)
                    new['step']['data_refs'].append(extra['id'])
                    new['semantic_version'] = 'synthetic-data-v2'
                    request = dict(explicit_request='SIMULATED change shared input', definition_digest=_digest(batch['step_definitions'][0]), replacement=new,
                        assessments=[dict(case_id=c, disposition=('reference' if c == 'LOW' else 'independent') if choice == 'mixed' else choice, reason='SIMULATED assessed') for c in ('LOW', 'HIGH')])
                    updated = confirm(prepare_feedback(batch, 'chat', actual_reply=request['explicit_request'], shared_change=request))['batch']
                    rendered = expanded(updated)
                    data = {d['id']: d for d in rendered['data']}
                    for case in rendered['cases']:
                        changed = case['priority'] == 'P0' or choice == 'reference' or (choice == 'mixed' and case['id'] == 'LOW')
                        expected = 'SIMULATED revised input' if changed else 'Sample notice'
                        self.assertEqual(data[case['steps'][0]['data_refs'][0]]['value'], expected)
                        if changed:
                            self.assertEqual(data[case['steps'][0]['data_refs'][1]]['value'], 'SIMULATED second input')
                            self.assertEqual(data[case['steps'][0]['data_refs'][0]]['generation_rule'], 'SIMULATED revised generation rule')
                    self.assertIn(old['step_definitions'][0], updated['step_definitions'])
                    self.assertTrue(all(d in updated['data'] for d in old['data']))
                    self.assertEqual(batch, old)
                    followup = copy.deepcopy(new)
                    followup['title'] = 'SIMULATED next title'
                    again = dict(explicit_request='SIMULATED formatting', definition_digest=_digest(new), replacement=followup)
                    confirm(prepare_feedback(updated, 'chat', actual_reply=again['explicit_request'], shared_change=again))  # Versioned source IDs remain maintainable.
                    local = prepare_feedback(updated, 'chat', actual_reply='SIMULATED local action', changes=[dict(collection='cases', id='LOW', path=['steps', 0, 'operation'], value='SIMULATED local only')])
                    local_result = confirm(local)['batch']
                    self.assertEqual(local_result['step_definitions'], updated['step_definitions'])
                    self.assertEqual(local_result['cases'][1], updated['cases'][1])

    def test_reviewed_source_change_preserves_history_and_independent_case(self):
        args = shared_design()
        other = copy.deepcopy(args[4]['candidates'][1])
        other['id'] = 'UNRELATED-NEW'
        other.pop('reuse_assessments')
        args[4]['candidates'].append(other)
        batch = build_extension(*args, mode='simulation')['batch']
        source = copy.deepcopy(args[0]['cases'][0])
        batch['cases'].append(source)
        batch['selection'].append(dict(case_id=source['id'], action='related', reason='SIMULATED displayed shared source'))
        base = batch['initial_copy_baseline']
        base['cases'].append(copy.deepcopy(source))
        base['copy_version'] = _digest({k: base[k] for k in ('cases', 'data', 'selection', 'step_definitions')})
        frozen = copy.deepcopy(batch)
        definition = copy.deepcopy(batch['step_definitions'][0])
        definition['step']['operation'] = 'SIMULATED revised common action'
        definition['semantic_version'] = 'synthetic-v2'
        request = dict(explicit_request='SIMULATED change P0 shared definition',
            definition_digest=_digest(batch['step_definitions'][0]), replacement=definition,
            assessments=[dict(case_id='LOW', disposition='reference', reason='SIMULATED still applicable'),
                         dict(case_id='HIGH', disposition='independent', reason='SIMULATED retains old requirement')])
        pending = prepare_feedback(batch, 'chat', actual_reply=request['explicit_request'], shared_change=request)
        self.assertEqual(batch, frozen)
        self.assertEqual(len(pending['shared_change']['assessments']), 2)
        from clarification import respond, summarize
        from feedback import apply_feedback
        held = copy.deepcopy(pending)
        held['grill'] = summarize(respond(held['grill'], [dict(question_id=q['id'], decision='deferred',
            actual_reply='SIMULATED defer this impact') for q in held['grill']['round_questions']]))
        retained = apply_feedback(held, dict(confirmed=True, actual_reply='SIMULATED retain pending',
            summary_id=held['grill']['summary']['id']))['batch']
        self.assertEqual(retained['step_definitions'], frozen['step_definitions'])
        self.assertEqual(expanded(retained)['cases'][0]['steps'], expanded(frozen)['cases'][0]['steps'])
        updated = confirm(pending)['batch']
        self.assertIn('step_reference', updated['cases'][0]['steps'][0])
        self.assertNotIn('step_reference', updated['cases'][1]['steps'][0])
        self.assertEqual(expanded(updated)['cases'][0]['steps'][0]['operation'], definition['step']['operation'])
        self.assertEqual(expanded(updated)['cases'][1]['steps'][0]['operation'], expanded(frozen)['cases'][1]['steps'][0]['operation'])
        self.assertIn(frozen['step_definitions'][0], updated['step_definitions'])
        self.assertEqual(updated['cases'][2], frozen['cases'][2])
        self.assertEqual(updated['cases'][3]['steps'][0]['operation'], definition['step']['operation'])
        self.assertEqual(updated['cases'][3]['semantic_version'], definition['semantic_version'])
        self.assertEqual(updated['cases'][3]['shared_definition_history'][0]['steps'], frozen['cases'][3]['steps'])
        self.assertEqual(batch, frozen)

    def test_formatting_and_invalid_identity(self):
        batch = build_extension(*shared_design(), mode='simulation')['batch']
        old = batch['step_definitions'][0]
        new = copy.deepcopy(old)
        new['title'] = 'SIMULATED presentation title'
        request = dict(explicit_request='SIMULATED format P0', definition_digest=_digest(old), replacement=new)
        pending = prepare_feedback(batch, 'chat', actual_reply=request['explicit_request'], shared_change=request)
        self.assertTrue(pending['shared_change']['formatting_only'])
        self.assertEqual(pending['affected_case_ids'], [])
        updated = confirm(pending)
        self.assertIn(new['title'], updated['xmind_markdown'])
        request['definition_digest'] = 'stale'
        with self.assertRaisesRegex(ValueError, 'version missing'):
            prepare_feedback(batch, 'chat', actual_reply='SIMULATED', shared_change=request)
        request['explicit_request'] = ''
        with self.assertRaisesRegex(ValueError, 'Explicit'):
            prepare_feedback(batch, 'chat', actual_reply='SIMULATED', shared_change=request)


if __name__ == '__main__':
    unittest.main()
