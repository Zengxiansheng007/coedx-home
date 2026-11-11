"""Thin feedback transition adapter for the existing sole Markdown record."""
import copy  # Isolate disposable projections.
import clarification as flow  # Preserve partial-answer and dependency behavior.
from feedback import prepare_feedback, apply_feedback, review_feedback  # Existing candidate-only workflow.


def transition(state, action, payload):  # Called only through the record's explicit action allowlist.
    if action == 'start_feedback':  # Save a new review chapter against this exact candidate.
        if state.get('feedback_pending'):  # Do not discard an unfinished proposal.
            raise ValueError('Finish current feedback before starting another proposal')  # Keep current answers.
        arguments = copy.deepcopy(payload)  # Remove record metadata before calling the pure API.
        reopened = set(arguments.pop('reopen_question_ids', []))  # Explicitly identified changed premises only.
        if not arguments.pop('source_ref', None):  # Actual feedback provenance is mandatory.
            raise ValueError('Feedback source required')  # Never infer a user's reply.
        batch = copy.deepcopy(state['batch'])  # Current replayed version is authoritative.
        batch['questions'] = copy.deepcopy(state['questions'])  # Carry stable answers and dependencies into review.
        arguments.setdefault('questions', copy.deepcopy(state['questions']))  # Unchanged rules retain their original signatures.
        questions = arguments['questions']  # Same graph retains stable identities and historical answers.
        if not reopened <= {q['id'] for q in questions}:  # Reject references outside this task graph.
            raise ValueError('Unknown feedback question to reopen')  # Do not guess affected scope.
        while True:  # Include only transitive dependencies of changed premises.
            expanded = reopened | {q['id'] for q in questions if set(q['depends_on']) & reopened}  # Exact graph closure.
            if expanded == reopened:  # Fixed point finishes the limited impact scan.
                break  # Independent decisions stay reusable.
            reopened = expanded  # Continue through direct dependencies.
        for question in questions:  # Reset active aspect answers, preserving their history.
            for target in question['target_paths']:  # Feedback may not hide writes to other selected cases.
                if len(target) < 3 or target[0] != 'cases' or type(target[1]) is not int or not 0 <= target[1] < len(batch['cases']) or batch['cases'][target[1]]['id'] != question['case_id']:  # Shared-data proposals use explicit changes and consumer tracking.
                    raise ValueError('Feedback answer target must belong to its affected case')  # Reject unrelated and unshown mutation paths.
            if question['id'] in reopened:  # Only changed decision paths reopen.
                question.update(stale=True, answered_parts={}, remaining_parts=list(question.get('answer_parts', {})))  # Old conditions remain in answer history.
            if not all(question.get(key) for key in ('evidence', 'boundary', 'example_kind')):  # Feedback follows normal persisted question completeness.
                raise ValueError('Feedback question needs evidence, boundary and example kind')  # No abbreviated follow-up cards.
        pending = prepare_feedback(batch, **arguments)  # All field/scope/version checks stay at the public seam.
        pending['persisted_feedback'] = True  # Retain this task's full stable graph after application.
        pending['decision_question_ids'] = [q['id'] for q in pending['grill']['questions'] if not flow._answered(q)]  # Changes only, not old unrelated decisions.
        result = copy.deepcopy(pending['grill'])  # Continue normal respond and summarize on this session.
        if state.get('coverage'):  # Retain recognized branches; require rereading against this feedback version.
            result['coverage'] = copy.deepcopy(state['coverage'])
            result['coverage']['revision'] = -1  # Prior closure is not current feedback coverage.
        result['feedback_proposal'] = pending['proposal_digest']  # Bind summary to exact proposed changes.
        pending['grill'] = copy.deepcopy(result)  # Freeze the same summary identity at application.
        result['feedback_pending'] = pending  # Disposable projection; events remain sole answer source.
        return result  # No candidate fields changed.
    if action == 'apply_feedback':  # Reuse the existing centralized confirmation gate.
        pending = copy.deepcopy(state.get('feedback_pending'))  # Reconstruct from the record, never separate JSON.
        if not pending:  # Avoid accidental normal-clarification application.
            raise ValueError('No feedback proposal is pending')  # Preserve the existing candidate.
        pending['grill'] = {k: copy.deepcopy(v) for k, v in state.items() if k not in ('feedback_pending', 'qa_record')}  # Current answers replace only the projection.
        old = {q['id']: q for q in state['feedback_pending']['grill']['questions']}  # Compare to the saved proposal frontier.
        pending['decision_question_ids'] = sorted(set(pending['decision_question_ids']) | {q['id'] for q in state['questions'] if q['id'] not in old or q['history'] != old[q['id']]['history']})  # Include actual later corrections only.
        result = apply_feedback(pending, payload)  # Existing scope and exact summary checks.
        session = copy.deepcopy(result['review_session'])  # Full updated cases await review.
        session.pop('feedback_pending', None)  # This proposal has been applied.
        session['feedback_result'] = result  # Keep existing review_feedback boundary available.
        return session  # Approval remains pending for affected cases.
    if action == 'review_feedback':  # Review the entire selected revised case at its new version.
        result = review_feedback(state['feedback_result'], payload)  # Existing review gate rejects stale versions.
        session = copy.deepcopy(result['review_session'])  # Retain precise approval scope.
        session['feedback_result'] = result  # Disposable rendering projection.
        return session  # Merge and execution remain separately authorized.
    if action in ('apply_summary', 'review') and state.get('feedback_pending'):  # Prevent ordinary actions from skipping pending proposal.
        raise ValueError('Pending feedback uses apply_feedback then review_feedback')  # One existing approval path.
    method = getattr(flow, action)  # Caller has already allowlisted normal actions.
    return method(state) if action == 'summarize' else method(state, payload)  # Preserve normal workflow behavior.
