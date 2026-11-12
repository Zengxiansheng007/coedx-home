"""Old-emitter/new-consumer feedback on frozen SIMULATED review artifacts."""
import copy  # Compare the retained baseline after interpreting a return.
import json  # Read the frozen public-emitter fixture.
from pathlib import Path  # Resolve fixture independently of current directory.
import unittest  # Exercise public feedback, never private mapping helpers.
import tempfile  # Isolate synthetic native returns.
import zipfile  # Build the already supported native container.

from feedback import prepare_feedback  # The supported return boundary.
from identity_test_support import bound_cases  # Explicit simulated identity decision.
from scoped_review import render_review_batch  # Verify normal delivery remains clean.
from xmind_feedback import prepare_xmind_feedback  # Same feedback contract through the native adapter.


class LegacyFeedbackTests(unittest.TestCase):
    def setUp(self):
        fixture = Path(__file__).resolve().parents[1] / 'assets/fixtures/legacy-review-294a12a.json'  # Frozen before repair.
        saved = json.loads(fixture.read_text(encoding='utf-8'))  # Never regenerate using today's renderer.
        self.batch, self.markdown = saved['batch'], saved['markdown']  # Retain exact initial semantics and layout.

    def test_old_emitter_scalar_return_binds_exact_operation(self):
        before = copy.deepcopy(self.batch)  # Interpretation cannot mutate the candidate.
        old = self.batch['cases'][0]['steps'][0]['operation']  # Change only the first projected operation.
        returned = self.markdown.replace(old, 'SIMULATED revised operation', 1)  # Other case and rule history stay intact.
        pending = prepare_feedback(self.batch, 'markdown', markdown=returned,
            actual_reply='SIMULATED revise first operation', case_bindings=bound_cases(self.batch, returned))  # Explicit identity evidence.
        self.assertEqual([(c['id'], c['path'], c['value']) for c in pending['changes']],
                         [('EDIT', ['steps', 0, 'operation'], 'SIMULATED revised operation')])  # Exact intended proposal only.
        self.assertEqual(self.batch, before)  # Original rules, content and baseline survive.

    def test_legacy_audit_structure_identity_and_shared_conflicts_still_rejected(self):
        old = self.batch['cases'][0]['steps'][0]['operation']  # Known editable leaf.
        edited = self.markdown.replace(old, 'SIMULATED revised operation', 1)  # Valid edit accompanies each invalid edit.
        variants = [edited.replace('SIMULATED keep original rule', 'SIMULATED forged audit', 1),
                    edited.replace('updates / path', 'forged label', 1),
                    edited + '  - SIMULATED unknown topology\n',
                    edited.replace('Notes', 'Unknown module', 1),
                    edited.replace(self.batch['content_version'], 'stale-version', 1),
                    edited.replace('Sample notice', 'SIMULATED conflicting shared data', 1)]  # All are outside scalar contract.
        for returned in variants:
            with self.subTest(returned=returned[-80:]), self.assertRaises(ValueError):
                prepare_feedback(self.batch, 'markdown', markdown=returned, actual_reply='SIMULATED invalid return',
                                 case_bindings=bound_cases(self.batch, returned))  # Bindings cannot authorize protected edits.
        with self.assertRaises(ValueError):
            prepare_feedback(self.batch, 'markdown', markdown=edited, actual_reply='SIMULATED unbound edit')  # Changed topic needs explicit identity.
        bindings = bound_cases(self.batch, edited)  # Tamper binding independently of source content.
        bindings['EDIT']['source_version'] = 'stale-version'  # Stale identity evidence cannot be reused.
        with self.assertRaises(ValueError):
            prepare_feedback(self.batch, 'markdown', markdown=edited, actual_reply='SIMULATED stale binding', case_bindings=bindings)

    def test_new_delivery_and_supported_native_return_preserve_history(self):
        current = render_review_batch(self.batch)  # Normal public renderer never selects legacy mode.
        self.assertNotIn('updates / path', current['xmind_markdown'])  # New delivery excludes the audit payload.
        self.assertIn('SIMULATED effective rule', current['human_view'])  # Effective business meaning remains.
        old = self.batch['cases'][0]['steps'][0]['operation']  # Change a single business scalar.
        for markdown in (self.markdown, current['xmind_markdown']):
            returned = markdown.replace(old, 'SIMULATED native revised operation', 1)  # Old and current contracts both work.
            lines = returned.splitlines()  # Build a format-only native fixture, no client acceptance claim.
            root = {'title': lines[0][2:]}
            stack = [(-1, root)]  # Preserve all topic ancestry and rule rows.
            for line in lines[1:]:
                level = (len(line) - len(line.lstrip())) // 2  # Native levels match the frozen hierarchy.
                topic = {'title': line.strip()[2:]}
                while stack[-1][0] >= level:
                    stack.pop()  # Find the actual parent.
                stack[-1][1].setdefault('children', {}).setdefault('attached', []).append(topic)
                stack.append((level, topic))  # Retain siblings at the same level.
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'simulated-return.xmind'  # No real native documents are touched.
                with zipfile.ZipFile(path, 'w') as archive:
                    archive.writestr('content.json', json.dumps([{'rootTopic': root}]))  # Supported single-sheet payload.
                before = path.read_bytes()  # The adapter must retain returned bytes.
                pending = prepare_xmind_feedback(self.batch, path, actual_reply='SIMULATED native return',
                                                 case_bindings=bound_cases(self.batch, returned))
                self.assertEqual(pending['status'], 'ready_for_clarification')  # Actual adapter acceptance, no fallback claim.
                self.assertEqual([(c['id'], c['path']) for c in pending['changes']], [('EDIT', ['steps', 0, 'operation'])])
                self.assertEqual(path.read_bytes(), before)  # Original native artifact survives interpretation.


if __name__ == '__main__':
    unittest.main()  # Standard library runner needs no extra dependencies.
