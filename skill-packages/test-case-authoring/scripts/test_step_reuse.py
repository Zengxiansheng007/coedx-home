"""Synthetic public authoring tests for whole-step P0 reuse."""
import unittest
from test_extension import expansion
from extension import build_extension, render_extension


class StepReuseTests(unittest.TestCase):
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
