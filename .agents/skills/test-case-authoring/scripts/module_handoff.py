"""Generated module instructions; original candidate remains the lossless authority."""
TITLE = '资料与Agent交接说明'
PROCESS_FIELDS = ('review_status', 'merge_status', 'execution_status')  # Rule identity remains visible in business prose.
CASE_AGENT_FIELDS = ('priority_basis', 'priority_factors', 'maintenance_action', 'rule_status', 'review_history', 'final_review', 'supplied_content_confirmation')  # 已知编写及审计职责，不作为业务操作输入。

NOTE_LABELS = {  # Display vocabulary is local to Agent notes, never editable business projections.
    'authoring_status': '编写状态', 'source_reference': '来源引用', 'source_ref': '来源引用',
    'execution_boundary': '执行边界', 'submission_policy': '提交策略',
    'maintenance_action': '维护动作', 'action': '变更动作', 'reason': '变更原因',
    'reuse_policy': '复用条件', 'invalidation_action': '失效后的处理', 'validity': '有效性',
    'input': '输入', 'inputs': '输入', 'value': '值', 'output': '产出', 'outputs': '产出',
    'object_ref': '业务对象', 'data_refs': '数据引用', 'credential_ref': '凭据引用',
    'review_status': '评审状态', 'merge_status': '合并状态', 'execution_status': '执行状态',
}
NOTE_ENUMS = {  # Only documented control fields may interpret these exact values.
    'authoring_status': {'candidate': '候选'},
    'execution_boundary': {'authoring_only': '仅编写'},
    'submission_policy': {'review_required': '需要评审'},
    'maintenance_action': {'add': '新增', 'modify': '修改', 'reuse': '复用', 'deactivate': '停用'},
    'action': {'add': '新增', 'modify': '修改', 'reuse': '复用', 'related': '相关', 'deactivate': '停用'},
    'review_status': {'pending': '待评审', 'approved': '已通过'},
    'merge_status': {'not_merged': '未合并'}, 'execution_status': {'not_executed': '未执行', 'not_run': '未执行'},  # 两种现有候选枚举含义一致。
}


def _note_value(path, value):
    text = str(value) if value is not None else '待核对'  # Preserve original scalar text and unknown values.
    meaning = NOTE_ENUMS.get(path[0], {}).get(value) if len(path) == 1 and isinstance(value, str) else None  # Only direct documented control fields receive display translations.
    return meaning + '（原值：' + text + '）' if meaning else text  # Nested actual inputs never become control enums.


def _handoff_lines(value, path=(), labels=()):
    if isinstance(value, dict):
        return [line for key, child in value.items() for line in _handoff_lines(child, (*path, key), (*labels, NOTE_LABELS[key] + '（' + key + '）' if key in NOTE_LABELS else key))]  # Unknown keys retain exact spelling.
    if isinstance(value, list):
        return [line for child in value for line in _handoff_lines(child, path, labels)]  # List order is authoritative.
    return [' / '.join(labels) + '：' + _note_value(path, value)]  # This projection cannot write back into a candidate.


def module_notes(batch):
    from step_reuse import resolve_step  # Share checked full-step resolution with business projections.
    from scoped_review import _business_lines  # Preserve the shared business-safe leaf projection.
    result = {}  # Complete semantic paths prevent same-name module collisions.
    for case in batch['cases']:
        notes = []  # Only direct owners create a branch.
        heading = case.get('title', '待核对用例')  # Stable English identities stay internal.
        from review_projection import technical_notes
        lines = technical_notes(batch, case, value_formatter=_note_value, labels=NOTE_LABELS)  # Explicit assessed governance retains owner/field applicability.
        from review_projection import active_records  # 已知控制说明的 readable 评估在说明保留，不重新污染业务树。
        for item in active_records(batch, 'cases', case):
            if item['disposition'] == 'readable' and item['path'][0] in CASE_AGENT_FIELDS + PROCESS_FIELDS:
                lines.append('状态与编写说明：' + item['text'] + '；原字段：/' + '/'.join(map(str, item['path'])))  # 归纳不改变原确认或评审状态。
        def source_notes(value, scope):  # 只读取已知 claim/data/step 根的来源，不进入真实 value。
            if isinstance(value, list):
                for ordinal, child in enumerate(value, 1):
                    source_notes(child, scope + '/' + str(ordinal))
            elif isinstance(value, dict) and value.get('source_ref'):
                lines.append('资料来源：' + str(value['source_ref']) + '；适用：' + scope)  # 原候选保持完整来源与行号。
        for field, claims in case.get('context', {}).items():
            source_notes(claims, '业务条件/' + field)  # context 的声明 claim 才是来源对象。
        refs = {ref for group in ('common_preconditions', 'special_preconditions', 'steps', 'special_postconditions', 'common_postconditions') for step in case.get(group, []) for ref in step.get('data_refs', [])}
        for data in batch['data']:
            if data['id'] in refs:
                source_notes(data, '数据/' + data['id'])  # 同名 value.source_ref 仍属于实际输入。
        for field in CASE_AGENT_FIELDS + PROCESS_FIELDS:
            if field not in case:
                continue
            if field in ('final_review', 'review_history', 'supplied_content_confirmation'):  # 原话单处保留，说明只给精确定位。
                records = case[field] if isinstance(case[field], list) else [case[field]]
                for ordinal, record in enumerate(records):
                    location = '/' + field + ('/' + str(ordinal) if isinstance(case[field], list) else '')
                    ref = record.get('qa_ref') or record.get('source_ref') if isinstance(record, dict) else None
                    lines.append('评审与确认记录：' + (str(ref) if ref else '见本用例候选位置 ' + location) + '；原话与适用版本保留在原记录')  # 不复制长 QA 形成第二权威。
            elif field in ('priority_basis', 'priority_factors') and case.get('priority_factors'):
                lines.extend(_handoff_lines({field: case[field]}))  # 具体风险理由在说明可查；默认状态只读原候选。
        for field in ('active_rule_decisions', 'rule_decisions', 'rule_decision_history', 'feedback_rule_history'):
            for rule in case.get(field, []):
                reply = rule.get('reply', {})
                ref = reply.get('qa_ref') or reply.get('source_ref')
                if ref:
                    lines.append('规则答复来源：' + str(ref) + '；内容及历史以原记录为准')  # 规则意义仍在业务条件，原话只链接。
        # Workflow state remains exclusively in the candidate authority.
        def handoff(value):
            return ([] if value.get('source_ref') or value.get('shared_section') else _handoff_lines({k: v for k, v in value.items() if k != 'document_ref'})) if isinstance(value, dict) else ['执行约束：须读取当前候选的技术交接原文后执行'] if value else []  # Legacy opaque text may embed stable machine identities.
        for group in ('common_preconditions', 'special_preconditions', 'steps', 'special_postconditions', 'common_postconditions'):
            for index, step in enumerate(case.get(group, []), 1):
                source_notes(step, group + '/' + str(index))  # 已知步骤来源不作为参数输入。
                source_notes(step.get('expected', []), group + '/' + str(index) + '/预期')
                source_notes(step.get('verification', []), group + '/' + str(index) + '/独立检查')
                step = resolve_step(batch, case, group, step)[0]  # Preserve current owner, group and ordinal while restoring source instructions.
                if step.get('source') or step.get('lines'):
                    label = {'recording': '录制资料', 'handwritten': '手写资料', 'prd': '需求资料'}.get(step.get('source'), '候选绑定资料')  # Unknown source identifiers stay internal.
                    location = '—'.join(str(n) for n in step.get('lines', []) if isinstance(n, int))  # Numeric source locations carry no credentials.
                    lines.append({'common_preconditions': '公共前置操作', 'special_preconditions': '特殊前置操作', 'steps': '测试步骤', 'special_postconditions': '特殊后置操作', 'common_postconditions': '公共后置操作'}[group] + ' ' + str(index) + '：' + label + ('，行 ' + location if location else '；定位见当前候选') + '；修改须重新核对')  # Same-version candidate retains complete original provenance.
                operation = _business_lines(step.get('operation', '待核对操作'), batch=batch)  # Render only the business operation, without internal step identity.
                scope = {'common_preconditions': '公共前置操作', 'special_preconditions': '特殊前置操作', 'steps': '测试步骤', 'special_postconditions': '特殊后置操作', 'common_postconditions': '公共后置操作'}[group] + ' ' + str(index) + '（' + '；'.join(line.removeprefix('操作：') for line in operation) + '）'  # Group and ordinal bind even sourceless steps.
                lines.extend(scope + '：' + note for note in dict.fromkeys(handoff(step.get('technical_handoff', {}))))  # Deduplicate only inside the same step scope.
        lines.extend(handoff(case.get('technical_handoff', {})))  # General reuse and invalidation instructions live here.
        if lines:
            lines.extend(_handoff_lines({field: case[field] for field in PROCESS_FIELDS if field in case}))  # 同版说明追溯当前控制状态；没有必要说明时不为状态新建文件。
            result.setdefault(tuple(case['module_path']), []).append((heading, list(dict.fromkeys(lines))))  # Deduplicate instructions only within their applicability.
    return result


def _filename(path):
    import hashlib
    import json
    return hashlib.sha256(json.dumps(list(path), ensure_ascii=False).encode()).hexdigest()[:20] + '.md'  # Full module identity, independent of batch/version.


def _source_refs(batch):
    refs = []
    for case in batch['cases']:
        for value in [case.get('technical_handoff', {}), *[s.get('technical_handoff', {}) for g in ('common_preconditions', 'special_preconditions', 'steps', 'special_postconditions', 'common_postconditions') for s in case.get(g, [])]]:
            if isinstance(value, dict) and value.get('shared_section'):
                shared = value['shared_section']
                if not all(shared.get(k) for k in ('source_ref', 'section', 'content', 'review_reply')):
                    raise ValueError('Shared content requires reviewed ownership of an existing document section')
                refs.append(shared['source_ref'] + '#' + shared['section'])
            if isinstance(value, dict) and value.get('source_ref'):
                refs.append(value['source_ref'])  # Existing authoritative material is linked directly.
    return list(dict.fromkeys(refs))


def document_ref(batch, path):
    refs = {c.get('technical_handoff', {}).get('document_ref') for c in batch['cases'] if tuple(c['module_path']) == tuple(path) and isinstance(c.get('technical_handoff', {}), dict)} - {None}
    if len(refs) > 1:
        raise ValueError('One module must retain one document owner')
    return next(iter(refs)) if refs else '../agent-notes/' + _filename(path)  # Optional existing owner supports unrelated batch directories.


def companion_links(batch, *, base_path=None, with_filenames=False):
    import re
    from pathlib import Path
    from urllib.parse import quote, unquote, urlsplit
    def link(ref):  # Resolve known local references only; do not rewrite remote source ownership.
        if base_path is None or '://' in ref:
            return quote(ref, safe='/:#')
        local, separator, fragment = ref.partition('#')
        return (Path(base_path) / local).resolve().as_uri() + (separator + quote(fragment, safe='') if separator else '')
    def entry(label, ref):
        if with_filenames:
            path = urlsplit(ref).path.replace('\\', '/')
            filename = Path(unquote(path)).name or ref
            label += ' · ' + re.sub(r'[\[\]\r\n]', ' ', filename)  # 路径字符避免改变链接标签边界。
        return '[' + label + '](' + link(ref) + ')'
    links = [entry('Agent说明 ' + ' / '.join(path), document_ref(batch, path)) for path in module_notes(batch)]
    links.extend(entry('已有技术来源', ref) for ref in _source_refs(batch))
    return links


def entrance(batch, *, base_path=None, with_filenames=False):  # 保留旧稿首的连接形式。
    links = companion_links(batch, base_path=base_path, with_filenames=with_filenames)
    return '配套资料：' + ('；'.join(links) if links else '无必要技术说明')


def _case_markers(case_id):
    import hashlib
    import re
    key = hashlib.sha256(case_id.encode()).hexdigest()  # Preserve the persisted case identity across all lifecycle paths.
    begin, end = '<!-- case:' + key + ' -->', '<!-- /case:' + key + ' -->'  # One protocol owns both section boundaries.
    return begin, end, re.escape(begin) + r'.*?' + re.escape(end)  # Literal boundaries prevent regex interpretation of markers.


def write_artifacts(result, output, *, source_catalog=None, review_ids=None, reader_stage=None):
    """Save technical documents and the business tree; sibling batch folders share notes."""
    from pathlib import Path
    import re
    import json
    original = result['batch']  # Candidate remains the sole state/history authority.
    if review_ids is None:
        review_ids = result.get('review_ids')  # An agreed reader return retains its original selection.
    from authoring import _credential_guard
    _credential_guard([original, source_catalog])
    import os
    output = Path(os.path.abspath(output))
    from restoration import preflight
    checked = preflight(original, source_catalog=source_catalog, base_path=output, require_current_sources=True)  # Re-read current sources before planning any notes mutation.
    previous_blockers = result.get('blocked_case_ids', [])  # A corrected source restores the previously hidden scope.
    result.update({k: v for k, v in checked.items() if k != 'complete_batch'})
    batch = dict(original, cases=[c for c in original['cases'] if c['id'] in checked['ready_case_ids']])  # Only fully restored selected owners may update or retire notes.
    if review_ids is None and (checked['blockers'] or previous_blockers):
        from authoring import render_batch
        if batch.get('kind') == 'scoped_review_copy':
            from scoped_review import render_review_batch
            rendered = render_review_batch(original, source_catalog=source_catalog)  # Retain pending source operations and valid definitions; unrelated reference blockers stay filtered.
        else:
            rendered = render_batch(batch)
        result.update(xmind_markdown=rendered['xmind_markdown'], human_view=rendered['human_view'])  # Review may show incomplete scope actions; only ready cases below update notes.
    plans = []
    for ref in _source_refs(batch):
        if '://' not in ref and not (output / ref.split('#')[0]).resolve().is_file():
            raise ValueError('Existing technical source does not exist')  # Never publish a phantom local link.
    for path in dict.fromkeys(tuple(c['module_path']) for c in batch['cases']):  # Include ready owners whose last note was removed.
        target = (output / document_ref(batch, path)).resolve()
        header = '# Agent说明：' + ' / '.join(path) + '\n'  # Only this exact generated shell may be removed.
        content = target.read_text(encoding='utf-8') if target.exists() else header
        owners = [c for c in batch['cases'] if tuple(c['module_path']) == path]
        for case in owners:  # Stable identity permits duplicate business titles.
            begin, end, pattern = _case_markers(case['id'])  # Retirement and replacement use the same owner boundaries.
            own_notes = module_notes(dict(batch, cases=[case])).get(path, [])
            if not own_notes:
                content = re.sub(pattern, '', content, flags=re.S)  # Preserve manual text and every unselected/blocked section.
                continue
            heading, lines = own_notes[0]
            position = next(i for i, owner in enumerate(original['cases']) if owner is case)  # Position in the complete persisted authority, including blocked owners.
            candidate_path = (output / 'candidate.json').resolve()
            candidate_ref = candidate_path.as_uri()
            if review_ids is not None and candidate_path.drive == target.drive:
                from urllib.parse import quote
                candidate_ref = quote(Path(os.path.relpath(candidate_path, target.parent)).as_posix(), safe='/')
            binding = '候选来源：[' + case['id'] + '](' + candidate_ref + '#/cases/' + str(position) + ')；内容版本（content_version）：' + str(original.get('content_version', '未指定'))  # Bind the displayed section to its complete original candidate position.
            lines = [binding, '版本映射：语义 ' + str(case.get('semantic_version', '未指定')) + '；数据 ' + str(case.get('data_version', '未指定')), *lines]  # Retain per-case semantic and data versions beside the source.
            section = begin + '\n## ' + heading + '\n' + '\n'.join('- ' + line for line in lines) + '\n' + end
            content = re.sub(pattern, lambda _: section, content, flags=re.S) if begin in content else content.rstrip() + '\n\n' + section + '\n'
        if content.strip() != header.strip() or target.exists():  # Never create an empty document.
            plans.append((target, None if content.strip() == header.strip() else content))  # Preserve other cases during partial later batches.
    for case in batch['cases']:
        shared = case.get('technical_handoff', {}).get('shared_section')
        if shared:
            target = (output / shared['source_ref']).resolve()  # Reviewed ownership never defaults to a first module.
            if not target.is_file():
                raise ValueError('Shared owner must be an existing document')
            content = next((text for path, text in plans if path.resolve() == target), target.read_text(encoding='utf-8')) or ''  # A shared section keeps its chosen existing owner alive.
            begin, end = '<!-- shared:' + shared['section'] + ' -->', '<!-- /shared:' + shared['section'] + ' -->'
            section = begin + '\n## ' + shared['section'] + '\n' + shared['content'] + '\n' + end
            pattern = re.escape(begin) + r'.*?' + re.escape(end)
            content = re.sub(pattern, lambda _: section, content, flags=re.S) if begin in content else content.rstrip() + '\n\n' + section + '\n'
            plans = [(path, text) for path, text in plans if path.resolve() != target] + [(target, content)]
    candidate = output / 'candidate.json'  # Materialize the same complete authority before publishing links.
    previous = json.loads(candidate.read_text(encoding='utf-8-sig')) if candidate.exists() else None  # Read before any artifact writes.
    if previous is not None and previous != original:
        for owner in previous.get('cases', []):  # Include omitted modules, not just this batch's plans.
            old_target = (output / document_ref(previous, owner['module_path'])).resolve()
            if not old_target.exists():
                continue
            replaced = any(c['id'] == owner['id'] and (output / document_ref(batch, c['module_path'])).resolve() == old_target for c in batch['cases'])  # A restored same-owner replacement permits this candidate update.
            content = next((text for path, text in plans if path == old_target), old_target.read_text(encoding='utf-8')) or ''  # Inspect planned content before deciding whether the old authority is still needed.
            marker, _, _ = _case_markers(owner['id'])  # Retained-source protection shares the persisted section identity.
            if not replaced and marker in content:
                raise ValueError('A retained section still requires this candidate; use a new sibling output directory')  # Preserve every old artifact before refusing source destruction.
    if previous != original:
        temporary = candidate.with_suffix('.tmp')
        temporary.write_text(json.dumps(original, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')  # Persist the full authority, including blocked owners, before publishing links.
        temporary.replace(candidate)  # Preserve exact existing bytes when the original candidate is already present.
    for target, content in plans:
        if content is None:
            target.unlink(missing_ok=True)  # Retire only the now-empty generated shell.
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_suffix('.tmp')
        temporary.write_text(content, encoding='utf-8')
        temporary.replace(target)  # No per-batch copy or append-only status history.
    from incremental_review import LAYOUT
    selected_ids = review_ids if review_ids is not None else [c['id'] for c in original['cases']]
    blocked = {row['case_id'] for row in checked['blockers'] if not row.get('scope_only')}
    from reader_delivery import visible_review_ids
    visible_ids = visible_review_ids(original, selected_ids, blocked)
    if reader_stage or review_ids is not None or any(c.get('feedback_disposition') == 'excluded_this_round' for c in original['cases']):
        from source_preparation import render_selection
        view = render_selection(original, selected_ids, blocked_ids=blocked, source_catalog=source_catalog,
                                companion_base=output if original.get('review_layout') == LAYOUT else None)
        result.update(xmind_markdown=view['xmind_markdown'], human_view=view['human_view'])
    elif original.get('review_layout') == LAYOUT:
        from scoped_review import render_review_batch
        result['xmind_markdown'] = render_review_batch(
            original, source_catalog=source_catalog, companion_base=output)['xmind_markdown']
    else:
        lines = result['xmind_markdown'].splitlines()  # 历史布局的配套入口保持原位置。
        lines[2] = lines[2].partition('配套资料：')[0] + entrance(batch, base_path=output)
        result['xmind_markdown'] = '\n'.join(lines) + '\n'
    from reader_delivery import write_agent_index
    stage = reader_stage or ('premerge' if original.get('kind') == 'scoped_review_copy'
                             else 'full' if len(selected_ids) == len(original['cases']) else 'draft')
    write_agent_index(output, original, visible_ids, stage, source_catalog, checked['blockers'])
    (output / 'xmind.md').write_text(result['xmind_markdown'], encoding='utf-8')
    for target, content in plans:
        if (target.exists() if content is None else target.read_text(encoding='utf-8') != content):
            raise ValueError('Agent document readback failed')
    result['artifact_status'] = 'materialized'  # Pure render/build stays planned.
    return [str(target) for target, content in plans if content is not None]
