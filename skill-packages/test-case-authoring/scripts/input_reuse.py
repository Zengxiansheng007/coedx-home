"""Project a source-assessed P0 invocation and exact JSON changes for a human reader."""
import copy
import json

from authoring import _cell, _credential_guard, _digest
from invocation_input import input_label, json_input
from step_reuse import resolve_step


def changes_between(before, after, path=()):
    """Object keys can be added/deleted; arrays are replaced atomically in their original order."""
    if isinstance(before, dict) and isinstance(after, dict):
        for key in before:
            child = (*path, key)
            if key in after:
                yield from changes_between(before[key], after[key], child)
            else:
                yield dict(op='remove', path=list(child), before=before[key])
        for key in after:
            if key not in before:
                yield dict(op='add', path=[*path, key], after=after[key])
    elif json.dumps(before, ensure_ascii=False, sort_keys=True, allow_nan=False) != json.dumps(
            after, ensure_ascii=False, sort_keys=True, allow_nan=False):
        yield dict(op='replace', path=list(path), before=before, after=after)


def _retained(row, before, after):
    """Show explicitly assessed, unchanged keys that matter to this test point."""
    retained = []
    paths = row.get('focus_paths', [])
    if not isinstance(paths, list):
        raise ValueError('关注字段需要 JSON 键路径列表')
    for path in paths:
        if not isinstance(path, list) or not path or not all(isinstance(k, str) for k in path):
            raise ValueError('关注字段需要非空 JSON 键路径')
        left, right = before, after
        for key in path:
            if not isinstance(left, dict) or not isinstance(right, dict) or key not in left or key not in right:
                break  # Added or removed focus keys are covered by the regular diff.
            left, right = left[key], right[key]
        else:
            if not list(changes_between(left, right)):
                retained.append(dict(op='keep', path=path, after=right))
    return retained


def _one(rows, identity, label):
    matches = [row for row in rows if row['id'] == identity]
    if len(matches) != 1:
        raise ValueError(f'{label}缺失或不唯一：{identity}')
    return matches[0]


def _call(batch, case_id, step_id, data_id):
    case = _one(batch['cases'], case_id, '用例')
    stored = _one(case['steps'], step_id, '业务步骤')
    step, _ = resolve_step(batch, case, 'steps', stored)
    data = _one(batch['data'], data_id, '输入')
    if step.get('data_refs', []).count(data_id) != 1 or not json_input(data):
        raise ValueError(f'调用与 JSON 输入不匹配：{step_id} / {data_id}')
    label = input_label(data, step, {entry['id']: entry for entry in batch['data']})
    return case, step, data, case['steps'].index(stored) + 1, label


def _describe(batch, case_id, row, source_catalog):
    fields = ('p0_case_id', 'p0_step_id', 'p0_data_id', 'step_id', 'data_id', 'source_basis')
    if not all(isinstance(row.get(k), str) and row[k].strip() for k in fields):
        raise ValueError(f'输入复用需要完整调用定位及来源依据：{case_id}')
    catalog = batch
    if not any(case['id'] == row['p0_case_id'] for case in batch['cases']):
        from preparation_scope import scope_context
        if source_catalog is None or not batch.get('initial_copy_baseline'):
            raise ValueError('缺少同版 P0 所在的完整父稿：' + row['p0_case_id'])
        catalog, unavailable = scope_context(batch, source_catalog, require_parent=True)
        if unavailable:
            raise ValueError('P0 的完整父稿版本或摘要不符：' + row['p0_case_id'])
    source, source_step, source_data, source_number, source_label = _call(catalog, *(row[k] for k in fields[:3]))
    target, target_step, target_data, target_number, target_label = _call(batch, case_id, row['step_id'], row['data_id'])
    if source['priority'] != 'P0' or target['priority'] not in ('P1', 'P2'):
        raise ValueError('输入基准须为 P0，目标须为 P1 或 P2：' + case_id)
    # An approved field edit changes the diff. Reassigning either box or changing its
    # use requires a fresh assessment. Neither side stores another copy of its payload.
    binding = _digest([[c['id'], c['module_path'], s['id'], s['operation'], d['id'], d.get('object_ref')]
                       for c, s, d in [(source, source_step, source_data), (target, target_step, target_data)]])
    return dict(binding=binding, source_case=source, source_step=source_step, source_data=source_data,
                source_label=source_label, target_label=target_label,
                source_number=source_number, target_step=target_step, target_data=target_data,
                target_number=target_number, retained=_retained(row, source_data['value'], target_data['value']),
                changes=list(changes_between(source_data['value'], target_data['value'])))


def bind_inputs(batch, assessments, *, source_catalog=None):
    """Replace each supplied case's input assessments, retaining the complete authored cases."""
    _credential_guard([batch, assessments, source_catalog])
    result = copy.deepcopy(batch)
    relations = result.setdefault('input_reuse', {})
    for case_id, rows in assessments.items():
        _one(batch['cases'], case_id, '目标用例')
        if not isinstance(rows, list):
            raise ValueError('每例应按调用提供输入评估列表：' + case_id)
        seen, bound = set(), []
        for row in rows:
            detail = _describe(batch, case_id, row, source_catalog)
            key = (row['step_id'], row['data_id'])
            if key in seen:
                raise ValueError('本例同一输入绑定了多个基准：' + str(key))
            seen.add(key)
            bound.append(dict(copy.deepcopy(row), binding=detail['binding']))
        relations[case_id] = bound
    result['content_version'] = _digest({key: value for key, value in result.items() if key != 'content_version'})
    return result


def resolve_input(batch, case_id, row, *, source_catalog=None):
    detail = _describe(batch, case_id, row, source_catalog)
    if row.get('binding') != detail['binding']:
        raise ValueError('调用定位或用途已变化：' + case_id)
    return detail


def _literal(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(', ', ': '))


def format_change(change):
    path = ''
    for key in change['path']:
        path += (('.' if path else '') + key) if key.isidentifier() else '[' + _literal(key) + ']'
    if change['op'] == 'keep':
        return f'保留 {path}，值为 {_literal(change["after"])}'
    if change['op'] == 'add':
        return f'新增 {path}，值为 {_literal(change["after"])}'
    if change['op'] == 'remove':
        return f'删除 {path}（原值 {_literal(change["before"])}）'
    subject = '保留 ' + path + '，值' if path else '整个输入'
    return f'{subject}由 {_literal(change["before"])} 改为 {_literal(change["after"])}'


def project_inputs(batch, case, node, origins, source_catalog):
    rows = {(r['step_id'], r['data_id']): r for r in batch.get('input_reuse', {}).get(case['id'], [])}
    data = {item['id']: item for item in batch['data']}
    seen = set()

    def visit(parent):
        for child in parent['children']:
            visit(child)
            for origin in child['origins']:
                if origin not in origins:
                    continue
                identity = origins[origin]
                _, step_id, ref = identity
                child['input_call'] = identity
                child['json_value'] = data[ref]['value']
                row = rows.get((step_id, ref))
                if row is None:
                    continue
                seen.add((step_id, ref))
                try:
                    detail = resolve_input(batch, case['id'], row, source_catalog=source_catalog)
                except ValueError as error:
                    child['children'].append(dict(text='输入复用待核对：' + _cell(str(error)), children=[], origins=[]))
                    continue
                source, label = detail['source_case'], detail['source_label']
                target_label = detail['target_label']
                source_label = f'P0「{source["title"]}」（{source["id"]}）第 {detail["source_number"]} 步「{label}」'
                source_call = (source['id'], row['p0_step_id'], row['p0_data_id'])
                child['copy_source'] = (source_call, _cell(source_label), detail['source_data']['value'])
                child['text'] = _cell(f'本例第 {detail["target_number"]} 步「{target_label}」复用同版 {source_label}')
                child.pop('json_value')
                changes = [format_change(change) for change in detail['changes']] or ['输入完全相同，直接复制']
                changes.extend(format_change(item) for item in detail['retained'])
                child['children'] = [dict(text=_cell(line), children=[], origins=[]) for line in changes]
    visit(node)
    for step_id, ref in sorted(rows.keys() - seen):
        node['children'].append(dict(text=_cell(f'输入复用待核对：本例调用或输入已变化 {step_id} / {ref}'),
                                     children=[], origins=[]))


def attach_copy_sources(root):
    """Link only visible references to inputs present in the final layout or its appendix."""
    displayed, references = set(), []

    def collect(node):
        if 'copy_source' in node:
            references.append(node)
        elif 'input_call' in node and 'json_value' in node:
            displayed.add(node['input_call'])
        for child in node['children']:
            collect(child)

    collect(root)
    appendix = {}
    for node in references:
        identity, label, value = node['copy_source']
        if identity in displayed:
            node['text'] += '（见该用例正文）'
        else:
            node['text'] += '（见文末“供复制”）'
            appendix.setdefault(identity, dict(text=label, json_value=value, children=[], origins=[]))
    if appendix:
        root['children'].append(dict(text='供复制', children=list(appendix.values()), origins=[]))
