"""Synthetic public review and feedback regression; no real business execution."""
import copy
import unittest
import json
import tempfile
import zipfile
from pathlib import Path
from xmind_feedback import prepare_xmind_feedback
from authoring import render_batch
from feedback import prepare_feedback
from test_aggregation import synthetic_scope


class ModuleHandoffTests(unittest.TestCase):
    def test_module_notes_keep_business_conditions_and_roundtrip(self):
        batch = synthetic_scope()['batch']  # Existing scoped public input.
        first, second = batch['cases']  # Parent and child both own cases.
        second['module_path'] = first['module_path'] + ['子模块']
        first['technical_handoff'] = {'reuse_policy': '每次重新核对授权', 'invalidation_action': '失效后重新澄清'}
        first['steps'][0]['validity'] = '当日有效'  # Business applicability must remain in the step.
        before = copy.deepcopy(batch)
        shown = render_batch(batch)
        self.assertEqual(shown['xmind_markdown'].count('- 资料与Agent交接说明'), 2)
        for view in ('human_view', 'xmind_markdown'):
            self.assertIn('每次重新核对授权', shown[view])
            self.assertIn('当日有效', shown[view])
        pending = prepare_feedback(batch, 'markdown', markdown=shown['xmind_markdown'], actual_reply='SIMULATED unchanged')
        self.assertEqual(pending['changes'], [])
        self.assertEqual(batch, before)

    def test_distinct_paths_and_parent_without_direct_cases(self):
        batch = synthetic_scope()['batch']  # No parent owns cases in this variant.
        batch['cases'][1]['module_path'][1] = '另一平台'
        shown = render_batch(batch)
        self.assertEqual(shown['xmind_markdown'].count('- 资料与Agent交接说明'), 2)
        self.assertEqual(shown['xmind_markdown'].count('- 模拟项目\n'), 1)
        self.assertNotIn('OTHER', shown['xmind_markdown'])  # Omitted catalog cases stay omitted.

    def test_native_roundtrip_and_instruction_edit_need_interpretation(self):
        batch = synthetic_scope()['batch']
        batch['cases'][0]['technical_handoff'] = {'reuse_policy': '每次重新核对授权'}
        shown = render_batch(batch)['xmind_markdown']
        with self.assertRaisesRegex(ValueError, 'interpretation'):
            prepare_feedback(batch, 'markdown', markdown=shown.replace('每次重新核对授权', '直接执行'), actual_reply='SIMULATED ambiguous instruction edit')
        lines = shown.splitlines()
        root = {'title': lines[0][2:]}
        stack = [(-1, root)]
        for line in lines[1:]:
            depth = (len(line) - len(line.lstrip())) // 2
            node = {'title': line.strip()[2:]}
            while stack[-1][0] >= depth:
                stack.pop()
            stack[-1][1].setdefault('children', {}).setdefault('attached', []).append(node)
            stack.append((depth, node))
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'synthetic.xmind'
            with zipfile.ZipFile(path, 'w') as archive:
                archive.writestr('content.json', json.dumps([{'rootTopic': root}]))
            pending = prepare_xmind_feedback(batch, path, actual_reply='SIMULATED unchanged native return')
        self.assertEqual(pending['changes'], [])


if __name__ == '__main__':
    unittest.main()
