"""One Markdown task record; technical state is replayed from its actual events."""
import copy  # Never alter caller data.
import json  # Store lossless event payloads inside the sole Markdown source.
import os  # Replace completed records atomically.
import re  # Locate explicitly delimited event blocks.
import tempfile  # Prepare replacement on the same filesystem.
import hashlib  # Bind actual source bytes during handoff.
from pathlib import Path  # Canonical task location.
import clarification as flow  # Reuse existing decisions and review gates.
from authoring import _credential_guard  # Preserve existing privacy checks.


def _replay(events):  # Technical projection has no independently editable answers.
    first = events[0]  # Initial event binds task, stage and candidate version.
    state = flow.start_grill(first['batch'], first['questions'])  # Existing public seam.
    for event in events[1:]:  # Preserve correction order and original replies.
        if event['action'] in ('record_note', 'record_context'):  # Report facts/questions and raw replies do not edit candidates.
            continue  # A note grants no business decision.
        if event['action'] == 'start_extension':  # Reuse the same public P0-gated phase transition during replay.
            state = _extension_stage(state, event['payload'])  # Historical questions remain in this MD.
            continue  # New stage already supplied its live projection.
        if event['action'] not in ('record_coverage', 'append_questions', 'respond', 'summarize', 'apply_summary', 'review', 'record_actions', 'start_feedback', 'apply_feedback', 'review_feedback'):  # Validate feedback replay too.
            raise ValueError('Unknown recorded action')  # Never dispatch arbitrary names from disk.
        from feedback_record import transition  # Lazy adapter avoids import cycles.
        prior = state.get('prior_stages')  # Feedback returns a fresh projection of the current stage.
        state = transition(state, event['action'], event['payload'])  # Existing workflows share the same event source.
        if prior is not None:  # Keep older P0 questions visible through later feedback.
            state['prior_stages'] = prior  # These remain projections of earlier same-file events.
    state['qa_record'] = {'task_id': first['task_id'], 'path': first['path'], 'event_count': len(events)}  # Source binding only.
    return state  # Callers receive a disposable projection.


def _extension_stage(state, payload):  # Thin adapter around the existing full-scope P0 gate.
    from extension import build_extension  # No second P1/P2 builder or evidence rule.
    if state.get('feedback_pending') or not payload.get('source_ref'):  # Preserve unfinished feedback and actual provenance.
        raise ValueError('Finish feedback and supply extension source provenance')  # Never silently abandon a proposal.
    batch = build_extension(**payload['envelope'], mode=payload.get('mode', 'production'))['batch']  # Recheck the established evidence gate.
    previous = state.get('prior_stages', []) + [{k: copy.deepcopy(v) for k, v in state.items() if k not in ('prior_stages', 'qa_record')}]  # Derived history stays recoverable.
    used = {q['id'] for stage in previous for q in stage['questions']}  # Permanent question anchors cannot be reused.
    for question in payload['questions']:  # New candidate doubts still require complete presentation.
        if question['id'] in used or not all(question.get(k) for k in ('evidence', 'boundary', 'example_kind')):  # Preserve unique provenance.
            raise ValueError('Extension needs new question IDs and complete presentation')  # Old answers must be referenced, not cloned.
    result = flow.start_grill(batch, payload['questions'])  # Existing candidate and dependency validation.
    result['prior_stages'] = previous  # Recovery can inspect earlier questions and unresolved scope.
    return result  # No new business answer or case approval is invented.


def _render(events):  # Human text and machine payload share one authoritative file.
    lines = ['# 任务问答记录', '', '实际答复以本文件事件原文为准；候选及程序状态由此推导。', '']  # Explain source ownership.
    for index, event in enumerate(events):  # Append stages within the same task file.
        lines.extend([f'## 记录 {index + 1} · {event["action"]}', '', event.get('display', ''), ''])  # Full saved question precedes sending.
        for reply in event.get('payload', []) if event['action'] == 'respond' else []:  # Stable reply anchors.
            lines.extend([f'<a id="{reply["question_id"]}-A{reply["answer_version"]}"></a>', f'原话：{reply["actual_reply"]}', f'来源：{reply["source_ref"]}', f'归纳：{reply["interpretation"]}', ''])  # Visible actual words.
        payload = json.dumps(event, ensure_ascii=False, sort_keys=True).replace('`', '\\u0060')  # Prevent fence injection.
        lines.extend(['```tca-event', payload, '```', ''])  # Lossless single-file record.
    return '\n'.join(lines)  # Deterministic representation detects manual divergence.


def _load(path):  # Read and check both prose and payload before any transition.
    text = path.read_text(encoding='utf-8')  # Never trust an in-memory answer cache.
    events = [json.loads(value) for value in re.findall(r'^```tca-event\n(.*?)\n```$', text, re.M | re.S)]  # Explicit record format.
    if not events or _render(events) != text or events[0]['path'] != str(path.resolve()):  # Refuse changed sources or copied task records.
        raise ValueError('Q&A record differs from its source; reconcile before updating')  # Keep conflicting evidence intact.
    return events  # Events alone determine state.


def read_record(path):  # Public read-back boundary.
    return _replay(_load(Path(path)))  # No separate session JSON required.


def read_notes(path):  # Report selection resumes from the same authoritative MD.
    return copy.deepcopy([event for event in _load(Path(path)) if event['action'] in ('record_note', 'record_context')])  # Disposable source projection, not a second answer file.


def checkpoint_record(path, stage, candidate_path, sources, next_step):  # Save recovery metadata inside the existing sole MD.
    state = read_record(path)  # Never checkpoint a caller's cached answers.
    candidate_path = Path(candidate_path).resolve()  # Stable actual artifact location.
    candidate = json.loads(candidate_path.read_text(encoding='utf-8-sig'))  # Inspect the supplied candidate itself.
    if candidate != state['batch']:  # Version equality alone cannot establish matching content.
        raise ValueError('Candidate differs from Q&A projection; reconcile affected content first')  # No automatic overwrite.
    if stage not in ('p0', 'report', 'p1-p2', 'review') or not next_step or not sources:  # TCA stages, not another workflow.
        raise ValueError('Recovery needs a TCA stage, actual sources and next action')  # No empty handoff.
    known = {q['id'] for q in state['questions']}  # Dependencies use permanent question IDs.
    bindings = []  # Store identities and digests, never another business answer.
    for source in sources:  # Every supplied source is actually read.
        source_path = Path(source['path']).resolve()  # Explicit authorized source path.
        ids = source.get('question_ids', [])  # Empty means stage-wide evidence, not a guessed question.
        if not set(ids) <= known:  # Fail when the proposed mapping is not from this task.
            raise ValueError('Unknown source question binding')  # Keep the prior checkpoint intact.
        bindings.append(dict(path=str(source_path), sha256=hashlib.sha256(source_path.read_bytes()).hexdigest(), question_ids=ids))  # Actual byte identity.
    recovery = dict(stage=stage, candidate_path=str(candidate_path), sources=bindings, next_step=next_step, content_version=candidate['content_version'])  # Technical recovery location only.
    display = '恢复位置：' + stage + '\n候选：' + str(candidate_path) + '\n下一步：' + next_step  # Human-readable stage chapter.
    return advance_record(path, 'record_context', dict(display=display, basis=[b['path'] for b in bindings], recovery=recovery))  # Reuse atomic save/read-back.


def resume_record(path):  # Fresh context reads actual MD, candidate and required sources.
    events = _load(Path(path))  # Validate the sole record before trusting metadata.
    state = _replay(events)  # Derived technical state has no independent business authority.
    checkpoints = [e['payload']['recovery'] for e in events if e['action'] == 'record_context' and 'recovery' in e['payload']]  # Existing events remain compatible.
    if not checkpoints:  # Legacy records still have valid replay and notes.
        return dict(state=state, recovery=None, conflicts=[], needs_checkpoint=True)  # Agent must inspect actual candidate/sources before advancing.
    recovery = copy.deepcopy(checkpoints[-1])  # Latest saved recovery location only.
    conflicts = []  # Report affected differences without mutating either source.
    candidate_path = Path(recovery['candidate_path'])  # Read the actual candidate from the handoff.
    try:  # Missing files are evidence gaps, never success.
        candidate = json.loads(candidate_path.read_text(encoding='utf-8-sig'))  # Do not trust a stored version label.
        if candidate != state['batch']:  # Compare complete content including decisions and approvals.
            conflicts.append(dict(kind='candidate', path=str(candidate_path), reason='Candidate differs from current Q&A projection', case_ids=[c['id'] for c in state['batch']['cases'] if c not in candidate.get('cases', [])]))  # Scope case differences explicitly.
    except (OSError, ValueError, TypeError, AttributeError) as error:  # Only artifact-read problems are classified here.
        conflicts.append(dict(kind='candidate', path=str(candidate_path), reason=type(error).__name__, case_ids=[]))  # Unknown scope requires evidence inspection.
    for source in recovery['sources']:  # Recheck current source bytes, not hidden conversation memory.
        try:  # Preserve missing and changed source identities.
            changed = hashlib.sha256(Path(source['path']).read_bytes()).hexdigest() != source['sha256']  # Exact source evidence.
        except OSError:  # Inaccessible source cannot count as verified.
            changed = True  # Agent reports the gap and its dependent work.
        if changed:  # Unrelated source bindings stay valid.
            conflicts.append(dict(kind='source', path=source['path'], question_ids=source['question_ids'], reason='Source changed or unavailable'))  # No inferred business answer.
    return dict(state=state, recovery=recovery, conflicts=conflicts, needs_checkpoint=False)  # Read-only diagnostic; Agent resolves actual meaning.


def start_record(path, task_id, batch, questions):  # Save complete questions before exposing chat.
    path = Path(path).resolve()  # Bind one canonical path for the task.
    if not task_id or batch.get('qa_record'):  # Existing tasks must resume their bound record.
        raise ValueError('Use the existing task Q&A path')  # Avoid accidental second answer source.
    for question in questions:  # Require presentation evidence for this persisted entry.
        if not all(question.get(key) for key in ('evidence', 'boundary', 'example_kind')):  # Unknown evidence must state its gap.
            raise ValueError('Question needs evidence, boundary and example kind')  # Incomplete questions stay unsent.
        if question['example_kind'] not in ('hypothetical', 'evidence'):  # Distinguish examples from facts.
            raise ValueError('Unknown example provenance')  # No implied factual examples.
    state = flow.start_grill(batch, questions)  # Validate all existing graph and candidate constraints.
    events = [dict(action='start', task_id=task_id, path=str(path), batch=batch, questions=questions, display=state['chat'])]  # Only initial seed plus events.
    _credential_guard(events)  # Check metadata as well as candidate text.
    with path.open('x', encoding='utf-8', newline='\n') as stream:  # Never overwrite an existing task.
        stream.write(_render(events))  # Save before returning any user-facing question.
    return read_record(path)  # Read-back failure stops the conversation transition.


def advance_record(path, action, payload=None):  # Persist real user actions through existing public gates.
    path = Path(path).resolve()  # Keep the task binding stable.
    if action not in ('start_extension', 'record_coverage', 'append_questions', 'record_context', 'record_note', 'respond', 'summarize', 'apply_summary', 'review', 'record_actions', 'start_feedback', 'apply_feedback', 'review_feedback'):  # Explicit existing phase entries only.
        raise ValueError('Unknown Q&A action')  # Refuse unsupported effects.
    events = _load(path)  # Always start from the sole answer record.
    state = _replay(events)  # Reconstruct existing technical state.
    payload = copy.deepcopy(payload)  # Add provenance without mutating caller objects.
    if action == 'append_questions':  # Old phase IDs remain permanently reserved.
        used = {q['id'] for stage in state.get('prior_stages', []) for q in stage['questions']}  # Same task history.
        if any(q['id'] in used for q in payload):  # Existing flow checks current-stage collisions too.
            raise ValueError('Question ID already used in an earlier stage')  # Prevent duplicate answer anchors.
    if action == 'respond':  # Validate the minimum actual-answer contract.
        for reply in payload:  # No defaults from recommendations.
            if not all(reply.get(key) for key in ('source_ref', 'interpretation', 'actual_reply')):  # Preserve raw words and source.
                raise ValueError('Actual reply, source and interpretation required')  # Unknown is not authorization.
            if reply['decision'] == 'provisional' and not reply.get('authorized_expectation'):  # Explicit temporary expected behavior.
                raise ValueError('Provisional authorization needs an explicit expectation')  # Product condition alone is insufficient.
            question = next(q for q in state['questions'] if q['id'] == reply['question_id'])  # Stable source identity.
            reply['answer_version'] = len(question['history']) + 1  # Retain every correction.
            reply['qa_ref'] = f'{path}#{question["id"]}-A{reply["answer_version"]}'  # Candidate decisions cite this record.
    _credential_guard(payload)  # Protect actual replies and confirmation metadata.
    if action == 'start_extension':  # Keep new candidate and old questions in one task source.
        updated = _extension_stage(state, payload)  # Reuse the production P0 gate and existing extension builder.
    elif action == 'record_context':  # Save report facts or complete questions without inventing a user reply.
        if not payload.get('display') or not payload.get('basis'):  # Context must cite its actual source or explicit gap.
            raise ValueError('Context needs display and source basis')  # Incomplete context stays unsent.
        updated = state  # Facts and questions grant no business authorization.
    elif action == 'record_note':  # Save raw words before any dependent judgment.
        if not payload.get('actual_reply') or not payload.get('source_ref'):  # Preserve source identity.
            raise ValueError('Raw note needs actual reply and source')  # Do not create invented notes.
        updated = state  # Unknown business rules remain open.
    else:  # Existing public state transitions retain their gates.
        from feedback_record import transition  # Reuse exact replay behavior before publishing.
        updated = transition(state, action, payload)  # Validate before changing the record.
        if 'prior_stages' in state:  # Current-stage feedback must not hide earlier questions.
            updated['prior_stages'] = copy.deepcopy(state['prior_stages'])  # Replay uses the same retention rule.
    event = dict(action=action, payload=payload, display=updated['chat'] if action in ('start_extension', 'respond', 'append_questions') else '')  # Save newly eligible questions before sending.
    if action == 'record_context':  # Report-stage text remains visible in the sole task record.
        event['display'] = payload['display']  # Exactly the text to send after successful read-back.
    elif action == 'start_feedback':  # Same task, new review chapter with actual proposal and questions.
        event['display'] = '评审回问\n原话：' + payload['actual_reply'] + '\n拟变更：' + json.dumps(updated['feedback_pending']['changes'], ensure_ascii=False) + '\n' + updated['chat']  # Record before displaying.
    elif action == 'record_note':  # Actual non-rule answers must be readable without inspecting JSON.
        event['display'] = '原话：' + payload['actual_reply'] + '\n来源：' + payload['source_ref']  # Preserve real words and provenance.
    elif action == 'record_coverage':  # Keep source review readable beside its authoritative event.
        event['display'] = '覆盖复核：' + payload['conclusion'] + '\n' + '\n'.join(f"{b['id']}：{b['topic']}；{b['status']}；来源：{b['source']}；依据：{b['basis']}；下一步：{b['next_step']}" for b in payload['branches'])  # Unknowns remain visible.
    new_events = events + [event]  # Preserve historical events unchanged.
    temporary = None  # Allocation itself can fail before any write.
    try:  # Failed writes leave the old source available.
        descriptor, temporary = tempfile.mkstemp(dir=path.parent, suffix='.tmp')  # Same-volume atomic publication.
        with os.fdopen(descriptor, 'w', encoding='utf-8', newline='\n') as stream:  # Close before replace on Windows.
            stream.write(_render(new_events))  # Complete replacement content.
        if _load(path) != events:  # Detect a concurrent task edit before publication.
            raise ValueError('Q&A changed during update; read it again')  # Do not overwrite newer answers.
        os.replace(temporary, path)  # Publish a complete record.
    except OSError as error:  # Preserve the failed action for truthful recovery reporting.
        error.pending_payload = copy.deepcopy(payload)  # Exact attempted content, not an invented saved answer.
        error.record_path = str(path)  # Stable resume location.
        error.pending_action = action  # Only this dependent transition remains unsaved.
        raise  # Do not return successful state after a failed write.
    finally:  # Remove only our own temporary file.
        if temporary is not None and os.path.exists(temporary):  # Replacement already consumed it on success.
            os.unlink(temporary)  # No task history deletion.
    return read_record(path)  # Confirm the saved source before any dependent action.
