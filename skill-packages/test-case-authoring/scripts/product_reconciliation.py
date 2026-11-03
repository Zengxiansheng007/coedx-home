"""Product conclusions and reuse decisions; historical results stay immutable."""
import copy

from authoring import _credential_guard, _digest
from p0_evidence import check_result_evidence
from scoped_review import build_scoped_review
from feedback import prepare_feedback


def _verify(result):
    if result.get('id') != _digest({k: v for k, v in result.items() if k != 'id'}):
        raise ValueError('Reconciliation changed; recheck source evidence')


def reconcile_product(catalog, baseline, reports, conclusion, *, mode='production'):
    """Locate direct rule and manual-check links, then propose rather than apply."""
    _credential_guard([catalog, baseline, reports, conclusion])
    if (conclusion.get('relation') not in ('consistent', 'changed') or
            not all(isinstance(conclusion.get(k), str) and conclusion[k].strip()
                    for k in ('rule_id', 'actual_reply', 'source_ref', 'tested_version'))):
        raise ValueError('Explicit product conclusion, source and tested version required')
    rule = conclusion['rule_id']
    indexed = {c['id']: c for c in catalog['cases']}
    links = list(catalog.get('coverage', [])) + list(catalog.get('extension_design', {}).get('coverage', []))
    affected = {c['id'] for c in catalog['cases'] if rule in c.get('rule_refs', [])}
    affected.update(cid for check in links if rule in check.get('rule_refs', [])
                    for cid in (check.get('case_ids', []) + [link['case_id'] for link in check.get('links', [])]))
    design = catalog.get('extension_design', {})
    for point in design.get('manual_points', []):
        for check in point.get('checks', []):
            if rule in check.get('rule_refs', []):
                affected.update(link['case_id'] for row in design.get('coverage', [])
                                if row.get('check_id') == check['id'] for link in row.get('links', []))
    if not affected or not affected <= indexed.keys():
        raise ValueError('Rule/coverage references missing or unresolved; inspect source')
    checked = check_result_evidence(catalog, baseline, reports, conclusion['tested_version'], mode=mode)
    rows = {r['case_id']: r for r in checked['cases']}
    reuse = []
    if conclusion['relation'] == 'consistent':
        for cid in sorted(affected):
            row = rows.get(cid)
            reusable = row is not None and row['execution_status'] == 'passed'
            reuse.append({'case_id': cid, 'module_path': indexed[cid]['module_path'],
                          'status': 'suggest_reuse' if reusable else 'pending_check',
                          'reason': row['reason'] if row else 'No applicable frozen report scope',
                          'decision': 'awaiting_user'})
    result = {'kind': 'product_rule_reconciliation', 'catalog_digest': _digest(catalog),
              'content_version': catalog['content_version'], 'formal_conclusion': copy.deepcopy(conclusion),
              'affected_case_ids': sorted(affected), 'reuse': reuse, 'reuse_decisions': [],
              'historical_results': {'baseline': copy.deepcopy(baseline), 'reports': copy.deepcopy(reports)},
              'evidence_check': checked, 'evidence_nature': checked['evidence_nature'],
              'pending_retest': sorted(affected) if conclusion['relation'] == 'changed' else [],
              'next_step': 'clarify_update_final_review_then_user_started_retest' if conclusion['relation'] == 'changed'
                           else 'user_reuse_decision_or_resolve_evidence',
              'formal_integration': 'pending_joint_validation'}
    result['id'] = _digest(result)
    return result


def decide_reuse(result, decision):
    """Append a version-bound user decision without relabeling an old execution."""
    _credential_guard([result, decision])
    _verify(result)
    ids = decision.get('case_ids', [])
    rows = {r['case_id']: r for r in result['reuse']}
    if (decision.get('reconciliation_id') != result['id'] or not decision.get('actual_reply', '').strip()
            or not isinstance(decision.get('reuse'), bool) or not ids or len(set(ids)) != len(ids)
            or not set(ids) <= rows.keys()):
        raise ValueError('Explicit current reconciliation decision and scope required')
    if decision['reuse'] and any(rows[cid]['status'] != 'suggest_reuse' for cid in ids):
        raise ValueError('Insufficient evidence cannot be approved for reuse')
    updated = copy.deepcopy(result)
    for row in updated['reuse']:
        if row['case_id'] in ids:
            row['decision'] = 'reuse_approved' if decision['reuse'] else 'reuse_declined'
    updated['reuse_decisions'].append(copy.deepcopy(decision))
    updated['id'] = _digest({k: v for k, v in updated.items() if k != 'id'})
    return updated


def prepare_product_change(catalog, result, changes):
    """Reuse baseline feedback and batch grill; never apply a product change here."""
    _verify(result)
    if _digest(catalog) != result['catalog_digest'] or result['formal_conclusion']['relation'] != 'changed':
        raise ValueError('Reconcile changed product rule against current catalog first')
    affected = set(result['affected_case_ids'])
    from scoped_review import _references
    for change in changes:
        if change.get('collection') == 'cases':
            consumers = {change.get('id')}
        elif change.get('collection') == 'data':
            consumers = {c['id'] for c in catalog['cases'] if change.get('id') in _references(c)}
        else:
            consumers = set()
        if not consumers or not consumers <= affected:
            raise ValueError('Change would affect unapproved unrelated cases; reconcile scope first')
    if not changes:
        raise ValueError('Proposed business changes required')
    display_ids = affected | {link['case_id'] for row in catalog.get('extension_design', {}).get('coverage', [])
                              for link in row.get('links', [])}
    scoped = build_scoped_review(catalog, result['id'], [
        {'case_id': cid, 'action': 'related', 'reason': 'Product rule reconciliation'}
        for cid in sorted(display_ids)])['batch']
    scoped['coverage'] = copy.deepcopy(catalog.get('coverage', []))
    if catalog.get('extension_design'):
        scoped['extension_design'] = copy.deepcopy(catalog['extension_design'])
    scoped['product_reconciliation'] = {'id': result['id'],
        'formal_conclusion': copy.deepcopy(result['formal_conclusion']),
        'pending_retest': copy.deepcopy(result['pending_retest']),
        'status': 'downstream_retest_pending_not_executed'}
    # The existing feedback path preserves prior decisions, updates one common
    # version only after summary agreement, and requires separate final review.
    pending = prepare_feedback(scoped, 'chat', actual_reply=result['formal_conclusion']['actual_reply'], changes=changes)
    # This explicit reconciliation applies only to this agreed proposal; a
    # later ordinary feedback round must not reuse an old product conclusion.
    pending['product_resolution'] = copy.deepcopy(result['formal_conclusion'])
    pending['proposal_digest'] = _digest({k: pending[k] for k in ('changes', 'deletions', 'product_resolution')})
    return pending
