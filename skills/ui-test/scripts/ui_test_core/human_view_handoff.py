"""UI-Test binding of a TCA Human View to one resolved formal build."""

from copy import deepcopy
from hashlib import sha256

from .case_contracts import canonical_hash, validate_document


TCA_RENDERER_VERSION = 'tca-human-view-v1'
HUMAN_VIEW_JOURNAL = '.human-view-activation.json'
FIELDS = ('case_id', 'branch_id', 'source_hash', 'test_data_hash', 'parameter_manifest_hash', 'renderer_version')
RUNTIME_REFS = ('value:', 'credential:', 'sequence:')


def _visible(reference, value, reference_only):
    if reference_only or reference.startswith(RUNTIME_REFS):
        return reference  # 运行时值只交付治理引用。
    return deepcopy(value)


def make_human_view_request(identity, build, display_name, resolved_steps, parameter_manifest):
    references = {item['parameter_id']: item['ref'] for item in parameter_manifest['parameters']}

    def assertion_value(assertion):
        ref = assertion.get('expected_reference', assertion['expected_ref'])
        if ref.startswith('parameter:'):
            ref = references[ref.partition(':')[2]]  # 断言复用参数也保留治理引用。
        return _visible(ref, assertion.get('expected_value'), assertion.get('reference_only'))

    steps = []
    for step in resolved_steps:
        parameters = [
            {'label': item['label'], 'value': _visible(item['ref'], item.get('value'), item.get('reference_only'))}
            for item in step['parameters']
        ]
        assertions = [
            {'id': item['assertion_id'], 'operator': item['operator'],
             'value': assertion_value(item)}
            for item in step['postconditions']
        ]
        steps.append(dict(sequence=step['sequence'], operation=step['intent'], parameters=parameters,
                          expected=step['expected_result'], assertions=assertions))
    request = {
        'schema_version': 'ui-test.tca-human-view-request.v1',
        'identity': {**{field: identity[field] for field in FIELDS}, 'build_fingerprint': build},
        'display_name': display_name,
        'steps': steps,
    }
    return {**request, 'request_hash': canonical_hash(request)}


def raw_digest(markdown):
    return 'sha256:' + sha256(markdown.encode('utf-8')).hexdigest()


def _verified_request(compiled):
    request = compiled.get('human_view_request')
    if not request:
        raise ValueError('E_HUMAN_VIEW_HANDOFF_REQUIRED')
    build = compiled['manifest']['build_fingerprint']
    expected = make_human_view_request(compiled['identity'], build, compiled['case_ir']['display_name'],
                                       compiled['resolved_ir']['resolved_steps'], compiled['parameter_manifest'])
    if request != expected or build != canonical_hash(compiled['identity']):
        raise ValueError('E_HUMAN_VIEW_REQUEST_DRIFT:' + compiled['manifest']['case_id'])
    return request


def bind_formal_human_view(compiled, artifact):
    """Attach the exact authored Markdown before the normal release planning entry."""
    request = _verified_request(compiled)
    if not isinstance(artifact, dict):
        raise ValueError('E_HUMAN_VIEW_HANDOFF_REQUIRED')
    if (artifact.get('schema_version') != 'tca.formal-human-view.v1'
            or artifact.get('identity') != request['identity']
            or artifact.get('request_hash') != request['request_hash']):
        raise ValueError('E_HUMAN_VIEW_IDENTITY:' + request['identity']['case_id'])
    markdown = artifact.get('markdown')
    required_prefix = (
        '<!-- do_not_edit: true -->\n'
        f'<!-- build_fingerprint: {request["identity"]["build_fingerprint"]} -->\n'
        f'<!-- tca_request: {request["request_hash"]} -->\n'
    )
    if (not isinstance(markdown, str) or not markdown.startswith(required_prefix)
            or not markdown.endswith('\n') or '\r' in markdown
            or raw_digest(markdown) != artifact.get('sha256')):
        raise ValueError('E_HUMAN_VIEW_ARTIFACT_BYTES:' + request['identity']['case_id'])
    result = deepcopy(compiled)
    outputs = result['outputs']
    outputs['human.md'] = markdown
    receipt = outputs['compile-receipt.json']
    receipt['artifact_names'] = sorted(outputs)
    manifest = result['manifest']
    manifest['human_view_sha256'] = artifact['sha256']
    manifest['artifacts'] = {name: canonical_hash(content) for name, content in sorted(outputs.items())}
    if 'provenance' in result:
        result['provenance']['artifacts'] = sorted(set(result['provenance']['artifacts']) | {'human.md'})
        result['provenance_hash'] = canonical_hash(result['provenance'])
    if validate_document(manifest, 'case-manifest-v2.schema.json'):
        raise ValueError('E_HUMAN_VIEW_BOUND_MANIFEST_INVALID')
    return result


def required_view_digest(compiled):
    if compiled['identity']['renderer_version'] != TCA_RENDERER_VERSION:
        return None
    request = _verified_request(compiled)
    markdown = compiled['outputs'].get('human.md')
    digest = compiled['manifest'].get('human_view_sha256')
    binding = f'<!-- tca_request: {request["request_hash"]} -->'
    if (not isinstance(markdown, str) or digest is None or raw_digest(markdown) != digest
            or binding not in markdown.splitlines()[:3]):
        raise ValueError('E_SYNC_HUMAN_VIEW_NOT_BOUND:' + compiled['manifest']['case_id'])
    return digest
