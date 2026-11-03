"""Native file boundary; synthetic archives never establish client acceptance."""
import tempfile
import unittest
import json
import zipfile
from pathlib import Path

from test_feedback import scope, confirm
from xmind_feedback import prepare_xmind_feedback


class XmindFeedbackTests(unittest.TestCase):
    def test_native_scalar_edits_use_existing_summary_and_both_views(self):
        original = scope()
        lines = original['xmind_markdown'].splitlines()
        root = {'title': lines[0][2:], 'children': {'attached': []}}
        stack = [(-1, root)]
        for line in lines[1:]:
            level = (len(line) - len(line.lstrip())) // 2
            topic = {'title': line.strip()[2:]}
            while stack[-1][0] >= level:
                stack.pop()
            stack[-1][1].setdefault('children', {}).setdefault('attached', []).append(topic)
            stack.append((level, topic))
        def revise(topic):
            topic['title'] = topic['title'].replace('Sample notice', 'Revised synthetic notice').replace(
                'Saved message is visible', 'Revised saved message is visible')
            for child in topic.get('children', {}).get('attached', []):
                revise(child)
        revise(root)
        with tempfile.TemporaryDirectory() as directory:
            returned = Path(directory) / 'returned.xmind'
            with zipfile.ZipFile(returned, 'w') as archive:
                archive.writestr('content.json', json.dumps([{'rootTopic': root}]))
            pending = prepare_xmind_feedback(original['batch'], returned,
                actual_reply='SIMULATED: edited native file')
            self.assertEqual(pending['status'], 'ready_for_clarification')
            self.assertEqual(pending['channel'], 'xmind')
            self.assertEqual(len(pending['changes']), 3)  # shared data and two case expectations
            self.assertEqual(original['batch']['data'][0]['value'], 'Sample notice')
            updated = confirm(pending)
            self.assertEqual(updated['batch']['feedback_history'][-1]['channel'], 'xmind')
            self.assertEqual(updated['batch']['feedback_history'][-1]['returned_source']['sha256'],
                             pending['returned_source']['sha256'])
            for view in ('human_view', 'xmind_markdown'):
                self.assertIn('Revised synthetic notice', updated[view])
                self.assertIn('Revised saved message is visible', updated[view])

            # Unknown case/path, a second sheet or unprojected notes must never
            # be guessed into a candidate update. These are format-only samples.
            import copy
            for broken in ('identity', 'path', 'notes', 'second_sheet'):
                changed = copy.deepcopy(root)
                def break_topic(topic):
                    if topic['title'].startswith('EDIT '):
                        if broken == 'identity':
                            topic['title'] = 'UNKNOWN unknown case'
                        if broken == 'notes':
                            topic['notes'] = {'plain': {'content': 'Different business condition'}}
                    if topic['title'] == 'Notes' and broken == 'path':
                        topic['title'] = 'Unknown module'
                    for child in topic.get('children', {}).get('attached', []):
                        break_topic(child)
                break_topic(changed)
                sheets = [{'rootTopic': changed}]
                if broken == 'second_sheet':
                    sheets *= 2
                with zipfile.ZipFile(returned, 'w') as archive:
                    archive.writestr('content.json', json.dumps(sheets))
                rejected = prepare_xmind_feedback(original['batch'], returned,
                    actual_reply='SIMULATED: ambiguous native return')
                self.assertEqual(rejected['status'], 'pending_verification', broken)
                self.assertNotIn('batch', rejected)

    def test_unsupported_file_retained_pending_without_guessing(self):
        with tempfile.TemporaryDirectory() as directory:
            returned = Path(directory) / 'returned.xmind'
            returned.write_bytes(b'unsupported legacy or corrupt document')
            original = returned.read_bytes()
            batch = scope()['batch']
            result = prepare_xmind_feedback(batch, returned,
                actual_reply='SIMULATED: attached native file')
            self.assertEqual(result['status'], 'pending_verification')
            self.assertNotIn('batch', result)
            self.assertEqual(returned.read_bytes(), original)
            self.assertEqual(result['source']['size_bytes'], len(original))


if __name__ == '__main__':
    unittest.main()
