"""Source-backed module preparation is selected from the complete authored batch."""
import unittest

from scoped_review import build_scoped_review
from test_preparation_scope import source
from source_preparation import assess_preparations, render_selection


class SourcePreparationTests(unittest.TestCase):
    def test_confirmed_input_is_enough_for_draft_without_creating_approval(self):
        full = source()
        cases = full['cases']
        definition = dict(name='订单准备', timing='每例开始前', instruction='检查订单', source='需求 §2',
                          module_path=cases[0]['module_path'],
                          applicable={c['id']: [c['common_preconditions'][0]['id']] for c in cases[:3]},
                          pending={c['id']: '旧准备未对应本例步骤' for c in cases[3:7]},
                          excluded={cases[7]['id']: '仅浏览'})
        candidate = assess_preparations(full, [definition])
        selection = [dict(case_id=c['id'], action='related', reason='选择') for c in (cases[1], cases[5])]
        selected = build_scoped_review(candidate, '节选', selection)['xmind_markdown']
        self.assertEqual(selected.count('检查订单'), 1)
        self.assertIn('适用范围待核对', selected)
        self.assertIn('准备模拟订单', selected)
        self.assertNotIn('模拟用例0', selected)
        self.assertNotIn('检查订单', render_selection(candidate, [cases[7]['id']])['xmind_markdown'])
        self.assertEqual(candidate['cases'], full['cases'])
        self.assertEqual(render_selection(candidate)['xmind_markdown'].count('检查订单'), 1)

    def test_missing_preparation_uses_assessed_starting_state_or_case_setup(self):
        batch = source()
        for case in batch['cases'][:3]:
            case['common_preconditions'] = []
            case.pop('common_preconditions_note', None)
            case['context']['initial_state'] = '已进入订单列表'
        first, second, unknown = batch['cases'][:3]
        second['special_preconditions'] = [second['steps'][0]]
        definition = dict(name='订单列表', timing='每例前', instruction='打开订单列表', source='需求 §1',
                          module_path=first['module_path'], applicable={first['id']: ['context/initial_state']},
                          pending={}, excluded={c['id']: '另有入口' for c in batch['cases'][1:]})
        candidate = assess_preparations(batch, [definition])
        for case in (first, second, unknown):
            rendered = render_selection(candidate, [case['id']])
            for view in ('human_view', 'xmind_markdown'):
                self.assertEqual('前置操作未提供，待核对' in rendered[view], case is unknown)

    def test_cli_full_and_excerpt_can_move_with_their_companion(self):
        import copy
        import json
        import re
        import shutil
        import subprocess
        import sys
        import tempfile
        from pathlib import Path
        from urllib.parse import unquote
        from authoring import build_handwritten_batch
        from test_handwritten import handwritten_sample

        candidate = build_handwritten_batch(*handwritten_sample())['batch']
        first = candidate['cases'][0]
        first['technical_handoff'] = {'reuse_policy': '复用前核对有效期'}
        second = copy.deepcopy(first)
        second.update(id='ANOTHER', title='另一独立用例')
        second['test_point'] = '核实第二项业务条件'
        candidate['cases'].append(second)
        script = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'input.json').write_text(json.dumps(candidate), encoding='utf8')
            (root / 'segments.json').write_text('{}', encoding='utf8')
            for directory, args in (
                ('full', ['source_preparation.py']),
                ('excerpt', ['source_preparation.py', '--case', second['id']]),
                ('segments', ['review_segments.py', '--assessments', 'segments.json']),
            ):
                subprocess.run([sys.executable, str(script / args[0]), *args[1:], '--candidate', 'input.json',
                                '--output-dir', 'bundle/' + directory], cwd=root, check=True)
            moved = Path(shutil.move(str(root / 'bundle'), str(root / 'relocated')))
            for directory in ('full', 'excerpt', 'segments'):
                view = (moved / directory / 'xmind.md').read_text(encoding='utf8')
                self.assertEqual('非全量' in view.splitlines()[0], directory == 'excerpt')
                self.assertEqual(first['title'] in view, directory != 'excerpt')
                for case in (second,) if directory == 'excerpt' else (first, second):
                    rows = view.splitlines()
                    heading = next(i for i, row in enumerate(rows) if row.rstrip().endswith(' ' + case['title']))
                    self.assertEqual(rows[heading + 1].strip(), '- 测试点：' + case.get('test_point', case['title']))
                links = re.findall(r'\[Agent说明 [^\]]+\]\(([^)]+)\)', view)
                self.assertTrue(links)
                for link in links:
                    self.assertNotIn('file:', link)
                    note = moved / directory / unquote(link)
                    self.assertTrue(note.is_file())
                    for ref in re.findall(r'候选来源：\[[^\]]+\]\(([^#]+)#', note.read_text(encoding='utf8')):
                        self.assertNotIn('file:', ref)
                        self.assertTrue((note.parent / unquote(ref)).is_file())

    def test_credentials_in_undisplayed_case_block_both_cli_bundles(self):
        import json
        import subprocess
        import sys
        import tempfile
        from pathlib import Path
        candidate = source()
        candidate['cases'][-1]['credential_ref'] = 'invalid'
        with self.assertRaisesRegex(ValueError, 'credential'):
            render_selection(candidate, [candidate['cases'][0]['id']])
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'candidate').write_text(json.dumps(candidate))
            (root / 'assessment').write_text('{}')
            for script, args in [('source_preparation.py', ['--case', 'SIM-0']),
                                 ('review_segments.py', ['--assessments', 'assessment'])]:
                run = subprocess.run([sys.executable, str(Path(__file__).with_name(script)),
                    '--candidate', 'candidate', '--output-dir', 'bundle', *args], cwd=root, capture_output=True)
                self.assertNotEqual(run.returncode, 0)
                self.assertFalse((root / 'bundle').exists())

    def test_reviewed_and_new_preparations_keep_original_step_owners(self):
        from preparation_scope import review_preparation_scope
        full = source()
        full['cases'] = full['cases'][:2]
        ids = [c['id'] for c in full['cases']]
        for c in full['cases']:
            c['common_preconditions'] = [dict(c['common_preconditions'][0], id=k, operation=k)
                                         for k in ('FIRST', 'SECOND', 'THIRD')]
        full = review_preparation_scope(full, scope_kind='module', operation_id='second',
            step_ids_by_case={cid: ['SECOND'] for cid in ids}, applicable_case_ids=ids,
            exception_case_ids=[], coverage='vast_majority_few_exceptions', basis='reviewed',
            actual_reply='verified', version='demo', frequency='each')
        candidate = assess_preparations(full, [dict(module_path=full['cases'][0]['module_path'],
            name='entry', timing='each', instruction='first method', source='material',
            applicable={cid: ['FIRST'] for cid in ids}, pending={}, excluded={})])
        view = render_selection(candidate)['xmind_markdown']
        self.assertEqual(view.count('：SECOND'), 1)
        self.assertEqual(view.count('：THIRD'), 2)

    def test_authorized_delta_assessed_with_exact_parent_via_cli(self):
        import copy
        import json
        import subprocess
        import sys
        import tempfile
        from pathlib import Path
        from extension import build_extension
        from test_extension import expansion
        args = expansion()
        parent = args[0]
        delta = build_extension(*args, mode='simulation')['batch']
        method = dict(module_path=delta['cases'][0]['module_path'], name='独立准备',
            timing='每例前', instruction='确认当前入口', source='业务材料',
            applicable={'LOW': ['context/initial_state']}, pending={}, excluded={'HIGH': '独立验证入口'})
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for filename, value in [('delta', delta), ('parent', parent), ('method', [method])]:
                (root / filename).write_text(json.dumps(value))
            subprocess.run([sys.executable, str(Path(__file__).with_name('source_preparation.py')),
                '--candidate', 'delta', '--source-catalog', 'parent', '--assessment', 'method',
                '--case', 'LOW', '--output-dir', 'bundle'], cwd=root, check=True)
            result = json.loads((root / 'bundle' / 'candidate.json').read_text(encoding='utf8'))
            self.assertEqual(result['extension_entry'], delta['extension_entry'])
            self.assertEqual(result['cases'], delta['cases'])
            self.assertIn('确认当前入口', (root / 'bundle' / 'xmind.md').read_text(encoding='utf8'))
            self.assertNotIn('确认当前入口', render_selection(result, ['HIGH'], source_catalog=parent)['xmind_markdown'])
        wrong = copy.deepcopy(parent)
        wrong['cases'].pop()
        for invalid in (None, wrong):
            with self.assertRaisesRegex(ValueError, 'source catalog'):
                assess_preparations(delta, [method], source_catalog=invalid)
