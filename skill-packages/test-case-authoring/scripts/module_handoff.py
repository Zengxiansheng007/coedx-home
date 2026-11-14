"""Generated module instructions; original candidate remains the lossless authority."""
TITLE = '资料与Agent交接说明'
PROCESS_FIELDS = ('review_status', 'merge_status', 'execution_status')  # Rule identity remains visible in business prose.


def module_notes(batch):
    from scoped_review import _business_lines  # Preserve the shared business-safe leaf projection.
    result = {}  # Complete semantic paths prevent same-name module collisions.
    for case in batch['cases']:
        notes = result.setdefault(tuple(case['module_path']), [])  # Only direct owners create a branch.
        heading = case.get('title', '待核对用例')  # Stable English identities stay internal.
        lines = ['适用用例：' + heading, '版本映射：当前候选 ' + batch['content_version']]
        lines.extend(_business_lines({k: case[k] for k in PROCESS_FIELDS if k in case}, batch=batch))
        def handoff(value):
            return _business_lines(value, batch=batch) if isinstance(value, dict) else ['执行约束：须读取当前候选的技术交接原文后执行'] if value else []  # Legacy opaque text may embed stable machine identities.
        for group in ('common_preconditions', 'special_preconditions', 'steps', 'special_postconditions'):
            for index, step in enumerate(case.get(group, []), 1):
                if step.get('source') or step.get('lines'):
                    label = {'recording': '录制资料', 'handwritten': '手写资料', 'prd': '需求资料'}.get(step.get('source'), '候选绑定资料')  # Unknown source identifiers stay internal.
                    location = '—'.join(str(n) for n in step.get('lines', []) if isinstance(n, int))  # Numeric source locations carry no credentials.
                    lines.append({'common_preconditions': '公共前置操作', 'special_preconditions': '特殊前置操作', 'steps': '测试步骤', 'special_postconditions': '特殊后置操作'}[group] + ' ' + str(index) + '：' + label + ('，行 ' + location if location else '；定位见当前候选') + '；修改须重新核对')  # Same-version candidate retains complete original provenance.
                operation = _business_lines(step.get('operation', '待核对操作'), batch=batch)  # Render only the business operation, without internal step identity.
                scope = {'common_preconditions': '公共前置操作', 'special_preconditions': '特殊前置操作', 'steps': '测试步骤', 'special_postconditions': '特殊后置操作'}[group] + ' ' + str(index) + '（' + '；'.join(line.removeprefix('操作：') for line in operation) + '）'  # Group and ordinal bind even sourceless steps.
                lines.extend(scope + '：' + note for note in dict.fromkeys(handoff(step.get('technical_handoff', {}))))  # Deduplicate only inside the same step scope.
        lines.extend(handoff(case.get('technical_handoff', {})))  # General reuse and invalidation instructions live here.
        notes.append((heading, list(dict.fromkeys(lines))))  # Deduplicate instructions only within their applicability.
    return result
