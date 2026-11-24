"""Versioned display of the existing scope tree and its source-line bindings."""

import re
from collections import Counter
from pathlib import Path


LAYOUT = 'incremental-v1'
TITLE_PREFIX = '# 增量用例评审｜'
VERSION_PREFIX = '  - 稿件版本：'
ACTION_LABELS = {'modify': '修改', 'reuse': '沿用', 'related': '关联查看', 'deactivate': '拟停用'}
STEP = re.compile(r'步骤 \d+：')


def _node(text, children=()):
    return dict(text=text, children=list(children), origins=[])  # 生成字段不承载可编辑的业务源行。


def _decorate(node, before, after):
    node['text'] = after + node['text'][len(before):]  # 显示前缀变动保留原业务内容。
    node['presentation_prefix'] = (before, after)  # 同一个投影提供回传逆映射。


def _data_label(node, prefix):
    trigger = prefix + 'trigger condition：'
    if node['text'].startswith(trigger):
        _decorate(node, trigger, '触发条件：')  # 后置条件紧跟实际操作，仍保留业务源字段。
    else:
        _decorate(node, prefix, '数据 · ')


def _steps(children):
    result = []
    number = 0
    for child in children:
        match = STEP.match(child['text'])
        if match is None:
            result.append(child)
            continue
        number += 1
        _decorate(child, match.group(), f'操作 {number}：')
        details = []
        for detail in child['children']:
            if detail['text'] == '预期':
                for assertion in detail['children']:
                    if not assertion['text'].startswith('验证点：'):
                        _decorate(assertion, '', '预期：')
                    details.append(assertion)
            elif detail['text'] == '参数/数据':
                for value in detail['children']:
                    _data_label(value, '')
                    details.append(value)
            else:
                if detail['text'].startswith('参数/数据：'):
                    _data_label(detail, '参数/数据：')
                details.append(detail)
        child['children'] = details
        result.append(child)
    return result


def _applicability(members, cases):
    from aggregation import business_path

    by_group = {}
    for case_id in members:
        case = cases[case_id]
        group = ' / '.join(business_path(case))
        short = case['title'].removeprefix(group.rsplit(' / ', 1)[-1] + '：') if group else case['title']
        by_group.setdefault(group, []).append(_node(case_id + '｜' + short))
    labels = []
    for group, items in by_group.items():
        labels.extend([_node(group, items)] if group else items)
    return _node(f'适用用例（本轮 {len(members)} 条）', labels)


def _group_common_operations(nodes):
    """Combine adjacent definitions when their applicable cases and direction match."""
    result = []
    for node in nodes:
        if node.get('scope'):
            previous = result[-1] if result else {}
            if (previous.get('scope') and previous['direction'] == node['direction']
                    and set(previous['members']) == set(node['members'])):
                existing = {item['text'] for item in previous['children'] if not item['origins']}
                previous['children'].extend(child for child in node['children']
                                            if child['origins'] or child['text'] not in existing)
                continue
        result.append(node)
    return result


def _selection_notes(selection, baseline):
    action = selection['action']
    reason = selection['reason']
    if action == 'modify':
        return [_node('本次修改：' + reason + '。' + selection['coverage_impact'])]
    if action == 'reuse':
        return [_node('沿用依据：' + reason + '（基线 ' + baseline + '）')]
    if action == 'related':
        notes = [_node('关联原因：' + reason)]
        if selection.get('detail_ref'):
            target = Path(selection['detail_ref']).resolve()
            if not target.is_file():
                raise ValueError('Related case detail is missing: ' + selection['case_id'])
            notes.append(_node('[查看关联用例详情](' + target.as_uri() + ')'))
        return notes
    if action == 'deactivate':
        replacement = selection.get('replacement_case_id')
        coverage = ('替代用例：' + replacement if replacement
                    else '覆盖缺口：' + selection.get('coverage_impact', '替代与覆盖影响待核对'))
        return [_node('停用原因：' + reason), _node(coverage), _node('原稿定位：' + baseline)]
    return []


def project(batch, root, *, companion_base=None):
    """Retain the established identities and edit origins while changing layout."""
    from module_handoff import companion_links

    cases = {case['id']: case for case in batch['cases']}
    selections = {item['case_id']: item for item in batch['selection']}
    visible_cases = []
    modules = {}
    baseline = batch['initial_copy_baseline']['catalog_version']

    def visit(parent):
        parent['children'] = _group_common_operations(parent['children'])
        displayed_applicability = {}  # 同一方向的相同名单跨非相邻动作也只列一次。
        for node in parent['children']:
            if 'module_path' in node:
                modules[node['module_path']] = node
            case_id = node.get('case_id')
            if case_id:
                visible_cases.append(case_id)
                from aggregation import business_path
                case = cases[case_id]
                action = ACTION_LABELS.get(selections[case_id]['action'])
                group = business_path(case)
                grade = case['priority'] + ' '
                qualified_grade = grade + group[-1] + '：' if group else grade
                source_prefix = qualified_grade if node['text'].startswith(qualified_grade) else grade
                if action or source_prefix != grade:
                    display_prefix = ('「' + action + '」' if action else '') + grade
                    _decorate(node, source_prefix, display_prefix)
                children = [_node('用例编号：' + case_id), *_selection_notes(selections[case_id], baseline)]
                if selections[case_id].get('detail_ref'):
                    node.update(children=children, origins=[])  # 只查来源的条目保留身份，正文留在原稿。
                    continue
                for child in node['children']:
                    if child['text'] in ('特殊前置操作', '测试步骤', '特殊后置操作'):
                        children.extend(child['children'])  # 用例内保留动作顺序，省去前后置分组。
                    else:
                        children.append(child)
                node['children'] = _steps(children)
            elif node.get('scope'):
                members = node['members']
                identity = (node['direction'], frozenset(members))
                if identity in displayed_applicability:
                    applicability = _node('适用名单：同「' + displayed_applicability[identity] + '」')
                else:
                    displayed_applicability[identity] = node['text']
                    applicability = _applicability(members, cases)
                children = [child for child in node['children']
                            if child['origins'] or not child['text'].startswith(
                                ('适用用例：', '范围版本：', '适用分组：', '例外用例：'))]
                node['children'] = [applicability, *_steps(children)]
            else:
                visit(node)

    visit(root)
    visible = [cases[case_id] for case_id in visible_cases]
    paths = list(dict.fromkeys(tuple(case['module_path']) for case in visible))
    scopes = [path[-1] if len(paths) == 1 else ' / '.join(path[-2:]) for path in paths]
    if len(scopes) != len(set(scopes)):
        scopes = [' / '.join(path) for path in paths]  # 同名模块保留完整业务定位。
    scope = '、'.join(scopes) or '待核对'
    priorities = dict.fromkeys(case['priority'] for case in visible)
    status_labels = {'pending': '待评审', 'approved': '已评审', 'rejected': '评审需修改'}
    statuses = dict.fromkeys(status_labels.get(case.get('review_status'), '待核对') for case in visible)
    counts = Counter(selections[case_id]['action'] for case_id in visible_cases)
    action_counts = '、'.join(f'{label} {counts[action]} 条' for action, label in
                             {'add': '新增', **ACTION_LABELS}.items() if counts[action])
    headline = f'本轮范围：{scope}，共 {len(visible)} 条（{"、".join(priorities)}）'
    if len(counts) > 1:
        headline += '。' + action_counts
    focus = dict.fromkeys(case['title'] for case in visible)
    summary = [
        _node('稿件版本：' + batch['content_version']),
        _node('基线：' + baseline),
        _node(headline),
        _node('评审重点：' + '、'.join(focus)),
        _node('评审状态：' + '、'.join(statuses)),
    ]
    if batch.get('hypothetical'):
        summary.append(_node('假设样稿。项目、规则、用例和数据均为版式示例'))
    questions = [q for q in batch['questions']
                 if q['case_id'] in visible_cases and (not q.get('history') or q.get('stale'))]
    if questions:
        summary.append(_node(f'待核对：{len(questions)} 项，见相应用例'))
    def materials(records):
        links = companion_links(dict(batch, cases=records), base_path=companion_base, with_filenames=True)
        return _node('资料与 Agent 交接说明', map(_node, links)) if links else None

    if len(paths) == 1:
        material = materials(visible)
        if material:
            summary.append(material)
    else:
        for path in paths:
            material = materials([case for case in visible if tuple(case['module_path']) == path])
            if material:
                children = modules[path]['children']
                position = next((index for index, child in enumerate(children)
                                 if child.get('direction') != 'pre'), len(children))
                children.insert(position, material)  # 保持公共前置和公共后置夹住用例范围。
    root['children'].insert(0, _node('评审范围', summary))
    return [TITLE_PREFIX + scope], root


def is_incremental(markdown):
    return markdown.startswith(TITLE_PREFIX)


def version_of(markdown):
    lines = markdown.splitlines()
    if len(lines) < 3 or lines[1] != '- 评审范围' or not lines[2].startswith(VERSION_PREFIX):
        raise ValueError('Incremental review scope/version is missing')
    return lines[2].removeprefix(VERSION_PREFIX)


def restore_text(node, rendered):
    """Decode only the prefix owned by the exact expected structural node."""
    prefix = node.get('presentation_prefix')
    if prefix is None:
        return rendered
    source, display = prefix
    if not rendered.startswith(display):
        raise ValueError('Changing an operation or field label needs explicit interpretation')
    return source + rendered[len(display):]
