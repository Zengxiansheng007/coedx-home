"""Bind edits in a returned two-reader Markdown file to the original invocation."""
import copy
import html
import json

from authoring import _digest
from input_reuse import changes_between, field_name, format_change, resolve_input


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('JSON 键重复：' + key)
        result[key] = value
    return result


def _invalid(number):
    raise ValueError('JSON 数值非法：' + number)


DECODER = json.JSONDecoder(object_pairs_hook=_object, parse_constant=_invalid)


def _literal(text):
    value = DECODER.decode(text)
    json.dumps(value, allow_nan=False)
    return value


def _path(text):
    keys = []
    while text:
        if text.startswith('['):
            key, end = DECODER.raw_decode(text[1:])
            if not isinstance(key, str) or text[end+1:end+2] != ']':
                raise ValueError('方括号内须为 JSON 键名')
            text = text[end+2:]
        else:
            if keys:
                if not text.startswith('.'):
                    break
                text = text[1:]
            end = 0
            while end < len(text) and (text[:end+1]).isidentifier():
                end += 1
            if not end:
                raise ValueError('缺少字段路径')
            key, text = text[:end], text[end:]
        keys.append(key)
    return tuple(keys), text


def _keys(value, path=()):
    if isinstance(value, dict):
        for key, child in value.items():
            yield (*path, key)
            yield from _keys(child, (*path, key))


def _command(text, known, baseline):
    if text.startswith('整个输入由 '):
        verb, path, rest = '保留', (), text[len('整个输入'):]
    else:
        verb, _, field = text.partition(' ')
        if verb not in ('新增', '删除', '省略', '保留') or not field:
            raise ValueError('请写明新增、删除、保留或省略的字段及取值')
        path, rest = _path(field)
        if len(path) == 1 and path not in known and verb != '新增':
            found = [k for k in known if k[-1] == path[0]]
            if len(found) != 1:
                raise ValueError('请使用完整字段路径：' + field)
            path = found[0]
    if path:
        in_source = path in set(_keys(baseline))
        if verb == '新增' and in_source:
            raise ValueError('同版 P0 已含该键，无法新增：' + field_name(path))
        if verb == '保留' and not in_source:
            raise ValueError('同版 P0 缺少该键，无法保留：' + field_name(path))
    if verb in ('删除', '省略'):
        if rest:
            if not rest.startswith('（原值 ') or not rest.endswith('）'):
                raise ValueError('省略/删除的字段说明不明确')
            _verify_old(baseline, path, _literal(rest[4:-1]))
        return path, {}
    if rest.startswith('，值为 '):
        return path, dict(after=_literal(rest[4:]))
    prefix = '，值由 ' if path else '由 '
    if not rest.startswith(prefix):
        raise ValueError('请给出确切 JSON 值')
    rest = rest[len(prefix):]
    before, end = DECODER.raw_decode(rest)
    _verify_old(baseline, path, before)
    if not rest[end:].startswith(' 改为 '):
        raise ValueError('改值必须标明变更后的 JSON 值')
    return path, dict(after=_literal(rest[end+4:]))


def _verify_old(value, path, before):
    for key in path:
        if not isinstance(value, dict) or key not in value:
            raise ValueError('原值缺失：' + field_name(path))
        value = value[key]
    if _digest(value) != _digest(before):
        raise ValueError('标注的原值与同版基准不符：' + field_name(path))


def _write(value, path, change):
    if not path:
        if 'after' not in change:
            raise ValueError('不能省略整个输入框')
        return copy.deepcopy(change['after'])
    parent = value
    for key in path[:-1]:
        if not isinstance(parent, dict) or key not in parent:
            raise ValueError('字段父级缺失：' + field_name(path))
        parent = parent[key]
    if not isinstance(parent, dict):
        raise ValueError('字段父级必须是对象：' + field_name(path))
    if 'after' in change:
        parent[path[-1]] = copy.deepcopy(change['after'])
    elif path[-1] in parent:
        del parent[path[-1]]
    return value


def _variant_value(batch, call, lines, catalog):
    cid, sid, did = call
    rows = [r for r in batch['input_reuse'][cid] if (r['step_id'], r['data_id']) == (sid, did)]
    if len(rows) != 1:
        raise ValueError('输入差异未唯一绑定到该调用')
    detail = resolve_input(batch, cid, rows[0], source_catalog=catalog)
    baseline = detail['source_data']['value']
    value = copy.deepcopy(detail['target_data']['value'])
    # Removing a whole sentence may be a mistaken deletion or an instruction to inherit.
    # Require a positive, located instruction before changing an existing assessment.
    bound = {format_change(ch):tuple(ch['path']) for ch in detail['changes'] + detail['retained']}
    missing = set(bound.values())
    known = set(_keys(value)) | set(_keys(baseline))
    seen = []
    for line in lines:
        line = html.unescape(line)
        if line == '输入完全相同，直接复制':
            if detail['changes']:
                raise ValueError('需要逐字段说明如何恢复 P0 的输入')
            continue
        if line in bound:
            path = bound[line]
        else:
            path, change = _command(line, known, baseline)
            if not change and path not in known:
                raise ValueError('要省略的字段不存在：' + field_name(path))
            value = _write(value, path, change)
        if any(path[:len(p)] == p or p[:len(path)] == path for p in seen):
            raise ValueError('字段修改重复或范围重叠：' + field_name(path))
        seen.append(path)
        missing.discard(path)
    if missing:
        raise ValueError('请明确被移除说明的字段应该如何处理：' + '、'.join(map(field_name, sorted(missing))))
    return value


def reader_ids(markdown):
    import incremental_review
    lines = markdown.splitlines()
    if incremental_review.is_incremental(markdown):
        markers = [line[9:] for line in lines if line.startswith('  - 待评用例：')]
        if len(markers) == 1:
            return markers[0].split('、')
    elif len(lines) >= 3 and '；待评用例：' in lines[2]:
        return lines[2].partition('；待评用例：')[2].partition('；')[0].split('、')
    return None


def read_return(batch, markdown, ids, companion_base, catalog, case_bindings=None):
    import incremental_review
    from aggregation import _parse, expand_feedback, feedback_topics
    from feedback import _decode_scalar_return
    from source_preparation import render_selection, reader_source
    incoming = markdown.splitlines()
    incremental = incremental_review.is_incremental(markdown)
    header_size = 1 if incremental else 3
    version = (incremental_review.version_of(markdown) if incremental
               else incoming[1].removeprefix('- 版本：') if len(incoming) > 1 else '')
    if version != batch['content_version']:
        raise ValueError('评审范围 / 稿件版本：请在当前版 ' + batch['content_version'] + ' 重新标注')
    slots = {}
    template = render_selection(batch, ids, companion_base=companion_base, source_catalog=catalog,
                                _return_bindings=slots)['xmind_markdown'].splitlines()
    root = _parse(template[header_size:])
    # The earlier two-reader delivery had no per-case number outside incremental review.
    # Reconstruct that layout only when the return has no direct case IDs at all.
    numbers = {'用例编号：' + cid for cid in ids}
    has_numbers = any(line.strip().removeprefix('- ') in numbers for line in incoming)
    def bind_origins(node):
        for child in node['children'][:]:
            row = header_size + child['origins'][0]
            if not incremental and not has_numbers and child['text'] in numbers and node.get('case_id'):
                node['only_reviewed_case'] = ids == [node['case_id']]
                node['children'].remove(child)
                continue
            child.update(origins=[], template_row=row, reader_indent=len(template[row])-len(template[row].lstrip()))
            child.update(slots.get(row, {}))
            bind_origins(child)
    bind_origins(root)
    if case_bindings:
        topics = feedback_topics(markdown)
        if set(case_bindings) - set(ids) or any(sum(t['returned_digest'] == b.get('returned_digest')
                for t in topics) != 1 for b in case_bindings.values()):
            raise ValueError('Identity evidence does not uniquely bind the raw return')
    records = {data['id']: data for data in batch['data']}
    edits = []
    def read_input(slot, actual, offset):
        i = slot['template_row']
        row = actual['origins'][0] + offset
        wanted = template[i]
        call = slot.get('call')
        location = ' / '.join(call) if call else '供复制 / ' + wanted.strip()
        indent = wanted[:len(wanted)-len(wanted.lstrip())] + '  '
        end = row + 1
        while end < len(incoming) and incoming[end].startswith(indent):
            end += 1
        block = incoming[row+1:end]
        if block == template[i+1:slot['end']]:
            return
        try:
            if slot['kind'] in ('json','copy'):
                first, rest = indent + '-     ', indent + '      '
                if not block or not block[0].startswith(first) or any(not line.startswith(rest) for line in block[1:]):
                    raise ValueError('请保留同一输入框的 Markdown JSON 块')
                after = _literal('\n'.join([block[0][len(first):], *[line[len(rest):] for line in block[1:]]]))
            else:
                prefix = indent + '- '
                if not block or any(not line.startswith(prefix) for line in block):
                    raise ValueError('请保留该次调用的字段变化列表')
                after = _variant_value(batch, slot['call'], [line[len(prefix):] for line in block], catalog)
            if slot['kind'] == 'copy':
                if list(changes_between(slot['value'], after)):
                    raise ValueError('附录仅供复制，请到原 P0 的对应输入框修改')
                return
            before = records[call[2]]['value']
            for delta in changes_between(before, after):
                action = {'add':'新增','remove':'删除','replace':'修改'}[delta['op']]
                edits.append(dict(call=list(slot['call']), summary='本例'+action+' '+field_name(delta['path']), **delta))
        except (KeyError, ValueError, TypeError) as error:
            raise ValueError(f'{location} / 第 {row+2} 行：{error}') from None
    flat = slots['flat']
    expanded = expand_feedback(batch, flat, markdown, case_bindings, reader_tree=(template[:header_size], root),
                               read_input=read_input)
    # Use the same eligible source leaves, types and shared-field agreement as existing file feedback.
    changes, missing = _decode_scalar_return(reader_source(batch), flat.splitlines(), expanded.splitlines(), {}, lambda _: False,
        source_catalog=catalog, module_review=True, incremental=incremental, display_ids=ids)
    return changes, edits, missing


def _touches(left, right):
    return left[:len(right)] == right or right[:len(left)] == left


def _invocations(batch):
    from step_reuse import GROUPS
    for case in batch['cases']:
        for group in GROUPS:
            for pos, step in enumerate(case.get(group, [])):
                for ref in step.get('step_reference', step).get('data_refs', []):
                    yield (case['id'], step['id'], ref), (group, pos)


def plan_impact(batch, edits, shared, displayed, catalog):
    """Only a named P0 invocation propagates; preserve each assessed variant's overrides."""
    if not shared:
        return edits, []
    from preparation_scope import scope_context
    context, unavailable = scope_context(batch, catalog, require_parent=True)
    if unavailable:
        raise ValueError('共享 P0 输入需完整同版父稿以列出范围外引用')
    source = tuple(shared)
    if len(source) != 3 or not edits or any(tuple(e['call']) != source for e in edits):
        raise ValueError('请将共享 P0 的用例、步骤、数据编号与本次实际修改对应')
    case = next(c for c in batch['cases'] if c['id'] == source[0])
    if case['priority'] != 'P0':
        raise ValueError('共享修改需指定 P0 的输入框')
    relations = dict((catalog or {}).get('input_reuse', {}), **batch.get('input_reuse', {}))
    impact = []
    projected = list(edits)
    for cid, rows in relations.items():
        for row in rows:
            if (row['p0_case_id'], row['p0_step_id'], row['p0_data_id']) != source:
                continue
            detail = resolve_input(context, cid, row, source_catalog=catalog)
            call = [cid, row['step_id'], row['data_id']]
            overrides = [c['path'] for c in detail['changes']] + row.get('focus_paths', [])
            applied, retained = [], []
            for delta in edits:
                if any(_touches(delta['path'], p) for p in overrides):
                    retained.append(delta['path'])
                    continue
                applied.append(delta['path'])
                projected.append(dict(delta, call=call, summary='随共享 P0 '+delta['summary'][2:]))
            impact.append(dict(call=call, outside_review=cid not in displayed, inherited=applied, preserved=retained))
    bound = {tuple(row['call']) for row in impact} | {source}
    for call, _ in _invocations(context):
        if call in bound or call[2] != source[2]:
            continue
        bound.add(call)
        impact.append(dict(call=list(call), outside_review=call[0] not in displayed,
                           inherited=[e['path'] for e in edits], preserved=[]))
        projected.extend(dict(e, call=list(call), summary='随共享 P0 '+e['summary'][2:]) for e in edits)
    return projected, impact


def apply_inputs(batch, edits, catalog):
    from collections import defaultdict
    from local_step_feedback import materialize, refresh
    from preparation_scope import scope_context
    from input_reuse import _describe
    calls = defaultdict(list)
    for edit in edits:
        calls[tuple(edit['call'])].append(edit)
    cases = {c['id']:c for c in batch['cases']}
    if any(cid not in cases for cid, _, _ in calls):
        raise ValueError('共享修改包含范围外用例；请从完整同版候选提交同一修改并确认完整影响范围')
    context, unavailable = scope_context(batch, catalog, require_parent=True)
    if unavailable:
        raise ValueError('请提供完整同版父稿以核对输入所有者')
    # Use the ownership snapshot before splitting any literals or updating bindings.
    owners = defaultdict(list)
    positions = {}
    for call, position in _invocations(context):
        owners[call[2]].append(call)
        if call in positions and call in calls:
            raise ValueError('输入框定位不唯一：' + ' / '.join(call))
        positions[call] = position
    records = {d['id']:d for d in batch['data']}
    renamed = {}
    changed = set()
    for call in calls:
        group, pos = positions[call]
        materialize(batch, cases[call[0]], [group, pos, 'data_refs'])
    for call, deltas in calls.items():
        cid, sid, ref = call
        group, pos = positions[call]
        step = cases[cid][group][pos]
        record = records[ref]
        def field_edits(owner):
            return [{k:v for k,v in e.items() if k not in ('summary','call')} for e in calls.get(owner, [])]
        together = all(_digest(field_edits(call)) == _digest(field_edits(owner)) for owner in owners[ref])
        if together and ref in changed:
            continue
        if not together:
            new_ref = ref + '/review-' + _digest([call, batch['content_version']])[:16]
            if new_ref in records:
                raise ValueError('本例输入编号冲突：' + new_ref)
            record = dict(copy.deepcopy(record), id=new_ref)
            records[new_ref] = record
            batch['data'].append(record)
            step['data_refs'] = [new_ref if item == ref else item for item in step['data_refs']]
            renamed[call] = new_ref
        changed.add(record['id'])
        for delta in deltas:
            if 'before' in delta:
                _verify_old(record['value'], delta['path'], delta['before'])
            record['value'] = _write(record['value'], delta['path'], delta)
        record['source'] = 'user_decision'
    for cid in {call[0] for call in calls}:
        refresh(batch, cases[cid])
    for cid, rows in batch.get('input_reuse', {}).items():
        for row in rows:
            target = (cid, row['step_id'], row['data_id'])
            source = (row['p0_case_id'], row['p0_step_id'], row['p0_data_id'])
            if target in renamed or source in renamed:
                row['data_id'] = renamed.get(target, row['data_id'])
                row['p0_data_id'] = renamed.get(source, row['p0_data_id'])
                row['binding'] = _describe(batch, cid, row, catalog)['binding']


def describe_proposal(pending):
    lines = []
    for edit in pending['input_edits']:
        before, after = [json.dumps(edit[k], ensure_ascii=False) if k in edit else '（键不存在）'
                         for k in ('before', 'after')]
        lines.append(' / '.join(edit['call']) + '：' + edit['summary'] + '；' + before + ' → ' + after)
    for impact in pending['input_impact']:
        lines.append(' / '.join(impact['call']) + ('（范围外）' if impact['outside_review'] else '（范围内）') +
                     ' 随共享修改：' + ('、'.join(map(field_name, impact['inherited'])) or '无') +
                     '；保留本例差异：' + ('、'.join(map(field_name, impact['preserved'])) or '无'))
    if pending['input_edits']:
        for case in pending['batch']['cases']:
            if case['id'] in {e['call'][0] for e in pending['input_edits']}:
                lines.append(f"需人工复核 {case['id']}「{case['title']}」的测试点、操作和业务预期与新入参是否一致。")
    return '\n'.join(lines)


def retire_changed_segments(batch, affected, catalog):
    """Use complete authored steps when an accepted edit invalidates an old compact summary."""
    from review_segments import signature
    sources = {c['id']:c for c in (catalog or batch)['cases']}
    retired = []
    for case in batch['cases']:
        row = case.get('review_segment')
        if not row or not {case['id'], row['p0_case_id']} & affected:
            continue
        binding = row['binding']
        version = binding.get('signature_version', 1)
        origin = sources.get(row['p0_case_id'])
        changed_source = origin and signature(origin, (catalog or batch)['data'], version) != binding['source_digest']
        if changed_source or signature(case, batch['data'], version) != binding['target_digest']:
            retired.append(dict(case_id=case['id'], original_binding=binding))
            del case['review_segment']
            case['semantic_version'] = _digest({k:v for k,v in case.items() if k != 'semantic_version'})
    return retired


def _key_order(source):
    # Q&A replay sorts object keys. Preserve only presentation order from the
    # original delivered candidate, sharing common shapes across the batch.
    orders, exceptions = {}, {}
    def visit(value, path):
        if isinstance(value, dict):
            keys = tuple(sorted(value))
            order = orders.setdefault(keys, list(value))
            if list(value) != order:
                exceptions[json.dumps(path, ensure_ascii=False)] = list(value)
            for key, child in value.items():
                visit(child, [*path, key])
        elif isinstance(value, list):
            for i, child in enumerate(value):
                visit(child, [*path, i])
    visit(source, [])
    return dict(orders=[order for keys, order in orders.items() if list(keys) != order], exceptions=exceptions)


def ordered_candidate(source, layout):
    orders = {tuple(sorted(order)):order for order in layout['orders']}
    exceptions = layout['exceptions']
    def visit(value, path):
        if isinstance(value, dict):
            keys = tuple(sorted(value))
            order = exceptions.get(json.dumps(path, ensure_ascii=False), orders.get(keys, keys))
            if set(order) != set(value) or len(order) != len(value):
                raise ValueError('原交付字段顺序与当前来源不同')
            return {k:visit(value[k], [*path,k]) for k in order}
        if isinstance(value, list):
            return [visit(child,[*path,i]) for i, child in enumerate(value)]
        return value
    return visit(source, [])


def start_reader_feedback(record, returned_file, agent_file, *, actual_reply, shared_input=None, case_bindings=None):
    """Record a returned Markdown against the original delivery's Agent selection and version."""
    from pathlib import Path
    from qa_record import advance_record, read_record
    from reader_delivery import case_references
    from single_case import read_json
    file = Path(returned_file)
    original = Path(agent_file)
    index = read_json(original)
    batch = read_record(record)['batch']
    if (index.get('format') != 'tca.agent-review.v1' or index.get('candidate') != 'candidate.json'
            or index.get('content_version') != batch['content_version']):
        raise ValueError('原交付 Agent 文件的格式、候选或稿件版本不符')
    source = read_json(original.parent / 'candidate.json')
    if (_digest({k:v for k,v in source.items() if k != 'content_version'}) != batch['content_version']
            or source['cases'] != batch['cases'] or source['data'] != batch['data']):
        raise ValueError('当前问答记录与原交付候选来源不符')
    ids = index['case_ids']
    owners = {case['id']:case for case in source['cases'] if case.get('feedback_disposition') != 'excluded_this_round'}
    if (not isinstance(ids, list) or not ids or not all(isinstance(cid,str) and cid in owners for cid in ids)
            or len(ids) != len(set(ids)) or index['cases'] != {cid:case_references(owners[cid]) for cid in ids}):
        raise ValueError('原交付 Agent 文件的待评清单与步骤或输入定位不符')
    payload = dict(channel='markdown', actual_reply=actual_reply, source_ref=str(file.resolve()),
                   source_version=batch['content_version'], markdown=file.read_text(encoding='utf-8-sig'),
                   review_ids=ids, reader_order=_key_order(source), clear_changes=True)
    if source.get('review_layout') == 'incremental-v1':
        payload['companion_base'] = str(original.parent.resolve())
    if shared_input is not None:
        payload['shared_input'] = shared_input
    if case_bindings is not None:
        payload['case_bindings'] = case_bindings
    if 'source_catalog' in index:
        if index['source_catalog'] != 'source-catalog.json':
            raise ValueError('原交付完整父稿的位置不符')
        payload['source_catalog'] = read_json(original.parent / 'source-catalog.json')
    return advance_record(record, 'start_feedback', payload)
