"""Selective generation and last complete directory preservation."""

import json
from hashlib import sha256
from pathlib import Path

import pytest

from scripts.ui_test_core import product_case_maps
from scripts.ui_test_core.product_aggregate import AggregateError, export_product_case_maps
from tests.test_product_case_maps_multi import release_sample
from tests.test_product_case_maps import read_links


ROOT = ('demo', 'sample-product', 'sample-system')
ROUTES = {ROOT + (key,): 'page' for key in ('records', 'assets')}
DISPLAY = {'modules': {'records': '公告管理', 'assets': '素材管理'}}


def export(branches, output):
    return export_product_case_maps(branches, output, navigation=ROUTES, display_registry=DISPLAY)


def test_xmind_exports_keep_machine_index_out_of_markdown(tmp_path):
    branch = release_sample(tmp_path, 'DEMO-A', ['records'], title='公告用例')
    published = export([branch], tmp_path / '总图')
    assert published['total'].read_text(encoding='utf-8').splitlines()[0] == '# demo总用例'
    for markdown in [published['total'], *published['modules']]:
        assert '<!--' not in markdown.read_text(encoding='utf-8')  # Windows XMind maps the comment into a topic.
    assert export([branch], tmp_path / '总图')['reused_modules'] == published['modules']


def test_refresh_migrates_inline_index_without_rewriting_modules(tmp_path):
    branch = release_sample(tmp_path, 'DEMO-A', ['records'], title='公告用例')
    output = tmp_path / '总图'
    published = export([branch], output)
    path = published['total']
    clean = path.read_bytes()
    sidecar = next((output / '.case-map-index').glob('*.json'))
    index = json.loads(sidecar.read_bytes())
    legacy = {key: index[key] for key in ('cases', 'modules')}
    path.write_bytes(clean + ('<!-- ui-test-case-maps: ' + json.dumps(legacy) + ' -->\n').encode('utf-8'))
    sidecar.unlink()  # 此隔离目录模拟升级前只有旧内嵌索引。
    module = published['modules'][0]
    modified_at = module.stat().st_mtime_ns

    current = export([branch], output)

    assert path.read_bytes() == clean
    assert current['reused_modules'] == [module] and module.stat().st_mtime_ns == modified_at
    assert current['generated_modules'] == []
    assert all(link.is_file() for link in read_links(clean.decode('utf-8')))
    assert json.loads(sidecar.read_bytes())['total_sha256'] == sha256(clean).hexdigest()


def test_mismatched_current_sidecar_leaves_active_total_intact(tmp_path):
    branch = release_sample(tmp_path, 'DEMO-A', ['records'], title='公告用例')
    output = tmp_path / '总图'
    published = export([branch], output)
    clean = published['total'].read_bytes()
    sidecar = next((output / '.case-map-index').glob('*.json'))
    index = json.loads(sidecar.read_bytes())
    index['total_sha256'] = '0' * 64
    sidecar.write_text(json.dumps(index), encoding='utf-8')

    with pytest.raises(AggregateError, match='E_MAP_CURRENT_INDEX_INVALID'):
        export([branch], output)

    assert published['total'].read_bytes() == clean
    assert all(link.is_file() for link in read_links(clean.decode('utf-8')))


def test_refresh_reuses_unaffected_module_and_publishes_only_complete_total(tmp_path, monkeypatch):
    a = release_sample(tmp_path, 'DEMO-A', ['records'], title='旧公告版本')
    b = release_sample(tmp_path, 'DEMO-B', ['assets'], title='既有素材')
    output = tmp_path / 'maps'
    before = export([a, b], output)
    total = before['total'].read_bytes()
    former_index = output / '.case-map-index' / (sha256(total).hexdigest() + '.json')
    former_index_bytes = former_index.read_bytes()
    saved_paths = read_links(total.decode('utf-8'))
    asset = next(path for path in before['modules'] if path.name.startswith('素材管理'))
    before_asset = asset.stat().st_mtime_ns
    current_a = release_sample(tmp_path, 'DEMO-A', ['records'], title='新公告版本')
    assert current_a == a
    original_replace = product_case_maps.os.replace

    def interrupted(source, target):
        if Path(target) == before['total']:
            raise OSError('simulated failure before the directory swap')
        return original_replace(source, target)

    with monkeypatch.context() as patch:
        patch.setattr(product_case_maps.os, 'replace', interrupted)
        with pytest.raises(AggregateError, match='DEMO-A'):
            export([a, b], output)
    assert before['total'].read_bytes() == total
    assert former_index.read_bytes() == former_index_bytes  # 失败后的读回仍指向旧总图和旧索引。
    assert all(path.is_file() for path in saved_paths)
    after = export([a, b], output)
    assert after['reused_modules'] == [asset]
    assert asset.stat().st_mtime_ns == before_asset
    assert '新公告版本' in after['total'].read_text(encoding='utf-8')
    assert former_index.read_bytes() == former_index_bytes
    assert len(after['generated_modules']) + len(after['reused_modules']) == 2
    assert all(path.is_file() for path in read_links(after['total'].read_text(encoding='utf-8')))


def test_broken_active_detail_reports_build_difference_and_retries(tmp_path):
    a = release_sample(tmp_path, 'DEMO-A', ['records'], title='旧公告版本')
    output = tmp_path / 'maps'
    original = export([a], output)
    total = original['total'].read_bytes()
    release_sample(tmp_path, 'DEMO-A', ['records'], title='新公告版本')
    pointer = json.loads((a / 'active.json').read_text(encoding='utf-8'))
    stable_view = a / 'views/human.md'
    correct = stable_view.read_bytes()
    stable_view.write_text('simulated wrong working view', encoding='utf-8')
    with pytest.raises(AggregateError, match='E_MAP_ACTIVE_VERSION_DIFF:DEMO-A:'):
        export([a], output)
    assert original['total'].read_bytes() == total
    assert pointer['build_fingerprint'] != original['cases'][0]['build_fingerprint']
    stable_view.write_bytes(correct)
    assert export([a], output)['cases'][0]['build_fingerprint'] == pointer['build_fingerprint']


def test_move_and_retirement_keep_the_original_module_available(tmp_path):
    a = release_sample(tmp_path, 'DEMO-A', ['records'], title='迁移用例')
    b = release_sample(tmp_path, 'DEMO-B', ['assets'], title='停用用例')
    output = tmp_path / 'maps'
    previous = export([a, b], output)
    archives = {module: module.read_bytes() for module in previous['modules']}
    release_sample(tmp_path, 'DEMO-A', ['assets'], title='迁移用例')
    next_version = export([a], output)  # 隔离生效集合已经不再包含 DEMO-B。
    assert len(next_version['modules']) == 1
    total = next_version['total'].read_text(encoding='utf-8')
    assert '公告管理' not in total and '停用用例' not in total
    assert next_version['cases'][0]['case_id'] == 'DEMO-A'
    assert all(path.read_bytes() == body for path, body in archives.items())
