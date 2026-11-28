"""Source-assessed preparation definitions for draft review; original cases stay complete."""
import argparse
import copy
import json
import os
from pathlib import Path

from authoring import _credential_guard, _digest


HEADINGS = {'preparation': '公共前置', 'operation': '公共操作与数据',
            'data': '公共操作与数据', 'evidence': '公共取证方法'}


def _bind(case, data):
    # A changed terminal check or request can change applicability even when preparation is identical.
    from scoped_review import _references
    refs = _references(case)
    return _digest([case, [item for item in data if item['id'] in refs]])


def assess_preparations(batch, definitions, *, source_catalog=None):
    """Bind the author's source-based assessment to every member of each complete module."""
    from preparation_scope import _authoring_scope
    _credential_guard([batch, definitions, source_catalog])
    authoring_scope = _authoring_scope(batch, source_catalog)
    result = copy.deepcopy(batch)
    members = {c['id']: c for c in batch['cases']}
    if len(members) != len(batch['cases']):
        raise ValueError('Duplicate candidate identity')
    used = set()
    names = set()
    for scope in batch.get('preparation_scopes', []):
        if scope.get('direction', 'pre') == 'pre':
            for cid in scope['applicable_case_ids']:
                steps = scope.get('step_ids_by_case', {}).get(cid, [s['id'] for s in members[cid].get('common_preconditions', [])])
                used.update((cid, step) for step in steps)
    records = []
    for item in definitions:
        if not all(isinstance(item.get(key), str) and item[key].strip()
                   for key in ('name', 'instruction', 'timing', 'source')):
            raise ValueError('Preparation requires instruction, source, timing and name')
        identity = (tuple(item['module_path']), item['name'])
        if identity in names:
            raise ValueError('Identify each definition uniquely within its module')
        names.add(identity)
        applicable, pending, excluded = (item[key] for key in ('applicable', 'pending', 'excluded'))
        ids = [*applicable, *pending, *excluded]
        module = {cid for cid, case in members.items() if case['module_path'] == item['module_path']}
        if not applicable or len(ids) != len(set(ids)) or set(ids) != module:
            raise ValueError('Assess every case in the complete module exactly once')
        if not all(isinstance(reason, str) and reason.strip() for reason in (*pending.values(), *excluded.values())):
            raise ValueError('Exceptions require a source-based reason')
        kind = item.get('kind', 'preparation')
        if 'review_condition' in item and not isinstance(item['review_condition'], str):
            raise ValueError('Review condition must be business text or an explicitly empty string')
        if kind not in HEADINGS:
            raise ValueError('Unknown shared method kind')
        for cid, slots in applicable.items():
            case = members[cid]
            available = {step['id'] for step in case.get('common_preconditions', [])}
            available.update('context/' + key for key in ('role', 'initial_state') if case.get('context', {}).get(key))
            if kind != 'preparation':
                from scoped_review import _references
                available = {'steps/' + step['id'] for step in case['steps']}
                if kind == 'data':
                    available.update('data/' + ref for ref in _references(case))
            if not isinstance(slots, list) or not slots or not all(isinstance(s, str) for s in slots) or len(set(slots)) != len(slots) or not set(slots) <= available:
                raise ValueError('Identify the original preparation steps or complete context fields')
            for slot in slots:
                # Timing, material and evidence may refer to the same business action.
                if kind in ('data', 'evidence'):
                    continue
                if (cid, slot) in used:
                    raise ValueError('Competing definitions for the same preparation')
                used.add((cid, slot))
        records.append(copy.deepcopy(item))
    result['source_preparations'] = dict(definitions=records, bindings={
        cid: _bind(case, batch['data']) for cid, case in members.items()}, sources=_digest(batch.get('sources')))
    if authoring_scope:
        result['source_preparations']['authoring_scope'] = authoring_scope
    result['content_version'] = _digest({k: v for k, v in result.items() if k != 'content_version'})
    return result


def current_definitions(batch, source_catalog=None):
    record = batch.get('source_preparations')
    if not record:
        return []
    from preparation_scope import scope_context
    complete, unavailable = scope_context(batch, source_catalog, require_parent=True)
    if unavailable:
        return []
    authoring_scope = record.get('authoring_scope')
    if authoring_scope:
        parent_ids = set(authoring_scope['parent_case_ids'])
        complete = dict(complete, cases=[c for c in complete['cases'] if c['id'] not in parent_ids])
    original = source_catalog or batch
    if authoring_scope and batch.get('initial_copy_baseline', {}).get('catalog_digest') == authoring_scope['catalog_digest']:
        original = batch
    if record['sources'] != _digest(original.get('sources')):
        return []
    members = {c['id']: c for c in complete['cases']}
    bindings = {cid: _bind(c, complete['data']) for cid, c in members.items()}
    current = []
    for item in record['definitions']:
        module = {cid for cid, c in members.items() if c['module_path'] == item['module_path']}
        ids = set(item['applicable']) | set(item['excluded']) | set(item['pending'])
        stale = {cid for cid in module & ids if bindings[cid] != record['bindings'].get(cid)}
        if module == ids and not stale:
            current.append(item)
            continue
        item = copy.deepcopy(item)
        for cid in (ids - module) | stale | (module - ids):
            for field in ('applicable', 'excluded', 'pending'):
                item[field].pop(cid, None)
            if cid in module:
                item['pending'][cid] = '用例或其关联数据已变化，须按当前来源复核'
        current.append(item)
    return current


def affected_case_ids(batch, module_path, name, version, *, source_catalog=None):
    """Resolve a proposed definition change against the complete, exact assessed version."""
    if batch.get('content_version') != version or _digest({k: v for k, v in batch.items() if k != 'content_version'}) != version:
        raise ValueError('Use the exact assessed candidate version')
    matches = [item for item in current_definitions(batch, source_catalog)
               if item['module_path'] == module_path and item['name'] == name]
    if len(matches) != 1:
        raise ValueError('Identify a current definition by complete module path and name')
    return [case['id'] for case in batch['cases'] if case['id'] in matches[0]['applicable']]


def applicable_preparations(batch, case_id, source_catalog=None):
    """Return the current ordered, source-bound instructions for an independent case."""
    return [item for item in current_definitions(batch, source_catalog) if case_id in item['applicable']]


def project_preparations(definitions, case, source, module, displayed, *, business_only=False):
    from scoped_review import BUSINESS_LABELS
    def node(label, children=None):
        return dict(text=label, children=children or [], origins=[])
    cid = case['id']
    for item in definitions:
        if cid in item['pending']:
            source['children'].append(node('适用范围待核对：' + item['name'] + '。' + item['pending'][cid]))
        if cid not in item['applicable']:
            continue
        kind = item.get('kind', 'preparation')
        if business_only and kind in ('data', 'evidence'):
            # Old evidence records bind their timing to exact invocations. Preserve the
            # observable window there while keeping the collection instructions in Agent.
            condition = item.get('review_condition', item['timing'] if kind == 'evidence' else '')
            if condition:
                operations = next((n for n in source['children'] if n['text'] == '测试步骤'), None)
                if operations:
                    for number, (step, child) in enumerate(zip(case['steps'], operations['children']), 1):
                        if 'steps/' + step['id'] in item['applicable'][cid]:
                            child['children'].insert(0, dict(node(item['name'] + '：' + condition),
                                                             condition_step=number))
            continue
        label = HEADINGS[kind]
        heading = next((n for n in module['children'] if n.get('source_preparation') and n['text'] == label), None)
        if heading is None:
            heading = dict(node(label), source_preparation=True, direction='pre', included=set())
            module['children'].append(heading)
        key = (item['name'], item['source'], item['instruction'], item['timing'])
        if key not in heading['included']:
            ids = [c['id'] for c in displayed if c['id'] in item['applicable']]
            timing = [] if business_only and kind == 'preparation' else [node('执行时机：' + item['timing'])]
            heading['children'].append(node(item['name'], [node('适用用例：' + '、'.join(ids)),
                                                          *timing, node(item['instruction'])]))
            heading['included'].add(key)
        slots = item['applicable'][cid]
        if kind != 'preparation':
            # Keep the case's trigger, data bindings, local assertions and last step.
            # Only the fixed interaction is abbreviated; each distinct invocation stays named.
            if kind == 'operation':
                group = next((n for n in source['children'] if n['text'] == '测试步骤'), None)
                if group:
                    for step, child in zip(case['steps'], group['children']):
                        if 'steps/' + step['id'] in slots and step.get('operation') == item['instruction']:
                            number = child['text'].partition('：')[0]
                            child['text'] = number + '：' + item['name']
                            child['origins'] = []
            continue
        for slot in slots:
            if slot.startswith('context/'):
                prefix = BUSINESS_LABELS['context'] + ' / ' + BUSINESS_LABELS[slot.split('/')[1]] + '：'
                source['children'] = [n for n in source['children'] if not n['text'].startswith(prefix)]
        group = next((n for n in source['children'] if n['text'] == '公共前置操作'), None)
        if group:
            group['children'] = [n for n in group['children'] if n.get('preparation_step_id') not in slots]


def render_selection(batch, case_ids=None, *, companion_base=None, blocked_ids=(), source_catalog=None):
    """Render selected cases against the complete assessed candidate and preserve input order."""
    from scoped_review import _render
    _credential_guard([batch, source_catalog])
    ids = [c['id'] for c in batch['cases']]
    chosen = ids if case_ids is None else case_ids
    if not chosen or len(chosen) != len(set(chosen)) or set(chosen) - set(ids):
        raise ValueError('Select distinct known case IDs')
    selection = {s['case_id']: s for s in batch.get('selection', [])}
    display = dict(batch, approved_validation_scope=batch.get('approved_validation_scope', []),
                   questions=batch.get('questions', []), selection=[
        selection.get(cid, dict(case_id=cid, action='related', reason='候选评审')) for cid in ids])
    visible = [cid for cid in chosen if cid not in blocked_ids]
    result = _render(display, reference_batch=source_catalog, _display_case_ids=visible, companion_base=companion_base, module_review=True)
    result['batch'] = copy.deepcopy(batch)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--source-catalog', type=Path, help='Exact complete parent for an authorized extension')
    parser.add_argument('--assessment', type=Path)
    parser.add_argument('--case', dest='ids', action='append')
    parser.add_argument('--impact', metavar='NAME', help='Review every current reference to this common definition')
    parser.add_argument('--module-path', action='append', help='Repeat for each ordered module path component')
    parser.add_argument('--version', help='Exact assessed content_version for --impact')
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    args.output_dir = Path(os.path.abspath(args.output_dir))
    batch = json.loads(args.candidate.read_text(encoding='utf-8-sig'))
    parent = json.loads(args.source_catalog.read_text(encoding='utf-8-sig')) if args.source_catalog else None
    if args.assessment:
        batch = assess_preparations(batch, json.loads(args.assessment.read_text(encoding='utf-8-sig')), source_catalog=parent)
    if args.impact:
        if args.ids or args.assessment or not args.module_path or not args.version:
            parser.error('--impact needs --module-path and --version on an assessed candidate, without --case or --assessment')
        args.ids = affected_case_ids(batch, args.module_path, args.impact, args.version, source_catalog=parent)
    elif args.module_path or args.version:
        parser.error('--version and --module-path require --impact')
    result = render_selection(batch, args.ids, source_catalog=parent)
    args.output_dir.mkdir(parents=True, exist_ok=False)
    from module_handoff import write_artifacts
    write_artifacts(result, args.output_dir, source_catalog=parent, review_ids=args.ids or [case['id'] for case in batch['cases']],
                    reader_stage='draft' if args.ids is not None else 'full')


if __name__ == '__main__':
    main()
