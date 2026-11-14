"""Exact shared-definition impact carried by the existing feedback review."""
import copy
from authoring import _digest
from step_reuse import GROUPS, resolve_step, signature
from local_step_feedback import refresh


def prepare(batch, request):
    if not request.get('explicit_request', '').strip():  # Never infer shared authority from a local edit.
        raise ValueError('Explicit P0 change request required')
    matches = [d for d in batch.get('step_definitions', []) if _digest(d) == request.get('definition_digest')]
    if len(matches) != 1:
        raise ValueError('Exact shared definition version missing')
    old, new = matches[0], request['replacement']
    if any(old[k] != new.get(k) for k in ('case_id', 'group', 'step_id', 'priority')) or new.get('priority') != 'P0':
        raise ValueError('Shared source identity changed')
    if 'step_reference' in new['step'] or new['step']['id'] != old['step']['id']:
        raise ValueError('Complete shared definition required')
    same = signature(old['step'], {d['id']: d for d in old['data']}) == signature(new['step'], {d['id']: d for d in new['data']})
    if not same and old['semantic_version'] == new['semantic_version']:
        raise ValueError('Business source change needs a new semantic version')
    impacts = []
    for case in batch['cases']:
        for group in GROUPS:
            for index, step in enumerate(case.get(group, [])):
                if step.get('step_reference', {}).get('definition_digest') == request['definition_digest']:
                    resolve_step(batch, case, group, step)  # Reject stale identity or applicability before planning.
                    impacts.append(dict(case_id=case['id'], group=group, index=index))
    source = next((c for c in batch['cases'] if c['id'] == old['case_id']), None)
    if source:
        steps = [s for s in source.get(old['group'], []) if s['id'] == old['step_id']]
        if source.get('priority') != 'P0' or source.get('semantic_version') != old['semantic_version'] or steps != [old['step']]:
            raise ValueError('Displayed P0 source differs from the exact definition version')
    assessments = request.get('assessments', []) if not same else [dict(case_id=cid, disposition='reference', reason='Presentation only; unchanged business definition') for cid in sorted({i['case_id'] for i in impacts})]
    if len({a['case_id'] for a in assessments}) != len(assessments) or {a['case_id'] for a in assessments} != {i['case_id'] for i in impacts}:
        raise ValueError('Assess every actual reference owner exactly once')
    for assessment in assessments:
        if assessment.get('disposition') not in ('reference', 'independent') or not assessment.get('reason', '').strip():
            raise ValueError('Specific applicability disposition and reason required')
    plan = copy.deepcopy(request)
    plan['impacts'] = impacts
    plan['assessments'] = assessments
    plan['formatting_only'] = same
    plan['source_present'] = source is not None
    return plan, [] if same else sorted({i['case_id'] for i in impacts} | ({old['case_id']} if source else set()))


def apply(batch, plan, blocked):
    affected = {i['case_id'] for i in plan['impacts']}
    if plan['source_present']:
        affected.add(plan['replacement']['case_id'])
    if affected & blocked:  # Shared change stays atomic when any owner is deferred.
        return set()
    old_batch = copy.deepcopy(batch)
    new = copy.deepcopy(plan['replacement'])
    batch.setdefault('step_definitions', []).append(new)  # Never overwrite historical definitions.
    if plan['source_present']:
        source = next(c for c in batch['cases'] if c['id'] == new['case_id'])
        source.setdefault('shared_definition_history', []).append(copy.deepcopy(source))
        index = next(i for i, s in enumerate(source[new['group']]) if s['id'] == new['step_id'])
        source[new['group']][index] = copy.deepcopy(new['step'])
        source['title'] = new['title']
        source['semantic_version'] = new['semantic_version']
    choices = {a['case_id']: a for a in plan['assessments']}
    for impact in plan['impacts']:
        case = next(c for c in batch['cases'] if c['id'] == impact['case_id'])
        group, index = impact['group'], impact['index']
        step = case[group][index]
        if choices[case['id']]['disposition'] == 'independent':
            case[group][index] = resolve_step(old_batch, case, group, step)[0]  # Preserve the reviewed old requirement as a full step.
        else:
            step['step_reference'].update(definition_digest=_digest(new), semantic_version=new['semantic_version'])
            resolve_step(batch, case, group, step)  # Current-case data rules must still fit; never guess bindings.
        refresh(batch, case)
    return affected
