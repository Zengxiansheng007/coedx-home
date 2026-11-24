"""Formal publication with the real TCA writing entry and an isolated branch."""

from hashlib import sha256
import json
from pathlib import Path
import sys

import pytest

from scripts.ui_test_core.case_sync import activate_prepared_sync_plan, dry_run, prepare_sync_plan
from scripts.ui_test_core.compiler_v2 import compile_case_v2
from scripts.ui_test_core.test_data_contracts import load_test_data
from tests.fixtures_v2 import make_test_data_document, page_module_registry, source_case_v2


def compile_authoring_case(path, *, branch='primary', title='普通通知', priority='P0', revision=1,
                           case_id='DEMO-CASE-A', operation=None, title_ref=None, expected=None):
    spec = source_case_v2()
    data = make_test_data_document()
    spec.update(branch_id=branch, priority=priority, case_id=case_id)
    if operation is not None:
        spec['steps'][1]['intent'] = operation
        spec['case_version'] += 1
    if title_ref is not None:
        spec['parameter_bindings'][0]['ref'] = title_ref
    if expected is not None:
        spec['steps'][1]['expected_result'] = expected
    registry = page_module_registry()
    for module in registry['modules'].values():
        module['branch_modes'][branch] = module['branch_modes']['primary']
    data.update(branch_id=branch, case_id=case_id, data_revision=revision)
    data['parameters']['title_template'] = title
    path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
    return compile_case_v2(
        source_case=spec, test_data=load_test_data(path, case_id=spec['case_id'], branch_id=branch),
        dependency_assets={name: {'version': 1} for name in spec['dependency_refs']},
        config_fingerprint='sha256:' + '1' * 64,
        runtime_values={'SERVICE_HOST': {'value': 'private-sample.invalid', 'classification': 'ordinary', 'sensitive': False}},
        credential_keys={'shared-login'}, sequence_keys={'popup-version'}, page_module_registry=registry,
        renderer_version='tca-human-view-v1',
    )


def render_tca(request):
    directory = Path(__file__).resolve().parents[3] / 'skill-packages/test-case-authoring/scripts'
    sys.path.insert(0, str(directory))
    try:
        from formal_human_view import render_formal_human_view
        return render_formal_human_view(request)
    finally:
        sys.path.pop(0)


def test_tca_artifact_is_archived_and_activated_byte_for_byte(tmp_path):
    from scripts.ui_test_core.human_view_handoff import bind_formal_human_view

    prepared = compile_authoring_case(tmp_path / 'data.json')
    scope = tmp_path / 'active-branch'
    assert 'human.md' not in prepared['outputs']
    with pytest.raises(RuntimeError, match='HUMAN_VIEW'):
        dry_run(prepared, scope)
    artifact = render_tca(prepared['human_view_request'])
    assert artifact == render_tca(prepared['human_view_request'])
    value = artifact['markdown']
    assert '| 序号 | 操作 | 参数/数据 | 预期结果 |' in value
    assert '标题正确；断言：A-TITLE equals 普通通知 |' in value
    assert 'value:SERVICE_HOST' in value and 'private-sample.invalid' not in value
    assert 'credential:shared-login' in value
    compiled = bind_formal_human_view(prepared, artifact)
    plan = dry_run(compiled, scope)
    expected = 'sha256:' + sha256(value.encode('utf-8')).hexdigest()
    assert plan['human_view_sha256'] == expected
    receipt = prepare_sync_plan(plan, lambda: compiled, scope)
    assert receipt['status'] == 'prepared'
    archive = Path(receipt['release_path']) / 'human.md'
    assert archive.read_bytes() == value.encode('utf-8')
    assert not (scope / 'active.json').exists()
    activated = activate_prepared_sync_plan(plan, lambda: compiled, scope)
    assert activated['status'] == 'applied'
    assert (scope / 'views/human.md').read_bytes() == archive.read_bytes()
    assert (scope / 'active.json').is_file()


def test_other_branch_artifact_does_not_replace_active_build(tmp_path):
    from scripts.ui_test_core.human_view_handoff import bind_formal_human_view

    source = compile_authoring_case(tmp_path / 'main.json')
    different = compile_authoring_case(tmp_path / 'other.json', branch='secondary')
    target = tmp_path / 'primary'
    compiled = bind_formal_human_view(source, render_tca(source['human_view_request']))
    plan = dry_run(compiled, target)
    assert prepare_sync_plan(plan, lambda: compiled, target)['status'] == 'prepared'
    assert activate_prepared_sync_plan(plan, lambda: compiled, target)['status'] == 'applied'
    active = (target / 'active.json').read_bytes()
    with pytest.raises(ValueError, match='HUMAN_VIEW_IDENTITY'):
        bind_formal_human_view(source, render_tca(different['human_view_request']))
    assert (target / 'active.json').read_bytes() == active
