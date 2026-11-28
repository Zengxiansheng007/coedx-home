"""Operation-range review contracts at first delivery and approved expansion."""
import copy
import unittest

from authoring import build_handwritten_batch, render_batch
from extension import build_extension, render_extension
from test_extension import expansion
from test_handwritten import handwritten_sample


def assessment(source, length):
    return dict(p0_case_id=source, source_start=1, target_start=1, length=length,
                test_point='GIF 单文件传输', source_basis='手写材料的选图和实收步骤',
                changes=[dict(step=2, text='换成可打开且小于 1 MiB 的 GIF')],
                criterion='实收文件的 SHA-256 与本次源 GIF 相同')


class RangeTests(unittest.TestCase):
    def test_first_mixed_delivery_preserves_full_target_and_pending_source(self):
        text, draft = handwritten_sample()
        draft.update(title='相册选图 JPG', case_id='JPG')
        actions = ['打开相册', '选择 JPG', '提交', '查接收记录', '比较 SHA-256']
        draft['steps'] = [dict(copy.deepcopy(draft['steps'][0]), operation=action) for action in actions]
        variant = copy.deepcopy(draft)
        variant.update(case_id='GIF', title='相册选图 GIF', priority='P1', priority_basis='约束内素材变体')
        variant['steps'][1]['operation'] = '选择本次 GIF'
        variant['steps'][-1]['verification'][0]['text'] = '核对本次源 GIF 的 SHA-256'
        variant['review_segment'] = assessment('JPG', 5)
        draft['initial_variants'] = [variant]
        result = build_handwritten_batch(text, draft)
        branch = result['xmind_markdown'].split('- P1 相册选图 GIF')[-1]
        self.assertTrue(branch.strip().startswith('- 测试点：GIF 单文件传输'))
        self.assertEqual(branch.count('第 1～5 步'), 1)
        for phrase in ('相册选图 JPG', '待评审', '第 2 步', '小于 1 MiB', '本次源 GIF'):
            self.assertIn(phrase, branch)
        self.assertNotIn('步骤 3：提交', branch)
        target = result['batch']['cases'][1]
        self.assertEqual([s['operation'] for s in target['steps']], [a if i != 1 else '选择本次 GIF' for i, a in enumerate(actions)])
        self.assertEqual((target['id'], target['execution_status']), ('GIF', 'not_run'))
        for change in ('missing', 'duplicate', 'stale'):
            batch = copy.deepcopy(result['batch'])
            if change == 'missing':
                batch['cases'].pop(0)
            elif change == 'duplicate':
                batch['cases'].append(copy.deepcopy(batch['cases'][0]))
            else:
                batch['cases'][0]['steps'][0]['operation'] = '已变更'
            self.assertIn('核对原始材料', render_batch(batch)['xmind_markdown'])

    def test_extension_requires_its_original_entry_and_retains_target_steps(self):
        args = expansion()
        source, target = args[0]['cases'][0], args[4]['candidates'][0]
        target['review_segment'] = assessment(source['id'], 2)
        result = build_extension(*args, mode='simulation')
        self.assertIn('第 1～2 步', result['xmind_markdown'])
        self.assertEqual(result['batch']['cases'][0]['steps'], target['steps'])
        self.assertIn('第 1～2 步', render_extension(result['batch'])['xmind_markdown'])
        with self.assertRaisesRegex(ValueError, 'P0 entry blocked'):
            build_extension(args[0], args[1], [], *args[3:], mode='simulation')

    def test_changed_preparation_or_its_data_invalidates_assessed_range(self):
        from review_segments import bind_segments
        from source_preparation import render_selection
        from test_preparation_scope import source
        full = source()
        origin, target = full['cases'][:2]
        target['priority'] = 'P1'
        baseline = copy.deepcopy(full['data'][0])
        baseline['id'] = 'setup-only'
        full['data'].append(baseline)
        origin['common_preconditions'][0]['data_refs'] = ['setup-only']
        candidate = bind_segments(full, {target['id']: assessment(origin['id'], 2)})
        for change in ('source condition', 'target condition', 'preparation data'):
            edited = copy.deepcopy(candidate)
            if change == 'preparation data':
                edited['data'][-1]['value'] = 'different prerequisite'
            else:
                case = edited['cases'][0 if change == 'source condition' else 1]
                case['common_preconditions'][0]['operation'] = 'changed entry'
            with self.subTest(change=change):
                self.assertIn('核对原始材料', render_selection(edited, [target['id']])['xmind_markdown'])

    def test_assessed_segment_and_whole_step_reuse_restore_same_version(self):
        from single_case import get_case
        from test_step_reuse import reuse_design
        args = reuse_design()
        target = args[4]['candidates'][0]
        target['review_segment'] = assessment(args[0]['cases'][0]['id'], 2)
        result = build_extension(*args, mode='simulation')
        batch = result['batch']
        self.assertIn('step_reference', batch['cases'][0]['steps'][0])
        packet = get_case(batch, batch['content_version'], target['id'], source_catalog=args[0])
        self.assertEqual(packet['case']['steps'], target['steps'])
        self.assertIn('第 1～2 步', result['xmind_markdown'])
