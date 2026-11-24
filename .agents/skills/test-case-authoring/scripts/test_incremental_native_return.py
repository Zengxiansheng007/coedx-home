"""Synthetic native documents for the versioned review entry."""

import json
from pathlib import Path
import re
import tempfile
import unittest
import zipfile

from module_handoff import write_artifacts
from feedback import prepare_feedback
from qa_record import advance_record, read_record, start_record
from scoped_review import render_review_batch
from test_feedback import confirm
from test_incremental_review import review_sample
from xmind_feedback import prepare_xmind_feedback


def native_file(path, markdown, *, change_link=None):
    lines = markdown.splitlines()
    root = {'title': lines[0][2:]}
    stack = [(-1, root)]
    for line in lines[1:]:
        depth = (len(line) - len(line.lstrip())) // 2
        label = line.lstrip()[2:]
        node = {'title': label}
        link = re.fullmatch(r'\[([^\]]+)\]\(([^)]+)\)', label)
        if link:
            node['title'] = link[1]
            node['href'] = change_link or link[2]
        while stack[-1][0] >= depth:
            stack.pop()
        stack[-1][1].setdefault('children', {}).setdefault('attached', []).append(node)
        stack.append((depth, node))
    with zipfile.ZipFile(path, 'w') as archive:
        archive.writestr('content.json', json.dumps([{'rootTopic': root}]))


class IncrementalNativeReturnTests(unittest.TestCase):
    def test_native_return_recognizes_an_intermediate_markdown_version(self):
        result, _ = review_sample()
        first = confirm(prepare_feedback(
            result['batch'], 'markdown', actual_reply='SIMULATED first edit',
            markdown=result['xmind_markdown'].replace('预期：显示本例默认结果 1', '预期：中间版'),
        ))['batch']
        stored = render_review_batch(first)['xmind_markdown']
        current = confirm(prepare_feedback(
            first, 'markdown', actual_reply='SIMULATED second edit',
            markdown=stored.replace('预期：中间版', '预期：当前版'),
        ))['batch']
        with tempfile.TemporaryDirectory() as directory:
            returned = Path(directory) / 'intermediate.xmind'
            native_file(returned, stored)
            report = prepare_xmind_feedback(current, returned, actual_reply='SIMULATED superseded return')
        self.assertEqual(report['status'], 'superseded_review')
        self.assertEqual(report['returned_version'], first['content_version'])

    def test_saved_native_feedback_resumes_without_duplicate_intake(self):
        from xmind_feedback import start_native_feedback

        result, _ = review_sample()
        result['batch']['questions'] = []
        for case in result['batch']['cases']:
            case['rule_status'] = 'formal'  # Fixture starts with prior rule confirmation.
        original_case = result['batch']['cases'][0]
        original_case['review_status'] = 'approved'
        original_case['final_review'] = dict(
            approved=True, case_ids=[original_case['id']],
            content_version=result['batch']['content_version'], actual_reply='SIMULATED prior approval',
        )
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'original'
            output.mkdir()
            write_artifacts(result, output)
            batch = result['batch']
            path = Path(directory) / 'qa.md'
            start_record(path, 'synthetic-native-feedback', batch, [])
            returned = Path(directory) / 'returned.xmind'
            original = (output / 'xmind.md').read_text(encoding='utf-8')
            native_file(returned, original.replace('预期：显示本例默认结果 1', '预期：显示四个渠道'))
            assessment = start_native_feedback(
                path, returned, actual_reply='SIMULATED clear change', companion_base=output,
                clear_changes=True,
            )
            self.assertEqual(assessment['status'], 'recorded', assessment)
            original_after_intake = path.read_bytes()
            duplicate = start_native_feedback(
                path, returned, actual_reply='SIMULATED repeat input', companion_base=output,
            )
            self.assertEqual(duplicate['status'], 'already_recorded')
            self.assertEqual(path.read_bytes(), original_after_intake)
            returned.unlink()
            self.assertEqual(read_record(path)['batch'], batch)
            state = advance_record(path, 'summarize')
            state = advance_record(path, 'apply_feedback', {
                'confirmed': True, 'actual_reply': 'SIMULATED summary agreed',
                'summary_id': state['summary']['id'],
            })
            self.assertEqual(state['batch']['feedback_history'][-1]['channel'], 'xmind')
            self.assertEqual(state['batch']['cases'][0], batch['cases'][0])
            self.assertEqual(read_record(path)['batch'], state['batch'])
            state = advance_record(path, 'review_feedback', {
                'approved': True, 'actual_reply': 'SIMULATED revised case approved',
                'content_version': state['batch']['content_version'], 'case_ids': ['SIM-1'],
            })
            self.assertEqual(state['batch']['cases'][1]['review_status'], 'approved')
            self.assertEqual(state['batch']['cases'][0]['final_review'], original_case['final_review'])

    def test_exact_link_and_current_scalar_then_stale_reference(self):
        result, _ = review_sample()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'original'
            output.mkdir()
            write_artifacts(result, output)
            batch = result['batch']
            source = (output / 'xmind.md').read_text(encoding='utf-8')
            returned = Path(directory) / 'retained.xmind'
            native_file(returned, source)
            unchanged = prepare_xmind_feedback(
                batch, returned, actual_reply='SIMULATED unchanged', companion_base=output,
            )
            self.assertEqual(unchanged['status'], 'ready_for_clarification')
            self.assertEqual(unchanged['changes'], [])
            edit = source.replace('预期：显示本例默认结果 1', '预期：显示四个渠道')
            native_file(returned, edit)
            outcome = prepare_xmind_feedback(
                batch, returned, actual_reply='SIMULATED local edit', companion_base=output,
            )
            self.assertEqual(outcome['status'], 'ready_for_clarification')
            self.assertEqual([(c['id'], c['path']) for c in outcome['changes']], [
                ('SIM-1', ['steps', 1, 'expected', 0, 'text']),
            ])
            accepted = confirm(outcome)
            current = accepted['batch']
            self.assertEqual(current['feedback_history'][-1]['returned_source'], outcome['returned_source'])
            new_output = Path(directory) / 'current'
            new_output.mkdir()
            write_artifacts(accepted, new_output)
            stale = prepare_xmind_feedback(
                current, returned, actual_reply='SIMULATED superseded file',
                companion_base=new_output,
            )
            self.assertEqual(stale['status'], 'superseded_review')
            self.assertEqual(stale['returned_version'], batch['content_version'])
            self.assertEqual(stale['current_review']['version'], current['content_version'])
            self.assertEqual(stale['current_review']['markdown'], str(new_output / 'xmind.md'))
            self.assertNotIn('changes', stale)

    def test_unknown_material_link_retained_for_verification(self):
        result, _ = review_sample()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'original'
            output.mkdir()
            write_artifacts(result, output)
            returned = Path(directory) / 'material-link.xmind'
            native_file(returned, (output / 'xmind.md').read_text(encoding='utf-8'),
                        change_link='file:///unrelated.md')
            report = prepare_xmind_feedback(result['batch'], returned,
                                           actual_reply='SIMULATED different link', companion_base=output)
            self.assertEqual(report['status'], 'pending_verification')
            self.assertEqual(report['reason_code'], 'native_material_link')
            self.assertIn('资料与 Agent 交接说明', report['location'])


if __name__ == '__main__':
    unittest.main()
