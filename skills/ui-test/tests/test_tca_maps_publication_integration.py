"""The same isolated case passes authoring return, activation and product maps."""

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys

from scripts.ui_test_core.case_sync import apply_sync_plan, dry_run, prepare_sync_plan
from scripts.ui_test_core.human_view_handoff import bind_formal_human_view
from scripts.ui_test_core.product_aggregate import export_product_case_maps
from tests.test_formal_human_view import compile_authoring_case, render_tca
from tests.test_product_case_maps import read_links
from tests.test_product_case_maps_multi import release_sample
from tests.test_product_case_maps_refresh import ROUTES, DISPLAY


def _review_case(root):
    source = Path(__file__).resolve().parents[3] / 'skill-packages/test-case-authoring/scripts'
    sys.path.insert(0, str(source))
    try:
        return _run_native_review(root)
    finally:
        sys.path.pop(0)


def _run_native_review(root):
    from module_handoff import write_artifacts
    from qa_record import advance_record, read_record, start_record
    from test_incremental_review import review_sample
    from test_incremental_native_return import native_file
    from xmind_feedback import start_native_feedback

    result, _ = review_sample()
    batch = result['batch']
    batch['questions'] = []
    for case in batch['cases']:
        case['rule_status'] = 'formal'  # 此处独立夹具提供已经确认的规则。
    output = root / '合成 增量评审'
    output.mkdir()
    write_artifacts(result, output)
    record = root / '合成问答.md'
    start_record(record, 'isolated-153', batch, [])
    returned = root / '合成反馈.xmind'
    original = (output / 'xmind.md').read_text(encoding='utf-8')
    edit = original.replace('预期：显示本例默认结果 1', '预期：表单显示本次日常通知标题')
    assert edit != original
    native_file(returned, edit)
    feedback = start_native_feedback(record, returned, actual_reply='SIMULATED a clear layout review',
                                     companion_base=output, clear_changes=True)
    assert feedback['status'] == 'recorded'
    saved = read_record(record)
    if saved['feedback_pending']['affected_case_ids'] != ['SIM-1']:
        raise AssertionError('Unexpected native edit scope')
    state = advance_record(record, 'summarize')
    state = advance_record(record, 'apply_feedback', {
        'confirmed': True, 'actual_reply': 'SIMULATED summary agreed', 'summary_id': state['summary']['id'],
    })
    accepted = advance_record(record, 'review_feedback', {
        'approved': True, 'actual_reply': 'SIMULATED case reviewed',
        'case_ids': ['SIM-1'], 'content_version': state['batch']['content_version'],
    })['batch']
    original_peers = [case for case in batch['cases'] if case['id'] != 'SIM-1']
    current_peers = [case for case in accepted['cases'] if case['id'] != 'SIM-1']
    assert original_peers == current_peers
    return next(case for case in accepted['cases'] if case['id'] == 'SIM-1')


def _compile(root, case, *, branch='primary', revision=1, title='社区日常通知', file='data.json'):
    step = case['steps'][1]
    request = compile_authoring_case(
        root / file, case_id=case['id'], branch=branch, priority=case['priority'],
        revision=revision, title=title, operation=step['operation'], expected=step['expected'][0]['text'],
    )
    artifact = render_tca(request['human_view_request'])
    return bind_formal_human_view(request, artifact), artifact


def validate_integrated(root):
    root.mkdir(parents=True, exist_ok=True)
    selected = _review_case(root)
    incumbent = release_sample(root / '正式 生效样本', selected['id'], ['records'], title='原公告用例')
    legacy = release_sample(root / '正式 生效样本', 'DEMO-LEGACY', ['assets'], title='沿用旧例')
    output = root / '总用例 图稿'
    original = export_product_case_maps([incumbent, legacy], output, navigation=ROUTES, display_registry=DISPLAY)
    old_total = original['total'].read_bytes()
    old_view = (incumbent / 'views/human.md').read_bytes()
    old_map = next(path for path in original['modules'] if path.name.startswith('素材管理'))
    legacy_view = (legacy / 'views/human.md').read_bytes()

    revised, document = _compile(root, selected)
    rejected = deepcopy(revised)
    rejected['outputs']['human.md'] += '\n'
    plan = dry_run(revised, incumbent)
    assert prepare_sync_plan(plan, lambda: rejected, incumbent)['status'] == 'plan_stale'
    assert (incumbent / 'views/human.md').read_bytes() == old_view
    previous = export_product_case_maps([incumbent, legacy], output, navigation=ROUTES, display_registry=DISPLAY)
    assert previous['total'].read_bytes() == old_total
    published = apply_sync_plan(plan, lambda: revised, incumbent)
    assert published['status'] == 'applied'
    authored_bytes = document['markdown'].encode('utf-8')
    assert (Path(published['release_path']) / 'human.md').read_bytes() == authored_bytes
    assert (incumbent / 'views/human.md').read_bytes() == authored_bytes
    assert '表单显示本次日常通知标题；断言：A-TITLE equals 社区日常通知' in document['markdown']

    popup, popup_doc = _compile(root, selected, branch='popup', title='办事提醒', file='popup.json')
    popup_branch = incumbent.with_name('popup')
    assert apply_sync_plan(dry_run(popup, popup_branch), lambda: popup, popup_branch)['status'] == 'applied'
    assert 'A-TITLE equals 办事提醒' in popup_doc['markdown']
    updated, latest = _compile(root, selected, revision=2, title='办事大厅日常通知', file='updated.json')
    assert apply_sync_plan(dry_run(updated, incumbent), lambda: updated, incumbent)['status'] == 'applied'
    assert 'A-TITLE equals 办事大厅日常通知' in latest['markdown']
    assert (popup_branch / 'views/human.md').read_text(encoding='utf-8') == popup_doc['markdown']
    assert (Path(published['release_path']) / 'human.md').read_bytes() == authored_bytes

    maps = export_product_case_maps([incumbent, legacy], output, navigation=ROUTES, display_registry=DISPLAY)
    assert maps['reused_modules'] == [old_map]
    assert len(maps['generated_modules']) == 1
    assert (legacy / 'views/human.md').read_bytes() == legacy_view
    assert all(path.is_file() for path in read_links(maps['total'].read_text(encoding='utf-8')))
    current_map = maps['generated_modules'][0]
    text = current_map.read_text(encoding='utf-8')
    assert '表单显示本次日常通知标题' in text and '办事大厅日常通知' in text
    return {'total': str(maps['total']), 'module': str(current_map),
            'current_human': str(incumbent / 'views/human.md'), 'legacy_human': str(legacy / 'views/human.md'),
            'cases': maps['cases'], 'reused_module': str(old_map)}


def test_full_candidate_feedback_release_and_maps(tmp_path):
    validate_integrated(tmp_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--isolated-output', type=Path, required=True)
    args = parser.parse_args()
    args.isolated_output.mkdir(parents=True, exist_ok=False)
    print(json.dumps(validate_integrated(args.isolated_output), ensure_ascii=False))
