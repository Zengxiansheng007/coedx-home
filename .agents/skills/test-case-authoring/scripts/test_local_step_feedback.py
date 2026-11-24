"""Synthetic public feedback on shared definitions."""
import copy
import unittest
from test_step_reuse import reuse_design
from extension import build_extension
from feedback import prepare_feedback
from test_feedback import confirm


def shared_design():
    args = reuse_design()
    args[4]['candidates'][1]['reuse_assessments'] = copy.deepcopy(args[4]['candidates'][0]['reuse_assessments'])
    return args


class LocalStepFeedbackTests(unittest.TestCase):
    def test_data_feedback_cannot_implicitly_change_displayed_p0(self):
        from authoring import _digest
        args = shared_design()
        batch = build_extension(*args, mode='simulation')['batch']
        source = copy.deepcopy(args[0]['cases'][0])
        batch['cases'].append(source)
        batch['selection'].append(dict(case_id=source['id'], action='related', reason='SIMULATED displayed source'))
        base = batch['initial_copy_baseline']
        base['cases'].append(copy.deepcopy(source))
        base['copy_version'] = _digest({k: base[k] for k in ('cases', 'data', 'selection', 'step_definitions')})
        frozen = copy.deepcopy(batch)
        pending = prepare_feedback(batch, 'chat', source_catalog=args[0], actual_reply='SIMULATED: adjust current candidate input', changes=[
            dict(collection='data', id=batch['data'][0]['id'], path=['value'], value='changed input')])
        with self.assertRaisesRegex(ValueError, 'unshown|Explicit P0'):
            confirm(pending)  # A global data leaf cannot bypass the shared-source impact proposal.
        self.assertEqual(batch, frozen)

    def test_dynamic_data_feedback_is_scoped_to_current_binding(self):
        from p0_evidence import approve_p0_scope
        args = list(shared_design())
        source = args[0]['data'][0]
        source['generation_rule'] = 'unique title per case, maximum 20 characters'
        args[1] = approve_p0_scope(args[0], 'synthetic-round', ['EDIT', 'LINK'], 'SIMULATED: dynamic baseline')
        args[3]['manual_start']['baseline_id'] = args[1]['id']
        for index, case in enumerate(args[4]['candidates']):
            item = dict(copy.deepcopy(source), id='current-' + str(index), value='Current ' + str(index))
            args[4]['candidate_data'].append(item)
            case['steps'][0]['data_refs'] = [item['id']]
        batch = build_extension(*args, mode='simulation')['batch']
        frozen = copy.deepcopy(batch)
        pending = prepare_feedback(batch, 'chat', source_catalog=args[0], actual_reply='SIMULATED: current data only', changes=[
            dict(collection='data', id='current-0', path=['value'], value='Revised')])
        updated = confirm(pending, source_catalog=args[0])['batch']
        self.assertEqual(pending['affected_case_ids'], ['LOW'])
        self.assertNotIn('step_reference', updated['cases'][0]['steps'][0])
        self.assertEqual(updated['cases'][1], frozen['cases'][1])
        self.assertEqual(updated['step_definitions'], frozen['step_definitions'])
        self.assertEqual(batch, frozen)

    def test_shared_data_feedback_requires_hidden_source_consumers(self):
        args = shared_design()
        batch = build_extension(*args, mode='simulation')['batch']
        frozen = copy.deepcopy(batch)
        pending = prepare_feedback(batch, 'chat', source_catalog=args[0], actual_reply='SIMULATED: edit shared data', changes=[
            dict(collection='data', id=batch['data'][0]['id'], path=['value'], value='changed input')])
        self.assertTrue({'LOW', 'HIGH', 'EDIT', 'LINK'}.issubset(pending['affected_case_ids']))
        with self.assertRaisesRegex(ValueError, 'unshown'):
            confirm(pending, source_catalog=args[0])  # Hidden P0 consumers require a separately authorized complete review.
        self.assertEqual(batch, frozen)

    def test_layout_whitespace_keeps_reference_and_review_scope(self):
        batch = build_extension(*reuse_design(), mode='simulation')['batch']
        old = batch['step_definitions'][0]['step']['operation']
        pending = prepare_feedback(batch, 'chat', actual_reply='SIMULATED: spacing only', changes=[
            dict(collection='cases', id='LOW', path=['steps', 0, 'operation'], value='  ' + old + '  ')])
        self.assertEqual(pending['changes'], [])
        self.assertEqual(pending['affected_case_ids'], [])

    def test_markdown_reference_action_is_local(self):
        from identity_test_support import bound_cases
        result = build_extension(*reuse_design(), mode='simulation')
        old = result['batch']['step_definitions'][0]['step']['operation']
        edited = result['xmind_markdown'].replace(old, 'SIMULATED: revised local action', 1)
        pending = prepare_feedback(result['batch'], 'markdown', actual_reply='SIMULATED: local edit',
            markdown=edited, case_bindings=bound_cases(result['batch'], edited))
        updated = confirm(pending)['batch']
        self.assertNotIn('step_reference', updated['cases'][0]['steps'][0])

    def test_chat_materializes_only_changed_step(self):
        args = shared_design()
        source = copy.deepcopy(args[0])
        result = build_extension(*args, mode='simulation')
        batch = result['batch']
        frozen = copy.deepcopy(batch)
        pending = prepare_feedback(batch, 'chat', actual_reply='SIMULATED: change current action', changes=[
            dict(collection='cases', id='LOW', path=['steps', 0, 'operation'], value='SIMULATED: revised local action')])
        updated = confirm(pending)['batch']
        step = updated['cases'][0]['steps'][0]
        self.assertNotIn('step_reference', step)
        self.assertEqual(step['operation'], 'SIMULATED: revised local action')
        self.assertTrue(step['expected'])
        self.assertTrue(step['verification'])
        self.assertEqual(updated['step_definitions'], frozen['step_definitions'])
        self.assertEqual(updated['cases'][1], frozen['cases'][1])
        self.assertEqual(batch, frozen)
        self.assertEqual(args[0], source)
        self.assertIn('step_reference', updated['cases'][1]['steps'][0])

    def test_native_changed_reference_and_protected_reference(self):
        import json
        import tempfile
        import zipfile
        from pathlib import Path
        from identity_test_support import bound_cases
        from xmind_feedback import prepare_xmind_feedback
        result = build_extension(*shared_design(), mode='simulation')
        old = result['batch']['step_definitions'][0]['step']['operation']
        markdown = result['xmind_markdown'].replace(old, 'SIMULATED: local native action', 1)
        lines = markdown.splitlines()
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
            pending = prepare_xmind_feedback(result['batch'], path, actual_reply='SIMULATED: local native edit',
                case_bindings=bound_cases(result['batch'], markdown))
            updated = confirm(pending)['batch']
        self.assertNotIn('step_reference', updated['cases'][0]['steps'][0])
        self.assertEqual(updated['cases'][1], result['batch']['cases'][1])
        with self.assertRaises(ValueError):
            prepare_feedback(result['batch'], 'chat', actual_reply='SIMULATED: corrupt source', changes=[
                dict(collection='cases', id='LOW', path=['steps', 0, 'step_reference', 'case_id'], value='OTHER')])


if __name__ == '__main__':
    unittest.main()
