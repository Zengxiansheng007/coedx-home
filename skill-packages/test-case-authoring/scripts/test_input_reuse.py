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
    def test_reassigned_target_box_is_pending_and_remains_copyable(self):
        from input_reuse import bind_inputs
        original, assessments = fixture()
        bound = bind_inputs(original, assessments)
        target = bound['cases'][1]
        target['steps'][0]['data_refs'] = [bound['cases'][0]['steps'][0]['data_refs'][0]]
        view = render_selection(bound, [target['id']])['xmind_markdown']
        self.assertIn('输入复用待核对', view)
        self.assertIn(target['id']+'/submit', view)
        self.assertIn('请求（完整 JSON）', view)
        self.assertNotIn('复用同版 P0', view)

    def test_outside_scope_requires_exact_parent_and_stale_calls_keep_own_input(self):
        from input_reuse import bind_inputs
        from scoped_review import build_scoped_review
        original, assessments = fixture()
        full = bind_inputs(original, assessments)
        source, target = full['cases'][:2]
        scope = build_scoped_review(full, '局部', [dict(case_id=target['id'], action='related', reason='评审')])['batch']
        self.assertIn('复用同版 P0', render_selection(scope, source_catalog=full)['xmind_markdown'])
        changed = copy.deepcopy(full)
        changed['cases'][0]['steps'][0]['operation'] = '另一调用'
        for parent in (None, changed):
            rendered = render_selection(scope, source_catalog=parent)['xmind_markdown']
            self.assertIn('输入复用待核对', rendered)
            self.assertIn('请求（完整 JSON）', rendered)

    def test_whole_step_reference_keeps_its_own_assessed_json(self):
        from input_reuse import bind_inputs
        from step_reuse import select_reuse
        original, assessments = fixture()
        source, target = original['cases'][:2]
        source['steps'][0]['data_refs'] = target['steps'][0]['data_refs']
        row = assessments[target['id']][0]
        row['p0_data_id'] = row['data_id']
        target['reuse_assessments'] = [dict(group='steps', step_id=row['step_id'],
            p0_case_id=source['id'], p0_step_id=row['p0_step_id'], applicability='同一输入框',
            endpoint='下一步检查本例报错', source_basis='两例业务来源', comparison={
                k:'此步来源一致' for k in ('operation','data','expected','verification')})]
        cases, defs = select_reuse(original, [target], original['data'])
        original['cases'][1], original['step_definitions'] = cases[0], defs
        self.assertIn('step_reference', cases[0]['steps'][0])
        bound = bind_inputs(original, assessments)
        view = render_selection(bound, [target['id']])['xmind_markdown']
        for phrase in ('整步引用', '复用同版 P0', '输入完全相同，直接复制', '拒绝提交，本次无新增记录'):
            self.assertIn(phrase, view)

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
