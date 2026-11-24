"""Formal Human Views use each branch's selected data revision."""

from pathlib import Path

from scripts.ui_test_core.case_sync import apply_sync_plan, dry_run
from scripts.ui_test_core.human_view_handoff import bind_formal_human_view
from scripts.ui_test_core.release_verifier import verify_release
from tests.test_formal_human_view import compile_authoring_case, render_tca


def publish(root, path, branch, title, revision):
    request = compile_authoring_case(path, branch=branch, title=title, revision=revision)
    handoff = render_tca(request['human_view_request'])
    compiled = bind_formal_human_view(request, handoff)
    result = apply_sync_plan(dry_run(compiled, root), lambda: compiled, root)
    assert result['status'] == 'applied'
    return compiled, Path(result['release_path']), handoff['markdown']


def test_branches_use_independent_values_and_retain_archived_revisions(tmp_path):
    sys_root = tmp_path / '系统'
    popup_root = tmp_path / '弹窗'
    sys_data = tmp_path / 'system-data.json'
    popup_data = tmp_path / 'popup-data.json'
    sys_build, sys_archive, sys_doc = publish(sys_root, sys_data, 'system-announcement', '社区办事通知', 1)
    popup_build, popup_archive, popup_doc = publish(popup_root, popup_data, 'popup-announcement', '预约提醒', 1)
    assert '标题规则：社区办事通知' in sys_doc and 'A-TITLE equals 社区办事通知' in sys_doc
    assert '标题规则：预约提醒' in popup_doc and 'A-TITLE equals 预约提醒' in popup_doc
    assert '预约提醒' not in sys_doc and '社区办事通知' not in popup_doc
    assert '时间后缀位数：3' in popup_doc
    assert 'sequence:popup-version' in popup_doc and 'credential:shared-login' in popup_doc
    assert 'private-sample.invalid' not in popup_doc
    bound_before = (popup_root / 'views/human.md').read_bytes()

    new_build, new_archive, new_doc = publish(sys_root, sys_data, 'system-announcement', '大厅办事通知', 2)
    assert new_build['identity']['source_hash'] == sys_build['identity']['source_hash']
    assert new_build['identity']['test_data_hash'] != sys_build['identity']['test_data_hash']
    assert new_build['manifest']['build_fingerprint'] != sys_build['manifest']['build_fingerprint']
    assert '标题规则：大厅办事通知' in new_doc and 'A-TITLE equals 大厅办事通知' in new_doc
    assert (sys_root / 'views/human.md').read_bytes() == (new_archive / 'human.md').read_bytes()
    assert (sys_archive / 'human.md').read_bytes() == sys_doc.encode('utf-8')
    assert verify_release(sys_archive, current_identity=sys_build['identity'])['input_sync'] == 'in_sync'
    assert (popup_root / 'views/human.md').read_bytes() == bound_before
    assert verify_release(popup_archive, current_identity=popup_build['identity'])['input_sync'] == 'in_sync'
