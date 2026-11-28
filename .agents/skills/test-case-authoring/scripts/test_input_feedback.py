"""Edit returned reader files through the same proposal and confirmation workflow."""
import copy
import unittest

from clarification import summarize
from feedback import apply_feedback, prepare_feedback
from input_reuse import bind_inputs
from source_preparation import render_selection
from test_input_reuse import fixture


def source():
    batch, assessments = fixture()
    batch.update(id='synthetic-returns', questions=[], coverage=[])
    return bind_inputs(batch, assessments)


def returned(batch, ids, edit, **kwargs):
    view = render_selection(batch, ids)['xmind_markdown']
    return prepare_feedback(batch, 'markdown', markdown=edit(view), actual_reply='SIMULATED: reviewed returned file',
                            review_ids=ids, clear_changes=True, **kwargs)


def accept(pending):
    pending['grill'] = summarize(pending['grill'])
    return apply_feedback(pending, dict(confirmed=True, actual_reply='SIMULATED: apply listed changes',
                                        summary_id=pending['grill']['summary']['id']))


class InputReturnTest(unittest.TestCase):
    def test_local_deletion_from_reuse_text_changes_only_variant_after_confirmation(self):
        batch = source()
        old = copy.deepcopy(batch)
        pending = returned(batch, ['EDIT','LINK'], lambda text: text.replace('保留 input.params，值为 {}', '省略 input.params'))
        field, = pending['input_edits']
        self.assertEqual(field['summary'], '本例删除 input.params')
        self.assertEqual(field['before'], {})
        self.assertNotIn('after', field)
        self.assertEqual(pending['affected_case_ids'], ['LINK'])
        self.assertEqual(batch, old)
        result = accept(pending)
        values = {d['id']:d['value'] for d in result['batch']['data']}
        self.assertNotIn('params', values['LINK/json']['input'])
        self.assertEqual(values['EDIT/json']['input']['params'], {})
        self.assertIn('删除 input.params', result['xmind_markdown'])


    def test_shared_source_change_lists_outside_variant_and_keeps_override(self):
        batch = source()
        def edit(view):
            return view.replace('"typed": 1','"typed": 2').replace('"empty": "x"','"empty": "y"').replace('"params": {},','"new.field": true,\n' + next(l.split('"params"')[0] for l in view.splitlines() if '"params"' in l) + '"params": {},')
        pending = returned(batch, ['EDIT'], edit, shared_input=['EDIT','EDIT/submit','EDIT/json'])
        self.assertEqual(pending['affected_case_ids'], ['EDIT','LINK'])
        impact, = pending['input_impact']
        self.assertTrue(impact['outside_review'])
        self.assertCountEqual(impact['preserved'], [['input','empty'],['input','typed']])
        result = accept(pending)
        values = {r['id']:r['value'] for r in result['batch']['data']}
        self.assertIs(values['LINK/json']['input']['new.field'], True)
        self.assertIs(values['LINK/json']['input']['typed'], True)
        self.assertEqual(values['LINK/json']['input']['empty'], '')

    def test_malformed_ambiguous_and_stale_are_located(self):
        batch = source()
        for edit, message in [(lambda s:s.replace('"typed": 1','"typed": }'),'EDIT/submit'),
                              (lambda s:s.replace('保留 input.params，值为 {}','待定'),'LINK/submit'),
                              (lambda s:s.replace(batch['content_version'],'bad-version'),'稿件版本')]:
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                returned(batch, ['EDIT','LINK'], edit)

    def test_single_case_overlay_for_shared_literal(self):
        batch = source()
        case, other = batch['cases'][:2]
        other['steps'][0]['data_refs'] = case['steps'][0]['data_refs'][:]
        row, = batch['input_reuse']['LINK']
        row['data_id'] = row['p0_data_id']
        batch = bind_inputs(batch, {'LINK':[row]})
        pending = returned(batch, ['EDIT','LINK'], lambda s:s.replace('保留 input.params，值为 {}','省略 params'))
        result = accept(pending)['batch']
        other_ref = result['cases'][1]['steps'][0]['data_refs'][0]
        self.assertNotEqual(other_ref, 'EDIT/json')
        self.assertEqual(result['input_reuse']['LINK'][0]['data_id'], other_ref)
        values = {r['id']:r['value'] for r in result['data']}
        self.assertEqual(values['EDIT/json']['input']['params'], {})
        self.assertNotIn('params', values[other_ref]['input'])

    def test_returned_operation_and_expected_update_exact_case(self):
        batch = source()
        case = batch['cases'][0]
        step = case['steps'][1]
        old = step['expected'][0]['text']
        def edit(view):
            needle = next(l for l in view.splitlines() if l.endswith('- '+old))
            return view.replace(needle, needle[:-len(old)]+'Fresh visible outcome',1)
        result = accept(returned(batch, ['EDIT'], edit))
        self.assertEqual(result['batch']['cases'][0]['steps'][1]['expected'][0]['text'],'Fresh visible outcome')
        self.assertIn('Fresh visible outcome', result['xmind_markdown'])

    def test_return_scope_is_checked_against_original_selection(self):
        batch = source()
        view = render_selection(batch, ['EDIT'])['xmind_markdown']
        for options in ({}, {'review_ids':['LINK']}):
            with self.assertRaisesRegex(ValueError, '待评用例清单'):
                prepare_feedback(batch, 'markdown', markdown=view, actual_reply='SIMULATED: return', **options)

    def test_shared_p0_reports_direct_literal_consumers_without_an_assessment(self):
        batch = source()
        batch['cases'][2]['steps'][0]['data_refs'] = ['EDIT/json']
        pending = returned(batch,['EDIT'], lambda v:v.replace('"typed": 1','"typed": 9'),
                           shared_input=['EDIT','EDIT/submit','EDIT/json'])
        self.assertIn('OTHER', pending['affected_case_ids'])
        result = accept(pending)['batch']
        self.assertEqual(result['cases'][2]['steps'][0]['data_refs'], ['EDIT/json'])
        self.assertEqual(next(d for d in result['data'] if d['id']=='EDIT/json')['value']['input']['typed'],9)

    def test_qa_return_binds_delivered_manifest_and_records_exact_fields(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from qa_record import start_record
        from module_handoff import write_artifacts
        from input_feedback import start_reader_feedback
        batch = source()
        with TemporaryDirectory() as tmp:
            out = Path(tmp)
            qa = out/'replies.md'
            start_record(qa, 'synthetic-return', batch, [])
            ids = ['LINK']
            write_artifacts(render_selection(batch, ids), out, review_ids=ids)
            returned = out/'returned.md'
            returned.write_text(render_selection(batch, ['EDIT'])['xmind_markdown'], encoding='utf8')
            original = qa.read_bytes()
            with self.assertRaisesRegex(ValueError,'待评用例清单'):
                start_reader_feedback(qa, returned, out/'agent.json', actual_reply='SIMULATED: returned')
            self.assertEqual(qa.read_bytes(), original)
            returned.write_text((out/'xmind.md').read_text('utf8').replace('保留 input.params，值为 {}','省略 input.params'),encoding='utf8')
            pending = start_reader_feedback(qa, returned, out/'agent.json', actual_reply='SIMULATED: returned')['feedback_pending']
            self.assertEqual(pending['affected_case_ids'], ['LINK'])
            self.assertIn('本例删除 input.params', qa.read_text('utf8'))
