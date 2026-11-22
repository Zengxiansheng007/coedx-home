"""Materialize a changed reference only in its current candidate case."""
from authoring import _digest
from step_reuse import GROUPS, resolve_step, signature


def materialize(batch, case, path):
    if len(path) >= 3 and path[0] in GROUPS and isinstance(path[1], int):  # Only a declared step edit owns a local copy.
        step = case[path[0]][path[1]]
        if 'step_reference' in step:
            case[path[0]][path[1]] = resolve_step(batch, case, path[0], step)[0]  # Retain current data bindings.


def materialize_data(batch, data_id):
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
        case['reuse_target_digest'] = _digest({group: [signature(resolve_step(batch, case, group, step)[0], data)
            for step in case.get(group, [])] for group in GROUPS})
