"""Apply reviewed P1/P2 deltas to an isolated full catalog, never formal assets."""
import argparse
import copy
import json
from pathlib import Path
import sys

from authoring import _credential_guard, _digest
from scoped_review import _references
from dependencies import review_dependencies
from clarification import _validate_content


def _provisional_conditions(case):
    active = case.get('active_rule_decisions', case.get('rule_decisions', []) + case.get('feedback_rule_history', []))
    return [d['reply'] for d in active if d.get('reply', {}).get('decision') == 'provisional'
            and d['reply'].get('actual_reply') and d['reply'].get('product_check')]


def _business_content(case):
    return {k: v for k, v in (case or {}).items() if k not in (
        'semantic_version', 'data_version', 'review_status', 'final_review', 'review_history',
        'merge_status', 'execution_status', 'rule_status', 'rule_decisions',
        'supplied_content_confirmation', 'feedback_rule_history', 'active_rule_decisions', 'rule_decision_history')}


def _apply_delta(current, data, candidates, candidate_data, selected, actions, instruction, eligible):
    """One projection for both dependency checks and the returned full target."""
    cases, values = copy.deepcopy(current), copy.deepcopy(data)
    for cid in eligible:
        action = actions[cid]
        if action == 'reuse':
            continue
        applied = copy.deepcopy(candidates[cid])
        applied['merge_status'] = 'isolated_merged'
        if action == 'deactivate':
            applied['lifecycle'] = 'inactive'
            applied.setdefault('deactivation_history', []).append(dict(original=copy.deepcopy(current[cid]),
                reason=selected[cid]['reason'], instruction=copy.deepcopy(instruction)))
        cases[cid] = applied
        for ref in _references(applied):
            values[ref] = copy.deepcopy(candidate_data[ref])
    return cases, values


def merge_reviewed(catalog, batch, instruction, *, target_kind):
    """Return a new full target and per-case results without mutating inputs."""
    _credential_guard([catalog, batch, instruction])
    if target_kind != 'isolated' or catalog.get('kind') != 'authoring_full_catalog' or catalog.get('schema_version') != 1:
        raise ValueError('Only isolated authoring_full_catalog v1 is supported')
    if batch.get('kind') != 'scoped_review_copy' or batch.get('schema_version') != 1:
        raise ValueError('Scoped candidate and initial baseline required')
    baseline = batch['initial_copy_baseline']
    if (instruction.get('kind') != 'merge_instruction' or not instruction.get('actual_reply', '').strip()
            or instruction.get('content_version') != batch['content_version']
            or instruction.get('baseline_version') != baseline['catalog_version']
            or catalog.get('source_ref') != baseline['source_ref']):
        raise ValueError('Explicit current-version instruction and matching baseline required')
    requested = instruction.get('case_ids', [])
    candidates = {c['id']: c for c in batch['cases']}
    if not requested or len(set(requested)) != len(requested) or not set(requested) <= candidates.keys():
        raise ValueError('Unique explicit known merge scope required')
    selected = {s['case_id']: s for s in batch['selection']}
    target = copy.deepcopy(catalog)
    current = {c['id']: c for c in target['cases']}
    data = {d['id']: d for d in target['data']}
    candidate_data = {d['id']: d for d in batch['data']}
    original_data = {d['id']: d for d in baseline['catalog_data']}
    originals = {c['id']: c for c in baseline['catalog_cases']}
    if (len(candidates) != len(batch['cases']) or len(current) != len(target['cases'])
            or len(data) != len(target['data']) or len(candidate_data) != len(batch['data'])
            or len(selected) != len(batch['selection']) or candidates.keys() != selected.keys()):
        raise ValueError('Unique case, data and selection identities required')
    reasons, actions = {}, {}
    for cid in requested:
        c = candidates[cid]
        action = 'deactivate' if c.get('maintenance_action') == 'deactivate' else selected[cid]['action']
        if action in ('reuse', 'related') and batch.get('feedback_history') and (
                _business_content(c) != _business_content(originals.get(cid)) or any(
                    data.get(ref) != candidate_data.get(ref) for ref in _references(c))):
            action = 'modify'
        actions[cid] = action
        reason = None
        approval = c.get('final_review', {})
        if c.get('priority') not in ('P1', 'P2'):
            reason = 'P0_merge_belongs_to_ui_test'
        elif (c.get('review_status') != 'approved' or approval.get('approved') is not True
                or approval.get('content_version') != batch['content_version']
                or cid not in approval.get('case_ids', []) or not approval.get('actual_reply')):
            reason = 'current_final_review_required'
        elif c.get('rule_status') not in ('formal', 'provisional'):
            reason = 'rule_unresolved'
        elif c.get('rule_status') == 'provisional' and not _provisional_conditions(c):
            reason = 'provisional_authorization_condition_required'
        elif c.get('feedback_disposition') == 'excluded_this_round':
            reason = 'excluded_this_round'
        elif action not in ('add', 'modify', 'deactivate', 'reuse'):
            reason = 'related_display_only'
        elif (not c.get('semantic_version') or not c.get('data_version') or len(c.get('module_path', [])) < 5
                or not all(c.get('context', {}).get(k) for k in ('role', 'initial_state'))):
            reason = 'incomplete_candidate'
        elif (action == 'add' and cid in current) or (action != 'add' and current.get(cid) != originals.get(cid)):
            reason = 'target_drift'
        elif any(ref not in candidate_data for ref in _references(c)):
            reason = 'unresolved_data'
        elif any(data.get(ref) != original_data.get(ref) for ref in _references(c)
                 if ref in original_data):
            reason = 'target_data_drift'
        elif _digest(catalog) != baseline['catalog_digest'] and any(
                ref in data and ref not in original_data for ref in _references(c)):
            reason = 'target_data_baseline_unknown'
        if reason:
            reasons[cid] = reason
        else:
            validation = copy.deepcopy(c)
            try:
                _validate_content(dict(cases=[validation], data=batch['data']))
                if any(not s.get('expected') or not s.get('verification')
                       for key in ('steps', 'common_preconditions', 'special_preconditions', 'special_postconditions')
                       for s in c.get(key, [])):
                    reasons[cid] = 'incomplete_candidate'
            except (ValueError, KeyError, TypeError):
                reasons[cid] = 'incomplete_candidate'
    # Compute dependency closure before any write, independent of request order.
    while True:
        previous = dict(reasons)
        for cid in requested:
            if cid in reasons:
                continue
            changed_refs = {ref for ref in _references(candidates[cid])
                            if data.get(ref) != candidate_data.get(ref)}
            if any(_references(owner) & changed_refs and
                   (owner['id'] not in requested or owner['id'] in reasons or
                    actions[owner['id']] in ('reuse', 'deactivate') or
                    not (_references(owner) & changed_refs) <= _references(candidates[owner['id']]))
                   for owner in current.values()):
                reasons[cid] = 'shared_data_affects_unapproved_content'
                continue
            effective_cases, effective_data = _apply_delta(current, data, candidates, candidate_data,
                selected, actions, instruction, [key for key in requested if key not in reasons])
            effective = dict(target, cases=list(effective_cases.values()), data=list(effective_data.values()))
            stack, visited = [(candidates[cid], set(), False)], set()
            while stack:
                owner, ancestors, leaving = stack.pop()
                if leaving:
                    visited.add(owner['id'])
                    continue
                if owner['id'] in visited:
                    continue
                # Check every owner's outgoing contracts, including owners that
                # remain unchanged in the target; root approval cannot supply a
                # missing descendant data or complete-reference decision.
                if owner.get('dependencies'):
                    proposals = [dict(edge, id='merge-dep-' + str(index), current_case_id=owner['id'],
                        decision=edge.get('scope_decision', {}),
                        final_state_matches=edge.get('final_state_matches', True),
                        applicability_basis=edge.get('applicability_basis', edge.get('basis')))
                        for index, edge in enumerate(owner['dependencies'])]
                    try:
                        checked = review_dependencies(effective, 'merge-dependency-check', [owner['id']], proposals,
                            batch.get('approved_validation_scope', []))
                        if checked['blockers'] or any(p['decision'].get('include') is not True for p in proposals):
                            reasons[cid] = 'dependency_data_or_scope_incomplete:' + owner['id']
                            break
                    except (ValueError, KeyError, TypeError):
                        reasons[cid] = 'dependency_data_or_scope_incomplete:' + owner['id']
                        break
                stack.append((owner, ancestors, True))
                for edge in owner.get('dependencies', []):
                    dep_id = edge['case_id']
                    dep = effective_cases.get(dep_id)
                    if (dep_id in ancestors | {owner['id']} or not dep
                            or edge.get('module_path') != dep.get('module_path')
                            or dep.get('rule_status') not in ('formal', 'provisional')
                            or (dep.get('rule_status') == 'provisional' and not _provisional_conditions(dep))
                            or (dep_id in candidates and candidates[dep_id].get('rule_status') not in ('formal', 'provisional'))
                            or (dep_id not in requested and dep_id in originals and current.get(dep_id) != originals[dep_id])
                            or (dep_id not in requested and dep_id not in originals and
                                _digest(catalog) != baseline['catalog_digest'])
                            or dep.get('lifecycle') == 'inactive'
                            or dep.get('feedback_disposition') == 'excluded_this_round'
                            or (dep_id in requested and (dep_id in reasons or actions[dep_id] == 'deactivate'))
                            or (dep_id not in requested and dep_id in candidates and
                                (selected[dep_id]['action'] in ('add', 'modify', 'deactivate') or
                                 dep.get('maintenance_action') == 'deactivate' or
                                 _business_content(dep) != _business_content(originals.get(dep_id))))
                            or dep.get('review_status') != 'approved'):
                        reasons[cid] = 'dependency_incomplete:' + dep_id
                        break
                    if dep_id not in visited:
                        stack.append((dep, ancestors | {owner['id']}, False))
                if cid in reasons:
                    break
        if previous == reasons:
            break
    results = []
    for cid in requested:
        if cid in reasons:
            results.append(dict(case_id=cid, status='pending', reason=reasons[cid]))
            continue
        results.append(dict(case_id=cid, status='applied', action=actions[cid]))
    current, data = _apply_delta(current, data, candidates, candidate_data, selected, actions,
        instruction, [cid for cid in requested if cid not in reasons])
    target['cases'] = list(current.values())
    target['data'] = list(data.values())
    if any(r['status'] == 'applied' for r in results):
        target['content_version'] = _digest({k: v for k, v in target.items() if k != 'content_version'})
    for cid in candidates:
        if cid in requested:
            continue
        results.append(dict(case_id=cid, status='pending', reason='outside_user_merge_scope'))
    for row in results:
        case = candidates[row['case_id']]
        row.update({key: copy.deepcopy(case.get(key)) for key in (
            'module_path', 'priority', 'rule_status', 'review_status', 'semantic_version', 'data_version', 'execution_status')})
        row['review_content_version'] = case.get('final_review', {}).get('content_version')
        row['provisional_conditions'] = copy.deepcopy(_provisional_conditions(case))
        row['merge_status'] = 'isolated_merged' if row['status'] == 'applied' else 'pending'
    return dict(catalog=target, cases=results, content_version=target['content_version'],
        approved_validation_scope=copy.deepcopy(batch.get('approved_validation_scope', [])),
        formal_sync='pending_joint_validation', execution='not_started',
        evidence_kind='isolated_authoring_result',
        next_step=('Recommend separately user-started ui-test; formal synchronization awaits the next PR.'
                   if any(r['status'] == 'applied' for r in results) else
                   'Resolve pending scope, approval, dependencies or drift before an isolated merge.'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog', required=True)
    parser.add_argument('--batch', required=True)
    parser.add_argument('--instruction', required=True)
    parser.add_argument('--target-kind', required=True, choices=['isolated'])
    parser.add_argument('--output-dir', required=True)
    args = parser.parse_args()
    try:
        read = lambda p: json.loads(Path(p).read_text(encoding='utf-8-sig'))
        result = merge_reviewed(read(args.catalog), read(args.batch), read(args.instruction), target_kind=args.target_kind)
        output = Path(args.output_dir)
        output.mkdir(parents=True, exist_ok=False)
        for name, value in [('catalog.json', result['catalog']), ('merge-result.json', result)]:
            (output / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    except (ValueError, KeyError, TypeError, AttributeError, OSError):
        print('Isolated merge rejected: check approval, scope, baseline and dependencies.', file=sys.stderr)
        return 1
    print('Isolated result written; formal synchronization pending, execution not started.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
