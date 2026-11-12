"""Synthetic public delivery contracts; cases remain unexecuted."""
import copy  # Check source immutability.
import unittest  # Public regression seam.
from authoring import build_batch  # Reuse the supported compiler.
from test_authoring import sample  # Explicit synthetic source.
import presentation  # Public chat projection entry.


class ChatDeliveryTests(unittest.TestCase):
    def test_explicit_selection_has_complete_cases_and_no_source_mutation(self):
        batch = build_batch(*sample())['batch']  # Start with a real candidate.
        original = copy.deepcopy(batch)  # Projection must not edit this source.
        result = presentation.render_chat(batch, [batch['cases'][0]['id']])  # Explicit one-case request.
        self.assertIn('Saved message is visible', result['human_view'])  # Preserve the expected check.
        self.assertEqual(result['content_version'], batch['content_version'])  # Bind displayed content.
        self.assertEqual(batch, original)  # Read-only presentation.
        self.assertNotIn('human_view', presentation.render_chat(batch))  # Default is scope delivery.

    def test_nine_of_ten_and_invalid_selections(self):
        batch = build_batch(*sample())['batch']  # Synthetic full source.
        prototype = batch['cases'][0]  # Preserve complete business content.
        batch['cases'] = [dict(copy.deepcopy(prototype), id=f'C{i}', title=f'模拟用例{i}') for i in range(10)]  # Ten distinct identities.
        ids = [case['id'] for case in batch['cases']]  # Internal selection only.
        result = presentation.render_chat(batch, ids[:9])  # Inclusive upper bound.
        self.assertEqual(result['human_view'].count('# 模拟用例'), 9)  # Exactly the requested cases.
        self.assertNotIn('模拟用例9', result['human_view'])  # Unselected case stays outside chat.
        self.assertEqual(len(batch['cases']), 10)  # No source deletion.
        for request in ([], ids, ['missing'], ['C0', 'C0'], 'C0'):  # No implicit all, skipping or truncation.
            with self.subTest(request=request), self.assertRaises(ValueError):
                presentation.render_chat(batch, request)  # Validate actual requested identities.

    def test_selected_case_keeps_reference_names_preparation_and_regenerated_version(self):
        from test_feedback import scope, confirm  # Synthetic public feedback workflow.
        from feedback import prepare_feedback  # Same entry used by actual chat feedback.
        batch = scope()['batch']  # EDIT and LINK have stable identities.
        batch['cases'][1]['title'] = '模拟关联来源'  # Linked case remains outside the requested display.
        batch['cases'][0]['steps'][0]['linked_source'] = {'case_id': 'LINK'}  # Business rule references a source.
        batch['cases'][0]['common_preconditions_note'] = {'text': '模拟准备规则完整保留'}  # Required preparation.
        shown = presentation.render_chat(batch, ['EDIT'])  # Only the consuming case is requested.
        self.assertIn('模拟关联来源', shown['human_view'])  # Resolve using the complete candidate.
        self.assertIn('模拟准备规则完整保留', shown['human_view'])  # Preserve preparation in chat.
        self.assertNotIn('# 模拟关联来源', shown['human_view'])  # No accidental extra case.
        pending = prepare_feedback(batch, 'chat', actual_reply='SIMULATED: revise the title', changes=[  # Real public proposal.
            {'collection': 'cases', 'id': 'EDIT', 'path': ['title'], 'value': '模拟修改后的标题'}])  # Stable ID survives rename.
        updated = confirm(pending)['batch']  # Deterministic fixture approval, not a behavioral transcript.
        revised = presentation.render_chat(updated, ['EDIT'])  # Re-display current accepted candidate.
        self.assertIn('模拟修改后的标题', revised['human_view'])  # Actual changed content appears.
        self.assertNotEqual(revised['content_version'], shown['content_version'])  # Version tracks the applied edit.
        self.assertEqual(updated['cases'][1], batch['cases'][1])  # Unselected case remains unchanged.

    def test_extension_selection_keeps_full_scope_and_single_case_compatibility(self):
        from test_extension import expansion  # Synthetic design and P0 evidence only.
        from extension import build_extension, render_extension  # Existing public regeneration seam.
        batch = build_extension(*expansion(), mode='simulation')['batch']  # No real execution evidence.
        default = render_extension(batch)  # Batch delivery has no chat dump.
        pair = render_extension(batch, case_ids=['LOW', 'HIGH'])  # Requested two-case display.
        self.assertNotIn('human_view', default)  # Preserve quiet default.
        self.assertEqual(pair['xmind_markdown'], default['xmind_markdown'])  # Display selection does not shrink review scope.
        self.assertEqual(render_extension(batch, case_id='LOW')['human_view'], presentation.render_chat(batch, ['LOW'])['human_view'])  # Legacy caller follows the same semantics.
        with self.assertRaises(ValueError):
            render_extension(batch, case_id='LOW', case_ids=['HIGH'])  # Competing selection sources are ambiguous.


if __name__ == '__main__':
    unittest.main()  # Local synthetic checks only.
