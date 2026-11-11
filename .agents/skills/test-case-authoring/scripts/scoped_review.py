"""Read-only full-catalog selection; review copies never replace their source."""
import argparse
import copy
import json
from pathlib import Path
import sys

from authoring import _credential_guard, _digest, _cell


GROUPS = ('common_preconditions', 'special_preconditions', 'steps', 'special_postconditions')


TECHNICAL_FIELDS = frozenset(('id', 'source', 'lines', 'basis', 'provenance',
    'semantic_version', 'data_version', 'assertion_id', 'assertion_ids', 'operator',
    'build_fingerprint', 'sha256', 'content_hash', 'technical_handoff'))  # Keep constraints in the candidate, outside business projections.
BUSINESS_LABELS = {
    'context': '业务条件', 'role': '角色', 'initial_state': '初始状态',
    'priority': '优先级', 'priority_basis': '分级依据', 'maintenance_action': '维护建议',
    'rule_status': '规则确认', 'review_status': '最终评审', 'merge_status': '合并状态',
    'execution_status': '执行状态', 'dependencies': '关联用例', 'case_id': '用例编号',
    'module_path': '模块路径', 'purpose': '用途', 'required_state': '所需状态',
    'object_binding': '业务对象关联', 'object_ref': '业务对象', 'data_ref': '数据引用',
    'input': '输入', 'inputs': '输入', 'output': '产出', 'outputs': '产出',
    'value': '值', 'credential_ref': '凭据引用', 'validity': '有效性',
    'reuse_policy': '复用策略', 'invalidation_action': '失效处理',
    'rule_decisions': '初始规则决定（历史）', 'active_rule_decisions': '当前有效规则决定',
    'rule_decision_history': '规则决定历史', 'feedback_rule_history': '反馈规则历史',
    'reply': '答复', 'decision': '决定',
    'actual_reply': '实际答复', 'product_check': '待产品核实',
}


def _business_lines(value, prefix=''):
    """One labelled business projection used by both review formats.

    Unknown extensions are flattened to labelled leaves, never opaque JSON.
    Technical provenance stays in candidate/baseline records instead of prose.
    """
    if isinstance(value, dict):
        lines = []
        for key, child in value.items():
            if key in TECHNICAL_FIELDS:
                continue
            label = '' if key == 'text' else BUSINESS_LABELS.get(key, key.replace('_', ' '))
            heading = ' / '.join(p for p in (prefix, label) if p)
            if key == 'module_path' and isinstance(child, list):
                lines.append(heading + '：' + ' / '.join(map(str, child)))
            else:
                lines.extend(_business_lines(child, heading))
        return lines
    if isinstance(value, list):
        return [line for child in value for line in _business_lines(child, prefix)]
    text = str(value) if value is not None else '待核对'
    return [prefix + '：' + text if prefix else text]


def _render(batch):
    tree = ['# 本轮范围副本（非全量）', '- 版本：' + batch['content_version'],
            '- 未展示不表示删除；关联展示不扩大功能验证范围']
    human = []
    data = {d['id']: d for d in batch['data']}
    selection = {s['case_id']: s for s in batch['selection']}
    for case in batch['cases']:
        indent = ''
        for part in case['module_path']:
            tree.append(indent + '- ' + _cell(part))
            indent += '  '
        tree.append(indent + '- ' + _cell(case['id'] + ' ' + case.get('title', '待核对')))
        indent += '  '
        human.extend(['# ' + _cell(case['id'] + ' ' + case.get('title', '待核对')),
                      '版本：' + batch['content_version'], '模块：' + ' / '.join(map(_cell, case['module_path']))])
        note = selection[case['id']]
        for key, value in [('入选用途', note['action'] + '：' + note['reason']),
                           ('本轮功能验证', '已单独列入批准范围' if case['id'] in batch['approved_validation_scope'] else '未列入批准范围')]:
            tree.append(indent + '- ' + key + '：' + _cell(value))
            human.append(key + '：' + _cell(value))
        metadata = {key: value for key, value in case.items()
                    if key not in (*GROUPS, 'id', 'title', 'module_path')}
        for line in _business_lines(metadata):
            tree.append(indent + '- ' + _cell(line))
            human.append(_cell(line))
        for group, label in zip(GROUPS, ('公共前置操作', '特殊前置操作', '测试步骤', '特殊后置操作')):
            if group.startswith('special_') and not case.get(group):
                continue
            tree.append(indent + '- ' + label)
            human.extend([label, '| 序号 | 操作 | 参数/数据 | 预期结果 |', '| --- | --- | --- | --- |'])
            if not case.get(group):
                tree.append(indent + '  - 未提供，待核对')
                human.append('未提供，待核对')
            for i, step in enumerate(case.get(group, []), 1):
                values = [line for ref in step.get('data_refs', [])
                          for line in _business_lines(data[ref])] or ['无']
                extensions = {k: v for k, v in step.items()
                              if k not in ('id', 'operation', 'data_refs', 'expected', 'verification')}
                business_conditions = _business_lines(extensions)
                if business_conditions and values == ['无']:
                    values = []
                values.extend(business_conditions)
                expected = _business_lines(step.get('expected', [])) or ['待核对']
                checks = _business_lines(step.get('verification', [])) or ['待核对']
                operation = step.get('operation', '待核对')
                tree.extend([indent + f'  - 步骤 {i}：' + _cell(operation), indent + '    - 参数/数据'])
                tree.extend(indent + '      - ' + _cell(v) for v in values)
                tree.append(indent + '    - 预期')
                tree.extend(indent + '      - ' + _cell(v) for v in expected)
                tree.append(indent + '      - 验证点：' + _cell('；'.join(checks)))
                human.append(f'| {i} | {_cell(operation)} | {_cell("；".join(values))} | 预期：{_cell("；".join(expected))}；验证点：{_cell("；".join(checks))} |')
        for question in batch['questions']:
            if question['case_id'] == case['id']:
                tree.append(indent + '- 待核对：' + _cell(question['field']))
                human.append('待核对：' + _cell(question['field']))
    return {'batch': copy.deepcopy(batch), 'human_view': '\n'.join(human) + '\n',
            'xmind_markdown': '\n'.join(tree) + '\n'}


def render_review_batch(batch):
    """Re-render a scoped candidate after clarification without losing groups."""
    _credential_guard(batch)
    return _render(batch)


def _differences(before, after, path=''):
    if isinstance(before, dict) and isinstance(after, dict):
        for key in sorted(before.keys() | after.keys()):
            child = path + '/' + key.replace('~', '~0').replace('/', '~1')
            if key not in before or key not in after:
                yield {'field': child, 'before': before.get(key), 'after': after.get(key),
                       'before_present': key in before, 'after_present': key in after}
            else:
                yield from _differences(before[key], after[key], child)
    elif isinstance(before, list) and isinstance(after, list):
        for index in range(max(len(before), len(after))):
            child = path + '/' + str(index)
            if index >= len(before) or index >= len(after):
                yield {'field': child, 'before': before[index] if index < len(before) else None,
                       'after': after[index] if index < len(after) else None,
                       'before_present': index < len(before), 'after_present': index < len(after)}
            else:
                yield from _differences(before[index], after[index], child)
    elif before != after:
        yield {'field': path, 'before': before, 'after': after,
               'before_present': True, 'after_present': True}


def _references(case):
    return {ref for group in GROUPS for step in case.get(group, [])
            for ref in step.get('data_refs', [])}


def build_scoped_review(catalog, batch_id, selection, approved_validation_scope=None,
                        candidates=None, candidate_data=None):
    """Select complete catalog records without granting change or execution approval."""
    _credential_guard([catalog, selection, candidates, candidate_data])
    if catalog.get('kind') != 'authoring_full_catalog' or catalog.get('schema_version') != 1:
        raise ValueError('Expected authoring_full_catalog v1, not a candidate or formal asset')
    if not catalog.get('source_ref') or not catalog.get('content_version') or not batch_id:
        raise ValueError('Catalog identity and version required')
    full = copy.deepcopy(catalog)
    indexed = {c['id']: c for c in full['cases']}
    if len(indexed) != len(full['cases']):
        raise ValueError('Duplicate case identity')
    for case in full['cases'] + list(candidates or []):
        if not isinstance(case['id'], str) or not case['id'].strip() or not isinstance(case.get('module_path'), list) or len(case['module_path']) < 5 or not all(isinstance(p, str) and p.strip() for p in case['module_path']):
            raise ValueError('Case identity and complete module path required')
    proposed = {c['id']: copy.deepcopy(c) for c in (candidates or [])}
    if len(proposed) != len(candidates or []):
        raise ValueError('Duplicate candidate identity')
    selected, selected_ids, originals = [], set(), []
    for item in selection:
        case_id = item['case_id']
        action = item['action']
        if case_id in selected_ids or action not in ('add', 'modify', 'reuse', 'deactivate', 'related') or not item.get('reason'):
            raise ValueError('Invalid selection')
        if action == 'add':
            if case_id in indexed or case_id not in proposed:
                raise ValueError('Add requires a new complete candidate')
        elif case_id not in indexed:
            raise ValueError('Selected case absent from catalog')
        else:
            originals.append(copy.deepcopy(indexed[case_id]))
        if action == 'modify':
            if case_id not in proposed or not item.get('basis') or not item.get('coverage_impact'):
                raise ValueError('Modification requires complete candidate, basis and coverage impact')
        if action not in ('add', 'modify') and case_id in proposed:
            raise ValueError('Unchanged selection cannot supply replacement content')
        selected.append(copy.deepcopy(proposed[case_id] if action in ('add', 'modify') else indexed[case_id]))
        selected_ids.add(case_id)
    if proposed.keys() - selected_ids:
        raise ValueError('Unselected candidates')
    if not selected:
        raise ValueError('Select at least one case')
    scope = list(approved_validation_scope or [])
    if len(set(scope)) != len(scope) or any(cid not in selected_ids for cid in scope):
        raise ValueError('Validation scope must identify selected cases')
    original_data = {d['id']: d for d in full['data']}
    if len(original_data) != len(full['data']):
        raise ValueError('Duplicate data identity')
    revised_data = dict(original_data)
    updates = candidate_data or []
    if len({d['id'] for d in updates}) != len(updates):
        raise ValueError('Duplicate candidate data identity')
    revised_data.update({d['id']: copy.deepcopy(d) for d in updates})
    data_refs = set().union(*[_references(c) for c in selected])
    baseline_refs = set().union(*[_references(c) for c in originals]) if originals else set()
    if baseline_refs - original_data.keys():
        raise ValueError('Catalog has unresolved data reference')
    data = [d for key, d in revised_data.items() if key in data_refs]
    if data_refs - {d['id'] for d in data}:
        raise ValueError('Unresolved data reference')
    baseline = {'catalog_version': full['content_version'], 'catalog_digest': _digest(full),
                'source_ref': full['source_ref'], 'cases': copy.deepcopy(selected),
                'data': copy.deepcopy(data), 'selection': copy.deepcopy(selection),
                'catalog_cases': originals,
                'catalog_data': [copy.deepcopy(d) for key, d in original_data.items() if key in baseline_refs],
                'not_displayed_case_ids': [c['id'] for c in full['cases'] if c['id'] not in selected_ids]}
    baseline['copy_version'] = _digest({'cases': selected, 'data': data, 'selection': selection})
    changes = []
    for item, case in zip(selection, selected):
        if item['action'] == 'add':
            continue
        prior = indexed[case['id']]
        diffs = list(_differences(prior, case))
        for ref in sorted(_references(prior) | _references(case)):
            diffs.extend(_differences(original_data.get(ref, {}), revised_data.get(ref, {}), '/data/' + ref))
        if diffs and item['action'] != 'modify':
            raise ValueError('Shared data change affects an unchanged selection; review explicitly')
        for diff in diffs:
            changes.append(dict(diff, case_id=case['id'], module_path=case['module_path'],
                                reason=item['reason'], basis=item['basis'], coverage_impact=item['coverage_impact']))
    questions = []
    for case in selected:
        required = ('title', 'priority', 'priority_basis', 'context', 'steps', 'common_preconditions',
                    'rule_status', 'review_status', 'merge_status', 'execution_status', 'semantic_version', 'data_version')
        for key in required:
            if key not in case or case[key] is None or case[key] == '':
                questions.append({'case_id': case['id'], 'field': key, 'reason': '源记录缺失，待核对'})
        for key in ('role', 'initial_state'):
            if not case.get('context', {}).get(key):
                questions.append({'case_id': case['id'], 'field': 'context/' + key, 'reason': '源记录缺失，待核对'})
        for group in GROUPS:
            for i, step in enumerate(case.get(group, [])):
                for key in ('operation', 'data_refs', 'expected', 'verification'):
                    if key not in step or (key != 'data_refs' and not step[key]):
                        questions.append({'case_id': case['id'], 'field': f'{group}/{i}/{key}', 'reason': '源记录缺失，待核对'})
    batch = {'schema_version': 1, 'id': batch_id, 'stage': 'P1/P2', 'kind': 'scoped_review_copy',
             'sources': [{'kind': 'existing_catalog', 'ref': full['source_ref'], 'sha256': _digest(full)}],
             'initial_copy_baseline': baseline, 'selection': copy.deepcopy(selection),
             'approved_validation_scope': scope, 'cases': selected, 'data': data, 'questions': questions}
    batch['data_version'] = _digest(data)
    batch['content_version'] = _digest(batch)
    result = _render(batch)
    result['changes'] = changes
    result['review_notes'] = '\n'.join(['# 本轮范围副本说明',
        '仅用于评审；未展示不表示删除；关联展示不授予修改或功能执行批准。',
        '正式 ui-test 读取和同步待适配；此目录不是正式 Source Case。',
        '功能验证范围：' + ', '.join(scope),
        *[f"- {s['case_id']}：{s['action']}；{s['reason']}" for s in selection],
        '## 实际字段变化',
        *[json.dumps(d, ensure_ascii=False) for d in changes]]) + '\n'
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog', required=True)
    parser.add_argument('--request', required=True)
    parser.add_argument('--output-dir', required=True)
    args = parser.parse_args()
    try:
        catalog = json.loads(Path(args.catalog).read_text(encoding='utf-8-sig'))
        request = json.loads(Path(args.request).read_text(encoding='utf-8-sig'))
        result = build_scoped_review(catalog, **request)
        output = Path(args.output_dir)
        output.mkdir(parents=True, exist_ok=False)
        for filename, content in [('candidate.json', result['batch']),
                                  ('initial-copy-baseline.json', result['batch']['initial_copy_baseline']),
                                  ('changes.json', result['changes'])]:
            (output / filename).write_text(json.dumps(content, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        for filename, key in [('human-view.md', 'human_view'), ('xmind.md', 'xmind_markdown'),
                              ('review-notes.md', 'review_notes')]:
            (output / filename).write_text(result[key], encoding='utf-8')
    except (ValueError, KeyError, TypeError, AttributeError, OSError):
        print('Scope copy rejected: check catalog, explicit selection, data and new output directory.', file=sys.stderr)
        return 1
    print('Review copy written; full catalog unchanged, no feedback applied or merge performed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
