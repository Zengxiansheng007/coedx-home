"""Negative paths authored through the mixed first-delivery entry."""
import copy
import unittest

from authoring import build_handwritten_batch
from test_handwritten import handwritten_sample


def make_case(branch, *, shared=0):
    text, base = handwritten_sample()
    actions = ['发起开始调用', '读开始回执', '发起停止调用', '读成功音频']
    def steps(names):
        result = []
        for name in names:
            step = copy.deepcopy(base['steps'][0])
            step.update(operation=name)
            step['verification'][0]['text'] = '核对' + name
            result.append(step)
        return result
    variant = dict(copy.deepcopy(base), case_id='NEG', priority='P1',
                   priority_basis='校验拒绝路径', title='缺参应拒绝', steps=steps(branch))
    if shared:
        variant['review_segment'] = dict(
            p0_case_id=base['case_id'], source_start=1, target_start=1, length=shared,
            branch_step=3, changes=[], test_point='停止调用缺参',
            source_basis='开始调用和回执与同版基准相同，第三步首次分叉',
            criterion='起始成功回执须属于本次调用')
    base['steps'] = steps(actions)
    base['initial_variants'] = [variant]
    return build_handwritten_batch(text, base)


class BranchReviewTests(unittest.TestCase):
    def test_range_cannot_hide_declared_first_divergent_step(self):
        with self.assertRaisesRegex(ValueError, '分叉'):
            make_case(['发起开始调用', '读开始回执', '停止缺参', '读停止错误'], shared=3)

    def test_tail_is_inline_and_stops_at_its_own_check(self):
        branch = ['发起开始调用', '读开始回执', '停止缺参', '读停止错误', '查本次无上传']
        result = make_case(branch, shared=2)
        view = result['xmind_markdown'].split('- P1 缺参应拒绝')[-1]
        self.assertIn('第 1～2 步', view)
        for number, action in enumerate(branch[2:], 3):
            self.assertIn(f'步骤 {number}：{action}', view)
            self.assertIn('核对' + action, view)
        self.assertNotIn('读成功音频', view)
        self.assertEqual([s['operation'] for s in result['batch']['cases'][1]['steps']], branch)

    def test_no_shared_path_retains_all_steps(self):
        branch = ['开始缺参', '读开始错误', '核对本次窗口无上传']
        result = make_case(branch)
        view = result['xmind_markdown'].split('- P1 缺参应拒绝')[-1]
        for number, action in enumerate(branch, 1):
            self.assertIn(f'步骤 {number}：{action}', view)
            self.assertIn('核对' + action, view)
        self.assertNotIn('复用：P0', view)
        self.assertNotIn('读成功音频', view)
