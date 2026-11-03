"""Baseline-bound feedback into shared authoring content, never formal assets."""
import copy
import html

from authoring import _credential_guard, _digest
from clarification import start_grill, summarize, review, _validate_content
from scoped_review import _render, _references, GROUPS, TECHNICAL_FIELDS


PROTECTED = TECHNICAL_FIELDS | frozenset(('module_path', 'data_refs', 'credential_ref',
    'review_status', 'rule_status', 'merge_status', 'execution_status', 'final_review',
    'review_history', 'rule_decisions', 'supplied_content_confirmation'))


def _leaves(value, path=()):
    if isinstance(value, dict):
        for key, child in value.items():
            if key not in PROTECTED:
                yield from _leaves(child, (*path, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _leaves(child, (*path, index))
    elif isinstance(value, str):
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
    if _digest({k: base[k] for k in ('cases', 'data', 'selection')}) != base['copy_version']:
        raise ValueError('Initial displayed baseline changed')
    result = copy.deepcopy(batch)
    for key in ('cases', 'data', 'selection'):
        result[key] = copy.deepcopy(base[key])
    # The original generated version is captured when feedback is first read.
    result['content_version'] = batch.get('initial_display_version', batch['content_version'])
    result['questions'] = copy.deepcopy(batch.get('initial_display_questions', batch['questions']))
    return result


def _markdown_changes(batch, markdown):
    """Read scalar edits of the generated hierarchy; reject structural ambiguity.

    Probe the actual renderer to bind each visible leaf to its existing business
    path. This mapping is derived, not another maintained content source.
    """
    initial = _initial(batch)
    incoming = markdown.splitlines()
    # Later review files still map through the immutable initial semantic
    # baseline in prepare_feedback, while their layout includes accepted history.
    if len(incoming) > 1 and incoming[1] == '- 版本：' + batch['content_version']:
        initial = copy.deepcopy(batch)
        initial['cases'] = [c for c in initial['cases'] if c.get('feedback_disposition') != 'excluded_this_round']
    original = _render(initial)['xmind_markdown'].splitlines()
    if incoming[:3] != original[:3]:
        raise ValueError('Markdown header/version must match initial display')
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
            result[cid] = lines[start:end]
        return result
    before, after = blocks(original), blocks(incoming)
    changes, missing = [], list(before.keys() - after.keys())
    all_bindings = {}
    for collection in ('cases', 'data'):
        for index, item in enumerate(initial[collection]):
            for path in _leaves(item):
                probe = copy.deepcopy(initial)
                marker = 'TCAFEEDBACKLEAFMARKER'
                _set(probe[collection][index], path, marker)
                rendered = blocks(_render(probe)['xmind_markdown'].splitlines())
                for cid, lines in rendered.items():
                    for line_index, line in enumerate(lines):
                        if marker in line:
                            if line.count(marker) != 1:
                                continue
                            prefix, suffix = line.split(marker)
                            all_bindings.setdefault((cid, line_index), []).append(
                                (collection, item['id'], list(path), prefix, suffix))
    seen = {}
    for cid, lines in after.items():
        if len(lines) != len(before[cid]):
            raise ValueError('Structural Markdown edit needs explicit chat interpretation')
        for index, (old, new) in enumerate(zip(before[cid], lines)):
            if old == new:
                continue
            bindings = all_bindings.get((cid, index), [])
            if len(bindings) != 1:
                raise ValueError('Unmapped Markdown edit')
            collection, identity, path, prefix, suffix = bindings[0]
            if not new.startswith(prefix) or (suffix and not new.endswith(suffix)):
                raise ValueError('Markdown structure or labels changed')
            value = new[len(prefix):len(new)-len(suffix) if suffix else None]
            value = html.unescape(value.replace('<br>', '\n'))
            key = (collection, identity, tuple(path))
            if key in seen and seen[key] != value:
                raise ValueError('Repeated shared data edits disagree')
            seen[key] = value
    # Every repeated projection must agree, including occurrences left unchanged.
    for key, value in seen.items():
        for (cid, index), bindings in all_bindings.items():
            if cid not in after:
                continue
            for col, identity, path, prefix, suffix in bindings:
                if (col, identity, tuple(path)) == key:
                    line = after[cid][index]
                    actual = html.unescape(line[len(prefix):len(line)-len(suffix) if suffix else None].replace('<br>', '\n'))
                    if actual != value:
                        raise ValueError('Repeated shared data edits disagree')
        changes.append({'collection': key[0], 'id': key[1], 'path': list(key[2]), 'value': value})
    return changes, missing


def _question(qid, cid, field, reason, checks):
    return {'id': qid, 'case_id': cid, 'field': field, 'reason': reason,
            'affected_checks': checks or ['scope-review'], 'target_paths': [], 'depends_on': [],
            'options': ['formal', 'provisional', 'deferred'],
            'recommendation': 'Confirm only the intended business change',
            'rationale': 'Changed content needs explicit business understanding and new final review',
            'example': 'SIMULATED: use the revised expected result; keep product check if provisional'}


def prepare_feedback(batch, channel, *, actual_reply, changes=None, markdown=None,
                     removed_case_ids=None, deletion_decisions=None):
    """Locate proposed changes against first display and later accepted content."""
    _credential_guard([batch, actual_reply, changes, markdown, deletion_decisions])
    if not actual_reply or channel not in ('chat', 'markdown'):
        raise ValueError('Actual feedback and supported channel required')
    initial = _initial(batch)
    if channel == 'markdown':
        if changes or removed_case_ids or markdown is None:
            raise ValueError('Read Markdown itself, not a substituted interpretation')
        changes, removed_case_ids = _markdown_changes(batch, markdown)
    normalized, affected = [], set()
    for change in changes or []:
        collection, identity, path = change['collection'], change['id'], change['path']
        if collection not in ('cases', 'data') or not path or any(p in PROTECTED for p in path if isinstance(p, str)):
            raise ValueError('Identity, reference and workflow changes need a new scoped baseline')
        base = next((v for v in initial[collection] if v['id'] == identity), None)
        current = next((v for v in batch[collection] if v['id'] == identity), None)
        if base is None or current is None or tuple(path) not in set(_leaves(base)):
            raise ValueError('Unknown displayed business field')
        old, accepted, new = _get(base, path), _get(current, path), change['value']
        if not isinstance(new, str) or not new.strip():
            raise ValueError('Nonempty business text required')
        if old == new or accepted == new:
            continue
        if accepted != old:
            raise ValueError('Feedback conflicts with an accepted later change; clarify')
        normalized.append(dict(change, before=old, accepted=accepted))
        affected.update([identity] if collection == 'cases' else
                        [c['id'] for c in batch['cases'] if identity in _references(c)])
    unique = {(c['collection'], c['id'], tuple(c['path'])) for c in normalized}
    if len(unique) != len(normalized):
        raise ValueError('Duplicate feedback field')
    deletions = []
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
    proposal_digest = _digest({'changes': normalized, 'deletions': deletions})
    for index, change in enumerate(normalized):
        ids = [change['id']] if change['collection'] == 'cases' else [c['id'] for c in batch['cases'] if change['id'] in _references(c)]
        for cid in ids:
            questions.append(_question(f'feedback-{proposal_digest}-{index}-{cid}', cid, '/'.join(map(str, change['path'])),
                                       'Review business change: ' + repr(change['before']) + ' → ' + repr(change['value']) +
                                       '; accepted current value: ' + repr(change['accepted']), []))
    for q in questions:
        if q['field'] == 'deletion':
            q['id'] += '-' + proposal_digest
    for index, doubt in enumerate(batch['questions']):
        questions.append(_question('existing-' + str(index), doubt['case_id'], doubt['field'], doubt['reason'], []))
    return {'batch': copy.deepcopy(batch), 'channel': channel, 'actual_reply': actual_reply,
            'base_version': batch['content_version'], 'changes': normalized, 'deletions': deletions,
            'affected_case_ids': sorted(affected), 'proposal_digest': proposal_digest,
            'grill': start_grill(batch, questions)}


def _views(batch):
    displayed = copy.deepcopy(batch)
    displayed['cases'] = [c for c in displayed['cases'] if c.get('feedback_disposition') != 'excluded_this_round']
    return _render(displayed)


def apply_feedback(pending, confirmation, deletion_decisions=None):
    """Apply one explicitly agreed summary atomically; all effects stay candidate-side."""
    _credential_guard([pending, confirmation, deletion_decisions])
    current = summarize(pending['grill'])['summary']
    if pending['proposal_digest'] != _digest({'changes': pending['changes'], 'deletions': pending['deletions']}):
        raise ValueError('Feedback proposal changed after presentation')
    if (pending['grill'].get('summary') != current or confirmation.get('confirmed') is not True or
            not confirmation.get('actual_reply') or confirmation.get('summary_id') != current['id'] or
            pending['batch'] != pending['grill']['batch'] or pending['base_version'] != pending['batch']['content_version']):
        raise ValueError('Current feedback summary needs explicit agreement')
    batch = copy.deepcopy(pending['batch'])
    batch.setdefault('initial_display_version', pending['base_version'])
    batch.setdefault('initial_display_questions', copy.deepcopy(batch['questions']))
    blocked = set(current['blocked_cases'])
    affected = set(pending['affected_case_ids']) - blocked
    for change in pending['changes']:
        consumers = {change['id']} if change['collection'] == 'cases' else {c['id'] for c in batch['cases'] if change['id'] in _references(c)}
        if consumers & blocked:
            continue
        target = next(v for v in batch[change['collection']] if v['id'] == change['id'])
        _set(target, change['path'], change['value'])
        parent = _get(target, change['path'][:-1])
        if isinstance(parent, dict) and 'source' in parent:
            parent['source'] = 'user_decision'
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
    validation = copy.deepcopy(batch)
    for case in validation['cases']:
        if len(case['module_path']) < 5:
            raise ValueError('Complete module path required')
        case['module_path'] = case['module_path'][:5]
    _validate_content(validation)
    batch['data_version'] = _digest(batch['data'])
    for case in batch['cases']:
        if case['id'] not in affected | blocked:
            continue
        case['data_version'] = batch['data_version']
        case['review_status'] = 'pending'
        if 'final_review' in case:
            case.setdefault('review_history', []).append(case.pop('final_review'))
        decisions = [d for d in current['decisions'] if d['case_id'] == case['id']]
        if case['id'] in blocked:
            case['rule_status'] = 'deferred'
        elif any(d['reply']['decision'] == 'provisional' for d in decisions):
            case['rule_status'] = 'provisional'
        elif decisions:
            case['rule_status'] = 'formal'
        case.setdefault('feedback_rule_history', []).extend(copy.deepcopy(decisions))
        case['semantic_version'] = _digest({k: v for k, v in case.items() if k != 'semantic_version'})
    for check in batch.get('coverage', []):
        linked = [c for c in batch['cases'] if c['id'] in check.get('case_ids', [])]
        if not any(c['id'] in affected for c in linked):
            continue
        check.setdefault('history', []).append({k: copy.deepcopy(v) for k, v in check.items() if k != 'history'})
        check['status'] = 'pending_review'
        check['expected_summary'] = '; '.join(claim['text'] for c in linked for group in GROUPS for s in c.get(group, []) for claim in s['expected'])
        check['verification_summary'] = '; '.join(claim['text'] for c in linked for group in GROUPS for s in c.get(group, []) for claim in s['verification'])
        check['data_refs'] = sorted(set().union(*[_references(c) for c in linked]))
    batch.setdefault('feedback_history', []).append({'channel': pending['channel'], 'actual_reply': pending['actual_reply'],
        'summary': current, 'confirmation': confirmation, 'changes': pending['changes'], 'deletions': pending['deletions']})
    # Keep enriched original doubts and their actual answer history so the
    # existing grill can reuse identical decisions on later feedback rounds.
    batch['questions'] = [copy.deepcopy(q) for q in pending['grill']['questions']
                          if q['id'].startswith('existing-')]
    batch['content_version'] = _digest({k: v for k, v in batch.items() if k != 'content_version'})
    result = _views(batch)
    result['batch'] = batch
    result['changes'] = copy.deepcopy(pending['changes'])
    result['review_notes'] = 'Candidate feedback only; final review required. Formal source synchronization and execution remain pending.\n' + str(batch.get('coverage', []))
    session = copy.deepcopy(pending['grill'])
    session.update(batch=copy.deepcopy(batch), summary_confirmation=copy.deepcopy(confirmation),
                   applied_content_version=batch['content_version'])
    result['review_session'] = session
    return result


def review_feedback(result, final_review):
    """Use the existing batch final-review gate for the complete revised content."""
    if result['batch'] != result['review_session']['batch']:
        raise ValueError('Revised content changed after summary application')
    selected = final_review.get('case_ids', [])
    if any(c.get('feedback_disposition') == 'excluded_this_round' for c in result['batch']['cases'] if c['id'] in selected):
        raise ValueError('Excluded content is outside this round review')
    session = review(result['review_session'], final_review)
    updated = copy.deepcopy(result)
    updated.update(_views(session['batch']))
    updated['batch'] = session['batch']
    updated['review_session'] = session
    updated['next_step'] = 'Candidate review recorded. Formal mapping remains pending; user starts execution or merge separately.'
    return updated
