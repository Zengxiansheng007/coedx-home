"""Resolve whole independent cases from the currently supplied source catalog."""
import copy
from authoring import _digest

GROUPS = ('common_preconditions', 'special_preconditions', 'steps', 'special_postconditions', 'common_postconditions')


def reference_digest(catalog, target):
    """Bind actual case bytes and referenced data, not a copied version label."""
    refs = {ref for group in GROUPS for step in target.get(group, []) for ref in step.get('data_refs', [])}  # Include trailing operations.
    data = {d['id']: d for d in catalog['data']}  # Caller supplies the current readable catalog.
    if refs - data.keys():
        raise ValueError('Missing referenced case data')
    return _digest({'case': {k: v for k, v in target.items() if k not in ('review_status', 'final_review', 'review_history', 'execution_status', 'merge_status')}, 'data': [data[r] for r in sorted(refs)]})  # No manually maintained expanded artifact.


def resolve_case_reference(catalog, edge):
    """Return the complete source or reject missing/drifted bindings on recovery."""
    if any(key in edge for key in ('step_ids', 'step_range', 'steps', 'skip_steps')):
        raise ValueError('Partial independent case references are not supported')
    target = next((c for c in catalog['cases'] if c['id'] == edge.get('case_id')), None)  # Read actual source content.
    if target is None:
        raise ValueError('Missing complete source case')
    if target.get('module_path') != edge.get('module_path') or reference_digest(catalog, target) != edge.get('source_digest'):
        raise ValueError('Referenced case changed; reassess affected reference')
    if target.get('endpoint') and target['endpoint'] != edge['required_state']:
        raise ValueError('Referenced endpoint changed; clarify before reuse')
    return copy.deepcopy(target)  # Identity, all actions and final state remain independent.
