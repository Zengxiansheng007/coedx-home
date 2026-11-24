"""Release rejection and recovery through the v2 formal publishing entry."""

from copy import deepcopy
import json
from pathlib import Path

import pytest

from scripts.ui_test_core import case_sync
from scripts.ui_test_core.case_sync import activate_prepared_sync_plan, apply_sync_plan, dry_run, prepare_sync_plan
from scripts.ui_test_core.human_view_handoff import bind_formal_human_view, raw_digest
from tests.test_formal_human_view import compile_authoring_case, render_tca


def compile_bound(path, title):
    compiled = compile_authoring_case(path, title=title)
    return bind_formal_human_view(compiled, render_tca(compiled['human_view_request']))


def test_invalid_handoffs_and_changed_archives_keep_the_released_view(tmp_path):
    path = tmp_path / 'case'
    initial = compile_bound(tmp_path / 'initial.json', '旧版通知')
    initial_plan = dry_run(initial, path)
    release = apply_sync_plan(initial_plan, lambda: initial, path)
    view = path / 'views/human.md'
    before = view.read_bytes()
    pointer = (path / 'active.json').read_bytes()
    offered = compile_bound(tmp_path / 'offered.json', '新版通知')
    with pytest.raises(ValueError, match='POINTER|REF'):
        compile_authoring_case(tmp_path / 'invalid.json', title_ref='test-data:/parameters/nonexistent')
    wrong = render_tca(offered['human_view_request'])
    wrong['identity']['build_fingerprint'] = 'sha256:' + '0' * 64
    with pytest.raises(ValueError, match='HUMAN_VIEW_IDENTITY'):
        bind_formal_human_view(offered, wrong)
    plan = dry_run(offered, path)
    missing = deepcopy(offered)
    del missing['outputs']['human.md']
    assert prepare_sync_plan(plan, lambda: missing, path)['status'] == 'plan_stale'
    changed = deepcopy(offered)
    changed['outputs']['human.md'] += 'SIMULATED extra text\n'
    changed['manifest']['human_view_sha256'] = raw_digest(changed['outputs']['human.md'])
    assert prepare_sync_plan(plan, lambda: changed, path)['status'] == 'plan_stale'

    installed = prepare_sync_plan(plan, lambda: offered, path)
    file = Path(installed['release_path']) / 'human.md'
    correct = file.read_bytes()
    file.write_bytes(correct.replace(b'\n', b'\r\n'))
    assert activate_prepared_sync_plan(plan, lambda: offered, path)['status'] == 'validation_failed'
    assert prepare_sync_plan(plan, lambda: offered, path)['status'] == 'validation_failed'
    assert view.read_bytes() == before and (path / 'active.json').read_bytes() == pointer

    file.write_bytes(correct)
    assert activate_prepared_sync_plan(plan, lambda: offered, path)['status'] == 'applied'
    assert activate_prepared_sync_plan(plan, lambda: offered, path)['no_op'] is True
    file.write_bytes(correct + b'extra')
    assert apply_sync_plan(dry_run(offered, path), lambda: offered, path)['status'] == 'validation_failed'
    assert (Path(release['release_path']) / 'human.md').read_bytes() == before


@pytest.mark.parametrize('pending_file', ['active.json', 'human.md'])
def test_interrupted_pointer_rolls_back_and_retries_from_the_same_entry(tmp_path, monkeypatch, pending_file):
    path = tmp_path / 'case'
    before = compile_bound(tmp_path / 'a.json', '原版通知')
    after = compile_bound(tmp_path / 'b.json', '新的通知')
    assert apply_sync_plan(dry_run(before, path), lambda: before, path)['status'] == 'applied'
    plan = dry_run(after, path)
    assert prepare_sync_plan(plan, lambda: after, path)['status'] == 'prepared'
    atomic_write = case_sync._atomic_bytes

    def interrupted(destination, document):
        if Path(destination).name == pending_file:
            raise KeyboardInterrupt('simulated abrupt process interruption')
        return atomic_write(destination, document)

    with monkeypatch.context() as patch:
        patch.setattr(case_sync, '_atomic_bytes', interrupted)
        with pytest.raises(KeyboardInterrupt):
            activate_prepared_sync_plan(plan, lambda: after, path)
    assert (path / 'views/human.md').read_bytes() == before['outputs']['human.md'].encode('utf-8')
    assert prepare_sync_plan(plan, lambda: after, path)['status'] == 'prepared'
    view = path / 'views/human.md'
    assert view.read_bytes() == before['outputs']['human.md'].encode('utf-8')
    assert activate_prepared_sync_plan(plan, lambda: after, path)['status'] == 'applied'
    assert view.read_bytes() == after['outputs']['human.md'].encode('utf-8')


def test_a_second_plan_cannot_replace_the_concurrent_winner(tmp_path):
    root = tmp_path / 'case'
    active = compile_bound(tmp_path / 'a.json', '起始通知')
    first = compile_bound(tmp_path / 'b.json', '第一稿')
    second = compile_bound(tmp_path / 'c.json', '第二稿')
    assert apply_sync_plan(dry_run(active, root), lambda: active, root)['status'] == 'applied'
    a = dry_run(first, root)
    b = dry_run(second, root)
    assert prepare_sync_plan(a, lambda: first, root)['status'] == 'prepared'
    assert apply_sync_plan(b, lambda: second, root)['status'] == 'applied'
    assert activate_prepared_sync_plan(a, lambda: first, root)['status'] == 'concurrent_update'
    pointer = json.loads((root / 'active.json').read_text(encoding='utf-8'))
    assert pointer['build_fingerprint'] == second['manifest']['build_fingerprint']
    assert (root / 'views/human.md').read_bytes() == second['outputs']['human.md'].encode('utf-8')
