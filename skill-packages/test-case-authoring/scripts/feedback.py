"""Baseline-bound feedback into shared authoring content, never formal assets."""
import copy
import html
import incremental_review

from authoring import _credential_guard, _digest, _cell
from clarification import start_grill, summarize, review, _validate_content, _apply_rule_decisions
from scoped_review import _render, _references, GROUPS, TECHNICAL_FIELDS
from review_expression import field_role, path_role  # 与展示共享准确框架/实际业务值职责。


PROTECTED = TECHNICAL_FIELDS | frozenset(('step_reference', 'module_path', 'data_refs', 'credential_ref',
    'review_status', 'rule_status', 'merge_status', 'execution_status', 'final_review',
    'review_history', 'rule_decisions', 'active_rule_decisions', 'rule_decision_history',
    'feedback_rule_history', 'supplied_content_confirmation'))


def _leaves(value, path=(), *, data=False, role=None):  # 仅准确声明的实际输入/产出解除框架键保护。
    role = role if path else 'data' if data else 'case'  # 每次从准确 owner 根开始解释类型。
    if isinstance(value, dict):
        for key, child in value.items():
            if role == 'literal' or key not in PROTECTED:  # 真正引用、来源和身份仍不可作为业务叶修改。
                yield from _leaves(child, (*path, key), data=data, role=field_role(role, key))  # 字面边界贯穿全部后代。
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _leaves(child, (*path, index), data=data, role=role)  # 列表索引保持原角色。
    elif isinstance(value, (str, int, float, bool)):  # Bind scalar types, including compact data values.
        yield path


def _get(value, path):
    for part in path:
        value = value[part]
    return value


def _set(value, path, replacement):
    target = _get(value, path[:-1])
    target[path[-1]] = copy.deepcopy(replacement)


def _initial(batch):
    if batch.get('kind') != 'scoped_review_copy':
        raise ValueError('Scoped review baseline required')
    base = batch['initial_copy_baseline']
    if _digest({k: base[k] for k in ('cases', 'data', 'selection', *(['step_definitions'] if 'step_definitions' in base else []))}) != base['copy_version']:
        raise ValueError('Initial displayed baseline changed')
    result = copy.deepcopy(batch)
    if 'step_definitions' in base:
        result['step_definitions'] = copy.deepcopy(base['step_definitions'])  # Restore the original display dependency snapshot.
    for key in ('cases', 'data', 'selection'):
        result[key] = copy.deepcopy(base[key])
    # The original generated version is captured when feedback is first read.
    result['content_version'] = batch.get('initial_display_version', batch['content_version'])
    result['questions'] = copy.deepcopy(batch.get('initial_display_questions', batch['questions']))
    return result


def _markdown_changes(batch, markdown, case_bindings=None, companion_base=None, source_catalog=None):  # Explicit export origin binds materialized links.
    if incremental_review.is_incremental(markdown):
        if batch.get('review_layout') != incremental_review.LAYOUT:
            raise ValueError('Incremental review layout does not match the saved candidate')
        if incremental_review.version_of(markdown) != batch['content_version']:
            raise ValueError('Submit feedback on the current review version: ' + batch['content_version'])
        return _markdown_layout_changes(batch, markdown, case_bindings, companion_base=companion_base,
                                        source_catalog=source_catalog)
    errors = []  # Each supported layout binds the same immutable semantic baseline.
    layouts = ((False, False, False), (False, True, False), (False, False, True), (False, True, True), (True, True, True))  # 已知旧生成布局，非任意兼容。
    for legacy, data_legacy, common_legacy, trailing_legacy, metadata_legacy in [(*layout, trailing, metadata) for metadata in (False, True) for trailing in (False, True) for layout in layouts]:  # 仅枚举本地曾发布的准确旧 metadata 布局。
        try:
            return _markdown_layout_changes(batch, markdown, case_bindings, legacy=legacy,
                data_legacy=data_legacy, common_legacy=common_legacy, companion_base=companion_base, source_catalog=source_catalog, trailing_legacy=trailing_legacy, metadata_legacy=metadata_legacy)  # 原始身份、digest 和来源门保持。
        except ValueError as error:
            errors.append(error)
    raise errors[0] from None  # Unknown layouts stay pending clarification.


def _markdown_layout_changes(batch, markdown, case_bindings=None, *, legacy=False, data_legacy=False, companion_base=None, common_legacy=False, source_catalog=None, trailing_legacy=False, metadata_legacy=False):  # 旧 metadata 只控制准确预期布局。
    """Read scalar edits of the generated hierarchy; reject structural ambiguity.

    Probe the actual renderer to bind each visible leaf to its existing business
    path. This mapping is derived, not another maintained content source.
    """
    initial = _initial(batch)
    incoming = markdown.splitlines()
    # Later review files still map through the immutable initial semantic
    # baseline in prepare_feedback, while their layout includes accepted history.
    incremental = incremental_review.is_incremental(markdown)
    current = incremental_review.version_of(markdown) == batch['content_version'] if incremental else (
        len(incoming) > 1 and incoming[1] == '- 版本：' + batch['content_version'])
    if current:
        initial = copy.deepcopy(batch)
        initial['cases'] = [c for c in initial['cases'] if c.get('feedback_disposition') != 'excluded_this_round']
    from aggregation import expand_feedback  # Restore source bindings before scalar interpretation.
    module_review = (any(line.startswith('  - 待评用例：') for line in incoming) if incremental
                     else len(incoming) > 2 and '；待评用例：' in incoming[2])
    metadata_bindings = {}  # 渲染器按准确用例根字段提供瞬时源行身份。
    flat = _render(initial, flat=True, reference_batch=source_catalog, _legacy_feedback=legacy, _data_legacy=data_legacy, _metadata_legacy=metadata_legacy, _metadata_bindings=metadata_bindings, module_review=module_review)['xmind_markdown']  # 同一布局用于初始投影和标量探针。
    original = flat.splitlines()
    if not incremental and companion_base is not None and len(incoming) >= 3:  # 旧稿只归一化真实生成的入口。
        from module_handoff import entrance
        if incoming[2] == original[2].partition('配套资料：')[0] + entrance(initial, base_path=companion_base):
            incoming[2] = original[2]
            markdown = '\n'.join(incoming) + '\n'
    if not incremental and incoming[:3] != original[:3]:
        raise ValueError('Markdown header/version must match initial display')
    def trusted_review(cid):  # 只有准确同版实际通过才兼容其更早 pending 视图。
        case = next(c for c in batch['cases'] if c['id'] == cid)  # owner 由已有稳定身份给定。
        approval = case.get('final_review', {})  # 不读取业务字符串或嵌套同名字段。
        return (case.get('review_status') == 'approved' and approval.get('approved') is True and
                approval.get('content_version') == batch['content_version'])  # 漂移或缺少真实通过均不归一化。

    def normalize_case(cid, node, template):  # 用准确源行字段对齐控制位置，不按全树文字消费业务叶。
        if not trusted_review(cid):  # 未审稿保留原先严格结构核对。
            return node  # 没有可信同版元数据豁免。
        wanted, actual = template['children'], node['children']  # 只处理该准确用例直属节点。
        roles = [next((metadata_bindings[origin][1] for origin in child['origins']
                       if metadata_bindings.get(origin, (None,))[0] == cid), None) for child in wanted]  # 嵌套业务叶无控制身份。
        if not any(roles):  # 新布局已外置审计；同文业务叶不参与归一化。
            return node  # 原始业务节点和偏移完整保留。
        from functools import lru_cache  # 可选历史行对齐只缓存本次准确用例。
        from aggregation import _shape  # 与后续结构比较使用同一树形契约。
        @lru_cache(None)
        def align(source, returned):  # 控制行可缺省，业务节点必须各自消耗一个实际节点。
            if source == len(wanted):  # 结束时任何额外节点仍是非法结构。
                return ((),) if returned == len(actual) else ()  # 不吞掉未知插入或业务行。
            role = roles[source]  # 由渲染器的实际源字段决定职责。
            choices = []  # 至多保留两个不同业务形状，明确报告歧义。
            if role in ('final_review', 'review_history'):  # 早于当前最终评审的原稿可能没有这些可信行。
                choices.extend(align(source + 1, returned))  # 只跳过已知源控制行。
            if returned < len(actual):  # 所有被消耗节点都来自原始返回。
                current = actual[returned]  # 子节点结构不借文本豁免。
                allowed = current['text'] == wanted[source]['text']  # 审计正文仍须逐字可信。
                if role == 'review_status':  # 仅这个准确直属源字段可接受更早状态。
                    allowed = current['text'] in ('最终评审：pending', '最终评审：approved')  # 业务同文不触发该分支。
                if not role or (not current['children'] and allowed):  # 业务节点由后续映射核对编辑，控制行只能是准确叶。
                    for tail in align(source + 1, returned + 1):  # 保留顺序及完整源 owner。
                        choices.append(((returned,) + tail) if not role else tail)  # 只去掉已绑定控制节点。
            unique = {}  # 同文重复但业务结果完全相同可复用；不同结果必须澄清。
            for indexes in choices:  # 不按标题或字段名字猜测用户编辑。
                shape = repr([_shape(actual[index]) for index in indexes])  # 业务子树完整参与判断。
                unique.setdefault(shape, indexes)  # 仅合并业务意义完全相同的对齐。
                if len(unique) > 1:  # 禁止指数枚举，也不任选一个业务编辑解释。
                    break  # 两个不同业务解释已经足以判定歧义。
            return tuple(unique.values())  # 缓存只在本次调用存活。
        choices = align(0, 0)  # 原始摘要验证由外层先完成。
        if len(choices) != 1:  # 缺失或多解均保守停止，不能吞掉真实编辑。
            raise ValueError('Review metadata owner is ambiguous; clarify the actual business edit')  # 明确回到澄清。
        return dict(node, children=[actual[index] for index in choices[0]])  # 业务叶与原始偏移不变。

    if case_bindings:  # 保留原先的全局原始摘要唯一性检查，不因局部树归一化而放宽身份。
        from aggregation import feedback_topics  # 读取未归一化的实际返回。
        raw_topics = feedback_topics('\n'.join(incoming))  # 不重写用户绑定的digest。
        if any(sum(topic['returned_digest'] == binding.get('returned_digest') for topic in raw_topics) != 1 for binding in case_bindings.values()):
            raise ValueError('Identity evidence does not uniquely bind the raw return')  # 同摘要多处出现仍需业务澄清。
    incoming = expand_feedback(initial, '\n'.join(original), '\n'.join(incoming), case_bindings,
        handoff=not legacy, common_legacy=common_legacy, source_catalog=source_catalog, _normalize_case=normalize_case, _trailing_legacy=trailing_legacy, companion_base=companion_base, module_review=module_review).splitlines()  # 原始摘要与资料位置先验证。

    return _decode_scalar_return(initial, original, incoming, metadata_bindings, trusted_review,
        source_catalog=source_catalog, legacy=legacy, data_legacy=data_legacy, metadata_legacy=metadata_legacy,
        module_review=module_review, incremental=incremental)


def _decode_scalar_return(initial, original, incoming, metadata_bindings, trusted_review, *,
                          source_catalog=None, legacy=False, data_legacy=False, metadata_legacy=False,
                          module_review=False, incremental=False, display_ids=None):
    source_starts = {}  # 原始 flat 块起点不随回传删除或保留范围移动。
    def blocks(lines):
        headers = []
        for index, line in enumerate(lines[3:], 3):
            for case in initial['cases']:
                prefix = '  ' * len(case['module_path']) + '- ' + case['id'] + ' '
                if line.startswith(prefix):
                    headers.append((index - len(case['module_path']), case['id']))
        if headers and headers[0][0] != 3:
            raise ValueError('Unrecognized Markdown content')
        if not headers and len(lines) > 3:
            raise ValueError('Unknown Markdown identity')
        result = {}
        for pos, (start, cid) in enumerate(headers):
            if cid in result:
                raise ValueError('Duplicate Markdown identity')
            end = headers[pos + 1][0] if pos + 1 < len(headers) else len(lines)
            source_starts.setdefault(cid, start)  # 首次读取准确原始布局，后续回传与探针复用本owner相对偏移。
            offsets = {origin + 3 - source_starts[cid] for origin, owner in metadata_bindings.items() if owner[0] == cid} if trusted_review(cid) else set()  # 整例删除不移动其他owner的源身份。
            result[cid] = [line for offset, line in enumerate(lines[start:end]) if offset not in offsets]  # 按准确源偏移移除控制行，保留同文业务叶。
        return result
    before, after = blocks(original), blocks(incoming)
    changes, missing = [], list(before.keys() - after.keys())
    changed_cases = {cid for cid in after if after[cid] != before[cid]}
    if not changed_cases:
        return changes, missing
    probe_ids = set(changed_cases)
    probe_data = {ref for case in initial['cases'] if case['id'] in changed_cases for ref in _references(case)}
    all_bindings = {}
    from restoration import feedback_projection as expanded  # Probe inherited visible business leaves without exposing source metadata.
    resolved = expanded(initial)
    # The original reader render has already checked eligibility. Probe just the
    # displayed owners of potentially edited fields, including shared inputs.
    probe_source = initial
    if display_ids is not None:
        affected_owners = [case for case in initial['cases'] if case['id'] in display_ids and
                           (case['id'] in changed_cases or _references(case) & probe_data)]
        needed_data = {ref for case in affected_owners for ref in _references(case)}
        probe_source = dict(initial, cases=affected_owners, data=[d for d in initial['data'] if d['id'] in needed_data])
    for collection in ('cases', 'data'):
        indexes = {owner['id']: pos for pos, owner in enumerate(probe_source[collection])}
        for item in resolved[collection]:
            if item['id'] not in (probe_ids if collection == 'cases' else probe_data):
                continue
            index = indexes[item['id']]
            for path in _leaves(item, data=collection == 'data'):  # data 根身份受保护，真实 value 内业务 id 可定位。
                probe = dict(probe_source)
                probe[collection] = list(probe_source[collection])
                probe[collection][index] = copy.deepcopy(probe[collection][index])
                marker = 'TCAFEEDBACKLEAFMARKER'
                if collection == 'cases':
                    from local_step_feedback import materialize  # Probe copy alone may contain an inline step.
                    materialize(probe, probe[collection][index], path)
                _set(probe[collection][index], path, marker)
                rendered = blocks(_render(probe, flat=True, reference_batch=source_catalog or initial,
                    _legacy_feedback=legacy, _expression_baseline=initial, _data_legacy=data_legacy,
                    _metadata_legacy=metadata_legacy, module_review=module_review,
                    _skip_preflight=display_ids is not None)['xmind_markdown'].splitlines())
                for cid, lines in rendered.items():
                    for line_index, line in enumerate(lines):
                        if marker in line:
                            if line.count(marker) != 1:
                                continue
                            prefix, suffix = line.split(marker)
                            all_bindings.setdefault((cid, line_index), []).append(
                                (collection, item['id'], list(path), prefix, suffix))
    from data_projection import decode_line  # Compound fields retain their own source paths.
    seen, decoded = {}, {}
    for cid, lines in after.items():
        if len(lines) != len(before[cid]):
            raise ValueError('Structural Markdown edit needs explicit chat interpretation')
        for index, (old, new) in enumerate(zip(before[cid], lines)):
            bindings = all_bindings.get((cid, index), [])
            if old != new and not bindings:
                raise ValueError('Unmapped Markdown edit')
            if not bindings:
                continue
            values = decode_line(old, new, bindings)  # Read unchanged occurrences too, to detect inconsistent shared edits.
            decoded[(cid, index)] = values
            originals = decode_line(old, old, bindings)
            for key, value in values.items():
                if value == originals[key]:
                    continue
                if key in seen and seen[key] != value:
                    raise ValueError('Repeated shared data edits disagree')
                seen[key] = value
    for key, value in seen.items():
        if any(key in values and values[key] != value for values in decoded.values()):
            raise ValueError('Repeated shared data edits disagree')
        original_value = _get(next(item for item in resolved[key[0]] if item['id'] == key[1]), key[2])
        from data_projection import typed_value  # Parse only against the exact source type.
        changes.append({'collection': key[0], 'id': key[1], 'path': list(key[2]), 'value': typed_value(value, original_value, display_encoded=not (legacy or metadata_legacy) and key[0] == 'data' and key[2] == ('value',), incremental=incremental)})  # 仅新版确切数据值能解码留空。
    return changes, missing


def _question(qid, cid, field, reason, checks):
    return {'id': qid, 'case_id': cid, 'field': field, 'reason': reason,
            'affected_checks': checks or ['scope-review'], 'target_paths': [], 'depends_on': [],
            'options': ['formal', 'provisional', 'deferred'],
            'recommendation': 'Confirm only the intended business change',
            'rationale': 'Changed content needs explicit business understanding and new final review',
            'example': 'SIMULATED: use the revised expected result; keep product check if provisional'}


def _data_owners(batch, data_ids, source_catalog):
    if not data_ids:
        return {}  # Local edits and unchanged legacy returns do not depend on hidden data ownership.
    from preparation_scope import scope_context
    context, unavailable = scope_context(batch, source_catalog, require_parent=True)
    if unavailable:
        raise ValueError('Actual complete parent required for shared-data impact')
    return {identity: [c['id'] for c in context['cases'] if identity in _references(c)]
        for identity in data_ids}  # All groups and current reference bindings, independent of operation exceptions.


def prepare_feedback(batch, channel, *, actual_reply, changes=None, markdown=None,
                     removed_case_ids=None, deletion_decisions=None, source_version=None, case_bindings=None,
                     clear_changes=False, questions=None, shared_change=None, companion_base=None, source_catalog=None, review_ids=None, shared_input=None, reader_order=None):  # Shared impact uses the same review boundary.
    """Locate proposed changes against first display and later accepted content."""
    _credential_guard([batch, actual_reply, changes, markdown, deletion_decisions, case_bindings])  # Binding replies follow the same credential boundary.
    if not actual_reply or channel not in ('chat', 'markdown'):
        raise ValueError('Actual feedback and supported channel required')
    from input_feedback import reader_ids, read_return
    displayed = reader_ids(markdown) if channel == 'markdown' and markdown else None
    if displayed is not None and review_ids is None:
        review_ids = [case['id'] for case in batch['cases'] if case.get('feedback_disposition') != 'excluded_this_round']
    if review_ids is not None and list(review_ids) != displayed:
        raise ValueError('评审范围 / 待评用例清单与原稿不符')
    reader = displayed is not None
    if shared_input and not reader:
        raise ValueError('共享 P0 输入变更需要实际评审稿')
    initial = batch if reader else _initial(batch)
    input_edits, input_impact = [], []
    shared_plan, shared_ids = None, []
    if shared_change is not None:
        from shared_step_feedback import prepare
        _credential_guard(shared_change)
        if channel != 'chat' or changes or markdown or removed_case_ids:
            raise ValueError('Shared source request must be explicit and separate from local edits')
        shared_plan, shared_ids = prepare(batch, shared_change)
    if source_version is not None and source_version != batch['content_version']:
        raise ValueError('Feedback source version is not current')
    current_source = source_version == batch['content_version']
    if channel == 'markdown':
        if changes or removed_case_ids or markdown is None:
            raise ValueError('Read Markdown itself, not a substituted interpretation')
        if reader:
            from input_feedback import ordered_candidate
            original_display = ordered_candidate(batch, reader_order) if reader_order else batch
            changes, input_edits, removed_case_ids = read_return(
                original_display, markdown, displayed, companion_base, source_catalog, case_bindings)
            from input_feedback import plan_impact
            input_edits, input_impact = plan_impact(batch, input_edits, shared_input, displayed, source_catalog)
        else:
            changes, removed_case_ids = _markdown_changes(batch, markdown, case_bindings, companion_base, source_catalog)
        current_source = (incremental_review.version_of(markdown) == batch['content_version']
                          if incremental_review.is_incremental(markdown)
                          else markdown.splitlines()[1] == '- 版本：' + batch['content_version'])
    normalized, affected = [], {e['call'][0] for e in input_edits}
    for change in changes or []:
        collection, identity, path = change['collection'], change['id'], change['path']
        if collection not in ('cases', 'data') or not path:  # 具体可编辑字段由同一 typed 叶枚举核对，不再次按路径键全树拦截。
            raise ValueError('Identity, reference and workflow changes need a new scoped baseline')
        from restoration import feedback_projection as expanded  # Read inherited business fields through the existing resolver.
        base = next((v for v in expanded(initial)[collection] if v['id'] == identity), None)
        current = next((v for v in expanded(batch)[collection] if v['id'] == identity), None)
        if base is None or current is None or tuple(path) not in set(_leaves(base, data=collection == 'data')):
            raise ValueError('Unknown displayed business field')
        old, accepted, new = _get(base, path), _get(current, path), change['value']
        if type(new) is not type(accepted) or (isinstance(new, str) and not new.strip() and not (collection == 'data' and path == ['value'])):  # Empty literal input is meaningful; names and prose still require text.
            raise ValueError('Business scalar must retain its source type and valid text')
        if type(new) is float:
            import math
            if not math.isfinite(new):
                raise ValueError('Finite business scalar required')
        if collection == 'cases' and len(path) == 3 and path[0] in GROUPS and path[2] == 'operation' and new.strip() == accepted.strip():  # Outer display whitespace does not alter business action.
            continue  # Keep valid references and approvals for a formatting-only return.
        if current_source and channel == 'chat' and change.get('before') != accepted:
            raise ValueError('Explicit current field value required for a revision')
        if accepted == new or (old == new and not current_source):
            continue
        if accepted != old and not current_source:
            raise ValueError('Feedback conflicts with an accepted later change; clarify')
        normalized.append(dict(change, before=old, accepted=accepted))
        affected.update([identity] if collection == 'cases' else
                        [c['id'] for c in batch['cases'] if identity in _references(c)])
    scope_impact = []  # A partial display cannot silently turn a shared edit into a local one.
    if normalized:  # Shared data has full impact in chat and file returns alike.
        from preparation_scope import operation_scopes
        changed_data = {c['id'] for c in normalized if c['collection'] == 'data'}
        data_owners = _data_owners(batch, changed_data, source_catalog)
        scopes, _ = operation_scopes(initial, source_catalog)
        touched = set()
        def record_impact(identity, owners):
            owners = sorted(set(owners))  # Operation exceptions and independent data consumers supply distinct ownership sets.
            if identity not in touched:
                touched.add(identity)
                scope_impact.append(dict(scope_id=identity, affected_case_ids=owners,
                    unshown_case_ids=sorted(set(owners) - {c['id'] for c in batch['cases']})))
                affected.update(owners)  # The same proposal binding and application guard cover every shared impact.
        for change in normalized:
            if change['collection'] == 'data':
                record_impact('data:' + change['id'], data_owners[change['id']])  # All groups and reference bindings, independent of common exclusions.
                continue
            if channel != 'markdown' or len(change['path']) < 3:  # Explicit case chat edits retain their local scope.
                continue
            group, index = change['path'][:2]
            if group not in ('common_preconditions', 'common_postconditions'):
                continue
            case = next(c for c in initial['cases'] if c['id'] == change['id'])
            for scope in scopes.get(change['id'], []):
                if scope['direction'] == ('pre' if group == 'common_preconditions' else 'post') and case[group][index]['id'] in scope['step_ids_by_case'][case['id']] and scope['id'] not in touched:
                    record_impact(scope['id'], set(scope['applicable_case_ids']) - set(scope['exception_case_ids']))  # Exclusions apply only to this operation.
    unique = {(c['collection'], c['id'], tuple(c['path'])) for c in normalized}
    if len(unique) != len(normalized):
        raise ValueError('Duplicate feedback field')
    deletions = []
    supplied_questions = copy.deepcopy(questions)  # Preserve explicit rule identities and dependencies.
    questions = []
    decisions = deletion_decisions or {}
    for cid in removed_case_ids or []:
        if cid not in {c['id'] for c in initial['cases']}:
            raise ValueError('Unshown case is not a deletion')
        decision = decisions.get(cid) or batch.get('deletion_decisions', {}).get(cid)
        if decision and (decision.get('action') not in ('exclude', 'deactivate', 'restore') or not decision.get('actual_reply')):
            raise ValueError('Explicit deletion meaning required')
        deletions.append({'case_id': cid, 'decision': copy.deepcopy(decision)})
        affected.add(cid)
        if not decision:
            q = _question('delete-' + cid, cid, 'deletion', 'Deletion intent is unclear', [])
            q['options'] = ['exclude this round', 'deactivate long term and retain record', 'restore']
            q['recommendation'] = 'Restore until maintenance intent is explicit'
            q['example'] = 'SIMULATED: exclude this round; keep the existing record active'
            questions.append(q)
    proposal_digest = _digest({'changes': normalized, 'deletions': deletions, **({'shared_scope_impact': scope_impact} if scope_impact else {})})
    reader_proposal = dict(review_ids=displayed, input_edits=input_edits, input_impact=input_impact) if reader else {}
    if reader:
        proposal_digest = _digest(dict(changes=normalized, deletions=deletions, **reader_proposal,
                                       **({'shared_scope_impact':scope_impact} if scope_impact else {})))
    if shared_plan:
        proposal_digest = _digest({'changes': normalized, 'deletions': deletions, 'shared_change': shared_plan})
        affected.update(shared_ids)
        for assessment in ([] if shared_plan['formatting_only'] else shared_plan['assessments']):
            questions.append(_question('shared-' + proposal_digest + '-' + assessment['case_id'], assessment['case_id'],
                'shared_definition', 'P0 change: ' + repr(shared_plan['replacement']['step']) + '; ' + assessment['disposition'] + ': ' + assessment['reason'], []))
        if shared_plan['source_present'] and not shared_plan['formatting_only']:
            questions.append(_question('shared-source-' + proposal_digest, shared_plan['replacement']['case_id'],
                'shared_definition', 'Review displayed P0 source update: ' + repr(shared_plan['replacement']['step']), []))
    binding_digest = _digest(case_bindings or {})  # Bind identity evidence separately from shared product proposals.
    scope_identity = {'batch_id': batch.get('id'), 'copy_version': (batch.get('initial_copy_baseline') or {}).get('copy_version', batch['content_version'])}
    question_proposal = _digest(dict(scope_identity, proposal=proposal_digest))
    for index, change in enumerate(normalized):
        if clear_changes:  # A clear textual proposal waits for summary, without redundant rule approval.
            if change.get('rule_id') and not supplied_questions:  # Changed rules need their affected decision graph.
                raise ValueError('Rule changes require focused clarification questions')  # Do not silently formalize a condition.
            continue  # Retain proposal for the existing summary confirmation.
        ids = [change['id']] if change['collection'] == 'cases' else [c['id'] for c in batch['cases'] if change['id'] in _references(c)]
        field = '/'.join(map(str, change['path']))
        if change['collection'] == 'data':
            field = 'data/' + change['id'] + '/' + field
        for cid in ids:
            questions.append(_question(f'feedback-{question_proposal}-{index}-{cid}', cid, field,
                                       'Review business change: ' + repr(change['before']) + ' → ' + repr(change['value']) +
                                       '; accepted current value: ' + repr(change['accepted']), []))
            if change.get('rule_id'):
                questions[-1]['rule_id'] = change['rule_id']
    for q in questions:
        if q['field'] == 'deletion':
            q['id'] += '-' + question_proposal
    for index, doubt in enumerate(batch['questions'] if supplied_questions is None else []):
        origin = doubt.get('feedback_origin') or _digest(dict(scope_identity, question={
            k: v for k, v in doubt.items() if k not in ('history', 'stale')}))
        q = _question('existing-' + origin, doubt['case_id'], doubt['field'], doubt['reason'], [])
        q['feedback_origin'] = origin
        if doubt.get('rule_id'):
            q['rule_id'] = doubt['rule_id']
        questions.append(q)
    if supplied_questions is not None:  # Preserve caller-enriched stable questions instead of rebuilding their graph.
        questions.extend(supplied_questions)  # start_grill validates omissions and dependencies.
        affected.update(q['case_id'] for q in supplied_questions if q.get('stale') or not q.get('history'))  # Reopened dependencies also need review.
    grill = start_grill(batch, questions)
    if reader:
        grill['feedback_proposal'] = proposal_digest
    return {**reader_proposal, 'batch': copy.deepcopy(batch), 'channel': channel, 'actual_reply': actual_reply,
            'base_version': batch['content_version'], 'changes': normalized, 'deletions': deletions, 'shared_change': shared_plan,
            'affected_case_ids': sorted(affected), 'proposal_digest': proposal_digest, 'shared_scope_impact': scope_impact,
            'grill': grill, 'case_bindings': copy.deepcopy(case_bindings or {}), 'binding_digest': binding_digest}  # Preserve actual identity clarification with the proposal.


def _views(batch, source_catalog=None):
    displayed = copy.deepcopy(batch)
    displayed['cases'] = [c for c in displayed['cases'] if c.get('feedback_disposition') != 'excluded_this_round']
    return _render(displayed, reference_batch=source_catalog)


def apply_feedback(pending, confirmation, deletion_decisions=None, *, source_catalog=None):
    """Apply one explicitly agreed summary atomically; all effects stay candidate-side."""
    _credential_guard([pending, confirmation, deletion_decisions])
    if any(item['unshown_case_ids'] for item in pending.get('shared_scope_impact', [])):
        raise ValueError('Shared definition affects unshown cases; expand the review scope before applying')  # Never partially apply a global definition.
    owners = _data_owners(pending['batch'], {c['id'] for c in pending['changes'] if c['collection'] == 'data'}, source_catalog)
    for consumers in owners.values():
        if set(consumers) - {c['id'] for c in pending['batch']['cases']}:
            raise ValueError('Shared data affects unshown cases; expand the review scope before applying')  # Older prepared proposals also recheck actual ownership.
        if set(consumers) - set(pending['affected_case_ids']):
            raise ValueError('Shared-data impact changed; prepare feedback again')  # Never silently broaden the agreed proposal.
    current = summarize(pending['grill'])['summary']
    if pending.get('binding_digest') != _digest(pending.get('case_bindings', {})):
        raise ValueError('Identity clarification changed after presentation')
    proposal = {'changes': pending['changes'], 'deletions': pending['deletions']}
    if pending.get('shared_scope_impact'):
        proposal['shared_scope_impact'] = pending['shared_scope_impact']  # Impact belongs to the exact proposal.
    if pending.get('shared_change'):
        proposal['shared_change'] = pending['shared_change']
    if 'review_ids' in pending:
        proposal.update({key: pending[key] for key in ('review_ids', 'input_edits', 'input_impact')})
    if pending.get('product_resolution'):
        proposal['product_resolution'] = pending['product_resolution']
        if pending['product_resolution'] != pending['batch'].get('product_reconciliation', {}).get('formal_conclusion'):
            raise ValueError('Product conclusion differs from the reconciled proposal')
    if pending['proposal_digest'] != _digest(proposal):
        raise ValueError('Feedback proposal changed after presentation')
    if (pending['grill'].get('summary') != current or confirmation.get('confirmed') is not True or
            not confirmation.get('actual_reply') or confirmation.get('summary_id') != current['id'] or
            pending['batch'] != pending['grill']['batch'] or pending['base_version'] != pending['batch']['content_version']):
        raise ValueError('Current feedback summary needs explicit agreement')
    if 'review_ids' in pending and current.get('feedback_proposal') != pending['proposal_digest']:
        raise ValueError('本次字段修改及其影响范围需要重新确认')
    batch = copy.deepcopy(pending['batch'])
    batch.setdefault('initial_display_version', pending['base_version'])
    batch.setdefault('initial_display_questions', copy.deepcopy(batch['questions']))
    blocked = set(current['blocked_cases'])
    affected = set(pending['affected_case_ids']) - blocked
    active_decisions = [d for d in current['decisions'] if not pending.get('persisted_feedback') or d['question_id'] in pending['decision_question_ids']]  # Reused old decisions are not new edits.
    if pending.get('persisted_feedback'):  # Pure legacy feedback retains its explicitly computed affected scope.
        affected.update(d['case_id'] for d in active_decisions if d['case_id'] not in blocked)  # Include actual changed rules and dependencies.
    from clarification import _collect_update  # Reuse normal summary conflict semantics.
    writes = {}  # Validate all effective changes before any candidate mutation.
    for change in pending['changes']:
        consumers = {change['id']} if change['collection'] == 'cases' else {c['id'] for c in batch['cases'] if change['id'] in _references(c)}
        if not consumers & blocked:  # Deferred prerequisites preserve their original content.
            index = next(i for i, item in enumerate(batch[change['collection']]) if item['id'] == change['id'])
            _collect_update(writes, dict(path=[change['collection'], index] + change['path'], value=change['value']))
    for decision in active_decisions:  # Include actual answer-derived updates in the same set.
        if decision['case_id'] not in blocked:
            for update in decision['reply'].get('updates', []):
                _collect_update(writes, update)
    for change in pending['changes']:
        consumers = {change['id']} if change['collection'] == 'cases' else {c['id'] for c in batch['cases'] if change['id'] in _references(c)}
        if consumers & blocked:
            continue
        target = next(v for v in batch[change['collection']] if v['id'] == change['id'])
        from local_step_feedback import materialize, materialize_data, refresh  # Copies never touch shared definitions.
        data_consumers = materialize_data(batch, change['id']) if change['collection'] == 'data' else []
        if change['collection'] == 'cases':
            materialize(batch, target, change['path'])  # Persist a full step, never a field override.
        _set(target, change['path'], change['value'])
        for consumer in data_consumers:
            refresh(batch, consumer)  # Bind complete revised steps without rewriting source snapshots.
        parent = _get(target, change['path'][:-1])
        if change['collection'] == 'data' and 'source' in target:
            target['source'] = 'user_decision'  # 只更新 data 根溯源，不篡改实际 value.source。
        elif change['collection'] == 'cases' and path_role(change['path'][:-1]) in ('step', 'claim') and isinstance(parent, dict) and 'source' in parent:  # 仅准确框架步骤或声明 claim 更新来源。
            parent['source'] = 'user_decision'  # literal 输入/产出的 source 完整保持真实业务值。
        if change['collection'] == 'cases':
            refresh(batch, target)  # Bind the revised order and endpoint before validation.
    from clarification import _patch  # Use the same validated business update seam as normal clarification.
    for decision in active_decisions:  # Completed focused answers join the centralized write only now.
        if decision['case_id'] not in blocked:  # Deferred dependencies remain unchanged.
            for update in decision['reply'].get('updates', []):  # Only declared question targets passed respond.
                from local_step_feedback import materialize, refresh  # Actual answers use the same local copy rule.
                path = update['path']
                from local_step_feedback import materialize_data
                data_consumers = materialize_data(batch, batch['data'][path[1]]['id']) if len(path) > 2 and path[0] == 'data' else []
                if len(path) > 2 and path[0] == 'cases':
                    materialize(batch, batch['cases'][path[1]], path[2:])
                _patch(batch, update)  # Candidate-only update with existing protected-field guards.
                for consumer in data_consumers:
                    refresh(batch, consumer)
                if len(path) > 2 and path[0] == 'cases':
                    refresh(batch, batch['cases'][path[1]])
                affected.add(decision['case_id'])  # Complete revised case must return to review.
    if pending.get('input_edits'):
        from input_feedback import apply_inputs
        if blocked & {e['call'][0] for e in pending['input_edits']}:
            raise ValueError('字段修改涉及已延期用例，请重新核对影响范围')
        apply_inputs(batch, pending['input_edits'], source_catalog)
    for deletion in pending['deletions']:
        cid = deletion['case_id']
        if cid in blocked:
            continue
        reply = next((d['reply'] for d in current['decisions'] if d['case_id'] == cid and d['field'] == 'deletion'), {})
        answered = {'action': reply.get('deletion_action'), 'actual_reply': reply.get('actual_reply')}
        decision = deletion['decision'] or answered
        if deletion_decisions and cid in deletion_decisions and deletion_decisions[cid] != decision:
            raise ValueError('Deletion decision must match the agreed summary')
        if not decision or decision.get('action') not in ('exclude', 'deactivate', 'restore') or not decision.get('actual_reply'):
            raise ValueError('Resolve deletion as exclude, deactivate or restore')
        batch.setdefault('deletion_decisions', {})[cid] = copy.deepcopy(decision)
        case = next(c for c in batch['cases'] if c['id'] == cid)
        if decision['action'] == 'deactivate':
            case['maintenance_action'] = 'deactivate'
        elif decision['action'] == 'exclude':
            case['feedback_disposition'] = 'excluded_this_round'
        else:
            case.pop('feedback_disposition', None)
    if pending.get('shared_change'):
        from shared_step_feedback import apply as apply_shared
        applied = apply_shared(batch, pending['shared_change'], blocked)
        if not applied:
            affected.difference_update(pending['affected_case_ids'])
            blocked.update(pending['affected_case_ids'])  # A deferred shared proposal cannot masquerade as applied.
    _validate_content(batch)
    batch['data_version'] = _digest(batch['data'])
    for case in batch['cases']:
        if case['id'] not in affected | blocked:
            continue
        case['data_version'] = batch['data_version']
        case['review_status'] = 'pending'
        if 'final_review' in case:
            case.setdefault('review_history', []).append(case.pop('final_review'))
        decisions = [d for d in active_decisions if d['case_id'] == case['id']]  # Preserve unrelated provisional decisions without replaying them.
        product = pending.get('product_resolution')
        _apply_rule_decisions(case, decisions, blocked=case['id'] in blocked, product=product)
        case.setdefault('feedback_rule_history', []).extend(copy.deepcopy(decisions))
        case['semantic_version'] = _digest({k: v for k, v in case.items() if k != 'semantic_version'})
        if pending.get('shared_change') and case['id'] == pending['shared_change']['replacement']['case_id'] and case['id'] not in blocked:
            case['semantic_version'] = pending['shared_change']['replacement']['semantic_version']  # Source and reviewed definition share the same declared version.
    for check in batch.get('coverage', []):
        from restoration import feedback_projection as expanded  # Feedback summaries share the exact review resolver.
        linked = [c for c in expanded(batch)['cases'] if c['id'] in check.get('case_ids', [])]
        if not any(c['id'] in affected for c in linked):
            continue
        check.setdefault('history', []).append({k: copy.deepcopy(v) for k, v in check.items() if k != 'history'})
        check['status'] = 'pending_review'
        check['expected_summary'] = '; '.join(claim['text'] for c in linked for group in GROUPS for s in c.get(group, []) for claim in s['expected'])
        check['verification_summary'] = '; '.join(claim['text'] for c in linked for group in GROUPS for s in c.get(group, []) for claim in s['verification'])
        check['data_refs'] = sorted(set().union(*[_references(c) for c in linked]))
    batch.setdefault('feedback_history', []).append({'channel': pending['channel'], 'actual_reply': pending['actual_reply'],
        'summary': current, 'confirmation': confirmation, 'changes': pending['changes'], 'deletions': pending['deletions']})
    if 'review_ids' in pending:
        batch['feedback_history'][-1].update({k:copy.deepcopy(pending[k]) for k in ('review_ids','input_edits','input_impact')})
    if pending.get('returned_source'):
        batch['feedback_history'][-1]['returned_source'] = copy.deepcopy(pending['returned_source'])
    if batch.get('review_layout') == incremental_review.LAYOUT:
        batch['feedback_history'][-1]['source_version'] = pending['base_version']  # 任一渠道保存的旧稿版本均可回查。
    if pending.get('shared_change'):
        batch['feedback_history'][-1]['shared_change'] = copy.deepcopy(pending['shared_change'])
    if pending.get('case_bindings'):  # Empty optional metadata must not change historical semantic versions.
        batch['feedback_history'][-1]['case_bindings'] = copy.deepcopy(pending['case_bindings'])  # Retain actual identity evidence only.
    # Keep enriched original doubts and their actual answer history so the
    # existing grill can reuse identical decisions on later feedback rounds.
    batch['questions'] = [copy.deepcopy(q) for q in pending['grill']['questions']
                          if pending.get('persisted_feedback') or q['id'].startswith('existing-')]  # Same-task feedback retains the complete stable graph.
    if 'review_ids' in pending:
        from input_feedback import retire_changed_segments
        retired = retire_changed_segments(batch, affected, source_catalog)
        if retired:
            batch['feedback_history'][-1]['retired_review_segments'] = retired
    batch['content_version'] = _digest({k: v for k, v in batch.items() if k != 'content_version'})
    if 'review_ids' in pending:
        from source_preparation import render_selection
        result = render_selection(batch, pending['review_ids'], source_catalog=source_catalog)
        result['review_ids'] = list(pending['review_ids'])
    else:
        result = _views(batch, source_catalog)
    result['batch'] = batch
    result['changes'] = copy.deepcopy(pending['changes'])
    result['review_notes'] = 'Candidate feedback only; final review required. Formal source synchronization and execution remain pending.\n' + str(batch.get('coverage', []))
    session = copy.deepcopy(pending['grill'])
    session.update(batch=copy.deepcopy(batch), summary_confirmation=copy.deepcopy(confirmation),
                   applied_content_version=batch['content_version'])
    result['review_session'] = session
    return result


def review_feedback(result, final_review, *, source_catalog=None):
    """Use the existing batch final-review gate for the complete revised content."""
    if result['batch'] != result['review_session']['batch']:
        raise ValueError('Revised content changed after summary application')
    selected = final_review.get('case_ids', [])
    if any(c.get('feedback_disposition') == 'excluded_this_round' for c in result['batch']['cases'] if c['id'] in selected):
        raise ValueError('Excluded content is outside this round review')
    session = review(result['review_session'], final_review, source_catalog=source_catalog)
    updated = copy.deepcopy(result)
    if 'review_ids' in result:
        from source_preparation import render_selection
        updated.update(render_selection(session['batch'], result['review_ids'], source_catalog=source_catalog))
    else:
        updated.update(_views(session['batch'], source_catalog))
    updated['batch'] = session['batch']
    updated['review_session'] = session
    updated['next_step'] = 'Candidate review recorded. Formal mapping remains pending; user starts execution or merge separately.'
    return updated
