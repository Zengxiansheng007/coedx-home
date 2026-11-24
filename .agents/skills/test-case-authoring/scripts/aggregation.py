"""Lossless hierarchy projection with reversible source-line bindings."""
import copy
import json
import hashlib
import incremental_review
from presentation import case_name  # Resolve generated applicability identities only.
from review_expression import title  # Grade is presentation, not stored Chinese name.


def business_path(case):
    """Return only explicitly source-assessed grouping; never infer from titles."""
    group = case.get('business_group')  # Absent metadata preserves historical tasks.
    if group is None:
        return []
    if not isinstance(group, dict) or not isinstance(group.get('source'), str) or not group['source'].strip():
        raise ValueError('Business grouping requires an explicit source assessment')
    path = group.get('path')  # No empty grouping or implicit default categories.
    if not isinstance(path, list) or not path or any(not isinstance(p, str) or not p.strip() or '\n' in p or '\r' in p for p in path):
        raise ValueError('Business grouping requires nonempty single-line labels')
    return path


def _semantic(value):
    if isinstance(value, dict):  # Ignore only provenance and generated local identity.
        return {k: _semantic(v) for k, v in value.items() if k not in ('source', 'lines')}  # Nested business object IDs remain significant.
    if isinstance(value, list):  # Sequence is part of preparation meaning.
        return [_semantic(v) for v in value]
    return value


def _parse(lines):
    root = {'text': '', 'children': [], 'origins': []}  # Virtual root retains source offsets.
    stack = [(-1, root)]
    for index, line in enumerate(lines):
        depth = (len(line) - len(line.lstrip())) // 2  # Two spaces encode one Markdown child level.
        node = {'text': line.lstrip()[2:], 'children': [], 'origins': [index]}  # 缩进属于树层级，尾部空格属于真实业务值。
        while stack[-1][0] >= depth:  # Leave completed siblings before attaching this topic.
            stack.pop()  # The remaining stack top is the exact semantic parent.
        stack[-1][1]['children'].append(node)  # Preserve sibling order from the source.
        stack.append((depth, node))  # Subsequent deeper topics belong to this node.
    return root


def _merge_origins(target, source):
    target['origins'].extend(source['origins'])  # One visible leaf can belong to several cases.
    for left, right in zip(target['children'], source['children']):
        _merge_origins(left, right)


def _shape(node):  # Source offsets can combine only when their rendered descendants align.
    return [node['text'], [_shape(child) for child in node['children']]]


def projection(batch, markdown, *, handoff=True, common_legacy=False, source_catalog=None, display_case_ids=None, _trailing_legacy=False):  # 旧投影模式仅用于精确复原历史生成布局。
    from module_handoff import TITLE, module_notes  # Generated nodes never acquire business edit origins.
    instructions = module_notes(dict(batch, cases=[c for c in batch['cases'] if display_case_ids is None or c['id'] in display_case_ids]))  # Companion notes cannot resolve undisplayed blocked references.
    attached = set()  # Attach exactly once per complete module path.
    lines = markdown.splitlines()
    root = _parse([line.rstrip() for line in lines[3:]] if _trailing_legacy else lines[3:])  # 只复现旧基线丢尾空格的生成行为，不改实际回传或原始值。
    merged = {'text': '', 'children': [], 'origins': []}
    data = {d['id']: d for d in batch['data']}
    groups = {}
    from preparation_scope import active_scopes  # Recheck on every render and resume.
    approved = active_scopes(batch, source_catalog)
    from preparation_scope import operation_scopes
    operations, pending = operation_scopes(batch, source_catalog)  # Per-item exclusions remain in one candidate record.
    indexed = {case['id']: case for case in batch['cases']}  # Full current batch still drives scope validation above.
    displayed = batch['cases'] if display_case_ids is None else [indexed[cid] for cid in display_case_ids]  # Match the ordered flat source exactly.
    for case, branch in zip(displayed, root['children']):  # Only selected branches are visible.
        target, source = merged, branch  # Walk source hierarchy and shared target in lockstep.
        for level, part in enumerate(case['module_path']):  # Match level and ancestor, never text globally.
            node = next((n for n in target['children'] if n.get('directory') == (level, part)), None)
            if node is None:
                node = dict(text=source['text'], children=[], origins=[], directory=(level, part))
                target['children'].append(node)
            node['origins'].extend(source['origins'])
            target = node
            source = source['children'][0]  # Flat source has exactly one path branch per case.
        source['case_id'] = case['id']
        path = tuple(case['module_path'])  # Parents without direct cases never reach this branch.
        target['module_path'] = path  # 配套资料按完整模块路径定位。
        scope_target = target  # Module fallback or the explicitly reviewed ancestor.
        for level, part in enumerate(business_path(case)):  # Group only inside the existing module owner.
            node = next((n for n in target['children'] if n.get('directory') == ('business', level, part)), None)
            if node is None:
                node = dict(text=part, children=[], origins=[], directory=('business', level, part))  # Generated hierarchy has no scalar edit origin.
                target['children'].append(node)
            target = node
            if (not handoff or common_legacy) and case['id'] in approved and level + 1 == len(approved[case['id']]['business_path']):
                scope_target = target  # Frozen legacy feedback keeps its original business-group placement.
        source['text'] = title(case) if handoff else source['text'][len(case['id']) + 1:]  # Historical layout retains historical ungraded headings.
        for direction, group, label, position in (('pre', 'common_preconditions', '公共前置操作', '前置'), ('post', 'common_postconditions', '公共后置操作', '后置')):  # Shared membership and feedback mapping in both directions.
            common = next((n for n in source['children'] if n['text'] == label), None)
            if common is None:
                continue
            attributed = [r for r in operations.get(case['id'], []) if r['direction'] == direction and r.get('attribution') == 'special']  # 显式本例归属沿原步骤身份投影。
            records = [r for r in operations.get(case['id'], []) if r['direction'] == direction and r.get('attribution') != 'special']  # 每个公共项保留独立适用关系。
            if direction == 'pre' and case['id'] in approved:
                records = [approved[case['id']]]  # Legacy whole-list scope is still readable.
            removed = []
            if attributed and handoff and not common_legacy:
                ids = {step_id for scope in attributed for step_id in scope['step_ids_by_case'][case['id']]}
                children = [node for node, step in zip([node for node in common['children'] if node['text'].startswith('步骤 ')], case.get(group, [])) if step['id'] in ids]  # 不改源下标、原序或 origins。
                special_label = '特殊前置操作' if direction == 'pre' else '特殊后置操作'
                special = next((node for node in source['children'] if node['text'] == special_label), None)
                if special is None:
                    special = dict(text=special_label, children=[], origins=[], attributed_special=True)  # 只有实际评估通过且有步骤才建节点。
                    source['children'].insert(1 if direction == 'pre' else len(source['children']), special)
                special['attributed_special'] = True  # 已存在的真实特殊组同样从最终投影生成对话表。
                special['children'] = children + special['children'] if direction == 'pre' else special['children'] + children  # 原 common 与真实特殊项的执行顺序保持。
                removed.extend(children)
            for scope in records:
                ids = scope.get('step_ids_by_case', {}).get(case['id'])
                children = common['children'] if ids is None else [node for node, step in zip(
                    [n for n in common['children'] if n['text'].startswith('步骤 ')], case.get(group, [])) if step['id'] in ids]
                key = (tuple(case['module_path']), scope['id'])  # Display owner is always the module.
                if key not in groups:
                    shared = dict(text=label + ' ' + str(1 + sum(k[0] == key[0] for k in groups)),
                                  children=copy.deepcopy(children), origins=[], scope=scope, members=[], direction=direction)
                    groups[key] = shared
                    scope_target['children'].append(shared)  # Business grouping never controls definition placement.
                else:
                    shared = groups[key]
                    for left, right in zip(shared['children'], children):
                        _merge_origins(left, right)  # Every applicable source receives a proposed shared edit.
                shared['members'].append(case['id'])
                removed.extend(children)
            if not common_legacy and handoff:
                common['children'] = [node for node in common['children'] if node not in removed]
            if handoff and not common_legacy:
                source['children'].remove(common)  # No repeated common heading or reference list in case nodes.
                insertion = 0 if direction == 'pre' else len(source['children'])  # Pending post obligations keep their trailing position.
                if common['children'] and case.get(group) and not records:
                    common['text'] = '待核对：' + position + '适用范围'  # Unreviewed common content is never silently relabelled special.
                    common['origins'] = []
                    source['children'].insert(insertion, common)  # Keep unresolved original actions inspectable.
                elif any(n['text'].startswith('步骤 ') for n in common['children']):
                    common['text'] = '待核对：未归属' + position + '操作'  # A partial definition must not hide leftover obligations.
                    common['origins'] = []
                    source['children'].insert(insertion, common)
                elif common['children'] and case.get(group):
                    common['text'] = '待核对：未归属' + position + '说明'  # Whole-list notes cannot be silently assigned to one common item.
                    common['origins'] = []
                    source['children'].insert(insertion, common)
                elif case.get(group + '_note') and not case.get(group):
                    source['children'][insertion:insertion] = common['children']  # Explicit absence conditions remain readable without an empty heading.
                elif direction == 'pre' and not case.get(group) and not case.get(group + '_note'):
                    source['children'].insert(0, dict(text='前置操作未提供，待核对', children=[], origins=[]))
            elif records:
                common['children'] = [{'text': '适用：' + shared['text'] + '（执行时仍须完成）', 'children': [], 'origins': []}]  # Historical feedback retains its explicit reference layout.
        target['children'].append(source)  # Keep each individual case after its shared preparation.
    for shared in groups.values():  # Final membership is available after all cases are projected.
        shared['children'].insert(0, {'text': '适用用例：' + '、'.join(case_name(batch, cid) for cid in shared['members']), 'children': [], 'origins': []})  # Display names while preserving internal member IDs.
        scope = shared['scope']  # Generated scope metadata cannot edit case obligations.
        for text in ('范围版本：' + scope['version'], '适用分组：' + ' / '.join(scope['module_path'] + scope['business_path']), '例外用例：' + ('、'.join(case_name(source_catalog or batch, cid) for cid in scope['exception_case_ids']) or '无'), '执行频次：' + scope['frequency']):
            shared['children'].insert(0, {'text': text, 'children': [], 'origins': []})
    if handoff and not common_legacy:
        def order_definitions(node):  # Stable semantic buckets preserve all source origins and business order.
            node['children'].sort(key=lambda child: {'pre': 0, 'post': 2}.get(child.get('direction'), 1))
            for child in node['children']:
                order_definitions(child)
        order_definitions(merged)
    return lines[:3], merged


def aggregate(batch, markdown, source_catalog=None, *, display_case_ids=None, companion_base=None):  # 保留完整范围及资料交付位置。
    header, root = projection(batch, markdown, source_catalog=source_catalog, display_case_ids=display_case_ids)  # Shared display contract.
    if batch.get('review_layout') == incremental_review.LAYOUT:
        header, root = incremental_review.project(batch, root, companion_base=companion_base)  # 新版共用准确的业务源行。
    lines = list(header)
    def visit(node, depth):
        lines.append('  ' * depth + '- ' + node['text'])
        for child in node['children']:
            visit(child, depth + 1)
    for node in root['children']:
        visit(node, 0)
    return '\n'.join(lines) + '\n'


def _fingerprint(node):
    return hashlib.sha256(json.dumps(_shape(node), ensure_ascii=False).encode('utf-8')).hexdigest()  # Bind the complete returned subtree.


def feedback_topics(markdown):
    """Inspect return topics for agent-side binding after business clarification."""
    result = []
    def visit(node, path):
        for child in node['children']:
            result.append(dict(title=child['text'], path=path, returned_digest=_fingerprint(child)))  # No inferred source identity.
            visit(child, path + [child['text']])
    start = 1 if incremental_review.is_incremental(markdown) else 3  # 新版摘要属于正文主支。
    visit(_parse(markdown.splitlines()[start:]), [])
    return result


def expand_feedback(batch, flat_markdown, incoming, case_bindings=None, *, handoff=True, common_legacy=False, source_catalog=None, _normalize_case=None, _trailing_legacy=False, companion_base=None):  # 交付位置约束材料链接的回传。
    """Expand edits through exact baseline bindings before existing feedback review."""
    header, expected = projection(batch, flat_markdown, handoff=handoff, common_legacy=common_legacy, source_catalog=source_catalog, _trailing_legacy=_trailing_legacy)  # 历史布局仍绑定同版候选及完整原始源偏移。
    lines = incoming.splitlines()
    incremental = batch.get('review_layout') == incremental_review.LAYOUT and incremental_review.is_incremental(incoming)  # 只对已登记的新稿启用新版解释。
    if incremental:
        header, expected = incremental_review.project(batch, expected, companion_base=companion_base)
    if lines[:len(header)] != header:
        raise ValueError('Markdown header/version must match initial display')
    actual = _parse(lines[len(header):])
    def legacy(node, path):  # Historic generated IDs remain explicit source identity within the exact baseline path.
        for case in batch['cases']:
            if path == case['module_path'] + business_path(case) and node['text'].startswith(case['id'] + ' '):
                node['legacy_case_id'] = case['id']
                node['text'] = (case['priority'] + ' ' if handoff else '') + node['text'][len(case['id']) + 1:]  # Historical explicit identity gains only the active layout grade.
                break
        original_title = node['text']
        for child in node['children']:
            legacy(child, path + [original_title] if original_title else path)
    legacy(actual, [])
    output = flat_markdown.splitlines()
    removed = set()
    bindings = case_bindings or {}  # Only explicit business clarification may bind edited cases.
    if set(bindings) - {c['id'] for c in batch['cases']}:
        raise ValueError('Unknown feedback binding identity')
    for binding in bindings.values():
        if not binding.get('actual_reply') or binding.get('source_version') != batch['content_version']:
            raise ValueError('Feedback identity needs a current version and actual business reply')
    used = set()
    def remove_cases(node):  # Omitted complete branches retain explicit deletion clarification.
        if node.get('case_id'):
            removed.add(node['case_id'])
        for child in node['children']:
            remove_cases(child)

    def match(wanted, got):
        remaining = list(got['children'])
        for child in wanted['children']:
            if child.get('case_id'):
                binding = bindings.get(child['case_id'])
                normalize = (lambda node: _normalize_case(child['case_id'], node, child)) if _normalize_case else (lambda node: node)  # 按当前已知身份核对可信评审元数据，不按标题猜身份。
                def normalized_shape(node):  # 扫描其他候选时，对齐失败只表示不是这个准确owner。
                    try:  # 真正选中后仍完整执行严格归一化。
                        return _shape(normalize(node))  # 保留所有业务节点形状。
                    except ValueError:  # 不给不相关用例的控制行套用当前owner身份。
                        return None  # 无法对齐的候选不能借机被接受。
                expected_shape = normalized_shape(child)  # 准确源模板只计算一次。
                if incremental and not binding:
                    identity = '用例编号：' + child['case_id']  # 同名用例按直属稳定编号找回原记录。
                    matches = [n for n in remaining if n['children'] and n['children'][0]['text'] == identity]
                else:
                    matches = [n for n in remaining if (_fingerprint(n) == binding.get('returned_digest') if binding else n.get('legacy_case_id') == child['case_id'] or (not n.get('legacy_case_id') and expected_shape is not None and normalized_shape(n) == expected_shape))]  # 显式绑定仍先核对原始返回摘要。
                if len(matches) > 1:
                    raise ValueError('Ambiguous identical cases; clarify the business distinction')
                found = matches[0] if matches else None
                if binding:
                    if found is None:
                        raise ValueError('Returned subtree differs from clarified binding')
                    used.add(child['case_id'])
                if found is None:
                    removed.add(child['case_id'])
                    continue
            elif child.get('scope'):  # Exact generated definition identity also accepts historical insertion order.
                matches = [n for n in remaining if n['text'] == child['text']]
                if len(matches) != 1:
                    raise ValueError('Shared definition identity needs explicit interpretation')
                found = matches[0]
            elif child.get('directory'):  # Directory identity includes its exact ancestor and level.
                found = next((n for n in remaining if n['text'] == child['text']), None)
                if found is None:
                    remove_cases(child)
                    continue
            else:
                found = remaining[0] if remaining else None
            if found is None:
                raise ValueError('Structural Markdown edit needs explicit chat interpretation')
            remaining.remove(found)
            if child.get('case_id') and _normalize_case:  # 层级匹配后，双方仅移除该用例可信同版评审文字。
                child, found = normalize(child), normalize(found)  # 保留源行偏移，后续业务叶仍逐项核对。
            if child['text'] != found['text']:
                if child.get('directory') or not child['origins']:
                    raise ValueError('Directory or applicability edit needs explicit interpretation')
                for origin in child['origins']:
                    old = output[origin + 3]
                    prefix = child['case_id'] + ' ' if child.get('case_id') else ''  # Restore internal identity for the existing scalar mapper.
                    text = incremental_review.restore_text(child, found['text'])  # 先去掉新版的呈现前缀。
                    import re
                    ordinal = re.match(r'步骤 \d+：', child.get('presentation_prefix', (child['text'],))[0])  # 各源行保留自己的步骤位置。
                    if ordinal:
                        if not text.startswith(ordinal.group()):
                            raise ValueError('Step ordinal edit needs explicit interpretation')
                        source_prefix = re.match(r'步骤 \d+：', old.strip()[2:]).group()
                        text = source_prefix + text[len(ordinal.group()):]
                    if child.get('case_id') and handoff:
                        grade = next(c['priority'] for c in batch['cases'] if c['id'] == child['case_id']) + ' '
                        if not text.startswith(grade):
                            raise ValueError('Priority changes require explicit chat interpretation')
                        text = text[len(grade):]  # Never persist presentation prefix into the name.
                    output[origin + 3] = old[:len(old) - len(old.lstrip())] + '- ' + prefix + text
            match(child, found)
        if remaining:
            raise ValueError('Unknown Markdown identity or structure')
    match(expected, actual)
    if used != set(bindings):
        raise ValueError('Unused identity binding; clarify the actual returned scope')
    if removed:  # Rebuild the flat source only when complete cases were omitted.
        starts = []  # Collect original block boundaries before removing any lines.
        for index, line in enumerate(output[3:], 3):  # Skip the header while retaining absolute line offsets.
            for case in batch['cases']:  # Bind block starts to known case identities.
                if line.startswith('  ' * len(case['module_path']) + '- ' + case['id'] + ' '):  # Match the case at its exact module depth.
                    starts.append((index - len(case['module_path']), case['id']))  # Include the flat branch's module ancestors in its block.
        kept = output[:3]  # Preserve the immutable display header.
        for pos, (start, cid) in enumerate(starts):  # Keep source order across surviving case blocks.
            end = starts[pos + 1][0] if pos + 1 < len(starts) else len(output)  # Stop before the next block, or at the source end.
            if cid not in removed:  # Omission affects only the explicitly missing case.
                kept.extend(output[start:end])  # Preserve the entire surviving branch without re-rendering.
        output = kept  # Feed the filtered flat source to existing scalar feedback mapping.
    return '\n'.join(output) + '\n'
