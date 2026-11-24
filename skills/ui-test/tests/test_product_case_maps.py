"""Isolated active releases consumed through the product map entry."""

from pathlib import Path
import re
from urllib.parse import urlsplit
from urllib.request import url2pathname

import pytest

from scripts.ui_test_core.case_sync import apply_sync_plan, dry_run
from tests.fixtures_v2 import compiled_v2


NAVIGATION = {('demo', 'sample-product', 'sample-system', 'records'): 'page'}
DISPLAY = {
    'project_groups': {'demo': '示例项目组'},
    'systems': {'sample-system': '示例系统'},
    'modules': {'records': '记录管理'},
    'functions': {'create': '创建'},
}


def released_case(tmp_path):
    compiled, _ = compiled_v2(tmp_path / 'test-data.json')
    branch = tmp_path / '记录 产品' / 'primary'
    result = apply_sync_plan(dry_run(compiled, branch), lambda: compiled, branch)
    assert result['status'] == 'applied'
    human = branch / 'views' / 'human.md'
    human.parent.mkdir()
    human.write_bytes((Path(result['release_path']) / 'human.md').read_bytes())
    return compiled, branch, human


def read_links(markdown):
    return [Path(url2pathname(urlsplit(uri).path))
            for uri in re.findall(r'\]\((file://[^)]+)\)', markdown)]


def test_maps_reference_one_active_build_and_reconstruct_its_steps(tmp_path):
    from scripts.ui_test_core.product_aggregate import export_product_case_maps

    compiled, branch, human = released_case(tmp_path)
    published = export_product_case_maps([branch], tmp_path / '图稿 包', navigation=NAVIGATION, display_registry=DISPLAY)
    total = published['total'].read_text(encoding='utf-8')
    assert total.count('打开记录管理完整用例图') == 1
    assert '用例 ID DEMO-CASE-A' in total
    module, current = read_links(total)
    assert module.is_file() and current == human
    detail = module.read_text(encoding='utf-8')
    assert '查看完整步骤与预期' not in detail
    assert len(re.findall(r'^ +\- 操作 \d+：', detail, re.M)) == 5
    assert '预期：受众正确' in detail
    assert 'credential:shared-login' in detail
    assert published['cases'][0]['build_fingerprint'] == compiled['manifest']['build_fingerprint']


def test_view_drift_and_missing_route_keep_output_unpublished(tmp_path):
    from scripts.ui_test_core.product_aggregate import AggregateError, export_product_case_maps

    _, branch, human = released_case(tmp_path)
    target = tmp_path / 'maps'
    with pytest.raises(AggregateError, match='DEMO-CASE-A'):
        export_product_case_maps([branch], target, navigation={}, display_registry=DISPLAY)
    assert not target.exists()
    human.write_text('version drift', encoding='utf-8')
    with pytest.raises(AggregateError, match='DEMO-CASE-A'):
        export_product_case_maps([branch], target, navigation=NAVIGATION, display_registry=DISPLAY)
    assert not target.exists()
