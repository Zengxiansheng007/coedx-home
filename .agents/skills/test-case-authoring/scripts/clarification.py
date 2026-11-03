"""Public, pure batch clarification API. The skill supplies business judgments."""
import copy
from authoring import _credential_guard, _digest, render_batch


def _question_map(session):
    return {q['id']: q for q in session['questions']}


def _answered(q):
    return bool(q['history']) and not q.get('stale', False)


def _blocked(questions):
    blocked = {q['id'] for q in questions.values() if _answered(q) and q['history'][-1]['decision'] == 'deferred'}
    while True:
        expanded = blocked | {q['id'] for q in questions.values() if set(q['depends_on']) & blocked}
        if expanded == blocked:
            return blocked
        blocked = expanded


def _presentation(session):
    questions = _question_map(session)
    # Hold a round open for partial replies: newly eligible questions join only
    # after all questions already presented in that round have been answered.
    pending = [questions[qid] for qid in session.get('round_ids', [])
               if not _answered(questions[qid]) and qid not in _blocked(questions)]
    if not pending:
        pending = [q for q in questions.values() if not _answered(q) and
                   all(_answered(questions[d]) and questions[d]['history'][-1]['decision'] != 'deferred'
                       for d in q['depends_on'])]
        session['round_ids'] = [q['id'] for q in pending]
    session['round_questions'] = copy.deepcopy(pending)
    lines = []
    for q in pending:
        lines.extend([f"{q['id']}: {q['reason']}",
                      f"Affected: {q['case_id']}; checks: {', '.join(q['affected_checks'])}",
                      'Options: ' + '; '.join(q['options']),
                      'Recommendation: ' + q['recommendation'],
                      'Reason: ' + q['rationale'], 'Example: ' + q['example']])
    session['chat'] = '\n'.join(lines)
    return session


def start_grill(batch, questions):
    """Enrich all candidate doubts, plus dependent questions, before asking."""
    _credential_guard([batch, questions])
    questions = copy.deepcopy(questions)
    identities = [q['id'] for q in questions]
    if len(set(identities)) != len(identities):
        raise ValueError('Duplicate question identity')
    case_ids = {c['id'] for c in batch['cases']}
    previous = {q.get('id'): q for q in batch['questions'] if q.get('id')}
    for q in questions:
        for field in ('id', 'reason', 'recommendation', 'rationale', 'example', 'affected_checks'):
            if not q.get(field):
                raise ValueError('Incomplete chat question')
        if q['case_id'] not in case_ids or len(q['options']) < 2:
            raise ValueError('Invalid affected case or options')
        if any(d not in identities or d == q['id'] for d in q['depends_on']):
            raise ValueError('Unknown question dependency')
        old = previous.get(q['id'])
        signature = lambda value: {k: v for k, v in value.items() if k not in ('history', 'stale')}
        if old and signature(old) == signature(q) and _answered(old):
            q['history'] = copy.deepcopy(old['history'])
        else:
            q['history'] = copy.deepcopy(old.get('history', [])) if old else []
            q['stale'] = bool(q['history'])
    # A topological pass rejects cycles rather than hiding an unaskable question.
    visited = set()
    while len(visited) < len(questions):
        ready = {q['id'] for q in questions if set(q['depends_on']) <= visited}
        if ready <= visited:
            raise ValueError('Cyclic question dependency')
        visited |= ready
    if any(not any(q['case_id'] == old['case_id'] and q['field'] == old['field']
                   for q in questions) for old in batch['questions']):
        raise ValueError('Candidate doubt omitted')
    return _presentation({'batch': copy.deepcopy(batch), 'questions': questions,
                          'round_ids': [], 'revision': 0, 'summary': None,
                          'summary_confirmation': None, 'actions': []})


def respond(session, replies):
    """Record actual replies only; never edit candidate content during grill."""
    _credential_guard(replies)
    result = copy.deepcopy(session)
    questions = _question_map(result)
    for reply in replies:
        q = questions[reply['question_id']]
        if not _answered(q) and q['id'] not in result['round_ids']:
            raise ValueError('Question not yet presented')
        if reply['decision'] not in ('formal', 'provisional', 'deferred') or not reply.get('actual_reply', '').strip():
            raise ValueError('Explicit actual reply and three-way decision required')
        if reply['decision'] == 'provisional' and not reply.get('product_check'):
            raise ValueError('Provisional rule needs product verification condition')
        if reply['decision'] == 'deferred' and reply.get('updates'):
            raise ValueError('Deferred rule cannot update candidate content')
        if any(update['path'] not in q['target_paths'] for update in reply.get('updates', [])):
            raise ValueError('Update outside declared affected fields')
        descendants = {q['id']}
        while True:
            expanded = descendants | {item['id'] for item in questions.values() if set(item['depends_on']) & descendants}
            if expanded == descendants:
                break
            descendants = expanded
        for qid in descendants - {q['id']}:
            questions[qid]['stale'] = True
        q['history'].append(copy.deepcopy(reply))
        q['stale'] = False
    if replies:
        result['revision'] += 1
        result['summary'] = None
        result['summary_confirmation'] = None
    return _presentation(result)


def summarize(session):
    """Produce the exact decision snapshot to confirm in chat before updating."""
    result = copy.deepcopy(session)
    questions = _question_map(result)
    blocked = _blocked(questions)
    if any(not _answered(q) and q['id'] not in blocked for q in questions.values()):
        raise ValueError('Required questions remain unanswered')
    summary = {'content_version': result['batch']['content_version'], 'revision': result['revision'],
               'decisions': [{'question_id': q['id'], 'case_id': q['case_id'], 'field': q['field'],
                              'reply': q['history'][-1]} for q in questions.values() if _answered(q) and
                             not (set(q['depends_on']) & blocked)],
               'blocked_questions': [qid for qid in questions if qid in blocked and not _answered(questions[qid])],
               'blocked_cases': sorted({q['case_id'] for q in questions.values() if q['id'] in blocked})}
    summary['id'] = _digest(summary)
    result['summary'] = summary
    return result


def _patch(batch, update):
    path = update['path']
    if not isinstance(path, list) or len(path) < 3 or path[0] not in ('cases', 'data'):
        raise ValueError('Expected business content path')
    if type(path[1]) is not int or not 0 <= path[1] < len(batch[path[0]]):
        raise ValueError('Unknown content identity')
    if path[2] in ('id', 'review_status', 'rule_status', 'merge_status', 'execution_status',
                    'semantic_version', 'data_version', 'final_review', 'rule_decisions'):
        raise ValueError('Workflow and identity fields cannot be edited as business answers')
    if any(str(key).startswith('_') for key in path):
        raise ValueError('Invalid business content path')
    target = batch
    for part in path[:-1]:
        target = target[part]
    target[path[-1]] = copy.deepcopy(update['value'])


def _validate_content(batch):
    ids = [d['id'] for d in batch['data']]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate data identity')
    for item in batch['data']:
        if ('value' in item) == ('credential_ref' in item):
            raise ValueError('Data requires value or credential reference')
    for case in batch['cases']:
        if not case['title'] or len(case['module_path']) != 5 or not case['steps']:
            raise ValueError('Incomplete candidate case')
        for group in ('steps', 'common_preconditions', 'special_preconditions', 'special_postconditions'):
            for step in case.get(group, []):
                if not step['operation'] or any(ref not in ids for ref in step['data_refs']):
                    raise ValueError('Invalid step or data reference')
                for field in ('expected', 'verification'):
                    if any(not claim.get('text') or not claim.get('source') for claim in step[field]):
                        raise ValueError('Invalid business claim')
    _credential_guard(batch)


def apply_summary(session, confirmation):
    """Apply only an explicitly confirmed, current summary as one new version."""
    _credential_guard(confirmation)
    current = summarize(session)['summary']
    if session.get('summary') != current or confirmation.get('confirmed') is not True or not confirmation.get('actual_reply') or confirmation.get('summary_id') != current['id']:
        raise ValueError('Current summary needs explicit understanding confirmation')
    result = copy.deepcopy(session)
    batch = result['batch']
    before = copy.deepcopy(batch)
    updates = {}
    for decision in current['decisions']:
        if decision['case_id'] in current['blocked_cases']:
            continue
        for update in decision['reply'].get('updates', []):
            key = tuple(update['path'])
            if key in updates and updates[key] != update:
                raise ValueError('Conflicting confirmed updates require clarification')
            updates[key] = update
    for update in updates.values():
        _patch(batch, update)
    _validate_content(batch)
    batch['data_version'] = _digest(batch['data'])
    for case in batch['cases']:
        old = next(c for c in before['cases'] if c['id'] == case['id'])
        decisions = [d for d in current['decisions'] if d['case_id'] == case['id']]
        if decisions:
            case['rule_decisions'] = copy.deepcopy(decisions)
        # A complete supplied case has no clarification question to answer.
        # Only this explicit current-summary agreement can confirm that content;
        # initial conversion and a final-review request alone confer no approval.
        supplied_confirmation = not decisions and not any(
            q['case_id'] == case['id'] for q in result['questions']) and old['rule_status'] == 'unconfirmed'
        if supplied_confirmation:
            case['supplied_content_confirmation'] = copy.deepcopy(confirmation)
        case['rule_status'] = ('deferred' if case['id'] in current['blocked_cases'] else
                               'provisional' if any(d['reply']['decision'] == 'provisional' for d in decisions) else
                               'formal' if decisions or supplied_confirmation else old['rule_status'])
        case['data_version'] = batch['data_version']
        def semantic(value):
            return {k: v for k, v in value.items() if k not in ('semantic_version', 'review_status', 'final_review', 'review_history', 'merge_status', 'execution_status')}
        changed = semantic(old) != semantic(case)
        case['semantic_version'] = _digest(semantic(case)) if changed else old['semantic_version']
        if changed:
            case['review_status'] = 'pending'
            if 'final_review' in case:
                case.setdefault('review_history', []).append(case.pop('final_review'))
    batch['questions'] = copy.deepcopy(result['questions'])
    batch.setdefault('clarification_history', []).append({'summary': copy.deepcopy(current),
                                                        'confirmation': copy.deepcopy(confirmation)})
    batch['content_version'] = _digest({k: v for k, v in batch.items() if k != 'content_version'})
    result['summary_confirmation'] = copy.deepcopy(confirmation)
    result['applied_content_version'] = batch['content_version']
    result.update(render_batch(batch))
    return result


def review(session, final_review):
    """Record full-case review of the current version, independently of rules."""
    _credential_guard(final_review)
    batch = session['batch']
    if (not session.get('summary_confirmation') or not session.get('summary') or
            session['summary']['revision'] != session['revision'] or
            session.get('applied_content_version') != batch['content_version']):
        raise ValueError('Confirmed understanding and updated candidates required')
    if final_review.get('approved') is not True or not final_review.get('actual_reply') or final_review.get('content_version') != batch['content_version']:
        raise ValueError('Explicit current-version final review required')
    selected = final_review.get('case_ids', [])
    if not selected or not set(selected) <= {c['id'] for c in batch['cases']}:
        raise ValueError('Explicit known review scope required')
    if any(c['rule_status'] not in ('formal', 'provisional') for c in batch['cases'] if c['id'] in selected):
        raise ValueError('Deferred or unconfirmed cases cannot pass final review')
    result = copy.deepcopy(session)
    for case in result['batch']['cases']:
        if case['id'] in selected:
            if case.get('final_review') and case['final_review'] != final_review:
                case.setdefault('review_history', []).append(case['final_review'])
            case['final_review'] = copy.deepcopy(final_review)
            case['review_status'] = 'approved'
    result.update(render_batch(result['batch']))
    result['next_step'] = 'Recommend ui-test for formal scripts and complete verification; user starts it separately. P0 remains unmerged.'
    return result


def record_actions(session, actions):
    """Retain explicit requests, without running tests or merging anything."""
    _credential_guard(actions)
    result = copy.deepcopy(session)
    for action in actions:
        if action.get('kind') not in ('execution_start', 'merge_instruction') or not action.get('actual_reply'):
            raise ValueError('Explicit execution or merge request required')
        if action.get('content_version') != session['batch']['content_version'] or not action.get('case_ids') or not set(action['case_ids']) <= {c['id'] for c in session['batch']['cases']}:
            raise ValueError('Action requires current version and known scope')
        if action not in result['actions']:
            result['actions'].append(copy.deepcopy(action))
    return result
