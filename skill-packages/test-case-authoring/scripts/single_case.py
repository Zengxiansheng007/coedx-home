"""Retrieve one complete business case from an exact assessed candidate."""
import argparse
import copy
import json
from pathlib import Path

from authoring import _credential_guard, _digest
from preparation_scope import operation_scopes, scope_context
from reader_delivery import case_references
from restoration import preflight, validate_executable_step
from review_segments import checked_range, signature
from scoped_review import GROUPS, _references
from source_preparation import current_definitions


def _one(records, identity, label):
    matches = [row for row in records if row['id'] == identity]
    if len(matches) != 1:
        raise ValueError(f'{label} {identity}: expected one source, found {len(matches)}')
    return matches[0]


def get_case(batch, version, case_id, *, source_catalog=None, base_path=None):
    if not version or version != batch.get('content_version') or version != _digest({
            key: value for key, value in batch.items() if key != 'content_version'}):
        raise ValueError('Candidate version mismatch: ' + str(version))
    case = _one(batch['cases'], case_id, 'Case')
    complete, missing = scope_context(batch, source_catalog, require_parent=True)
    if missing:
        raise ValueError('Missing or changed complete parent: ' + str(batch['initial_copy_baseline']['catalog_version']))
    source = source_catalog or complete
    segment = case.get('review_segment')
    if segment:
        origin = _one(source['cases'], segment['p0_case_id'], 'P0')
        signature_version = segment['binding'].get('signature_version', 1)
        if (signature(origin, source['data'], signature_version) != segment['binding']['source_digest'] or
                signature(case, batch['data'], signature_version) != segment['binding']['target_digest']):
            raise ValueError('Changed assessed segment source: ' + origin['id'])
        checked_range(segment, case, origin)

    _, unresolved = operation_scopes(batch, source_catalog)
    if case_id in unresolved:
        raise ValueError(case_id + ': ' + unresolved[case_id])
    restored = preflight(dict(batch, cases=[case], preparation_scopes=[]), source_catalog=source, base_path=base_path,
                         require_current_sources=True)
    if restored['blockers']:
        raise ValueError(case_id + ': ' + restored['blockers'][0]['reason'])
    case = restored['complete_batch']['cases'][0]
    if not case.get('steps'):
        raise ValueError(case_id + ': missing business steps')
    if not all(case.get('context', {}).get(key) for key in ('role', 'initial_state')):
        raise ValueError(case_id + ': missing role or initial state')
    refs = set()
    def collect(owner):
        refs.update(_references(owner))
        for group in GROUPS:
            step_ids = [step.get('id') for step in owner.get(group, [])]
            if any(not sid for sid in step_ids) or len(step_ids) != len(set(step_ids)):
                raise ValueError(f"{owner['id']}/{group}: missing or repeated step identity")
            for step in owner.get(group, []):
                validate_executable_step(owner['id'], group, step)
                if 'resolved_case' in step:
                    collect(step['resolved_case'])
    collect(case)
    data = {}
    for ref in sorted(refs):
        records = batch['data'] if any(d['id'] == ref for d in batch['data']) else source['data']
        data[ref] = _one(records, ref, 'Data')
    definitions = current_definitions(batch, source_catalog)
    if batch.get('source_preparations', {}).get('definitions') and not definitions:
        raise ValueError(case_id + ': missing current preparation source')
    methods, pending = [], []
    for definition in definitions:
        if case_id in definition['applicable']:
            fields = ('name', 'kind', 'timing', 'instruction', 'source')
            method = {key: definition[key] for key in fields if key in definition}
            methods.append(dict(method, applies_at=definition['applicable'][case_id]))
        if case_id in definition['pending']:
            pending.append(dict(name=definition['name'], reason=definition['pending'][case_id]))
    last = case['steps'][-1]
    case.pop('review_segment', None)
    packet = dict(content_version=version, case=case, data=data, methods=methods,
                  applicability_pending=pending, sources=batch.get('sources', []),
                  endpoint=dict(step_id=last['id'], order=len(case['steps']), verification=last['verification']),
                  evidence_policy='按本次运行保存各步观测。已观察的违例判失败；必查证据缺失或无法关联本次时标为待取证，写明缺口，整例不得判通过。')
    _credential_guard(packet)
    return copy.deepcopy(packet)


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def get_agent_case(path, version, case_id):
    index = read_json(path)
    if (not isinstance(index, dict) or index.get('format') != 'tca.agent-review.v1'
            or index.get('candidate') != 'candidate.json'):
        raise ValueError('Expected a delivered Agent review index with its adjacent candidate.json')
    if index.get('content_version') != version:
        raise ValueError('Agent index version mismatch: ' + version)
    ids, bindings = index['case_ids'], index['cases']
    if (not isinstance(ids, list) or not isinstance(bindings, dict)
            or not all(isinstance(cid, str) and cid for cid in ids)
            or len(ids) != len(set(ids)) or set(ids) != set(bindings)):
        raise ValueError('Inconsistent Agent case scope')
    if case_id not in ids:
        raise ValueError('Case outside delivered Agent scope: ' + case_id)
    for blocker in index['blockers']:
        if blocker['case_id'] == case_id:
            raise ValueError(case_id + ': ' + blocker['reason'])
    batch = read_json(path.parent / 'candidate.json')
    case = _one(batch['cases'], case_id, 'Case')
    if case.get('feedback_disposition') == 'excluded_this_round':
        raise ValueError('Case excluded from this review: ' + case_id)
    if bindings[case_id] != case_references(case):
        raise ValueError('Agent step or data identities differ from the candidate: ' + case_id)
    parent = None
    if 'source_catalog' in index or 'source_catalog_version' in index:
        baseline = batch.get('initial_copy_baseline') or {}
        if (index.get('source_catalog') != 'source-catalog.json' or not baseline.get('catalog_version')
                or index.get('source_catalog_version') != baseline['catalog_version']):
            raise ValueError('Agent source catalog has no matching candidate parent binding')
        parent = read_json(path.parent / 'source-catalog.json')
    return get_case(batch, version, case_id, source_catalog=parent, base_path=path.parent)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--agent', type=Path, help='agent.json from the delivered review scope')
    source.add_argument('--candidate', type=Path, help='Direct access to an assessed candidate')
    parser.add_argument('--version', required=True)
    parser.add_argument('--case', required=True)
    parser.add_argument('--source-catalog', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.agent:
            if args.source_catalog:
                parser.error('--agent resolves its own source catalog')
            packet = get_agent_case(args.agent, args.version, args.case)
        else:
            packet = get_case(read_json(args.candidate), args.version, args.case,
                              source_catalog=read_json(args.source_catalog) if args.source_catalog else None,
                              base_path=args.candidate.parent)
        with args.output.open('x', encoding='utf-8') as stream:
            json.dump(packet, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
    except (ValueError, KeyError, OSError) as error:
        parser.exit(2, f'{error}\n')


if __name__ == '__main__':
    main()
