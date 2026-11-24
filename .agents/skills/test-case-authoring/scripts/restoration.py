"""Transient, case-local restoration from current caller supplied sources."""
import copy
import hashlib
from pathlib import Path
from step_reuse import GROUPS, expanded
from cross_module_references import resolve_case_reference


def preflight(batch, *, source_catalog=None, base_path=None, require_current_sources=False):
    """Read current meaning; keep failed originals and expose only independent ready cases."""
    source = source_catalog if source_catalog is not None else batch  # A caller snapshot is evidence, never an installed/cache authority.
    data = {d['id']: d for d in source.get('data', [])}
    data.update({d['id']: d for d in batch.get('data', [])})  # Current candidate data overrides catalog history.
    definitions, conflicts = {}, set()
    for definition in source.get('step_definitions', []) + batch.get('step_definitions', []):
        key = (definition.get('case_id'), definition.get('group'), definition.get('step_id'), definition.get('semantic_version'))
        if key in definitions and {k: v for k, v in definitions[key].items() if k != 'title'} != {k: v for k, v in definition.items() if k != 'title'}:
            conflicts.add(key)  # Conflicting definitions cannot silently override current sources.
        definitions[key] = definition
    context = dict(source, data=list(data.values()), step_definitions=list(definitions.values()))
    complete, blockers = [], []
    from preparation_scope import operation_scopes
    _, scope_pending = operation_scopes(batch, source_catalog)  # Current scope conflicts block only affected cases.

    def technical(value):
        if not isinstance(value, dict):
            return
        value = value.get('shared_section', value)
        ref = value.get('source_ref')
        if not ref or base_path is None:
            return  # Pure renders have planned links; materialization/recovery supply an actual location.
        location, _, anchor = ref.partition('#')
        if '://' in location:
            raise ValueError('Technical source requires caller-readable evidence: ' + ref)
        text = (Path(base_path) / location).read_text(encoding='utf-8')  # Existence alone never proves a valid source.
        if not text.strip() or (anchor and anchor not in text):
            raise ValueError('Technical source empty or missing section: ' + ref)
        if value.get('sha256') and hashlib.sha256(text.encode()).hexdigest() != value['sha256']:
            raise ValueError('Technical source version changed: ' + ref)
        for key in ('version', 'object', 'applicability', 'endpoint'):
            if value.get(key) and str(value[key]) not in text:
                raise ValueError('Technical source ' + key + ' mismatch: ' + ref)

    def restore(case, chain):
        if case['id'] in chain:
            raise ValueError('Dependency cycle: ' + ' -> '.join(chain + [case['id']]))
        chain = chain + [case['id']]
        for group in GROUPS:
            for step in case.get(group, []):
                ref = step.get('step_reference')
                if ref and any(key[0] == ref.get('case_id') and key[2] == ref.get('step_id') for key in conflicts):
                    raise ValueError('Conflicting P0 source definitions')
                if ref and require_current_sources and source_catalog is None:
                    raise ValueError('Current P0 source required for step reference: ' + str(ref.get('case_id')))
                if ref and source_catalog is not None and (require_current_sources or source_catalog.get('kind') == 'authoring_full_catalog'):
                    origin = next((c for c in source['cases'] if c['id'] == ref['case_id']), None)
                    definition = next((d for d in context['step_definitions'] if d.get('case_id') == ref['case_id'] and d.get('step_id') == ref['step_id']), None)
                    if origin is None or definition is None:
                        raise ValueError('Missing current P0 source: ' + ref['case_id'])
                    actual = next((s for s in origin.get(group, []) if s['id'] == ref['step_id']), None)
                    if origin.get('semantic_version') != ref['semantic_version'] or actual != definition['step'] or any(next((d for d in source['data'] if d['id'] == item['id']), None) != item for item in definition['data']):
                        raise ValueError('P0 source version or step changed: ' + ref['case_id'])
        resolved = expanded(dict(context, cases=[case]))['cases'][0]  # Existing full-step order/data proof remains authoritative.
        technical(case.get('technical_handoff'))
        for group in GROUPS:
            for step in resolved.get(group, []):
                if any(r not in data for r in step.get('data_refs', [])):
                    raise ValueError('Missing data association: ' + step['id'])
                technical(step.get('technical_handoff'))
                edge = step.get('dependency')
                if edge:
                    target_id = edge.get('case_id')
                    if target_id in chain:
                        raise ValueError('Dependency cycle: ' + ' -> '.join(chain + [target_id]))
                    target = resolve_case_reference(source if source_catalog is not None else context, edge)  # Complete current independent case, never a step slice.
                    if source_catalog is not None:
                        source_data = {item['id']: item for item in source['data']}
                        target_refs = {ref for g in GROUPS for item in target.get(g, []) for ref in item.get('step_reference', item).get('data_refs', [])}
                        if any(data.get(ref) != source_data.get(ref) for ref in target_refs):
                            raise ValueError('Candidate data differs from current referenced source: ' + str(target_id))  # Validate and restore the same object data.
                    if edge.get('complete_case') is not True or not all(edge.get(k) for k in ('purpose', 'inputs', 'outputs', 'object_binding', 'data_refs')):
                        raise ValueError('Incomplete reference conditions: ' + str(target_id))
                    if not isinstance(edge['object_binding'], dict) or any(r not in edge['data_refs'] or r not in data for r in edge['object_binding'].values()):
                        raise ValueError('Wrong object data association: ' + str(target_id))
                    if edge.get('endpoint') != edge.get('required_state'):
                        raise ValueError('Inapplicable reference endpoint: ' + str(target_id))
                    restored_target = restore(target, chain)  # Resolve valid whole-step references before judging completeness.
                    if not restored_target.get('steps') or any(not item.get(k) for g in GROUPS for item in restored_target.get(g, []) for k in ('operation', 'expected', 'verification')):
                        raise ValueError('Incomplete referenced operations or assertions: ' + str(target_id))
                    step['resolved_case'] = restored_target  # Transient nested complete operations/assertions/endpoint.
        if case['id'] in scope_pending:
            raise ValueError(scope_pending[case['id']])  # Display scope-pending actions only after all references resolve.
        return resolved

    for case in batch['cases']:
        try:
            complete.append(restore(case, []))
        except (ValueError, KeyError, TypeError, OSError) as error:
            blockers.append(dict(case_id=case['id'], scope_only=case['id'] in scope_pending and str(error) == scope_pending[case['id']], reason=str(error), next_step='核实当前来源并澄清受影响引用'))
    ready = [c['id'] for c in complete]
    return dict(complete_batch=dict(copy.deepcopy(batch), cases=complete, data=list(data.values())),
                ready_case_ids=ready, blocked_case_ids=[b['case_id'] for b in blockers],
                blockers=blockers, clarifications=copy.deepcopy(blockers))  # Disposable result, no per-case ledger.


def feedback_projection(batch):
    """Preserve positions and blocked originals for editing; this is not readiness proof."""
    checked = preflight(batch)
    resolved = {c['id']: c for c in checked['complete_batch']['cases']}
    return dict(copy.deepcopy(batch), cases=[resolved.get(c['id'], copy.deepcopy(c)) for c in batch['cases']])
