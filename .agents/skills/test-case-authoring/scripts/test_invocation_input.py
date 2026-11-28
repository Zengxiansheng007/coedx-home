"""A reviewer copies exactly one submitted payload from the corresponding operation."""
import copy
import json
import unittest

from source_preparation import render_selection
from test_scoped_review import catalog


class InvocationInputTests(unittest.TestCase):
    def test_copy_two_independent_calls_from_their_own_steps(self):
        full = catalog()
        case = full['cases'][0]
        start = {'nested': {'empty': {}, 'count': 1, 'enabled': False},
                 'message': '<tag> | `text` &\nnext', 'list': []}
        stop = [{'message': None}, 'end']
        for step, ref, value in zip(case['steps'], ('begin', 'end'), (start, stop)):
            step['data_refs'] = [ref]
            full['data'].append(dict(copy.deepcopy(full['data'][0]), id=ref,
                                     object_ref='调用参数', value=value))
        markdown = render_selection(full, [case['id']])['xmind_markdown']
        lines = markdown.splitlines()
        blocks = []
        positions = []
        for index, line in enumerate(lines):
            if line.endswith('（完整 JSON）'):
                child_indent = ' ' * (len(line) - len(line.lstrip()) + 2)
                first = lines[index + 1]
                # A child list item directly owns the payload. The parent label
                # must never be part of the copied item's text.
                self.assertTrue(first.startswith(child_indent + '-     '), first)
                indent = child_indent + '      '
                body = [first[len(indent):]]
                for code_line in lines[index + 2:]:
                    if not code_line.startswith(indent):
                        break
                    body.append(code_line[len(indent):])
                blocks.append('\n'.join(body))
                positions.append(markdown.index(first))
        self.assertEqual(len(blocks), 2)
        self.assertEqual([json.loads(body) for body in blocks], [start, stop])
        for step, position in zip(case['steps'], positions):
            self.assertLess(markdown.index(step['operation']), position)
        self.assertLess(positions[0], markdown.index(case['steps'][1]['operation']))
        self.assertNotIn('```', markdown)
        self.assertNotIn('值 / nested', markdown)
