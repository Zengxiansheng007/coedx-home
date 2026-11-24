"""Materialize a changed reference only in its current candidate case."""
from step_reuse import GROUPS, resolve_step, case_signature


def materialize(batch, case, path):
    if len(path) >= 3 and path[0] in GROUPS and isinstance(path[1], int):  # Only a declared step edit owns a local copy.
        step = case[path[0]][path[1]]
        if 'step_reference' in step:
            case[path[0]][path[1]] = resolve_step(batch, case, path[0], step)[0]  # Retain current data bindings.


def materialize_data(batch, data_id):
    owners = [case for case in batch['cases'] if any(data_id in step.get('step_reference', step).get('data_refs', [])
        for group in GROUPS for step in case.get(group, []))]  # Inspect the entire shared binding before copying or writing.
    if any(case.get('priority') == 'P0' for case in owners) and any(case.get('priority') in ('P1', 'P2') for case in owners):
        raise ValueError('Explicit P0 shared change required for data bound to P0 and P1/P2')  # Route mixed owners through reviewed shared impact.
    consumers = []  # Only actual current bindings own this edit, never frozen definitions.
    for case in batch['cases']:
        touched = False
        for group in GROUPS:
            for index, step in enumerate(case.get(group, [])):
                binding = step.get('step_reference', step)
                if data_id in binding.get('data_refs', []):
                    materialize(batch, case, [group, index, 'data_refs'])  # Resolve before data changes.
                    touched = True
        if touched:
            consumers.append(case)
    return consumers


def refresh(batch, case):
    if case.get('reuse_target_digest'):  # Rebind only after agreed local edits; source versions stay frozen.
        data = {item['id']: item for item in batch['data']}
        resolved = {group: [resolve_step(batch, case, group, step)[0] for step in case[group]]
            for group in GROUPS if group in case}  # This caller retains reference resolution policy.
        case['reuse_target_digest'] = case_signature(resolved, data)
