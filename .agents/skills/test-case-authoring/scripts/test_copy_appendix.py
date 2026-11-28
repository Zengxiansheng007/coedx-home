"""Reviewers can obtain exactly the inputs cited by their current selection."""
import copy
import json
import unittest

from input_reuse import bind_inputs
from scoped_review import build_scoped_review
from source_preparation import render_selection
from test_input_reuse import fixture


def copy_blocks(markdown):
    """Read the copyable child topics independently of the renderer."""
    lines = markdown.splitlines()
    result = []
    for index, line in enumerate(lines):
        if not line.lstrip().startswith('-     '):
            continue
        offset = line.index('-     ') + 6
        body = [line[offset:]]
        for continuation in lines[index + 1:]:
            if not continuation.startswith(' ' * offset):
                break
            body.append(continuation[offset:])
        result.append(json.loads('\n'.join(body)))
    return result


class CopyAppendixTests(unittest.TestCase):
    def test_two_variants_share_one_source_in_appendix_or_body(self):
        full, assessments = fixture()
        source, first, second = full['cases']
        second.update(steps=copy.deepcopy(first['steps']), priority='P1')
        assessments[second['id']] = copy.deepcopy(assessments[first['id']])
        full = bind_inputs(full, assessments)
        source_value = {'input': {'params': {}, 'empty': 'x', 'omit': {}, 'typed': 1}}
        for ids in ([first['id']], [first['id'], second['id']], [first['id'], second['id'], source['id']]):
            with self.subTest(ids=ids):
                md = render_selection(full, ids)['xmind_markdown']
                self.assertIn('待评用例：' + '、'.join(ids), md.splitlines()[2])
                self.assertEqual(copy_blocks(md), [source_value])
                inside = source['id'] in ids
                self.assertEqual(md.splitlines().count('- 供复制'), 0 if inside else 1)
                self.assertEqual(md.count('见该用例正文' if inside else '见文末“供复制”'), min(len(ids), 2))

    def test_two_calls_of_same_p0_survive_a_genuine_premerge_selection(self):
        full, assessments = fixture()
        source, target = full['cases'][:2]
        for case in (source, target):
            # The same box and identical JSON are used at two different times.
            case['steps'][1]['data_refs'] = list(case['steps'][0]['data_refs'])
        first = assessments[target['id']][0]
        assessments[target['id']].append(dict(first, step_id=target['steps'][1]['id'],
                                               p0_step_id=source['steps'][1]['id']))
        full = bind_inputs(full, assessments)
        selection = [dict(case_id=target['id'], action='reuse', reason='检查两次提交')]
        subset = build_scoped_review(full, 'selected', selection, review_layout='incremental-v1')['batch']
        self.assertEqual([c['id'] for c in subset['cases']], [target['id']])
        self.assertNotIn(first['p0_data_id'], [d['id'] for d in subset['data']])
        view = render_selection(subset, source_catalog=full)['xmind_markdown']
        origin = {'input': {'params': {}, 'empty': 'x', 'omit': {}, 'typed': 1}}
        self.assertEqual(copy_blocks(view), [origin, origin])
        appendix = view.split('\n- 供复制\n')[1]
        self.assertIn('第 1 步「请求」', appendix)
        self.assertIn('第 2 步「请求」', appendix)
        stale = copy.deepcopy(full)
        next(d for d in stale['data'] if d['id'] == first['p0_data_id'])['value'] = 'stale-source'
        for parent in (None, stale):
            pending = render_selection(subset, source_catalog=parent)['xmind_markdown']
            self.assertIn('输入复用待核对', pending)
            self.assertNotIn('\n- 供复制\n', pending)
            self.assertNotIn('stale-source', pending)

    def test_distinct_boxes_with_the_same_label_in_one_operation(self):
        full, assessments = fixture()
        source, target = full['cases'][:2]
        for case in (source, target):
            refs = case['steps'][0]['data_refs']
            data = next(d for d in full['data'] if d['id'] == refs[0])
            second = dict(data, id=data['id'] + '-2', value={'order': 2})
            full['data'].append(second)
            refs.append(second['id'])
        row = assessments[target['id']][0]
        assessments[target['id']].append(dict(row, data_id=row['data_id']+'-2',
                                              p0_data_id=row['p0_data_id']+'-2'))
        batch = bind_inputs(full, assessments)
        md = render_selection(batch, [target['id']])['xmind_markdown']
        body, appendix = md.split('\n- 供复制\n')
        for label in ('请求（同名框 1）', '请求（同名框 2）'):
            self.assertIn(label, body)
            self.assertIn(label, appendix)
        self.assertEqual(copy_blocks(appendix)[1], {'order': 2})
        full_md = render_selection(batch, [target['id'], source['id']])['xmind_markdown']
        for label in ('请求（同名框 1）', '请求（同名框 2）'):
            self.assertIn(label + '（完整 JSON）', full_md)
