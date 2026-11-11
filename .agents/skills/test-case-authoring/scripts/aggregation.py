"""Lossless hierarchy projection with reversible source-line bindings."""
import copy
import json


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
        node = {'text': line.strip()[2:], 'children': [], 'origins': [index]}
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


def projection(batch, markdown):
    lines = markdown.splitlines()
    root = _parse(lines[3:])  # Scoped renderer supplies a stable three-line header.
    merged = {'text': '', 'children': [], 'origins': []}
    data = {d['id']: d for d in batch['data']}
    groups = {}
    for case, branch in zip(batch['cases'], root['children']):  # The flat source supplies one branch per case.
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
        common = next(n for n in source['children'] if n['text'] == '公共前置操作')
        if case.get('common_preconditions'):
            refs = [ref for step in case['common_preconditions'] for ref in step.get('data_refs', [])]
            steps = [{k: v for k, v in step.items() if k != 'id'} for step in case['common_preconditions']]  # Only local step identity is irrelevant.
            meaning = [case.get('context'), case.get('dependencies'), steps,
                       [data[ref] for ref in refs], case.get('common_preconditions_note')]
            key = (tuple(case['module_path']), json.dumps([_semantic(meaning), _shape(common)], sort_keys=True, ensure_ascii=False))
            if key not in groups:
                shared = copy.deepcopy(common)
                shared['text'] += ' ' + str(1 + sum(k[0] == key[0] for k in groups))
                shared['members'] = []
                shared['origins'] = []  # Group title is generated, never a business edit.
                groups[key] = shared
                target['children'].append(shared)
            else:
                shared = groups[key]
                for left, right in zip(shared['children'], common['children']):
                    _merge_origins(left, right)
            shared['members'].append(case['id'])
            common['children'] = [{'text': '适用：' + shared['text'] + '（执行时仍须完成）', 'children': [], 'origins': []}]
            common['origins'] = []
        target['children'].append(source)
    for shared in groups.values():
        shared['children'].insert(0, {'text': '适用用例：' + '、'.join(shared['members']), 'children': [], 'origins': []})
    return lines[:3], merged


def aggregate(batch, markdown):
    header, root = projection(batch, markdown)
    lines = list(header)
    def visit(node, depth):
        lines.append('  ' * depth + '- ' + node['text'])
        for child in node['children']:
            visit(child, depth + 1)
    for node in root['children']:
        visit(node, 0)
    return '\n'.join(lines) + '\n'


def expand_feedback(batch, flat_markdown, incoming):
    """Expand edits through exact baseline bindings before existing feedback review."""
    header, expected = projection(batch, flat_markdown)
    lines = incoming.splitlines()
    if lines[:3] != header:
        raise ValueError('Markdown header/version must match initial display')
    actual = _parse(lines[3:])
    output = flat_markdown.splitlines()
    removed = set()
    def remove_cases(node):  # Omitted complete branches retain explicit deletion clarification.
        if node.get('case_id'):
            removed.add(node['case_id'])
        for child in node['children']:
            remove_cases(child)

    def match(wanted, got):
        remaining = list(got['children'])
        for child in wanted['children']:
            if child.get('case_id'):
                prefix = child['case_id'] + ' '
                found = next((n for n in remaining if n['text'].startswith(prefix)), None)
                if found is None:
                    removed.add(child['case_id'])
                    continue
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
            if child['text'] != found['text']:
                if child.get('directory') or not child['origins']:
                    raise ValueError('Directory or applicability edit needs explicit interpretation')
                for origin in child['origins']:
                    old = output[origin + 3]
                    output[origin + 3] = old[:len(old) - len(old.lstrip())] + '- ' + found['text']
            match(child, found)
        if remaining:
            raise ValueError('Unknown Markdown identity or structure')
    match(expected, actual)
    if removed:
        starts = []
        for index, line in enumerate(output[3:], 3):
            for case in batch['cases']:
                if line.startswith('  ' * len(case['module_path']) + '- ' + case['id'] + ' '):
                    starts.append((index - len(case['module_path']), case['id']))
        kept = output[:3]
        for pos, (start, cid) in enumerate(starts):
            end = starts[pos + 1][0] if pos + 1 < len(starts) else len(output)
            if cid not in removed:
                kept.extend(output[start:end])
        output = kept
    return '\n'.join(output) + '\n'
