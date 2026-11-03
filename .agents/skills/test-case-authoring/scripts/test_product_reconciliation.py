"""Synthetic product conclusions through public authoring boundaries."""
import copy
import unittest

from test_p0_evidence import fixture
from p0_evidence import approve_p0_scope
from p0_evidence import approve_result_scope, check_extension
from product_reconciliation import reconcile_product, decide_reuse, prepare_product_change
from feedback import apply_feedback, review_feedback
from clarification import respond, summarize


def sample():
    full, _, reports, request = fixture()
    full['cases'][0]['rule_refs'] = ['RULE-SAVE']
    full['cases'][0]['rule_status'] = 'provisional'
    full['cases'][0]['rule_decisions'] = [{'reply': {'decision': 'provisional',
        'product_check': 'SIMULATED: confirm save rule'}}]
    full['coverage'] = [{'check_id': 'CHECK-SAVE', 'rule_refs': ['RULE-SAVE'],
                         'case_ids': ['EDIT', 'LINK']}]
    baseline = approve_p0_scope(full, 'synthetic-round', ['EDIT', 'LINK'], 'SIMULATED: approve')
    conclusion = {'rule_id': 'RULE-SAVE', 'relation': 'consistent',
                  'actual_reply': 'SIMULATED: product confirms save rule unchanged',
                  'source_ref': 'synthetic://product-final', 'tested_version': request['tested_version']}
    return full, baseline, reports, conclusion


class ProductReconciliationTests(unittest.TestCase):
    def test_changed_extension_regenerates_design_coverage_from_revised_common_content(self):
        from test_extension import expansion
        from extension import build_extension, render_extension
        draft = build_extension(*expansion(), mode='simulation')['batch']
        for case in draft['cases']:
            case.update(rule_status='provisional', review_status='approved', rule_refs=['BOUNDARY'])
        full = {'schema_version': 1, 'kind': 'authoring_full_catalog', 'content_version': draft['content_version'],
                'source_ref': 'synthetic://extension', 'cases': draft['cases'], 'data': draft['data'],
                'extension_design': draft['extension_design']}
        baseline = approve_result_scope(full, 'synthetic-product', ['LOW', 'HIGH'], 'SIMULATED: original scope')
        conclusion = {'rule_id': 'BOUNDARY', 'relation': 'changed', 'source_ref': 'synthetic://product',
            'actual_reply': 'SIMULATED: require clear rejection at these boundaries', 'tested_version': 'synthetic-v2'}
        reconciliation = reconcile_product(full, baseline, [], conclusion, mode='simulation')
        pending = prepare_product_change(full, reconciliation, [
            {'collection': 'cases', 'id': cid, 'path': ['steps', 0, 'expected', 0, 'text'],
             'value': 'SIMULATED: clear boundary rejection'} for cid in ('LOW', 'HIGH')])
        pending['grill'] = summarize(respond(pending['grill'], [
            {'question_id': q['id'], 'decision': 'formal', 'actual_reply': 'SIMULATED: confirm rejection'}
            for q in pending['grill']['round_questions']]))
        updated = apply_feedback(pending, {'summary_id': pending['grill']['summary']['id'],
            'confirmed': True, 'actual_reply': 'SIMULATED: agree'})
        # Existing extension renderer consumes the revised common batch, never
        # a separately hand-edited coverage summary or historical report.
        rendered = render_extension(updated['batch'])
        self.assertIn('clear boundary rejection', rendered['coverage_notes'])
        self.assertEqual(rendered['coverage']['content_version'], updated['batch']['content_version'])
        self.assertEqual(rendered['batch']['product_reconciliation']['pending_retest'], ['HIGH', 'LOW'])

    def test_extension_coverage_links_and_tampered_decisions_are_checked(self):
        full, baseline, reports, conclusion = sample()
        full['coverage'] = []
        full['extension_design'] = {'coverage': [{'check_id': 'H1', 'links': [{'case_id': 'LINK'}]}],
            'manual_points': [{'checks': [{'id': 'H1', 'rule_refs': ['RULE-SAVE']}]}]}
        baseline = approve_result_scope(full, 'synthetic-round', ['EDIT', 'LINK'], 'SIMULATED: scope')
        result = reconcile_product(full, baseline, reports, conclusion, mode='simulation')
        self.assertEqual(result['affected_case_ids'], ['EDIT', 'LINK'])
        result['reuse'][0]['status'] = 'pending_check'
        with self.assertRaises(ValueError):
            decide_reuse(result, {'reconciliation_id': result['id'], 'case_ids': ['LINK'],
                'reuse': True, 'actual_reply': 'SIMULATED: reuse'})

    def test_p1_p2_reports_use_same_evidence_contract_without_relaxing_p0_gate(self):
        for priority in ('P1', 'P2'):
            full, _, reports, conclusion = sample()
            full['cases'][0]['priority'] = priority
            baseline = approve_result_scope(full, 'synthetic-round', ['EDIT', 'LINK'], 'SIMULATED: frozen scope')
            reports[0]['kind'] = 'case_execution_report'
            result = reconcile_product(full, baseline, reports, conclusion, mode='simulation')
            self.assertEqual(result['reuse'][0]['status'], 'suggest_reuse')
            self.assertNotIn('can_extend', result['evidence_check'])
            with self.assertRaises(ValueError):
                check_extension(full, baseline, reports, {}, mode='simulation')
            with self.assertRaises(ValueError):
                approve_p0_scope(full, 'synthetic-round', ['EDIT'], 'SIMULATED: invalid P0 scope')

    def test_consistent_checks_and_explicit_reuse_leave_history_untouched(self):
        full, baseline, reports, conclusion = sample()
        before = copy.deepcopy((full, baseline, reports))
        result = reconcile_product(full, baseline, reports, conclusion, mode='simulation')
        self.assertEqual(result['affected_case_ids'], ['EDIT', 'LINK'])
        self.assertEqual([r['status'] for r in result['reuse']], ['suggest_reuse'] * 2)
        self.assertNotIn('can_extend', result['evidence_check'])
        self.assertNotIn('blockers', result['evidence_check'])
        self.assertTrue(all(r['decision'] == 'awaiting_user' for r in result['reuse']))
        decided = decide_reuse(result, {'reconciliation_id': result['id'], 'case_ids': ['EDIT'],
            'reuse': True, 'actual_reply': 'SIMULATED: reuse EDIT only'})
        self.assertEqual([r['decision'] for r in decided['reuse']], ['reuse_approved', 'awaiting_user'])
        self.assertEqual((full, baseline, reports), before)
        self.assertIn('confirm save rule', str(decided['historical_results']))
        self.assertEqual(decided['formal_conclusion'], conclusion)

    def test_missing_stale_failed_and_non_p0_evidence_remain_pending(self):
        full, baseline, reports, conclusion = sample()
        for change in ({'tested_version': 'old'}, {'semantic_version': 'old'}, {'evidence': []}, {'result': 'failed'}):
            altered = copy.deepcopy(reports)
            altered[0].update(change)
            result = reconcile_product(full, baseline, altered, conclusion, mode='simulation')
            self.assertEqual(result['reuse'][0]['status'], 'pending_check')
            with self.assertRaises(ValueError):
                decide_reuse(result, {'reconciliation_id': result['id'], 'case_ids': ['EDIT'],
                    'reuse': True, 'actual_reply': 'SIMULATED: reuse'})
        full['coverage'][0]['case_ids'].append('OTHER')
        result = reconcile_product(full, baseline, reports, conclusion, mode='simulation')
        self.assertEqual(result['reuse'][-1]['status'], 'pending_check')
        with self.assertRaises(ValueError):
            reconcile_product(full, baseline, reports, conclusion)

    def test_changed_rule_routes_through_feedback_grill_and_exact_version_review(self):
        full, baseline, reports, conclusion = sample()
        conclusion['relation'] = 'changed'
        conclusion['actual_reply'] = 'SIMULATED: product now requires an authorization check'
        result = reconcile_product(full, baseline, reports, conclusion, mode='simulation')
        self.assertEqual(result['pending_retest'], ['EDIT', 'LINK'])
        self.assertEqual(result['reuse'], [])
        changes = [{'collection': 'cases', 'id': cid, 'path': ['title'],
                    'value': 'SIMULATED revised ' + cid} for cid in ('EDIT', 'LINK')]
        pending = prepare_product_change(full, result, changes)
        self.assertEqual(full['cases'][0]['title'], pending['batch']['cases'][0]['title'])
        pending['grill'] = summarize(respond(pending['grill'], [
            {'question_id': q['id'], 'decision': 'formal', 'actual_reply': 'SIMULATED: confirm change'}
            for q in pending['grill']['round_questions']]))
        updated = apply_feedback(pending, {'summary_id': pending['grill']['summary']['id'],
            'confirmed': True, 'actual_reply': 'SIMULATED: agree summary'})
        self.assertNotEqual(updated['batch']['content_version'], pending['batch']['content_version'])
        reviewed = review_feedback(updated, {'content_version': updated['batch']['content_version'],
            'approved': True, 'case_ids': ['EDIT', 'LINK'], 'actual_reply': 'SIMULATED: approve complete cases'})
        self.assertTrue(all(c['review_status'] == 'approved' for c in reviewed['batch']['cases']))
        self.assertEqual(full['cases'][2]['id'], 'OTHER')
        self.assertEqual(result['pending_retest'], ['EDIT', 'LINK'])
        with self.assertRaises(ValueError):
            prepare_product_change(full, result, [dict(changes[0], id='OTHER')])


if __name__ == '__main__':
    unittest.main()
