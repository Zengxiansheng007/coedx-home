"""Lossless hierarchy projection with reversible source-line bindings."""
import copy
import json
import hashlib
from presentation import case_name  # Resolve generated applicability identities only.


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
        source['text'] = source['text'][len(case['id']) + 1:]  # The flat source alone retains the English identity prefix.
        common = next(n for n in source['children'] if n['text'] == '公共前置操作')
        if case.get('common_preconditions'):  # Only explicit preparation steps can form a shared group.
            refs = [ref for step in case['common_preconditions'] for ref in step.get('data_refs', [])]  # Referenced data contributes its meaning, not just its ID.
            steps = [{k: v for k, v in step.items() if k != 'id'} for step in case['common_preconditions']]  # Only local step identity is irrelevant.
            meaning = [case.get('context'), case.get('dependencies'), steps,  # Context and dependencies constrain safe sharing.
                       [data[ref] for ref in refs], case.get('common_preconditions_note')]  # Preserve preparation data and explanatory meaning.
            key = (tuple(case['module_path']), json.dumps([_semantic(meaning), _shape(common)], sort_keys=True, ensure_ascii=False))  # Share only within one module path with equal meaning and descendant shape.
            if key not in groups:  # First equivalent case establishes the shared preparation branch.
                shared = copy.deepcopy(common)  # Keep the case branch independently editable.
                shared['text'] += ' ' + str(1 + sum(k[0] == key[0] for k in groups))  # Number groups within their module path.
                shared['members'] = []  # Collect applicability without changing case identities.
                shared['origins'] = []  # Group title is generated, never a business edit.
                groups[key] = shared  # Reuse this exact semantic and structural group later.
                target['children'].append(shared)  # Place shared preparation under its owning module.
            else:  # Equivalent preparation reuses the established branch.
                shared = groups[key]  # Retain the original displayed group identity.
                for left, right in zip(shared['children'], common['children']):  # Equal shapes ensure corresponding descendants align.
                    _merge_origins(left, right)  # Shared edits must reach every owning source line.
            shared['members'].append(case['id'])  # Track each case that still requires these steps.
            common['children'] = [{'text': '适用：' + shared['text'] + '（执行时仍须完成）', 'children': [], 'origins': []}]  # Replace repeated display with an explicit execution obligation.
            common['origins'] = []  # Generated applicability text is not a writable business leaf.
        target['children'].append(source)  # Keep each individual case after its shared preparation.
    for shared in groups.values():  # Final membership is available after all cases are projected.
        shared['children'].insert(0, {'text': '适用用例：' + '、'.join(case_name(batch, cid) for cid in shared['members']), 'children': [], 'origins': []})  # Display names while preserving internal member IDs.
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


def _fingerprint(node):
    return hashlib.sha256(json.dumps(_shape(node), ensure_ascii=False).encode('utf-8')).hexdigest()  # Bind the complete returned subtree.


def feedback_topics(markdown):
    """Inspect return topics for agent-side binding after business clarification."""
    result = []
    def visit(node, path):
        for child in node['children']:
            result.append(dict(title=child['text'], path=path, returned_digest=_fingerprint(child)))  # No inferred source identity.
            visit(child, path + [child['text']])
    visit(_parse(markdown.splitlines()[3:]), [])
    return result


def expand_feedback(batch, flat_markdown, incoming, case_bindings=None):
    """Expand edits through exact baseline bindings before existing feedback review."""
    header, expected = projection(batch, flat_markdown)
    lines = incoming.splitlines()
    if lines[:3] != header:
        raise ValueError('Markdown header/version must match initial display')
    actual = _parse(lines[3:])
    def legacy(node, path):  # Historic generated IDs remain explicit source identity within the exact baseline path.
        for case in batch['cases']:
            if path == case['module_path'] and node['text'].startswith(case['id'] + ' '):
                node['legacy_case_id'] = case['id']
                node['text'] = node['text'][len(case['id']) + 1:]
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
                matches = [n for n in remaining if (_fingerprint(n) == binding.get('returned_digest') if binding else n.get('legacy_case_id') == child['case_id'] or (not n.get('legacy_case_id') and _shape(n) == _shape(child)))]  # Legacy explicit IDs or complete bound content; never title/ordinal.
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
                    prefix = child['case_id'] + ' ' if child.get('case_id') else ''  # Restore internal identity for the existing scalar mapper.
                    output[origin + 3] = old[:len(old) - len(old.lstrip())] + '- ' + prefix + found['text']
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
