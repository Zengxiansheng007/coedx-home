"""Public, pure batch clarification API. The skill supplies business judgments."""
import copy
from authoring import _credential_guard, _digest, render_batch


def _question_map(session):
    return {q['id']: q for q in session['questions']}


def _answered(q):
    return bool(q['history']) and not q.get('stale', False) and q['history'][-1]['decision'] in ('formal', 'provisional', 'deferred') and (not q.get('remaining_parts') or q['history'][-1]['decision'] == 'deferred')  # A partial answer is not a business disposition.


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
               if not _answered(questions[qid]) and qid not in _blocked(questions) and all(_answered(questions[d]) for d in questions[qid]['depends_on'])]  # A corrected premise can invalidate an already shown question.
    if not pending:
        pending = [q for q in questions.values() if not _answered(q) and
                   all(_answered(questions[d]) and questions[d]['history'][-1]['decision'] != 'deferred'
                       for d in q['depends_on'])]
        session['round_ids'] = [q['id'] for q in pending]
    session['round_questions'] = copy.deepcopy(pending)
    session['round_ids'] = [q['id'] for q in pending]  # Accept replies only to the current eligible presentation.
    lines = []
    for q in pending:
        q = copy.deepcopy(q)  # Follow-up presentation never rewrites the original question.
        if q['history'] and q['history'][-1]['decision'] == 'unknown':  # An unknown answer requires an actual disposition question.
            q.update(reason='尚未明确的规则如何处置？原问题：' + q['reason'], options=['补充或核实规则后回答', '明确搁置相关内容，可指定后续向产品核实', '提供明确暂定预期及产品核对条件并授权继续'], recommendation='能查明时先补充规则；否则明确选择本轮处置', rationale='不知道只说明业务答案未知，处置仍需你的实际决定', boundary='搁置仅暂停相关内容；暂定需要明确预期和核对条件，沉默不作确认', example_kind='hypothetical', example='例如暂时不确定超限处理，可以明确搁置超限用例；独立明确内容继续整理。')  # Full Chinese dialogue, no assumed choice.
        if q.get('remaining_parts'):  # Show only the unresolved aspects without discarding known facts.
            lines.append('已答：' + '；'.join(f'{q["answer_parts"][key]}：{value}' for key, value in q.get('answered_parts', {}).items()))  # Preserve partial interpretation.
            lines.append('仍需回答：' + '；'.join(q['answer_parts'][key] for key in q['remaining_parts']))  # Concrete follow-up scope.
        lines.extend([f"{q['id']}：{q['reason']}",  # Stable identity in normal Chinese prose.
                      f"适用对象：{q['case_id']}；核对项：{', '.join(q['affected_checks'])}",  # Retain affected scope.
                      '证据：' + str(q.get('evidence', '未提供，需核对来源')),  # Separate observations from suggestions.
                      '选项：' + '；'.join(q['options']) + '。也可自定义回答。',  # Preserve user agency.
                      '推荐：' + q['recommendation'],  # A recommendation is never an answer.
                      '理由：' + q['rationale'],  # Explain the current choice.
                      '代价与边界：' + q.get('boundary', '未确认规则保持待定'),  # State uncertainty explicitly.
                      ('假设例子：' if q.get('example_kind', 'hypothetical') == 'hypothetical' else '证据例子：') + q['example']])  # Mark provenance.
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
        if q.get('answer_parts') and (not isinstance(q['answer_parts'], dict) or any(not key or not value for key, value in q['answer_parts'].items())):  # Named business aspects must be meaningful.
            raise ValueError('Answer parts require stable names and descriptions')  # Reject ambiguous tracking.
        q.setdefault('answered_parts', {})  # Technical projection of actual supplied aspects.
        q.setdefault('remaining_parts', list(q.get('answer_parts', {})))  # Missing aspects start open.
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


def append_questions(session, questions):  # Add discoveries without restarting answered questions.
    result = copy.deepcopy(session)  # Leave caller and candidate untouched.
    if not questions or set(_question_map(session)) & {q['id'] for q in questions}:  # Stable IDs are never recycled.
        raise ValueError('New questions need unused identities')  # Corrections use respond instead.
    if any(q.get('history') or q.get('answered_parts') for q in questions):  # Discovery cannot invent answers.
        raise ValueError('New questions cannot contain answers')  # Wait for actual user input.
    for question in questions:  # Apply the same persisted presentation contract.
        if not all(question.get(key) for key in ('evidence', 'boundary', 'example_kind')) or question['example_kind'] not in ('hypothetical', 'evidence'):  # Explicit provenance.
            raise ValueError('Question needs evidence, boundary and example kind')  # Incomplete questions remain unsent.
    checked = start_grill(session['batch'], session['questions'] + questions)  # Reuse graph and field validation.
    result['questions'].extend(checked['questions'][len(session['questions']):])  # Retain original histories exactly.
    result['revision'] += 1  # Invalidate prior summaries and coverage observations.
    result['summary'] = result['summary_confirmation'] = None  # Discovery requires a new understanding snapshot.
    return _presentation(result)  # Save this returned presentation before sending.


def respond(session, replies):
    """Record actual replies only; never edit candidate content during grill."""
    _credential_guard(replies)
    result = copy.deepcopy(session)
    questions = _question_map(result)
    for reply in replies:
        q = questions[reply['question_id']]
        if not _answered(q) and q['id'] not in result['round_ids']:
            raise ValueError('Question not yet presented')
        if reply['decision'] not in ('formal', 'provisional', 'deferred', 'partial', 'unknown') or not reply.get('actual_reply', '').strip():
            raise ValueError('Explicit actual reply and three-way decision required')
        parts = reply.get('answered_parts', {})  # Agent maps actual words to declared aspects.
        if not isinstance(parts, dict) or any(key not in q.get('answer_parts', {}) or not str(value).strip() for key, value in parts.items()):  # Do not create undeclared answers.
            raise ValueError('Unknown or empty answer aspect')  # Preserve the current question scope.
        if reply['decision'] in ('partial', 'unknown') and reply.get('updates'):  # Incomplete answers are notes, not candidate changes.
            raise ValueError('Incomplete answers cannot propose content updates')  # Wait for an explicit complete disposition.
        q['answered_parts'] = dict(q.get('answered_parts', {}), **parts)  # Retain answers from earlier turns.
        q['remaining_parts'] = [key for key in q.get('answer_parts', {}) if key not in q['answered_parts']]  # Derive omissions precisely.
        if reply['decision'] in ('formal', 'provisional') and q['remaining_parts']:  # Explicit choice alone cannot invent missing behavior.
            raise ValueError('Required answer aspects remain unanswered')  # Continue the same stable question.
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
            questions[qid]['answered_parts'] = {}  # Old dependency answers remain in history, not active evidence.
            questions[qid]['remaining_parts'] = list(questions[qid].get('answer_parts', {}))  # Require reconfirmation after premise changes.
        q['history'].append(copy.deepcopy(reply))
        q['stale'] = False
        if not _answered(q) and q['id'] not in result['round_ids']:  # A correction may reopen the premise itself.
            result['round_ids'].append(q['id'])  # Show it alongside other independent unanswered questions.
    if replies:
        result['revision'] += 1
        result['summary'] = None
        result['summary_confirmation'] = None
    return _presentation(result)


def record_coverage(session, observation):  # Record Agent source review without claiming semantic proof.
    _credential_guard(observation)  # Source notes obey the existing privacy boundary.
    result = copy.deepcopy(session)  # Never modify the caller or candidate.
    scope = observation.get('scope', {})  # Authoring scope is separate from approved P0 validation.
    if set(scope.get('batch_cases', [])) != {c['id'] for c in session['batch']['cases']} or 'direct_dependencies' not in scope or not scope.get('p0_scope_ref'):  # Require explicit scope identities.
        raise ValueError('Coverage needs current batch, direct dependencies and full P0 scope reference')  # Display subsets cannot silently replace scope.
    if not observation.get('sources') or not observation.get('history_basis') or not observation.get('conclusion'):  # Require actual read observations.
        raise ValueError('Coverage needs source findings, history read basis and limitations')  # This is an audit record, not a truth oracle.
    if any(not source.get('ref') or not source.get('finding') for source in observation['sources']):  # Locate the original text and its disposition.
        raise ValueError('Each reread source needs a location and finding')  # Filenames alone are insufficient audit context.
    branches = observation.get('branches', [])  # Include unasked and fact-blocked themes.
    if len({b['id'] for b in branches}) != len(branches):  # Stable branch identity within the review.
        raise ValueError('Duplicate coverage branch')  # No hidden overwritten themes.
    previous = session.get('coverage', {}).get('branches', [])  # Retain previously recognized themes.
    if not {b['id'] for b in previous} <= {b['id'] for b in branches}:  # Disposal requires a recorded state, not omission.
        raise ValueError('Recognized coverage branch omitted')  # Preserve unresolved facts.
    questions = _question_map(session)  # User decisions come from existing actual answers.
    for branch in branches:  # Check structure and disposition provenance only.
        if not all(branch.get(key) for key in ('id', 'topic', 'source', 'basis', 'next_step')) or 'dependencies' not in branch:  # Complete operational context.
            raise ValueError('Incomplete coverage branch')  # Agent must supply meaningful observations.
        if branch.get('status') not in ('unchecked', 'fact_pending', 'question_pending', 'waiting', 'resolved', 'deferred', 'excluded', 'not_applicable'):  # Separate facts and decisions.
            raise ValueError('Unknown coverage disposition')  # No ambiguous completion label.
        if branch['status'] in ('deferred', 'excluded'):  # Explicit user scope decisions are not Agent findings.
            question = questions.get(branch.get('question_id'))  # Same task's actual Q history.
            if not question or not _answered(question) or question['history'][-1]['decision'] != ('deferred' if branch['status'] == 'deferred' else 'formal'):  # Do not manufacture authorization.
                raise ValueError('Coverage disposition requires an actual matching question decision')  # Semantic scope matching remains Agent responsibility.
    result['coverage'] = dict(copy.deepcopy(observation), revision=session['revision'])  # Any subsequent reply/discovery requires recheck.
    result['summary'] = result['summary_confirmation'] = None  # New findings need a fresh snapshot.
    return result  # Persist through the sole Q&A adapter.


def summarize(session):
    """Produce the exact decision snapshot to confirm in chat before updating."""
    result = copy.deepcopy(session)
    questions = _question_map(result)
    blocked = _blocked(questions)
    coverage = result.get('coverage')  # Legacy pure callers retain their existing computation contract.
    if coverage and (coverage['revision'] != result['revision'] or any(b['status'] in ('unchecked', 'fact_pending', 'question_pending', 'waiting') for b in coverage['branches'])):  # Explicit unresolved observations never disappear with an empty frontier.
        raise ValueError('Coverage recheck or unresolved source disposition required')  # Live Skill must actually reread sources before recording closure.
    if any(not _answered(q) and q['id'] not in blocked for q in questions.values()):
        raise ValueError('Required questions remain unanswered')
    summary = {'content_version': result['batch']['content_version'], 'revision': result['revision'],
               'decisions': [{'question_id': q['id'], 'case_id': q['case_id'], 'field': q['field'],
                              'answered_parts': copy.deepcopy(q.get('answered_parts', {})),  # Carry earlier partial answers into the confirmed snapshot.
                              **({'rule_id': q['rule_id']} if q.get('rule_id') else {}),
                              'reply': q['history'][-1]} for q in questions.values() if _answered(q) and
                             not (set(q['depends_on']) & blocked)],
               'blocked_questions': [qid for qid in questions if qid in blocked and not _answered(questions[qid])],
               'blocked_cases': sorted({q['case_id'] for q in questions.values() if q['id'] in blocked})}
    if coverage:  # Preserve deferred/excluded facts and actual review scope in the confirmed snapshot.
        summary['coverage'] = copy.deepcopy(coverage)  # Disposition does not mean a known business rule.
    summary['id'] = _digest(summary)
    if session.get('feedback_proposal'):  # Exact textual proposals are part of feedback confirmation.
        summary['feedback_proposal'] = session['feedback_proposal']  # Prevent reuse for another proposal on the same version.
        summary['id'] = _digest({k: v for k, v in summary.items() if k != 'id'})  # Bind new proposal identity.
    result['summary'] = summary
    return result


def _patch(batch, update):
    path = update['path']
    if not isinstance(path, list) or len(path) < 3 or path[0] not in ('cases', 'data'):
        raise ValueError('Expected business content path')
    if type(path[1]) is not int or not 0 <= path[1] < len(batch[path[0]]):
        raise ValueError('Unknown content identity')
    if path[2] in ('id', 'review_status', 'rule_status', 'merge_status', 'execution_status',
                    'semantic_version', 'data_version', 'final_review', 'rule_decisions',
                    'active_rule_decisions', 'rule_decision_history', 'feedback_rule_history'):
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
        if not case['title'] or len(case['module_path']) < 5 or not case['steps']:
            raise ValueError('Incomplete candidate case')
        for group in ('steps', 'common_preconditions', 'special_preconditions', 'special_postconditions'):
            for step in case.get(group, []):
                if not step['operation'] or any(ref not in ids for ref in step['data_refs']):
                    raise ValueError('Invalid step or data reference')
                for field in ('expected', 'verification'):
                    if any(not claim.get('text') or not claim.get('source') for claim in step[field]):
                        raise ValueError('Invalid business claim')
    _credential_guard(batch)


def _apply_rule_decisions(case, decisions, *, blocked=False, supplied=False, product=None):
    """Keep independent rules, even when their business fields coincide.

    A title answer cannot discharge a save-policy condition. Legacy unscoped
    conditions stay active until an explicit, unambiguous product reconciliation.
    """
    def key(d):
        if d.get('rule_id'):
            return ('rule', d['rule_id'])
        if d.get('question_id'):
            return ('question', d['question_id'])
        # No identity means no safe supersession. Preserve distinct legacy
        # conditions rather than guessing identity from their field location.
        return ('legacy', _digest(d))
    active = copy.deepcopy(case.get('active_rule_decisions',
                                   case.get('rule_decisions', []) + case.get('feedback_rule_history', [])))
    indexed = {key(d): d for d in active}
    if not indexed and case['rule_status'] in ('provisional', 'deferred'):
        indexed[('legacy', 'unscoped')] = {'reply': {'decision': case['rule_status'],
            'actual_reply': 'Existing rule decision requires clarification',
            'product_check': 'Existing product verification condition requires clarification'}}
    for d in decisions:
        indexed[key(d)] = copy.deepcopy(d)
    if product and decisions and all(d['reply']['decision'] == 'formal' for d in decisions) and not blocked:
        rule = product['rule_id']
        for identity, d in list(indexed.items()):
            # Explicit rule links identify the condition. Older unscoped cases
            # may only resolve when exactly this one product rule is referenced.
            if (d.get('rule_id') == rule or d.get('question_id') == rule or
                    (identity[0] == 'legacy' and not d.get('field') and
                     len([k for k in indexed if k[0] == 'legacy']) == 1 and case.get('rule_refs') == [rule])):
                indexed[identity] = dict(d, reply={'decision': 'formal',
                    'actual_reply': product['actual_reply'], 'source_ref': product['source_ref']})
    if indexed or 'active_rule_decisions' in case:
        case['active_rule_decisions'] = list(indexed.values())
    if decisions:
        case.setdefault('rule_decisions', copy.deepcopy(decisions))
        case.setdefault('rule_decision_history', []).extend(copy.deepcopy(decisions))
    states = [d['reply']['decision'] for d in indexed.values()]
    case['rule_status'] = ('deferred' if blocked or 'deferred' in states else
                           'provisional' if 'provisional' in states else
                           'formal' if decisions or supplied else case['rule_status'])


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
        # A complete supplied case has no clarification question to answer.
        # Only this explicit current-summary agreement can confirm that content;
        # initial conversion and a final-review request alone confer no approval.
        supplied_confirmation = not decisions and not any(
            q['case_id'] == case['id'] for q in result['questions']) and old['rule_status'] == 'unconfirmed'
        if supplied_confirmation:
            case['supplied_content_confirmation'] = copy.deepcopy(confirmation)
        _apply_rule_decisions(case, decisions, blocked=case['id'] in current['blocked_cases'],
                              supplied=supplied_confirmation)
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
    result['next_step'] = ('Recommend user-started authoring merge of the reviewed P1/P2 scope; '
                           'after merge recommend separately user-started ui-test. Cases remain unmerged and not run.'
                           if batch['stage'] == 'P1/P2' else
                           'Recommend ui-test for formal scripts and complete verification; user starts it separately. P0 remains unmerged.')
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
