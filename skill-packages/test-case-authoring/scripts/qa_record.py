"""One Markdown task record; technical state is replayed from its actual events."""
import copy  # Never alter caller data.
import json  # Store lossless event payloads inside the sole Markdown source.
import os  # Replace completed records atomically.
import re  # Locate explicitly delimited event blocks.
import tempfile  # Prepare replacement on the same filesystem.
from pathlib import Path  # Canonical task location.
import clarification as flow  # Reuse existing decisions and review gates.
from authoring import _credential_guard  # Preserve existing privacy checks.


def _replay(events):  # Technical projection has no independently editable answers.
    first = events[0]  # Initial event binds task, stage and candidate version.
    state = flow.start_grill(first['batch'], first['questions'])  # Existing public seam.
    for event in events[1:]:  # Preserve correction order and original replies.
        if event['action'] in ('record_note', 'record_context'):  # Report facts/questions and raw replies do not edit candidates.
            continue  # A note grants no business decision.
        if event['action'] not in ('respond', 'summarize', 'apply_summary', 'review', 'record_actions'):  # Validate loaded data too.
            raise ValueError('Unknown recorded action')  # Never dispatch arbitrary names from disk.
        method = getattr(flow, event['action'])  # Actions are allowlisted before writing.
        state = method(state) if event['action'] == 'summarize' else method(state, event['payload'])  # Rebuild derived candidate.
    state['qa_record'] = {'task_id': first['task_id'], 'path': first['path'], 'event_count': len(events)}  # Source binding only.
    return state  # Callers receive a disposable projection.


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
    if action not in ('record_context', 'record_note', 'respond', 'summarize', 'apply_summary', 'review', 'record_actions'):  # No dynamic arbitrary dispatch.
        raise ValueError('Unknown Q&A action')  # Refuse unsupported effects.
    events = _load(path)  # Always start from the sole answer record.
    state = _replay(events)  # Reconstruct existing technical state.
    payload = copy.deepcopy(payload)  # Add provenance without mutating caller objects.
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
    if action == 'record_context':  # Save report facts or complete questions without inventing a user reply.
        if not payload.get('display') or not payload.get('basis'):  # Context must cite its actual source or explicit gap.
            raise ValueError('Context needs display and source basis')  # Incomplete context stays unsent.
        updated = state  # Facts and questions grant no business authorization.
    elif action == 'record_note':  # Save raw words before any dependent judgment.
        if not payload.get('actual_reply') or not payload.get('source_ref'):  # Preserve source identity.
            raise ValueError('Raw note needs actual reply and source')  # Do not create invented notes.
        updated = state  # Unknown business rules remain open.
    else:  # Existing public state transitions retain their gates.
        method = getattr(flow, action)  # Allowlisted existing state transition.
        updated = method(state) if action == 'summarize' else method(state, payload)  # Reject invalid transitions before writes.
    event = dict(action=action, payload=payload, display=updated['chat'] if action == 'respond' else '')  # Save newly eligible questions before sending.
    if action == 'record_context':  # Report-stage text remains visible in the sole task record.
        event['display'] = payload['display']  # Exactly the text to send after successful read-back.
    elif action == 'record_note':  # Actual non-rule answers must be readable without inspecting JSON.
        event['display'] = '原话：' + payload['actual_reply'] + '\n来源：' + payload['source_ref']  # Preserve real words and provenance.
    new_events = events + [event]  # Preserve historical events unchanged.
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, suffix='.tmp')  # Same-volume atomic publication.
    try:  # Failed writes leave the old source available.
        with os.fdopen(descriptor, 'w', encoding='utf-8', newline='\n') as stream:  # Close before replace on Windows.
            stream.write(_render(new_events))  # Complete replacement content.
        if _load(path) != events:  # Detect a concurrent task edit before publication.
            raise ValueError('Q&A changed during update; read it again')  # Do not overwrite newer answers.
        os.replace(temporary, path)  # Publish a complete record.
    finally:  # Remove only our own temporary file.
        if os.path.exists(temporary):  # Replacement already consumed it on success.
            os.unlink(temporary)  # No task history deletion.
    return read_record(path)  # Confirm the saved source before any dependent action.
