"""Several active scopes in one product, including two pages with the same name."""

import json
from pathlib import Path

import pytest

from scripts.ui_test_core.case_sync import apply_sync_plan, dry_run
from scripts.ui_test_core.compiler_v2 import compile_case_v2
from scripts.ui_test_core.product_aggregate import AggregateError, export_product_case_maps
from scripts.ui_test_core.test_data_contracts import load_test_data
from tests.fixtures_v2 import make_test_data_document, page_module_registry, source_case_v2
from tests.test_product_case_maps import read_links


def release_sample(root, case_id, modules, system=None, title=None):
    index = root / case_id
    index.mkdir(parents=True, exist_ok=True)
    source = source_case_v2()
    data = make_test_data_document()
    source.update(case_id=case_id, display_name=title or case_id)
    source['scope']['module_path'] = modules
    if system is not None:
        source['scope']['system'] = system
    data['case_id'] = case_id
    (index / 'data.json').write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
    compiled = compile_case_v2(
        source_case=source, test_data=load_test_data(index / 'data.json', case_id=case_id, branch_id='primary'),
        dependency_assets={ref: {'version': 1} for ref in source['dependency_refs']},
        config_fingerprint='sha256:' + '1' * 64,
        runtime_values={'SERVICE_HOST': {'value': 'sample.invalid', 'classification': 'ordinary', 'sensitive': False}},
        credential_keys={'shared-login'}, sequence_keys={'popup-version'}, page_module_registry=page_module_registry(),
    )
    branch = index / 'primary'
    installed = apply_sync_plan(dry_run(compiled, branch), lambda: compiled, branch)
    assert installed['status'] == 'applied'
    (branch / 'views').mkdir(exist_ok=True)
    (branch / 'views/human.md').write_bytes((Path(installed['release_path']) / 'human.md').read_bytes())
    return branch


def test_first_independent_page_keeps_full_route_and_distinct_same_names(tmp_path):
    root = ('demo', 'sample-product', 'sample-system')
    navigation = {
        root + ('settings',): 'menu',
        root + ('settings', 'messages'): 'redirect',
        root + ('settings', 'messages', 'records'): 'page',
        root + ('assets',): 'page',
        root + ('archive',): 'menu',
        root + ('archive', 'records'): 'page',
    }
    labels = {'modules': {'settings': '运营配置', 'messages': '消息管理', 'records': '公告管理',
                          'assets': '素材管理', 'archive': '归档管理', 'detail': '详情'}}
    cases = [
        release_sample(tmp_path, 'DEMO-A', ['settings', 'messages', 'records', 'detail']),
        release_sample(tmp_path, 'DEMO-B', ['assets']),
        release_sample(tmp_path, 'DEMO-C', ['archive', 'records']),
    ]
    output = tmp_path / 'maps'
    insufficient = dict(navigation)
    insufficient.pop(root + ('archive', 'records'))
    with pytest.raises(AggregateError, match='DEMO-C:.*/archive/records'):
        export_product_case_maps(cases, output, navigation=insufficient, display_registry=labels)
    assert not output.exists()
    result = export_product_case_maps(cases, output, navigation=navigation, display_registry=labels,
        dependency_details={'DEMO-B': [{'dependency_ref': 'flow.open-create', 'target_case_id': 'DEMO-A',
                                        'purpose': '读取可用对象', 'inputs': '公开示例对象编号',
                                        'outputs': '可选状态'}]})
    assert len(result['modules']) == 3 and len(set(result['modules'])) == 3
    assert len([path for path in result['modules'] if path.name.startswith('公告管理')]) == 2
    total = result['total'].read_text(encoding='utf-8')
    assert all(path.is_file() for path in read_links(total))
    assert '消息管理' in total and '素材管理' in total and '归档管理' in total
    detail = next(path.read_text(encoding='utf-8') for path in result['modules']
                  if '用例编号：DEMO-A' in path.read_text(encoding='utf-8'))
    assert '详情' in detail
    asset = next(path for path in result['modules'] if path.name.startswith('素材管理'))
    display = asset.read_text(encoding='utf-8')
    assert all(text in display for text in ('关联用例：DEMO-A', '读取可用对象', '公开示例对象编号', '可选状态'))
