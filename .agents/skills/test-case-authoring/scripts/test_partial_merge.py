"""Synthetic isolated catalog merges; no formal asset or business execution."""
import copy
import unittest

from test_scoped_review import catalog
from scoped_review import build_scoped_review
from clarification import start_grill, summarize, apply_summary, review
from partial_merge import merge_reviewed


def fixture():
    full = catalog()
    for c in full['cases']:
        c.update(priority='P1', priority_basis='Synthetic risk and frequency', rule_status='formal')
        for s in c['steps']:
            if not s['expected']:
                s['expected'] = [{'text': 'Synthetic entered data retained', 'source': 'user_decision'}]
                s['verification'] = [{'text': 'Read synthetic value', 'source': 'user_decision'}]
    changed = copy.deepcopy(full['cases'][0])
    changed['title'] = 'Synthetic revised title'
    added = copy.deepcopy(changed)
    added['id'] = 'NEW'
    batch = build_scoped_review(full, 'synthetic-merge', [
        dict(case_id='EDIT', action='modify', reason='Synthetic revision', basis='synthetic://rule', coverage_impact='CHECK-1'),
        dict(case_id='LINK', action='deactivate', reason='SIMULATED: retire old case'),
        dict(case_id='NEW', action='add', reason='Synthetic boundary')], candidates=[changed, added])['batch']
    # Use the real public final-review workflow, not fabricated approved flags.
    session = summarize(start_grill(batch, []))
    session = apply_summary(session, dict(confirmed=True, actual_reply='SIMULATED: agreed', summary_id=session['summary']['id']))
    session = review(session, dict(approved=True, actual_reply='SIMULATED: approve complete cases',
        content_version=session['batch']['content_version'], case_ids=['EDIT', 'LINK', 'NEW']))
    batch = session['batch']
    instruction = dict(kind='merge_instruction', actual_reply='SIMULATED: merge these three',
        content_version=batch['content_version'], baseline_version=full['content_version'],
        case_ids=['EDIT', 'LINK', 'NEW'])
    return full, batch, instruction


class PartialMergeTests(unittest.TestCase):
    def test_dependency_contract_accepts_preparation_without_claiming_functional_pass(self):
        from test_dependencies import fixture as dependency_fixture
        from dependencies import review_dependencies
        from clarification import respond
        full, proposal = dependency_fixture()
        full['cases'][0]['priority'] = 'P1'
        for c in full['cases']:
            c['priority_basis'] = 'Synthetic risk'
        full['cases'][1].update(review_status='approved', rule_status='formal')
        b = review_dependencies(full, 'synthetic-dependent-merge', ['EDIT'], [proposal])['batch']
        # Supplied synthetic record fields are complete; confirm rules through public gate.
        session = summarize(start_grill(b, []))
        session = apply_summary(session, dict(confirmed=True, actual_reply='SIMULATED: agree', summary_id=session['summary']['id']))
        session = review(session, dict(approved=True, actual_reply='SIMULATED: review dependent case',
            content_version=session['batch']['content_version'], case_ids=['EDIT']))
        b = session['batch']
        i = dict(kind='merge_instruction', actual_reply='SIMULATED: merge EDIT', content_version=b['content_version'],
            baseline_version=full['content_version'], case_ids=['EDIT'])
        r = merge_reviewed(full, b, i, target_kind='isolated')
        self.assertEqual(r['cases'][0]['status'], 'applied', r['cases'])
        self.assertEqual(r['catalog']['cases'][1], full['cases'][1])
        self.assertEqual(r['approved_validation_scope'], [])
        self.assertEqual(r['execution'], 'not_started')
        b['data'][0]['reuse_policy'] = 'exclusive'
        self.assertEqual(merge_reviewed(full, b, i, target_kind='isolated')['cases'][0]['status'], 'pending')

    def test_feedback_revision_merges_business_content_and_data_together(self):
        from feedback import prepare_feedback, review_feedback
        from test_feedback import confirm
        full, batch, instruction = fixture()
        result = confirm(prepare_feedback(batch, 'chat', actual_reply='SIMULATED: use updated title and own data', changes=[
            dict(collection='cases', id='EDIT', path=['title'], value='Latest feedback title')]))
        result = review_feedback(result, dict(approved=True, actual_reply='SIMULATED: reviewed latest complete case',
            case_ids=['EDIT'], content_version=result['batch']['content_version']))
        b = result['batch']
        i = dict(instruction, content_version=b['content_version'], case_ids=['EDIT'])
        r = merge_reviewed(full, b, i, target_kind='isolated')
        self.assertEqual(r['catalog']['cases'][0]['title'], 'Latest feedback title')
        self.assertEqual(r['catalog']['cases'][1:], full['cases'][1:])

    def test_feedback_on_initial_reuse_is_an_approved_modification(self):
        from feedback import prepare_feedback, review_feedback
        from test_feedback import confirm
        full, _, _ = fixture()
        b = build_scoped_review(full, 'synthetic-reuse', [dict(case_id='EDIT', action='reuse', reason='Reuse old case')])['batch']
        result = confirm(prepare_feedback(b, 'chat', actual_reply='SIMULATED: update reused case', changes=[
            dict(collection='cases', id='EDIT', path=['title'], value='Reused case revised')]))
        result = review_feedback(result, dict(approved=True, actual_reply='SIMULATED: approve complete revision',
            content_version=result['batch']['content_version'], case_ids=['EDIT']))
        i = dict(kind='merge_instruction', actual_reply='SIMULATED: merge revision', case_ids=['EDIT'],
            content_version=result['batch']['content_version'], baseline_version=full['content_version'])
        r = merge_reviewed(full, result['batch'], i, target_kind='isolated')
        self.assertEqual(r['catalog']['cases'][0]['title'], 'Reused case revised')
        self.assertEqual(r['cases'][0]['action'], 'modify')

    def test_valid_unique_data_change_and_provisional_conditions_preserved(self):
        full, batch, instruction = fixture()
        # A new data identity avoids changing the unshown/shared existing record.
        d = copy.deepcopy(batch['data'][0])
        d.update(id='NEW-DATA', value='Synthetic new owned value')
        batch['data'].append(d)
        c = batch['cases'][2]
        c['steps'][0]['data_refs'] = ['NEW-DATA']
        c['rule_status'] = 'provisional'
        c['rule_decisions'] = [{'reply': dict(decision='provisional', actual_reply='SIMULATED: proceed', product_check='Confirm limit with product')}]
        instruction['case_ids'] = ['NEW']
        r = merge_reviewed(full, batch, instruction, target_kind='isolated')
        self.assertEqual(r['catalog']['cases'][-1]['rule_decisions'], c['rule_decisions'])
        self.assertEqual(r['catalog']['cases'][-1]['rule_status'], 'provisional')
        self.assertEqual(r['catalog']['data'][-1], d)
        self.assertEqual(r['catalog']['data'][:-1], full['data'])
        c.pop('rule_decisions')
        self.assertEqual(merge_reviewed(full, batch, instruction, target_kind='isolated')['catalog'], full)

    def test_shared_data_and_target_drift_preserve_untouched_records(self):
        for variant in ('shared', 'data_drift', 'case_drift'):
            full, batch, instruction = fixture()
            before = copy.deepcopy(full)
            if variant == 'shared':
                batch['data'][0]['value'] = 'Unauthorized shared replacement'
            elif variant == 'data_drift':
                full['data'][0]['value'] = 'Changed externally'
            else:
                full['cases'][0]['title'] = 'Changed externally'
            r = merge_reviewed(full, batch, instruction, target_kind='isolated')
            rows = {c['case_id']: c for c in r['cases']}
            self.assertEqual(rows['EDIT']['status'], 'pending')
            self.assertEqual(r['catalog']['data'], full['data'])
            self.assertEqual(r['catalog']['cases'][2], before['cases'][2])

    def test_explicit_version_scope_P0_and_formal_boundary(self):
        full, batch, instruction = fixture()
        for field, value in [('content_version', 'old'), ('baseline_version', 'old'), ('actual_reply', ''), ('case_ids', [])]:
            bad = dict(instruction, **{field: value})
            with self.assertRaises(ValueError):
                merge_reviewed(full, batch, bad, target_kind='isolated')
        with self.assertRaises(ValueError):
            merge_reviewed(full, batch, instruction, target_kind='formal')
        batch['cases'][0]['priority'] = 'P0'
        batch['cases'][2]['final_review']['content_version'] = 'old'
        instruction['case_ids'] = ['EDIT', 'NEW']
        r = merge_reviewed(full, batch, instruction, target_kind='isolated')
        self.assertEqual(r['catalog'], full)
        self.assertEqual({x['case_id']: x['reason'] for x in r['cases']}['EDIT'], 'P0_merge_belongs_to_ui_test')

    def test_deferred_missing_or_unselected_changed_dependency_blocks_only_affected(self):
        for variant in ('deferred', 'missing', 'changed_unselected'):
            full, batch, instruction = fixture()
            batch['cases'][0]['dependencies'] = [{'case_id': 'LINK', 'module_path': full['cases'][1]['module_path']}]
            if variant == 'deferred':
                batch['cases'][1]['rule_status'] = 'deferred'
            elif variant == 'missing':
                batch['cases'][0]['dependencies'][0]['case_id'] = 'ABSENT'
            else:
                instruction['case_ids'] = ['EDIT', 'NEW']
                batch['cases'][1]['title'] = 'Unmerged prerequisite'
            r = merge_reviewed(full, batch, instruction, target_kind='isolated')
            rows = {c['case_id']: c for c in r['cases']}
            self.assertEqual(rows['EDIT']['status'], 'pending')
            self.assertEqual(rows['NEW']['status'], 'applied')
            self.assertEqual(r['catalog']['cases'][0], full['cases'][0])

    def test_approved_delta_keeps_full_target_and_retired_original(self):
        full, batch, instruction = fixture()
        before = copy.deepcopy((full, batch, instruction))
        result = merge_reviewed(full, batch, instruction, target_kind='isolated')
        self.assertEqual((full, batch, instruction), before)
        merged = {c['id']: c for c in result['catalog']['cases']}
        self.assertEqual(set(merged), {'EDIT', 'LINK', 'OTHER', 'NEW'})
        self.assertEqual(merged['EDIT']['title'], 'Synthetic revised title')
        self.assertEqual(merged['OTHER'], full['cases'][2])
        self.assertEqual(merged['LINK']['lifecycle'], 'inactive')
        self.assertEqual(merged['LINK']['deactivation_history'][-1]['original'], full['cases'][1])
        self.assertEqual(merged['EDIT']['execution_status'], batch['cases'][0]['execution_status'])
        self.assertEqual(result['formal_sync'], 'pending_joint_validation')
        self.assertEqual(result['execution'], 'not_started')
        self.assertIn('ui-test', result['next_step'])
        self.assertEqual([c['case_id'] for c in result['cases'] if c['status'] == 'applied'], ['EDIT', 'LINK', 'NEW'])


if __name__ == '__main__':
    unittest.main()
