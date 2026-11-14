"""Version-bound whole-step definitions; no execution or historic pass inheritance."""
import copy
from authoring import _digest

GROUPS = ('common_preconditions', 'special_preconditions', 'steps', 'special_postconditions')
TECHNICAL = {'id', 'source', 'lines', 'basis', 'provenance'}


def _business(value):
    if isinstance(value, dict):  # Compare business leaves independently of source addresses.
        return {key: _business(child) for key, child in value.items() if key not in TECHNICAL}
    if isinstance(value, list):
        return [_business(child) for child in value]
    return value


def signature(step, data, rules_only=False):
    result = _business({key: value for key, value in step.items() if key != 'data_refs'})  # Preserve unknown business conditions.
    result['data'] = [_business(data[ref]) for ref in step.get('data_refs', [])]  # Object identity alone is insufficient.
    if rules_only:
        for item in result['data']:
            if isinstance(item.get('generation_rule'), str) and item['generation_rule'].strip():
                item.pop('value', None)  # Only explicit generation rules separate values from semantics.
    return result


def select_reuse(catalog, candidates, candidate_data):
    """Choose references only from complete target designs with agent assessments."""
    cases = copy.deepcopy(candidates)  # Never mutate the supplied design.
    originals = {case['id']: case for case in catalog['cases']}
    source_data = {item['id']: item for item in catalog['data']}
    target_data = dict(source_data, **{item['id']: item for item in candidate_data})
    definitions = {}  # One technical definition per exact P0 step version.
    for case in cases:
        target_digest = _digest({group: [signature(step, target_data) for step in case.get(group, [])] for group in GROUPS})  # Capture the authored order and endpoint.
        selected = False
        for assessment in case.pop('reuse_assessments', []):
            group = assessment['group']
            if group not in GROUPS or case.get('priority') not in ('P1', 'P2'):
                raise ValueError('step reference needs a P1/P2 target and known group')
            if not all(assessment.get(key) for key in ('applicability', 'endpoint', 'source_basis')) or not all(isinstance(assessment.get('comparison', {}).get(key), str) and assessment['comparison'][key].strip() for key in ('operation', 'data', 'expected', 'verification')):
                raise ValueError('step reference needs substantive four-part agent assessment')
            source = originals.get(assessment['p0_case_id'])
            if not source or source.get('priority') != 'P0':
                raise ValueError('step reference source must be P0')
            matches = [step for step in source.get(group, []) if step['id'] == assessment['p0_step_id']]
            targets = [step for step in case.get(group, []) if step['id'] == assessment['step_id']]
            if len(matches) != 1 or len(targets) != 1 or 'step_reference' in matches[0]:
                raise ValueError('step reference source or target missing/ambiguous')
            source_step, target = matches[0], targets[0]
            source_refs, target_refs = source_step.get('data_refs', []), target.get('data_refs', [])  # Ordered whole-step bindings.
            if signature(source_step, source_data, True) != signature(target, target_data, True) or any(a != b and not source_data[a].get('generation_rule') for a, b in zip(source_refs, target_refs)):
                continue  # Any business difference remains a complete independent step.
            definition = {'case_id': source['id'], 'title': source['title'], 'group': group,
                          'step_id': source_step['id'], 'semantic_version': source['semantic_version'],
                          'priority': 'P0', 'step_number': source[group].index(source_step) + 1,
                          'step': copy.deepcopy(source_step),
                          'data': [copy.deepcopy(source_data[ref]) for ref in source_step.get('data_refs', [])]}
            digest = _digest(definition)
            definitions[digest] = definition
            target.clear()  # Reference and inline fields are mutually exclusive.
            target.update(id=assessment['step_id'], step_reference={
                'definition_digest': digest, 'case_id': source['id'], 'group': group,
                'step_id': source_step['id'], 'semantic_version': source['semantic_version'],
                'data_refs': copy.deepcopy(target_refs),
                'data_binding_digest': _digest([target_data[ref] for ref in target_refs]),  # Freeze current case values independently of P0.
                'context_digest': _digest(case.get('context', {})),
                'assessment': copy.deepcopy(assessment)})
            selected = True
        if selected:
            case['reuse_target_digest'] = target_digest  # Technical proof, not another maintained draft.
    return cases, list(definitions.values())


def resolve_step(batch, case, group, step):
    if 'step_reference' not in step:
        return copy.deepcopy(step), None  # Full candidates remain compatible.
    path = case['id'] + '/' + group + '/' + step.get('id', '?')
    if set(step) != {'id', 'step_reference'} or case.get('priority') not in ('P1', 'P2'):
        raise ValueError('step reference overrides or invalid target: ' + path)
    ref = step['step_reference']
    matches = [item for item in batch.get('step_definitions', []) if _digest(item) == ref.get('definition_digest')]
    if len(matches) != 1:
        raise ValueError('step reference missing or stale: ' + path)
    definition = matches[0]
    if ref.get('context_digest') != _digest(case.get('context', {})):
        raise ValueError('step reference applicability or binding changed: ' + path)
    if definition.get('priority') != 'P0' or 'step_reference' in definition['step'] or group != definition['group'] or any(ref.get(key) != definition.get(key) for key in ('case_id', 'group', 'step_id', 'semantic_version')):
        raise ValueError('step reference inapplicable: ' + path)
    data = {item['id']: item for item in batch['data']}
    current_refs = ref.get('data_refs', [])
    if any(key not in data for key in current_refs):
        raise ValueError('step reference data missing: ' + path)
    if ref.get('data_binding_digest'):
        if ref['data_binding_digest'] != _digest([data[key] for key in current_refs]):
            raise ValueError('step reference data binding changed: ' + path)
        bound = dict(definition['step'], data_refs=current_refs)
        if signature(bound, data, True) != signature(definition['step'], {item['id']: item for item in definition['data']}, True):
            raise ValueError('step reference data rules changed: ' + path)
    elif current_refs != definition['step'].get('data_refs', []) or any(data.get(item['id']) != item for item in definition['data']):
        raise ValueError('step reference data changed: ' + path)
    resolved = copy.deepcopy(definition['step'])
    resolved['id'] = step['id']  # Current case order and identity remain authoritative.
    resolved['data_refs'] = copy.deepcopy(current_refs)  # Bind the complete definition to current case data.
    return resolved, definition


def expanded(batch):
    result = copy.deepcopy(batch)
    for case in result['cases']:
        if any('step_reference' in step for group in GROUPS for step in case.get(group, [])) and not case.get('reuse_target_digest'):
            raise ValueError('step reference target verification missing: ' + case['id'])
        for group in GROUPS:
            if group in case:
                case[group] = [resolve_step(batch, case, group, step)[0] for step in case[group]]
        if case.get('reuse_target_digest'):
            data = {item['id']: item for item in result['data']}
            current = _digest({group: [signature(step, data) for step in case.get(group, [])] for group in GROUPS})
            if current != case['reuse_target_digest']:
                raise ValueError('step reference target sequence or endpoint changed: ' + case['id'])
    return result


def reference_data(case):
    """Return fixed-data identities carried by assessed reference bindings."""
    return {ref for group in GROUPS for step in case.get(group, [])
            for ref in step.get('step_reference', {}).get('data_refs', [])}
