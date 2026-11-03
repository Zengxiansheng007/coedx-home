"""Author dependency references and reviewed data conditions, without executing them."""
import argparse
import copy
import json
from pathlib import Path
import sys

from authoring import _credential_guard, _digest
from scoped_review import build_scoped_review, render_review_batch, GROUPS


P0_FLOW = ['recording', 'handwritten']


def review_dependencies(catalog, batch_id, current_case_ids, proposals,
                        approved_validation_scope=None):
    """Return a complete review copy plus unresolved scope/data decisions.

    Proposals are agent interpretations with source basis, never discoveries made
    by this deterministic helper. Each included edge is approved independently.
    """
    _credential_guard([catalog, proposals])
    full = copy.deepcopy(catalog)
    # Validate the whole catalog and retain the existing scoped-review boundary.
    build_scoped_review(full, batch_id, [dict(case_id=c['id'], action='related',
        reason='Read complete dependency source') for c in full['cases']])
    indexed = {c['id']: c for c in full['cases']}
    if not current_case_ids or len(set(current_case_ids)) != len(current_case_ids):
        raise ValueError('Unique current cases required')
    candidates = {cid: copy.deepcopy(indexed[cid]) for cid in current_case_ids}
    data = {d['id']: d for d in full['data']}
    selected = list(current_case_ids)
    findings, blockers, identities = [], [], set()
    for original in proposals:
        p = copy.deepcopy(original)
        identity = p['id']
        if not identity or identity in identities or p['current_case_id'] not in candidates or not p.get('basis'):
            raise ValueError('Unique proposal, current case and impact basis required')
        identities.add(identity)
        if p.get('direction') not in ('pre', 'post'):
            raise ValueError('Dependency direction must be pre or post')
        if any(key in p for key in ('step_ids', 'step_range', 'steps')):
            raise ValueError('Partial independent case references are not supported')
        decision = p.get('decision', {})
        if type(decision.get('include')) is not bool or not decision.get('actual_reply', '').strip():
            findings.append(dict(proposal=p, status='scope_decision_required'))
            blockers.append(identity + ':scope_decision_required')
            continue
        if not decision['include']:
            findings.append(dict(proposal=p, status='excluded_by_user'))
            continue
        target = indexed.get(p.get('case_id'))
        if target is None:
            findings.append(dict(proposal=p, status='missing_P0', routes=P0_FLOW,
                next_step='convert_clarify_review_user_ui_test_validate_merge'))
            blockers.append(identity + ':missing_P0')
            continue
        if p.get('module_path') != target['module_path']:
            raise ValueError('Reference identity and module path must match')
        if (p.get('complete_case') is not True or p.get('final_state_matches') is not True
                or not p.get('applicability_basis')):
            findings.append(dict(proposal=p, status='propose_add_or_split', routes=P0_FLOW,
                next_step='user_review_new_or_split_complete_P0'))
            blockers.append(identity + ':complete_applicable_case_required')
            continue
        missing = [key for key in ('purpose', 'required_state', 'inputs', 'outputs', 'object_binding', 'data_refs')
                   if not p.get(key)]
        if missing:
            findings.append(dict(proposal=p, status='reference_conditions_required', missing=missing))
            blockers.append(identity + ':reference_conditions_required')
            continue
        refs = p['data_refs']
        if (not isinstance(refs, list) or any(ref not in data for ref in refs)
                or not isinstance(p['object_binding'], dict)
                or not p['object_binding'] or any(ref not in refs for ref in p['object_binding'].values())):
            raise ValueError('Same business object must bind existing referenced data')
        # An incomplete independently maintained target returns to the common P0
        # route; no extracted subset is substituted for that record.
        if (target.get('priority') != 'P0' or not target.get('steps')
                or not target.get('title') or not target.get('semantic_version')
                or not target.get('data_version') or any(not target.get('context', {}).get(k) for k in ('role', 'initial_state')) or any(
                not s.get('operation') or not s.get('expected') or not s.get('verification')
                for group in GROUPS for s in target.get(group, []))):
            findings.append(dict(proposal=p, status='missing_P0', routes=P0_FLOW,
                next_step='convert_clarify_review_user_ui_test_validate_merge'))
            blockers.append(identity + ':missing_P0')
            continue
        asset = p.get('script_asset')
        if asset and not (asset.get('managed_by') == 'ui-test' and asset.get('applicable') is True
                          and asset.get('ref') and asset.get('basis')):
            findings.append(dict(proposal=p, status='script_requires_P0_input', routes=P0_FLOW))
            blockers.append(identity + ':script_requires_P0_input')
            continue
        for ref in refs:
            d = data[ref]
            required = ('identity_ref', 'object_ref', 'validity', 'validity_check', 'reuse_policy',
                        'invalidation_action', 'policy_decision')
            absent = [key for key in required if not d.get(key)]
            policy = d.get('reuse_policy')
            if policy not in ('long_term', 'time_limited', 'exclusive'):
                absent.append('three_way_reuse_policy')
            if policy == 'time_limited' and not (d.get('valid_until') and d.get('downstream_window')
                                                and d.get('covers_downstream_window') is True):
                absent.append('expiry_covers_downstream_window')
            if policy == 'exclusive':
                reuse = d.get('subsequent_use', {})
                if reuse.get('choice') not in ('reuse_if_valid', 'new_each_run') or not reuse.get('actual_reply', '').strip():
                    absent.append('user_subsequent_use_decision')
                if d.get('exclusive_case_id') != p['current_case_id']:
                    absent.append('exclusive_case_binding')
            if not isinstance(d.get('policy_decision'), dict) or not d['policy_decision'].get('actual_reply', '').strip():
                absent.append('user_policy_decision')
            if d.get('invalidation_action') not in ('ask_user', 'rebuild_complete_precondition'):
                absent.append('reviewed_invalidation_action')
            if d.get('invalidation_action') == 'rebuild_complete_precondition' and not d.get('rebuild_decision', {}).get('actual_reply', '').strip():
                absent.append('user_rebuild_decision')
            if absent:
                blockers.append(identity + ':data_conditions:' + ref)
                findings.append(dict(proposal_id=identity, data_ref=ref, status='data_decision_required', missing=absent))
        edge = {key: p[key] for key in ('case_id', 'module_path', 'direction', 'purpose',
                'required_state', 'inputs', 'outputs', 'object_binding', 'data_refs', 'basis')}
        edge.update(complete_case=True, scope_decision=decision,
                    validation_role='functional_target' if target['id'] in (approved_validation_scope or []) else 'preparation_only')
        if asset:
            edge['script_asset'] = asset
        current = candidates[p['current_case_id']]
        current.setdefault('dependencies', []).append(edge)
        group = 'special_preconditions' if p['direction'] == 'pre' else 'special_postconditions'
        current.setdefault(group, []).append(dict(id=identity,
            operation='完整引用 ' + target['id'] + ' / ' + ' / '.join(target['module_path']) + '；' + p['purpose'],
            data_refs=refs, dependency=edge,
            expected=[{'text': p['required_state'], 'source': 'inference'}],
            verification=[{'text': '核对同一业务对象关联及完整引用结果', 'source': 'inference'}]))
        if target['id'] not in selected:
            selected.append(target['id'])
        findings.append(dict(proposal=p, status='included_complete_reference'))
    for case in candidates.values():
        if case != indexed[case['id']]:
            case.update(rule_status='unconfirmed', review_status='pending', execution_status='not_run', merge_status='not_merged')
            case['semantic_version'] = _digest({k:v for k,v in case.items() if k != 'semantic_version'})
    changes = [c for c in candidates.values() if c != indexed[c['id']]]
    selection = [dict(case_id=cid, action='modify' if any(c['id'] == cid for c in changes) else 'related',
                      reason='本轮上下游关系评审', basis='用户决定与影响依据', coverage_impact='独立引用及数据条件')
                 for cid in selected]
    result = build_scoped_review(full, batch_id, selection, approved_validation_scope,
                                 candidates=changes)
    result['batch']['stage'] = 'P0' if all(c['priority'] == 'P0' for c in candidates.values()) else 'P1/P2'
    result['batch']['dependency_review'] = {'findings': findings, 'blockers': blockers}
    for blocker in blockers:
        proposal_id = blocker.split(':', 1)[0]
        proposal = next(p for p in proposals if p['id'] == proposal_id)
        result['batch']['questions'].append({'case_id': proposal['current_case_id'],
            'field': 'dependencies/' + proposal_id, 'reason': blocker})
    result['batch']['content_version'] = _digest({k:v for k,v in result['batch'].items() if k != 'content_version'})
    result.update(render_review_batch(result['batch']))
    result.update(findings=findings, blockers=blockers, ready_for_final_review=not blockers,
                  runtime='not_performed', formal_integration='pending_joint_validation')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog', required=True)
    parser.add_argument('--request', required=True)
    parser.add_argument('--output-dir', required=True)
    args = parser.parse_args()
    try:
        read = lambda p: json.loads(Path(p).read_text(encoding='utf-8-sig'))
        result = review_dependencies(read(args.catalog), **read(args.request))
        output = Path(args.output_dir)
        output.mkdir(parents=True, exist_ok=False)
        for filename, content in [('candidate.json', result['batch']), ('dependency-review.json',
                {k:v for k,v in result.items() if k not in ('batch', 'human_view', 'xmind_markdown', 'review_notes')})]:
            (output / filename).write_text(json.dumps(content, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        for filename, key in [('human-view.md', 'human_view'), ('xmind.md', 'xmind_markdown'), ('review-notes.md', 'review_notes')]:
            (output / filename).write_text(result[key], encoding='utf-8')
    except (ValueError, KeyError, TypeError, AttributeError, OSError):
        print('Dependency review rejected: inspect complete reference and data contract.', file=sys.stderr)
        return 1
    print('Dependency review written; no data preparation, execution or merge performed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
