"""Read-only full-catalog selection; review copies never replace their source."""
import argparse
import copy
import json
from pathlib import Path
import sys

from authoring import _credential_guard, _digest, _cell
from data_projection import data_lines  # Shared lossless object/value projection.
from review_expression import title, independent_checks, business_value, field_role  # 来源类型与实际业务字面值分开投影。
from incremental_review import LAYOUT


GROUPS = ('common_preconditions', 'special_preconditions', 'steps', 'special_postconditions', 'common_postconditions')


TECHNICAL_FIELDS = frozenset(('review_segment', 'reuse_target_digest', 'reuse_assessments', 'id', 'source', 'lines', 'basis', 'provenance',
    'semantic_version', 'data_version', 'assertion_id', 'assertion_ids', 'operator',
    'build_fingerprint', 'sha256', 'content_hash', 'summary_id', 'content_version', 'technical_handoff', 'business_group', 'rule_id', 'question_id'))  # Stable technical identities remain internal, including historical rule references.
BUSINESS_LABELS = {
    'data_preparation': '准备条件',  # 真实隔离及准备条件仍在正文可见。
    'context': '业务条件', 'role': '角色', 'initial_state': '初始状态',
    'priority': '优先级', 'priority_basis': '分级依据', 'maintenance_action': '维护建议',
    'rule_status': '规则确认', 'review_status': '最终评审', 'merge_status': '合并状态',
    'execution_status': '执行状态', 'dependencies': '关联用例', 'case_id': '用例名称', 'case_ids': '用例名称',
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


def _business_lines(value, prefix='', batch=None, *, _legacy=False, _literal=False):  # 实际输入子树不解释成测试关系或控制元数据。
    """One labelled business projection used by both review formats.

    Unknown extensions are flattened to labelled leaves, never opaque JSON.
    Technical provenance stays in candidate/baseline records instead of prose.
    """
    if isinstance(value, dict):
        lines = []
        for key, child in value.items():
            if _legacy and key in TECHNICAL_FIELDS:  # 旧稿按原格式解释；现代调用方按实际类型分工。
                continue
            label = key if _literal else '' if key == 'text' else BUSINESS_LABELS.get(key, key.replace('_', ' '))  # 字面业务键保留原名。
            heading = ' / '.join(p for p in (prefix, label) if p)
            if not _literal and key in ('case_id', 'case_ids') and batch is not None:  # 仅真实测试关系字段转为用例名。
                from presentation import case_name  # Keep business strings untouched.
                child = [case_name(batch, cid) for cid in child] if isinstance(child, list) else case_name(batch, child)  # Typed reference, never token substitution.
            if not _literal and key == 'module_path' and isinstance(child, list):
                lines.append(heading + '：' + ' / '.join(map(str, child)))
            else:
                lines.extend(_business_lines(child, heading, batch, _legacy=_legacy, _literal=not _legacy and field_role('literal' if _literal else None, key) == 'literal'))  # value 等实际输入/产出不继承框架类型。
        return lines
    if isinstance(value, list):
        return [line for child in value for line in _business_lines(child, prefix, batch, _legacy=_legacy, _literal=_literal)]
    text = str(value) if value is not None else 'null' if _literal else '待核对'  # 真实空值不伪装为规则未知。
    return [prefix + '：' + text if prefix else text]


RULE_FIELDS = ('active_rule_decisions', 'rule_decisions', 'rule_decision_history', 'feedback_rule_history')  # Case audit collections only.


def _rule_lines(case, batch, *, original_case=None):  # 原始决定只负责身份、状态及缺失判断；显示内容读逐叶投影。
    """Project effective decisions; original replies and machine updates remain in JSON."""
    original_case = original_case if original_case is not None else case  # 无评估旧候选保持原规则。
    active = original_case.get('active_rule_decisions')  # 显式空集合不能复活历史。
    visible = case.get('active_rule_decisions', [])  # 投影只删标量，数组对象位置保持原身份。
    if active is None:  # Older candidates predate the authoritative active collection.
        indexed = {}  # Preserve independent conditions, including legacy unscoped ones.
        for item, projected in zip(original_case.get('rule_decisions', []) + original_case.get('feedback_rule_history', []), case.get('rule_decisions', []) + case.get('feedback_rule_history', [])):  # 按原决定身份选择对应显示内容。
            key = ('rule', item['rule_id']) if item.get('rule_id') else ('question', item['question_id']) if item.get('question_id') else ('legacy', _digest(item))  # Same identity can supersede; same field cannot.
            indexed[key] = (item, projected)  # 同一规则后答复覆盖；独立条件仍保留。
        pairs = list(indexed.values())  # 历史集合不作为并行有效规则。
    else:
        pairs = list(zip(active, visible))  # 原始位置不受标量叶隐藏影响。
    lines = []  # Business context before actions, never audit payloads.
    for original, item in pairs:  # 业务条件及解释均用对应投影，原记录只控制真实语义。
        original_reply = original.get('reply', {})  # 原始整轮答复保持在候选与唯一 QA。
        reply = item.get('reply', {})  # Decisions produced by apply_summary and feedback.
        state = original_reply.get('decision', 'unknown')  # 真实规则状态不受显示措辞替换影响。
        label = {'formal': '已确认规则', 'provisional': '暂定规则', 'deferred': '延期规则'}.get(state, '待核对规则')  # Chinese meaning.
        meaning_key = 'interpretation' if original_reply.get('interpretation') else 'actual_reply'  # 原始缺解释的旧答复仍可回退。
        meaning = reply.get(meaning_key) if original_reply.get(meaning_key) else '规则内容待核对'  # 已明确隐藏的有效叶不复活原答复或制造未知。
        if meaning is not None:  # 仅显示中省略的规则解释没有占位；真实缺失仍待核。
            lines.extend(_business_lines(meaning, label, batch))  # 可读替换及未评估业务原文同样保留。
        parts = dict(reply.get('answered_parts', {}), **item.get('answered_parts', {}))  # Current accumulated parts win.
        for key, value in parts.items():  # Preserve applicable conditions beyond the short interpretation.
            part_label = {'invalid': '失效处理', 'reuse': '复用策略', 'validity': '有效性', 'condition': '适用条件', 'behavior': '结果行为'}.get(key, key.replace('_', ' '))  # Unknown business parts remain visible.
            lines.extend(_business_lines(value, label + ' / ' + part_label, batch))  # No natural-language guessing.
        for key, heading in (('authorized_expectation', '暂定预期'), ('product_check', '待产品核实'), ('validity', '有效性'), ('applicability', '适用条件')):
            if key in reply:
                lines.extend(_business_lines(reply[key], heading, batch))  # Retain explicit temporary outcomes and conditions.
        if item.get('scope_basis'):
            lines.extend(_business_lines(item['scope_basis'], '适用范围与依据', batch))  # Preserve excluded branch and reason.
        if state == 'deferred':
            lines.append('延期影响：' + ('独立分支延期；不阻塞当前用例评审；延期分支不执行' if original.get('disposition_scope') == 'separate_impact' else '当前用例规则未决；评审与执行保持阻塞'))  # Existing disposition semantics, no new authorization.
    return lines  # Source dictionaries remain untouched.


def _render(batch, *, flat=False, reference_batch=None, _legacy_feedback=False, _expression_baseline=None, _data_legacy=False, _skip_preflight=False, _display_case_ids=None, _metadata_legacy=False, _metadata_bindings=None, companion_base=None, _independent_case=None, module_review=False, _expand_whole_steps=False):  # 资料路径只影响交付显示，源行仍为反馈保留。
    if batch.get('review_layout') == LAYOUT and not _legacy_feedback:
        batch = json.loads(json.dumps(batch, ensure_ascii=False, sort_keys=True))  # 问答保存按键排序；首次出稿和探针使用相同顺序。
    metadata_legacy = _legacy_feedback or _metadata_legacy  # 不改变历史业务身份、原始值或版本。
    if _expression_baseline is not None:
        from restoration import preflight
        check = preflight(_expression_baseline, source_catalog=reference_batch)  # Probe eligibility uses the actual complete parent.
        ready = set(check['ready_case_ids']) | {b['case_id'] for b in check['blockers'] if b.get('scope_only')}  # Scope-pending actions remain editable; invalid references stay excluded.
        batch = dict(batch, cases=[c for c in batch['cases'] if c['id'] in ready])
        _expression_baseline = dict(_expression_baseline, cases=[c for c in _expression_baseline['cases'] if c['id'] in ready])
    if _expression_baseline is None and not _skip_preflight:
        from restoration import preflight  # Local dependency failures retain original candidate identity.
        check = preflight(batch, source_catalog=reference_batch)
        if check['blockers']:
            visible_ids = set(check['ready_case_ids']) | {b['case_id'] for b in check['blockers'] if b.get('scope_only')}  # Keep unaffected operations and unresolved source actions visible.
            visible_ids = [cid for cid in (_display_case_ids if _display_case_ids is not None else [c['id'] for c in batch['cases']]) if cid in visible_ids]  # Keep caller order and omit blocked references.
            result = _render(batch, flat=flat, reference_batch=reference_batch, _legacy_feedback=_legacy_feedback, _data_legacy=_data_legacy, _skip_preflight=True, _display_case_ids=visible_ids, _metadata_legacy=_metadata_legacy, _metadata_bindings=_metadata_bindings, companion_base=companion_base, module_review=module_review, _expand_whole_steps=_expand_whole_steps)  # 同一交付位置仍绑定缩小后的可见范围。
            result.update({k: v for k, v in check.items() if k != 'complete_batch'})
            result['batch'] = copy.deepcopy(batch)  # Unshown never means deleted.
            return result
    from module_handoff import PROCESS_FIELDS, TITLE, module_notes  # Shared generated instructions for both views.
    indexed_cases = {case['id']: case for case in batch['cases']}  # Full candidate remains the scope assessment context.
    displayed_cases = batch['cases'] if _display_case_ids is None else [indexed_cases[cid] for cid in _display_case_ids]  # Explicit ordered rendering scope.
    note_source = _expression_baseline or batch  # Feedback probes use unchanged source instructions.
    note_batch = dict(note_source, cases=[c for c in note_source['cases'] if c['id'] in {case['id'] for case in displayed_cases}])  # Notes cannot resolve blocked or unrequested references.
    tree = ['# 本轮范围副本（非全量）', '- 版本：' + batch['content_version'],
            '- 未展示不表示删除；关联展示不扩大功能验证范围']
    if module_review and batch.get('kind') != 'scoped_review_copy' and len(displayed_cases) == len(batch['cases']):
        tree[0] = '# 完整候选用例评审'
        tree[2] = '- 展示本版全部候选用例'
    if module_review:
        tree[2] += '；待评用例：' + '、'.join(case['id'] for case in displayed_cases)
    from module_handoff import entrance  # One entrance, direct links to necessary documents.
    if not _legacy_feedback:
        tree[2] += '；' + entrance(note_batch)  # Display-only note selection has no role in applicability validation.
    human = [] if _legacy_feedback else [entrance(note_batch)]  # Same visible companion entrance in both forms.
    from review_projection import project_record  # Source-assessed leaves only; no inferred semantic deletion.
    def displayed(collection, owner):
        original = next((r for r in (_expression_baseline or batch).get(collection, []) if r.get('id', r.get('case_id')) == owner.get('id', owner.get('case_id'))), owner)
        return project_record(_expression_baseline or batch, collection, owner, binding_owner=original)  # Probe visibility follows the unchanged baseline.
    data = {d['id']: displayed('data', d) for d in batch['data']}
    if module_review:
        runtime_fields = {'generation_rule', 'validity', 'reuse_policy', 'invalidation_action'}
        data = {ref: {key: value for key, value in entry.items() if key not in runtime_fields}
                for ref, entry in data.items()}
    selection = {s['case_id']: s for s in batch['selection']}
    case_prose = {}  # Keep each case bound by stable identity.
    input_bindings = {}  # A flat source row identifies the exact input through directory projection.
    source_data = {record['id']: record for record in batch['data']}
    case_group_ranges = {}  # 对话表的原分组范围，供显式归属后的同投影替换。
    for case in displayed_cases:
        group_ranges = {}  # 每例只维护当前瞬时显示位置，不是业务权威。
        visible_case = case if _legacy_feedback else displayed('cases', case)  # 列表叶评估同样用于步骤和业务条件。
        case_start = len(human)  # Capture its human display chunk.
        indent = ''
        for part in case['module_path']:
            tree.append(indent + '- ' + _cell(part))
            indent += '  '
        tree.append(indent + '- ' + _cell(case['id'] + ' ' + case.get('title', '待核对')))
        indent += '  '
        human.extend(['# ' + _cell(title(case)),
                      '版本：' + batch['content_version'], '模块：' + ' / '.join(map(_cell, case['module_path']))])
        if module_review:
            point = (case.get('review_segment') or {}).get('test_point') or case.get('test_point') or case['title']
            human.append('测试点：' + _cell(point))
        note = selection[case['id']] if _legacy_feedback else displayed('selection', selection[case['id']])
        for key, value in (([('入选用途', str(note.get('action', '')) + '：' + str(note.get('reason', '')))] if note.get('action') or note.get('reason') else []) + [('本轮功能验证', '已单独列入批准范围' if case['id'] in batch['approved_validation_scope'] else '未列入批准范围')] if metadata_legacy else []):  # 新正文不重复编写范围模板。
            tree.append(indent + '- ' + key + '：' + _cell(value))
            human.append(key + '：' + _cell(value))
        excluded_rules = () if _legacy_feedback else RULE_FIELDS  # Reconstruct only the known pre-repair audit layout for feedback probes.
        from module_handoff import CASE_AGENT_FIELDS  # 已知审计/过程契约单处声明，未知业务条件完整保留。
        metadata = {key: (business_value(value, 'context') if key == 'context' and not metadata_legacy else value) for key, value in visible_case.items()
                    if key not in (*GROUPS, *(('test_point',) if module_review else ()), *excluded_rules, *(() if _legacy_feedback else PROCESS_FIELDS), *(() if metadata_legacy else (*CASE_AGENT_FIELDS, *TECHNICAL_FIELDS, 'priority')), 'id', 'title', 'module_path', 'common_preconditions_note', 'common_postconditions_note')}  # 仅已知审计控制字段外置。
        for key, value in metadata.items():  # 每行保留实际根字段 owner，不从显示文字倒猜职责。
            for line in _business_lines({key: value}, batch=reference_batch or batch, _legacy=metadata_legacy):  # 顺序和原显示保持一致。
                if _metadata_bindings is not None and key in ('review_status', 'final_review', 'review_history'):  # 仅准确用例直属控制字段。
                    _metadata_bindings[len(tree) - 3] = (case['id'], key)  # 派生 flat 源偏移；不写入候选或工件。
                tree.append(indent + '- ' + _cell(line))  # 业务同文仍有自己的独立源行。
                human.append(_cell(line))  # 对话与导图共享原投影。
        for line in ([] if _legacy_feedback else _rule_lines(visible_case, reference_batch or batch, original_case=case)):  # Historical rule rows already appear in metadata.
            tree.append(indent + '- ' + _cell(line))  # Keep rules within their owning case.
            human.append(_cell(line))  # Never expose raw updates or repeated histories.
        if _independent_case:
            for method in _independent_case['methods']:
                human.append(f"- {method['name']}（{method['timing']}）：{method['instruction']}")
            for pending in _independent_case['applicability_pending']:
                human.append(f"- 适用范围待核对：{pending['name']}。{pending['reason']}")
        for group, label in zip(GROUPS, ('公共前置操作', '特殊前置操作', '测试步骤', '特殊后置操作', '公共后置操作')):
            group_human_start = len(human)  # Shared preparation is rendered once after business projection.
            if (group.startswith('special_') or group == 'common_postconditions') and not visible_case.get(group) and not visible_case.get(group + '_note'):
                continue
            tree.append(indent + '- ' + label)
            human.extend(['', label, ''])  # Separate prose and each Markdown table block.
            notes = _business_lines(business_value(visible_case.get(group + '_note', {}), 'claim') if not metadata_legacy else case.get(group + '_note', {}), batch=reference_batch or batch, _legacy=metadata_legacy) if group.startswith('common_') else []  # 仅已知说明 claim 的来源外置。
            for line in notes:  # One source note appears once under its preparation group.
                tree.append(indent + '  - ' + _cell(line))
                human.append(_cell(line))
            if not visible_case.get(group) and not notes:  # 原始未提供项继续待核。
                tree.append(indent + '  - 未提供，待核对')
                human.append('未提供，待核对')
            if visible_case.get(group):  # 原有特殊项仍完整展示。
                human.extend(['', '| 序号 | 操作 | 参数/数据 | 预期结果 |', '| --- | --- | --- | --- |'])  # Actual table boundary.
            for i, step in enumerate(visible_case.get(group, []), 1):  # 显式列表叶评估贯穿真正步骤投影。
                from step_reuse import resolve_step  # One resolver for every displayed step.
                owner = next((c for c in (_expression_baseline or batch)['cases'] if c['id'] == case['id']), case)  # Feedback probes cannot mutate reference applicability.
                reference_context = reference_batch or batch
                if 'step_reference' in step and not any(_digest(item) == step['step_reference']['definition_digest'] for item in reference_context.get('step_definitions', [])):
                    reference_context = batch  # Actual parent may predate candidate-owned frozen definitions and current data bindings.
                step, definition = resolve_step(reference_context, owner, group, step)
                if _expression_baseline is not None and not definition:  # Preserve compact layout for a materialized feedback probe.
                    original = owner.get(group, [])[i - 1]
                    if 'step_reference' in original:
                        _, definition = resolve_step(_expression_baseline, owner, group, original)  # Only visible action is mapped; source label stays immutable.
                if definition:
                    group_label = dict(zip(GROUPS, ('公共前置操作', '特殊前置操作', '测试步骤', '特殊后置操作', '公共后置操作')))[group]
                    label = 'P0 ' + definition['title'] + '，' + group_label + '步骤 ' + str(definition['step_number'])
                    if not _expand_whole_steps:
                        tree.append(indent + f'  - 步骤 {i}：' + _cell(step['operation']))
                        tree.append(indent + '    - 整步引用：' + _cell(label))
                        current_data = [line for ref in step.get('data_refs', []) if data[ref].get('generation_rule') for line in _business_lines(data[ref], batch=reference_batch or batch)]  # Dynamic values belong to this case.
                        for line in current_data:
                            tree.append(indent + '    - 本例数据：' + _cell(line))
                        human.append(f'| {i} | {_cell(step["operation"])} | 整步引用：{_cell(label)}；{_cell("；".join(current_data))} | 见引用步骤 |')
                        continue  # Shared data, expectation and assertion remain maintained in P0.
                from invocation_input import json_input
                values, input_positions = [], {}
                for ref in step.get('data_refs', []):
                    record = data[ref]
                    if module_review and json_input(source_data[ref]):
                        input_positions[len(values)] = ref
                        values.append(str(record.get('object_ref') or '输入参数') + '（完整 JSON）')
                        record = {k: v for k, v in record.items() if k not in ('value', 'object_ref', 'input_format')}
                    values.extend(data_lines(record, lambda value: _business_lines(value, batch=reference_batch or batch, _legacy=metadata_legacy),
                                             legacy=_legacy_feedback or _data_legacy, metadata_legacy=metadata_legacy,
                                             incremental=batch.get('review_layout') == LAYOUT))
                values = values or ['无']
                if definition and _expand_whole_steps:
                    values.insert(0, '整步引用：' + label)
                    for ref in step.get('data_refs', []):
                        if 'value' in data[ref]:
                            values.append(ref + ' = ' + json.dumps(data[ref]['value'], ensure_ascii=False))
                if _independent_case:
                    for ref in step.get('data_refs', []):
                        entry = _independent_case['data'][ref]
                        if 'value' in entry:
                            values.append(ref + ' = ' + json.dumps(entry['value'], ensure_ascii=False))
                extensions = {k: v for k, v in step.items()
                              if k not in ('id', 'operation', 'data_refs', 'expected', 'verification', *(() if metadata_legacy else (*TECHNICAL_FIELDS, 'source_ref')))}
                business_conditions = _business_lines(extensions, batch=reference_batch or batch, _legacy=metadata_legacy)  # 旧 metadata 逐字复原而非忽略新增字段。
                if business_conditions and values == ['无']:
                    values = []
                values.extend(business_conditions)
                expected = _business_lines(step.get('expected', []) if metadata_legacy else business_value(step.get('expected', []), 'claim'), batch=reference_batch or batch, _legacy=metadata_legacy) or ['待核对']  # 来源不成为新稿预期。
                checks = _business_lines(step.get('verification', []) if metadata_legacy else business_value(step.get('verification', []), 'claim'), batch=reference_batch or batch, _legacy=metadata_legacy) or ['待核对']  # 独立业务检查仍保留。
                if not _legacy_feedback:  # Compare whole assertions and preserve feedback source mappings.
                    original = None  # Ordinary generation uses the authored claims.
                    if _expression_baseline is not None:
                        original_case = next(c for c in _expression_baseline['cases'] if c['id'] == case['id'])
                        original_step = original_case[group][i - 1]  # Stable source order binds feedback.
                        original = (original_step.get('expected', []), original_step.get('verification', []))
                    if step.get('verification'):  # Missing observations still show the existing pending marker.
                        checks = independent_checks(step.get('expected', []), step['verification'],
                            lambda claim: _business_lines(claim if metadata_legacy else business_value(claim, 'claim'), batch=reference_batch or batch, _legacy=metadata_legacy), original)  # 精确旧布局沿旧 claim 投影。
                operation = step.get('operation', '待核对')
                tree.append(indent + f'  - 步骤 {i}：' + _cell(operation))  # Preserve operation and data ownership.
                if not _legacy_feedback and len(values) == 1 and values != ['无'] and not input_positions:  # One scalar needs no mechanical child level.
                    tree.append(indent + '    - 参数/数据：' + _cell(values[0]))  # Preserve literal and feedback mapping.
                else:
                    tree.append(indent + '    - 参数/数据')  # Complex branches retain individual leaves.
                    for position, value in enumerate(values):
                        if position in input_positions:
                            input_bindings[len(tree) - 3] = (case['id'], step['id'], input_positions[position])
                        tree.append(indent + '      - ' + _cell(value))
                tree.append(indent + '    - 预期')
                tree.extend(indent + '      - ' + _cell(v) for v in expected)
                if checks:  # No empty duplicate assertion node.
                    tree.append(indent + '      - 验证点：' + _cell('；'.join(checks)))
                check_text = '；验证点：' + _cell('；'.join(checks)) if checks else ''  # Same visible meaning in chat.
                table_values = list(values)
                for position, ref in input_positions.items():
                    table_values[position] += ' ' + json.dumps(source_data[ref]['value'], ensure_ascii=False)
                human.append(f'| {i} | {_cell(operation)} | {_cell("；".join(table_values))} | 预期：{_cell("；".join(expected))}{check_text} |')
            if group.startswith('common_') and not _legacy_feedback and _independent_case is None:
                human[group_human_start:] = []  # Module projection below supplies common or unresolved preparation.
            elif group in ('steps', 'special_preconditions', 'special_postconditions'):
                group_ranges[group] = (group_human_start - case_start, len(human) - case_start)  # 只用于当前对话片段位置。
        human.append('')  # End the final table before pending questions or the next case.
        for question in batch['questions']:
            if question['case_id'] == case['id'] and (not question.get('history') or question.get('stale')):  # Preserve history but display only unanswered or invalidated questions.
                pending = _cell(question['field']) + ('：' + _cell(question['reason']) if question.get('reason') and not _legacy_feedback else '')  # Known old exports omitted the reason suffix.
                tree.append(indent + '- 待核对：' + pending)  # Same unresolved meaning in both formats.
                human.append('待核对：' + pending)  # Legacy human callers retain clarification reasons.
        case_prose[case['id']] = human[case_start:]  # Stable IDs bind display chunks only.
        case_group_ranges[case['id']] = group_ranges
    from aggregation import aggregate  # Share the lossless directory projection.
    markdown = '\n'.join(tree) + '\n'  # Retain scalar-source offsets for feedback.
    if not _legacy_feedback and not flat:
        from aggregation import projection
        _, projected = projection(batch, markdown, source_catalog=reference_batch, display_case_ids=_display_case_ids, module_review=module_review)  # Full context, selected branches.
        preparation = [entrance(note_batch)]  # Reuse identical applicability and source-bound operations in chat.
        def common_prose(node, path):
            if node.get('case_id'):  # Project case prose at its stable module position.
                case = indexed_cases[node['case_id']]
                for child in node['children']:
                    if child['text'].startswith('待核对：') and '前置' in child['text']:
                        common_prose(child, path + [node['text']])
                if not case.get('common_preconditions'):
                    preparation.extend(_business_lines(case.get('common_preconditions_note', {}), batch=batch))
                    preparation.extend(child['text'] for child in node['children'] if child['text'] == '前置操作未提供，待核对')
                prose = case_prose[node['case_id']]
                ranges = case_group_ranges[node['case_id']]
                replacements = []  # 来源步骤仍留原组，只替换显示为特殊的真实节点。
                for direction, group, label in (('pre', 'special_preconditions', '特殊前置操作'), ('post', 'special_postconditions', '特殊后置操作')):
                    special = next((child for child in node['children'] if child['text'] == label and child.get('attributed_special')), None)
                    if special is not None:
                        fallback = ranges.get('steps', (len(prose), len(prose)))[0 if direction == 'pre' else 1]
                        start, end = ranges.get(group, (fallback, fallback))
                        replacements.append((start, end, special))
                offset = 0
                for start, end, special in sorted(replacements, key=lambda replacement: replacement[0]):
                    preparation.extend(prose[offset:start])
                    common_prose(special, [node['text']])  # 表格来源与最终 MD 真实特殊分支一致。
                    offset = end
                preparation.extend(prose[offset:])
                for child in node['children']:
                    if child['text'].startswith('待核对：') and '后置' in child['text']:
                        common_prose(child, path + [node['text']])
                if not case.get('common_postconditions') and case.get('common_postconditions_note'):
                    preparation.extend(_business_lines(case['common_postconditions_note'], batch=batch))
                return
            if node.get('source_preparation'):
                preparation.append('## ' + ' / '.join(path + [node['text']]))
                for item in node['children']:
                    preparation.append('- ' + item['text'])
                    preparation.extend('  - ' + child['text'] for child in item['children'])
                return
            if node['text'].startswith(('公共前置操作 ', '特殊前置操作', '特殊后置操作', '待核对：前置适用范围', '待核对：未归属前置操作', '待核对：未归属前置说明', '公共后置操作 ', '待核对：后置适用范围', '待核对：未归属后置操作', '待核对：未归属后置说明')):  # 显式特殊归属同样沿树生成对话表。
                preparation.append('## ' + ' / '.join(path) + ' / ' + node['text'])
                def leaves(item, depth):
                    preparation.append('  ' * depth + '- ' + item['text'])
                    for child in item['children']:
                        leaves(child, depth + 1)
                steps = [child for child in node['children'] if child['text'].startswith('步骤 ')]
                for child in node['children']:
                    if child not in steps:
                        leaves(child, 0)
                if steps:
                    preparation.extend(['', '| 序号 | 操作 | 参数/数据 | 预期结果 |', '| --- | --- | --- | --- |'])
                    def text_of(item):
                        return '；'.join([item['text'], *[text_of(c) for c in item['children']]])
                    for number, step in enumerate(steps, 1):
                        operation = step['text'].partition('：')[2]
                        values = '；'.join(text_of(c) for c in step['children'] if c['text'] != '预期')
                        expected = '；'.join(text_of(c) for c in step['children'] if c['text'] == '预期')
                        preparation.append(f'| {number} | {operation} | {values} | {expected} |')  # Same projected business leaves, now in a chat table.
                    preparation.append('')  # End the table before the next section.
                return
            for child in node['children']:
                common_prose(child, path + ([node['text']] if node['text'] else []))
        common_prose(projected, [])
        human = preparation
    return {'artifact_status': 'planned', 'ready_case_ids': [c['id'] for c in batch['cases']], 'blocked_case_ids': [], 'blockers': [], 'clarifications': [], 'batch': copy.deepcopy(batch), 'human_view': '\n'.join(human) + '\n',
            'xmind_markdown': markdown if flat else aggregate(batch, markdown, source_catalog=reference_batch, display_case_ids=_display_case_ids, companion_base=companion_base, module_review=module_review, input_bindings=input_bindings)}  # 两个投影共享请求范围。


def render_review_batch(batch, *, source_catalog=None, companion_base=None):
    """Re-render a scoped candidate after clarification without losing groups."""
    _credential_guard(batch)
    return _render(batch, reference_batch=source_catalog, companion_base=companion_base)  # 已交付稿复用真实资料位置。


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
    from step_reuse import reference_data  # Fixed bindings are data references, not execution dependencies.
    return reference_data(case) | {ref for group in GROUPS for step in case.get(group, [])
            for ref in step.get('data_refs', [])}


def build_scoped_review(catalog, batch_id, selection, approved_validation_scope=None,
                        candidates=None, candidate_data=None, *, review_layout=None, hypothetical=False):
    """Select complete catalog records without granting change or execution approval."""
    _credential_guard([catalog, selection, candidates, candidate_data])
    if review_layout not in (None, LAYOUT):
        raise ValueError('Unknown review layout')
    if type(hypothetical) is not bool or (hypothetical and review_layout != LAYOUT):
        raise ValueError('Hypothetical display requires the incremental layout')
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
        if review_layout == LAYOUT and 'detail_ref' in item:
            detail = Path(item['detail_ref'])
            if action != 'related' or not detail.is_absolute() or detail.suffix.lower() != '.md' or not detail.is_file():
                raise ValueError('Reference-only relationship needs its existing absolute detail Markdown')
        if review_layout == LAYOUT and item.get('replacement_case_id'):
            replacement = item['replacement_case_id']
            if action != 'deactivate' or replacement == case_id or replacement not in indexed.keys() | proposed.keys():
                raise ValueError('Replacement must identify an existing reviewed-scope case')
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
    if len(set(scope)) != len(scope) or any(cid not in indexed and cid not in proposed for cid in scope):  # Full approved scope can include undisplayed catalog cases.
        raise ValueError('Validation scope must identify known catalog or candidate cases')  # Reject unknown IDs without shrinking approval to the display.
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
    data = [d for key, d in revised_data.items() if key in data_refs]
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
                from step_reuse import resolve_step  # Scope completeness checks the actual inherited step.
                try:
                    step, _ = resolve_step(dict(full, data=data), case, group, step)
                except (ValueError, KeyError) as error:
                    questions.append(dict(case_id=case['id'], field=f'{group}/{i}', reason=str(error)))
                    continue  # Keep failed original for targeted clarification.
                for key in ('operation', 'data_refs', 'expected', 'verification'):
                    if key not in step or (key != 'data_refs' and not step[key]):
                        questions.append({'case_id': case['id'], 'field': f'{group}/{i}/{key}', 'reason': '源记录缺失，待核对'})
    batch = {'schema_version': 1, 'id': batch_id, 'stage': 'P1/P2', 'kind': 'scoped_review_copy',
             'sources': [{'kind': 'existing_catalog', 'ref': full['source_ref'], 'sha256': _digest(full)}],
             'initial_copy_baseline': baseline, 'selection': copy.deepcopy(selection),
             'approved_validation_scope': scope, 'cases': selected, 'data': data, 'questions': questions}
    if review_layout:
        batch['review_layout'] = review_layout  # 随候选版本一起保存，恢复时选回同一布局。
    if hypothetical:
        batch['hypothetical'] = True  # 本轮版式演示的声明随候选保存。
    if full.get('input_reuse'):
        batch['input_reuse'] = {cid: rows for cid, rows in full['input_reuse'].items() if cid in selected_ids}
    if full.get('source_preparations'):
        batch['source_preparations'] = copy.deepcopy(full['source_preparations'])
    if full.get('preparation_scopes'):
        batch['preparation_scopes'] = copy.deepcopy(full['preparation_scopes'])  # Selection never broadens approved membership.
        baseline['preparation_scopes'] = copy.deepcopy(full['preparation_scopes'])  # Preserve review evidence for restoration.
    batch['data_version'] = _digest(data)
    if full.get('step_definitions'):
        used = {s['step_reference']['definition_digest'] for c in selected for g in GROUPS for s in c.get(g, []) if 'step_reference' in s}
        batch['step_definitions'] = [copy.deepcopy(d) for d in full['step_definitions'] if _digest(d) in used]
        baseline['step_definitions'] = copy.deepcopy(batch['step_definitions'])
        baseline['copy_version'] = _digest({key: baseline[key] for key in ('cases', 'data', 'selection', 'step_definitions')})
    batch['content_version'] = _digest(batch)
    result = _render(batch, reference_batch=full)
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
        from module_handoff import write_artifacts  # Persist the same module documents across sibling batches.
        write_artifacts(result, output, source_catalog=catalog, reader_stage='premerge')  # Actual input remains available at delivery.
        for filename, content in [('initial-copy-baseline.json', result['batch']['initial_copy_baseline']),
                                  ('changes.json', result['changes'])]:
            (output / filename).write_text(json.dumps(content, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        for filename, key in [('xmind.md', 'xmind_markdown'),  # Persist the scope tree, never chat tables.
                              ('review-notes.md', 'review_notes')]:
            (output / filename).write_text(result[key], encoding='utf-8')
    except (ValueError, KeyError, TypeError, AttributeError, OSError):
        print('Scope copy rejected: check catalog, explicit selection, data and new output directory.', file=sys.stderr)
        return 1
    print('Review copy written; full catalog unchanged, no feedback applied or merge performed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
