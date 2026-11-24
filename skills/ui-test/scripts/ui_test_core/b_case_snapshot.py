"""Offline review snapshots: existing contracts, no execution or approval authority."""
from __future__ import annotations

import copy
import html
import json
import re
from typing import Any
from .case_contracts import canonical_hash, validate_source_case, validate_document
from .test_data_contracts import resolve_parameter_manifest, parse_typed_reference, TestDataError

_SENSITIVE = re.compile(r'password|passwd|pwd|token|cookie|authorization|storage_state|secret|credential|api_key|apikey|密码|口令|令牌', re.I)


def _mask(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: '<credential-ref>' if _SENSITIVE.search(key) else _mask(child) for key, child in value.items()}
    if isinstance(value, list):
        return [_mask(item) for item in value]
    return copy.deepcopy(value)


def _bindings(case):
    steps = [step for group in ('setup', 'feature', 'assertions') for step in case['steps'][group]]
    steps += case.get('special_preconditions', [])
    for step in steps:
        for parameter in step.get('parameters', []):
            yield step['step_id'], parameter


def _data_document(data):
    # Loader metadata is not part of the canonical Test Data schema/hash.
    document = {key: copy.deepcopy(value) for key, value in data.items() if key not in {'test_data_hash', 'source_path'}}
    if validate_document(document, 'test-data.schema.json'):
        raise ValueError('E_SNAPSHOT_TEST_DATA_SCHEMA_INVALID')
    document['test_data_hash'] = canonical_hash(document)
    return document


def create_snapshot(source_case: dict[str, Any], test_data: dict[str, Any], *,
                    source_path: str = '<inline>', data_path: str = '<inline>',
                    runtime_values: dict[str, Any] | None = None) -> dict[str, Any]:
    """Bind review text to current case/data content, retaining refs without reading secrets.

    Legacy /title refs are explicitly relative to Test Data.parameters; typed
    test-data:/parameters/title refs use the shared canonical resolver.
    Unknown references are review gaps, never silently accepted actual values.
    """
    if isinstance(source_case, dict) and source_case.get('schema_version') == 'ui-test.source-case.v2':
        return _create_v2_snapshot(source_case, test_data, source_path, data_path, runtime_values)
    if validate_source_case(source_case):
        raise ValueError('E_SNAPSHOT_SOURCE_CASE_INVALID')
    data = _data_document(test_data)
    if data['case_id'] != source_case['case_id']:
        raise ValueError('E_SNAPSHOT_CASE_MISMATCH')
    if source_case.get('branch_id') != data['branch_id']:
        raise ValueError('E_SNAPSHOT_BRANCH_MISMATCH')
    parameters, gaps, refs = [], [], []
    for index, (step_id, binding) in enumerate(_bindings(source_case)):
        kind = binding['source_type']
        label = binding['label']
        display = binding['display_value']
        raw_ref = binding.get('index_ref') or (display if kind in {'reference', 'environment'} else None)
        param = {'step_id': step_id, 'label': label, 'source_type': kind}
        sensitive = binding.get('sensitive', False) or bool(_SENSITIVE.search(label))
        if sensitive:
            param.update(value='<credential-ref>', reference_only=True)
            # Only typed credential identifiers may survive; a literal is never a ref.
            if isinstance(raw_ref, str) and re.fullmatch(r'credential:[A-Za-z0-9_.:/-]+', raw_ref):
                param['ref'] = raw_ref
            else:
                gaps.append({'code': 'CREDENTIAL_REF_REQUIRED', 'parameter_id': str(index)})
        elif kind == 'literal':
            param['value'] = display
        elif kind == 'generated':
            if display in data['generation_rules']:
                param.update(value='<generated:rule>', generation_rule=_mask(data['generation_rules'][display]))
            else:
                param.update(value='<unresolved>', generation_rule=None)
                gaps.append({'code': 'GENERATION_RULE_NOT_FOUND', 'parameter_id': str(index)})
        else:
            ref = raw_ref
            if kind in {'shared-data', 'public-data'} and isinstance(ref, str) and ref.startswith('/'):
                ref = 'test-data:/parameters' + ref
            try:
                prefix, target = parse_typed_reference(ref)
                if prefix == 'value':
                    # No environment or runtime vault reads in an offline review.
                    param.update(value='<environment-ref>', ref=ref, reference_only=True)
                    gaps.append({'code': 'RUNTIME_VALUE_NOT_RESOLVED', 'parameter_id': str(index)})
                else:
                    manifest = resolve_parameter_manifest(
                        parameter_bindings=[{'parameter_id': str(index), 'label': label, 'ref': ref}],
                        test_data=data,
                        credential_keys={target} if prefix == 'credential' else set(),
                        sequence_keys={target} if prefix == 'sequence' else set())
                    resolved = manifest['parameters'][0]
                    if resolved.get('reference_only'):
                        param.update(value='<credential-ref>' if prefix == 'credential' else '<sequence-ref>', ref=ref, reference_only=True)
                    elif _SENSITIVE.search(target):
                        param.update(value='<credential-ref>', reference_only=True)
                        gaps.append({'code': 'CREDENTIAL_REF_REQUIRED', 'parameter_id': str(index)})
                    else:
                        param.update(value=_mask(resolved['value']), ref=ref)
            except TestDataError:
                param['value'] = '<unresolved>'
                gaps.append({'code': 'PARAMETER_REFERENCE_UNRESOLVED', 'parameter_id': str(index)})
        if param.get('reference_only') and param.get('value') == '<credential-ref>':
            refs.append({key: copy.deepcopy(param[key]) for key in ('label', 'step_id', 'ref', 'reference_only') if key in param})
        parameters.append(param)
    # Include declared credential refs even when not bound to a particular step.
    for ref in data.get('runtime_refs', []):
        if ref.startswith('credential:') and not any(item.get('ref') == ref for item in refs):
            refs.append({'ref': ref, 'label': 'runtime', 'step_id': '', 'reference_only': True})
    dependencies = {'source_case': canonical_hash(source_case), 'test_data': data['test_data_hash']}
    snapshot = {
        'schema_version': 'ui-test.b-snapshot.v1', 'snapshot_type': 'parameter-review',
        'case_id': source_case['case_id'], 'case_version': source_case['case_version'],
        'branch_id': source_case['branch_id'], 'data_revision': data['data_revision'],
        'status': 'draft', 'approved': False, 'dependency_hashes': dependencies,
        'source_map': {'source_case_hash': dependencies['source_case'], 'test_data_hash': dependencies['test_data'],
                       'source_path': source_path, 'data_path': data_path},
        'parameters': parameters, 'generation_rules': _mask(data['generation_rules']),
        'credential_refs': refs, 'credential_values_resolved': False, 'gaps': gaps,
        'unbound_parameters': _mask(data['parameters']),
    }
    # Hash the actual review material as well as the original dependency digests.
    snapshot['snapshot_hash'] = canonical_hash(snapshot)
    return snapshot


def _create_v2_snapshot(source_case, test_data, source_path, data_path, runtime_values):
    # Keep the v1 path byte-for-byte in its output. V2 resolves the existing
    # compiler's parameter/step contracts, without invoking compilation or UI.
    from .compiler_v2 import _resolve_steps
    if validate_document(source_case, 'source-case-v2.schema.json'):
        raise ValueError('E_SNAPSHOT_SOURCE_CASE_INVALID')
    data = _data_document(test_data)
    if data['case_id'] != source_case['case_id']:
        raise ValueError('E_SNAPSHOT_CASE_MISMATCH')
    if data['branch_id'] != source_case['branch_id']:
        raise ValueError('E_SNAPSHOT_BRANCH_MISMATCH')
    if runtime_values is not None and not isinstance(runtime_values, dict):
        raise ValueError('E_SNAPSHOT_RUNTIME_VALUES_INVALID')
    ids = [p['parameter_id'] for p in source_case['parameter_bindings']]
    assertions = [p['assertion_id'] for step in source_case['steps'] for p in step['postconditions']]
    if len(ids) != len(set(ids)) or len(assertions) != len(set(assertions)):
        raise ValueError('E_SNAPSHOT_DUPLICATE_ID')
    for step in source_case['steps']:
        for expectation in step['postconditions']:
            prefix, _, target = expectation['expected_ref'].partition(':')
            if prefix == 'test-data' and _SENSITIVE.search(target):
                raise ValueError('E_SNAPSHOT_CREDENTIAL_REFERENCE_REQUIRED')
    declared = set(data['runtime_refs'])
    credentials = {parse_typed_reference(r)[1] for r in declared if r.startswith('credential:')}
    sequences = {parse_typed_reference(r)[1] for r in declared if r.startswith('sequence:')}
    resolved, gaps = [], []
    for binding in source_case['parameter_bindings']:
        pid, reference = binding['parameter_id'], binding['ref']
        prefix, target = parse_typed_reference(reference)
        item = {'parameter_id':pid, 'label':binding['label'], 'ref':reference,
                'source_type':prefix, 'required':binding.get('required', True)}
        sensitive = bool(_SENSITIVE.search(binding['label']) or _SENSITIVE.search(target))
        try:
            if sensitive and prefix != 'credential':
                raise TestDataError('E_CREDENTIAL_REFERENCE_REQUIRED')
            manifest = resolve_parameter_manifest(parameter_bindings=[binding], test_data=data,
                runtime_values=runtime_values, credential_keys=credentials, sequence_keys=sequences)
            item = _mask(manifest['parameters'][0]) if prefix not in {'credential','sequence'} else manifest['parameters'][0]
            if item.get('reference_only'):
                item['value'] = '<credential-ref>' if prefix == 'credential' else '<sequence-ref>'
        except TestDataError as error:
            # Stable error code only; never retain the failed value or exception text.
            code = str(error).split(':', 1)[0]
            item['value'] = '<unresolved>'
            gaps.append({'code':code, 'parameter_id':pid})
        resolved.append(item)
    try:
        steps = _resolve_steps(source_case, {'parameters':resolved}, data)
    except (ValueError, KeyError, TypeError) as error:
        raise ValueError('E_SNAPSHOT_STEP_CONTRACT_INVALID') from error
    parameters = [dict(copy.deepcopy(p), step_id=step['source_step_id'])
                  for step in steps for p in step['parameters']]
    used = {p['parameter_id'] for p in parameters}
    parameters += [dict(copy.deepcopy(p), step_id='') for p in resolved if p['parameter_id'] not in used]
    refs = [{'ref':r,'label':'runtime','step_id':'','reference_only':True}
            for r in data['runtime_refs'] if r.startswith('credential:')]
    dependencies = {'source_case':canonical_hash(source_case), 'test_data':data['test_data_hash']}
    snapshot = {
        'schema_version':'ui-test.b-snapshot.v1', 'snapshot_type':'parameter-review',
        'case_id':source_case['case_id'], 'case_version':source_case['case_version'],
        'branch_id':source_case['branch_id'], 'data_revision':data['data_revision'],
        'status':'draft', 'approved':False, 'dependency_hashes':dependencies,
        'source_map':{'source_case_hash':dependencies['source_case'],'test_data_hash':dependencies['test_data'],
                      'source_path':source_path,'data_path':data_path},
        'parameters':parameters,'generation_rules':_mask(data['generation_rules']),
        'credential_refs':refs,'credential_values_resolved':False,'gaps':gaps,
        'unbound_parameters':_mask(data['parameters']), 'resolved_steps':_mask(steps),
    }
    snapshot['snapshot_hash'] = canonical_hash(snapshot)
    return snapshot


def _cell(value):
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    return html.escape(text).replace('|', '&#124;').replace('\r', '').replace('\n', '<br>')


def render_snapshot_markdown(snapshot: dict[str, Any]) -> str:
    lines = ['# 参数审阅快照 — ' + _cell(snapshot['case_id']) + ' v' + str(snapshot['case_version']), '',
             '分支: ' + _cell(snapshot['branch_id']), '数据版本: ' + str(snapshot['data_revision']),
             '快照哈希: ' + snapshot['snapshot_hash'],
             '状态: 离线审阅材料；本文件不授予执行权限。', '', '## 参数清单', '',
             '| 步骤 | 标签 | 来源 | 实际值/规则 | 引用 |', '|---|---|---|---|---|']
    for param in snapshot['parameters']:
        lines.append('| ' + ' | '.join(_cell(value) for value in [param['step_id'], param['label'], param['source_type'], param.get('generation_rule', param.get('value')), param.get('ref', '')]) + ' |')
    for title, key in [('生成规则', 'generation_rules'), ('分支参数原文（敏感字段仅引用）', 'unbound_parameters'), ('凭据引用', 'credential_refs'), ('依赖哈希', 'dependency_hashes'), ('来源', 'source_map'), ('需澄清项', 'gaps')]:
        lines.extend(['', '## ' + title, '', _cell(snapshot[key])])
    return '\n'.join(lines) + '\n'


def detect_version_change(current_snapshot: dict[str, Any], prior_snapshot: dict[str, Any] | None) -> dict[str, Any]:
    """Return invalidation advice only; preserve prior snapshots and failure refs."""
    changes = []
    if prior_snapshot is not None:
        for key, code in [('case_id', 'case_changed'), ('case_version', 'case_version_changed'), ('branch_id', 'branch_changed')]:
            if current_snapshot.get(key) != prior_snapshot.get(key):
                changes.append(code)
        for key, code in [('source_case', 'source_case_changed'), ('test_data', 'test_data_changed')]:
            if current_snapshot['dependency_hashes'][key] != prior_snapshot['dependency_hashes'][key]:
                changes.append(code)
        if current_snapshot['snapshot_hash'] != prior_snapshot['snapshot_hash'] and not changes:
            changes.append('review_material_changed')
    stale = []
    if changes:
        stale = ['case-ir.json', 'human-view.md', 'midscene-prompt.json', 'playwright.py',
                 'resolved-test-data.json', 'parameter-manifest.json', 'parameter-snapshot.json', 'approval-record.json']
        if prior_snapshot.get('approved'):
            changes.append('approval_invalidated')
    return {'changed': bool(changes), 'change_types': changes, 'stale_derivative_refs': stale,
            'stale_refs_kind': 'logical-asset-roles-not-filesystem-paths',
            'preserved_failure_refs': copy.deepcopy((prior_snapshot or {}).get('failure_refs', []))}
