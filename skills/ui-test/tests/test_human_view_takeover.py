"""Only the selected legacy case crosses over to the authored view."""

from pathlib import Path

import pytest

from scripts.ui_test_core.case_sync import activate_prepared_sync_plan, dry_run, prepare_sync_plan
from scripts.ui_test_core.human_view_handoff import bind_formal_human_view
from scripts.ui_test_core.product_aggregate import export_product_case_maps
from scripts.ui_test_core.release_verifier import verify_release
from tests.test_formal_human_view import compile_authoring_case, render_tca
from tests.test_product_case_maps import DISPLAY, NAVIGATION, read_links, released_case
from tests.test_product_case_maps_multi import release_sample


def test_old_case_stays_readable_until_new_version_activates(tmp_path):
    legacy, root, view = released_case(tmp_path)
    sibling = release_sample(tmp_path, 'DEMO-LEGACY-B', ['records'])
    sibling_view = sibling / 'views/human.md'
    initial_view = view.read_bytes()
    initial_sibling = sibling_view.read_bytes()
    initial_fingerprint = legacy['manifest']['build_fingerprint'].removeprefix('sha256:')
    initial_archive = root / 'releases' / initial_fingerprint

    request = compile_authoring_case(tmp_path / 'edited.json', priority='P1',
                                     operation='填写新的通知标题')
    current = bind_formal_human_view(request, render_tca(request['human_view_request']))
    plan = dry_run(current, root)
    staged = prepare_sync_plan(plan, lambda: current, root)
    assert staged['status'] == 'prepared'
    assert view.read_bytes() == initial_view
    assert activate_prepared_sync_plan(plan, lambda: current, root)['status'] == 'applied'
    assert '填写新的通知标题' in view.read_text(encoding='utf-8')
    assert (initial_archive / 'human.md').read_bytes() == initial_view
    assert verify_release(initial_archive, current_identity=legacy['identity'])['release_integrity'] == 'valid'
    assert sibling_view.read_bytes() == initial_sibling

    maps = export_product_case_maps([root, sibling], tmp_path / '目录', navigation=NAVIGATION, display_registry=DISPLAY)
    assert set(read_links(maps['total'].read_text(encoding='utf-8'))) == {maps['modules'][0], view, sibling_view}
    assert '填写新的通知标题' in maps['modules'][0].read_text(encoding='utf-8')
    assert (Path(staged['release_path']) / 'human.md').read_bytes() == view.read_bytes()

    with pytest.raises(RuntimeError, match='HUMAN_VIEW_TAKEOVER_REQUIRED'):
        dry_run(legacy, root)
    assert sibling_view.read_bytes() == initial_sibling
