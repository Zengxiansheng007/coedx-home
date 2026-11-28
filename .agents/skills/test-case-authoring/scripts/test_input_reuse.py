"""A reviewer can reconstruct a variant input without inheriting the baseline endpoint."""
import copy
import unittest

from source_preparation import render_selection
from test_scoped_review import catalog


def fixture():
    batch = catalog()
    source, target = batch['cases'][:2]
    source['priority'], target['priority'] = 'P0', 'P2'
    for case, value in [(source, {'params': {}, 'empty': 'x', 'omit': {}, 'typed': 1}),
                        (target, {'params': {}, 'empty': '', 'new.key': [1], 'typed': True})]:
        step = case['steps'][0]
        step['id'] = case['id'] + '/submit'
        ref = case['id'] + '/json'
        step['data_refs'] = [ref]
        batch['data'].append(dict(copy.deepcopy(batch['data'][0]), id=ref,
                                  object_ref='请求', value={'input': value}))
    target['steps'][-1]['expected'][0]['text'] = '拒绝提交，本次无新增记录'
    row = dict(step_id=target['steps'][0]['id'], data_id=target['steps'][0]['data_refs'][0],
               p0_case_id=source['id'], p0_step_id=source['steps'][0]['id'],
               p0_data_id=source['steps'][0]['data_refs'][0], source_basis='材料中同一提交框，仅改变请求字段', focus_paths=[['input','params']])
    return batch, {target['id']: [row]}


class InputReuseTest(unittest.TestCase):
    def test_render_assessed_input_changes_independently_of_steps(self):
        from input_reuse import bind_inputs, resolve_input
        original, assessments = fixture()
        batch = bind_inputs(original, assessments)
        source, target = batch['cases'][:2]
        row = batch['input_reuse'][target['id']][0]
        changes = resolve_input(batch, target['id'], row)['changes']
        self.assertEqual(resolve_input(batch, target['id'], row)['retained'],
                         [dict(op='keep', path=['input','params'], after={})])
        self.assertCountEqual(changes, [
            dict(op='remove', path=['input','omit'], before={}),
            dict(op='add', path=['input','new.key'], after=[1]),
            dict(op='replace', path=['input','empty'], before='x', after=''),
            dict(op='replace', path=['input','typed'], before=1, after=True)])
        view = render_selection(batch, [source['id'], target['id']])['xmind_markdown']
        for phrase in ('删除 input.omit', '保留 input.empty，值由 "x" 改为 ""',
                       '保留 input.params，值为 {}', '新增 input["new.key"]，值为 [1]', '保留 input.typed，值由 1 改为 true',
                       source['id'], '第 1 步', '拒绝提交，本次无新增记录'):
            self.assertIn(phrase, view)
        self.assertEqual(view.count('请求（完整 JSON）'), 1)
        self.assertEqual(original['cases'], batch['cases'])

