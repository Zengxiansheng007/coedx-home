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
        if event['action'] not in ('record_coverage', 'append_questions', 'respond', 'summarize', 'apply_summary', 'review', 'record_actions', 'start_feedback', 'apply_feedback', 'review_feedback', 'assess_review_projection', 'review_preparation_scope'):  # 显示与公共适用评估沿同一事件回放。
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
        if event.get('record_anchor'):
            lines.extend(['<a id="' + event['record_anchor'] + '"></a>', ''])  # 新事件给准确原话链接，历史事件逐字保持。
        lines.extend([f'## 记录 {index + 1} · {event["action"]}', '', event.get('display', ''), ''])  # Full saved question precedes sending.
        for reply in event.get('payload', []) if event['action'] == 'respond' else []:  # Stable reply anchors.
            lines.extend([f'<a id="{reply["question_id"]}-A{reply["answer_version"]}"></a>', f'原话：{reply["actual_reply"]}', f'来源：{reply["source_ref"]}', f'归纳：{reply["interpretation"]}', ''])  # Visible actual words.
        payload = json.dumps(event, ensure_ascii=False, sort_keys=True).replace('`', '\\u0060')  # Prevent fence injection.
        lines.extend(['```tca-event', payload, '```', ''])  # Lossless single-file record.
    return '\n'.join(lines)  # Deterministic representation detects manual divergence.


def _load(path, *, permanent=None):  # Read and check both prose and payload before any transition.
    if permanent is None:
        permanent, _ = _document(path)  # Separate bounded disposable rows from permanent events.
    events = [json.loads(value) for value in re.findall(r'^```tca-event\n(.*?)\n```$', permanent, re.M | re.S)]  # Explicit record format.
    if not events or _render(events) != permanent or events[0]['path'] != str(path.resolve()):  # Refuse changed sources or copied task records.
        raise ValueError('Q&A record differs from its source; reconcile before updating')  # Keep conflicting evidence intact.
    return events  # Events alone determine state.


def read_record(path):  # Public read-back boundary.
    return _replay(_load(Path(path)))  # No separate session JSON required.


def read_notes(path):  # Report selection resumes from the same authoritative MD.
    return copy.deepcopy([event for event in _load(Path(path)) if event['action'] in ('record_note', 'record_context')])  # Disposable source projection, not a second answer file.


def _handoff_meaning(batch, extension_evidence=None, *, base_path=None, source_catalog=None):  # Same reconstruction at outgoing and incoming boundaries.
    from step_reuse import expanded  # Existing complete sequence and binding validation.
    from restoration import preflight  # Same current-source restoration as public review.
    if extension_evidence and source_catalog is None:
        source_catalog = json.loads(Path(extension_evidence).read_text(encoding='utf-8-sig'))['catalog']  # Current qualified source input, not cached definitions.
    restored = preflight(batch, source_catalog=source_catalog, base_path=base_path, require_current_sources=not extension_evidence)
    complete = restored['complete_batch']
    complete['restoration_blockers'] = restored['blockers']  # Transient findings never overwrite blocked originals.
    if 'extension_entry' in batch:  # P1/P2 retains the original full P0 qualification boundary.
        if not extension_evidence:
            raise ValueError('P0 current evidence file required for extension handoff')  # A cached entry is not current evidence.
        envelope = json.loads(Path(extension_evidence).read_text(encoding='utf-8-sig'))  # Re-read actual supplied artifacts.
        from p0_evidence import check_extension  # Reuse established qualification without another approval flow.
        entry = check_extension(**envelope)  # Current catalog, baseline, reports, request and explicit mode.
        if not entry['can_extend']:
            raise ValueError('P0 handoff blocked: ' + ', '.join(entry['blockers']))  # Unresolved and invalid dependencies remain visible.
        catalog = envelope['catalog']  # Bind fixed definitions to the currently qualified sources.
        cases = {case['id']: case for case in catalog['cases']}  # Stable identity, never Chinese display labels.
        qualified = {case['case_id'] for case in entry['cases'] if case['execution_status'] == 'passed'}  # Only this approved round supplies qualification.
        data = {item['id']: item for item in catalog['data']}  # Current source values as well as rules.
        from authoring import _digest  # Existing fixed-definition identity.
        from step_reuse import GROUPS  # Exact supported sequence groups.
        active = {step['step_reference']['definition_digest'] for case in batch['cases'] for group in GROUPS for step in case.get(group, []) if 'step_reference' in step}  # Historical definitions are retained but not active dependencies.
        for definition in batch.get('step_definitions', []):  # Reject valid but unrelated or superseded P0 evidence.
            if _digest(definition) not in active:
                continue  # Unused history never blocks a current independent step.
            if definition['case_id'] not in qualified:
                raise ValueError('P0 definition outside qualified scope: ' + definition['case_id'])  # Unrelated passed P0 cannot qualify an active source.
            source = cases.get(definition['case_id'], {})  # Missing sources remain a blocker.
            steps = [step for step in source.get(definition['group'], []) if step['id'] == definition['step_id']]  # Exact step identity.
            if source.get('semantic_version') != definition['semantic_version'] or steps != [definition['step']] or any(data.get(item['id']) != item for item in definition['data']):
                raise ValueError('P0 definition differs from current qualified source: ' + definition['case_id'])  # Historical closure cannot replace current validity.
    return complete  # Transient only; no maintained expanded file.


def checkpoint_record(path, stage, candidate_path, sources, next_step, *, extension_evidence=None, source_catalog_path=None):  # Save recovery metadata inside the existing sole MD.
    state = read_record(path)  # Never checkpoint a caller's cached answers.
    candidate_path = Path(candidate_path).resolve()  # Stable actual artifact location.
    candidate = json.loads(candidate_path.read_text(encoding='utf-8-sig'))  # Inspect the supplied candidate itself.
    if candidate != state['batch']:  # Version equality alone cannot establish matching content.
        raise ValueError('Candidate differs from Q&A projection; reconcile affected content first')  # No automatic overwrite.
    current_catalog = json.loads(Path(source_catalog_path).read_text(encoding='utf-8-sig')) if source_catalog_path else None  # Optional actual source; no mandatory state pack.
    _handoff_meaning(candidate, extension_evidence, base_path=candidate_path.parent, source_catalog=current_catalog)  # Complete meaning and current entry evidence before recording.
    if stage not in ('p0', 'report', 'p1-p2', 'review') or not next_step or not sources:  # TCA stages, not another workflow.
        raise ValueError('Recovery needs a TCA stage, actual sources and next action')  # No empty handoff.
    known = {q['id'] for stage_state in state.get('prior_stages', []) + [state] for q in stage_state['questions']}  # Source dependencies retain permanent IDs across stages.
    bindings = []  # Store identities and digests, never another business answer.
    for source in sources:  # Every supplied source is actually read.
        source_path = Path(source['path']).resolve()  # Explicit authorized source path.
        ids = source.get('question_ids', [])  # Empty means stage-wide evidence, not a guessed question.
        if not set(ids) <= known:  # Fail when the proposed mapping is not from this task.
            raise ValueError('Unknown source question binding')  # Keep the prior checkpoint intact.
        if not set(source.get('case_ids', [])) <= {c['id'] for c in candidate['cases']}:
            raise ValueError('Unknown source case binding')  # A guessed scope cannot authorize unrelated continuation.
        bindings.append(dict(path=str(source_path), sha256=hashlib.sha256(source_path.read_bytes()).hexdigest(), question_ids=ids, case_ids=source.get('case_ids', [])))  # Actual byte identity and explicit dependent scope.
    recovery = dict(stage=stage, candidate_path=str(candidate_path), sources=bindings, next_step=next_step, content_version=candidate['content_version'])  # Technical recovery location only.
    if source_catalog_path:
        recovery['source_catalog_path'] = str(Path(source_catalog_path).resolve())  # Re-read source, never persist an expanded snapshot.
    recovery['event_count'] = state['qa_record']['event_count']  # Bind actual decisions as well as candidate bytes.
    if extension_evidence is not None:  # Carry exact evidence location and bytes to the receiver.
        evidence_path = Path(extension_evidence).resolve()  # No hidden chat dependency.
        recovery['extension_evidence'] = dict(path=str(evidence_path), sha256=hashlib.sha256(evidence_path.read_bytes()).hexdigest())  # Same artifact version.
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
    checkpoint_index = max(i for i, event in enumerate(events) if event['action'] == 'record_context' and 'recovery' in event['payload'])  # Derive position for legacy checkpoints too.
    if recovery.get('event_count', checkpoint_index) != checkpoint_index or recovery['content_version'] != state['batch']['content_version'] or any(event['action'] not in ('record_context', 'record_note') for event in events[checkpoint_index + 1:]):
        conflicts.append(dict(kind='checkpoint', reason='Checkpoint predates current decisions or candidate; save a current checkpoint'))  # Notes alone remain compatible.
    candidate_path = Path(recovery['candidate_path'])  # Read the actual candidate from the handoff.
    candidate = None  # A missing actual candidate cannot fall back to replayed content.
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
            conflicts.append(dict(kind='source', path=source['path'], question_ids=source['question_ids'], case_ids=source.get('case_ids', []), reason='Source changed or unavailable'))  # No inferred business answer.
    complete = None  # Conflicted material never yields a usable complete projection.
    try:  # Revalidate even when the saved checkpoint had succeeded.
        if candidate is None:
            raise ValueError('Actual candidate unavailable')
        evidence = recovery.get('extension_evidence')  # Legacy extension checkpoints require fresh evidence.
        if evidence and hashlib.sha256(Path(evidence['path']).read_bytes()).hexdigest() != evidence['sha256']:
            raise ValueError('P0 evidence changed since checkpoint')  # Reconcile exact source version first.
        current_catalog = json.loads(Path(recovery['source_catalog_path']).read_text(encoding='utf-8-sig')) if recovery.get('source_catalog_path') else None
        resolved = _handoff_meaning(candidate, evidence['path'] if evidence else None, base_path=candidate_path.parent, source_catalog=current_catalog)  # Same outgoing validation logic.
        conflicts.extend(dict(kind='dependency', **b) for b in resolved.get('restoration_blockers', []))
        if not any(c['kind'] != 'dependency' and not (c['kind'] == 'source' and c.get('case_ids')) for c in conflicts):
            affected = {cid for c in conflicts for cid in c.get('case_ids', [])}
            complete = dict(resolved, cases=[c for c in resolved['cases'] if c['id'] not in affected])  # Only a coherent same-version restoration is exposed.
    except (OSError, ValueError, KeyError, TypeError) as error:  # Report missing or invalid material without inventing content.
        conflicts.append(dict(kind='handoff', reason=str(error)))  # Preserve a concrete actionable failure.
    return dict(state=state, recovery=recovery, conflicts=conflicts, needs_checkpoint=False, complete_batch=complete)  # Read-only transient reconstruction.


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


def advance_record(path, action, payload=None, *, _expected_record=None, _expected_artifact=None):  # 收尾保存须绑定此前通过的校验。
    path = Path(path).resolve()  # Keep the task binding stable.
    if action not in ('start_extension', 'record_coverage', 'append_questions', 'record_context', 'record_note', 'respond', 'summarize', 'apply_summary', 'review', 'record_actions', 'start_feedback', 'apply_feedback', 'review_feedback', 'assess_review_projection', 'review_preparation_scope'):  # 显示与公共适用评估沿同一保存入口。
        raise ValueError('Unknown Q&A action')  # Refuse unsupported effects.
    original_bytes = path.read_bytes()  # 追加事件绑定重放所用的原始字节。
    if _expected_record is not None and original_bytes != _expected_record:
        raise ValueError('Q&A changed before closure evidence save; read it again')  # 按当前决定重新校验收尾范围。
    permanent, temporary_rows = _document(path, snapshot=original_bytes)  # 用同一次读取重放事件并保留临时行。
    events = _load(path, permanent=permanent)
    state = _replay(events)  # Reconstruct existing technical state.
    closures = [event['payload']['scope_closure'] for event in events if event['action'] == 'record_context' and 'scope_closure' in event['payload']]  # Existing permanent metadata only.
    closed_questions = {identity for closure in closures for identity in closure.get('closed_question_ids', [])}  # Old anchors retain their original meaning.
    closed_branches = {branch['id']: branch for closure in closures for branch in closure['branches']}  # Never resurrect unchanged closed work.
    if action == 'respond' and any(reply['question_id'] in closed_questions for reply in payload):
        raise ValueError('Closed question needs a new ID for changed scope')  # Original valid answers remain permanent.
    if action == 'start_feedback' and set(payload.get('reopen_question_ids', [])) & closed_questions:
        raise ValueError('Closed question needs a new ID for changed scope')  # Feedback cannot revive a cleaned identity.
    incoming_questions = payload if action == 'append_questions' else payload.get('questions', []) if action in ('start_feedback', 'start_extension') else []  # Only new questions need fresh numbers.
    known_questions = {q['id'] for stage in state.get('prior_stages', []) + [state] for q in stage['questions']}  # Existing unanswered questions keep identities.
    admissions = [('Q', q['id']) for q in incoming_questions if q['id'] not in known_questions] + ([('B', branch['id']) for branch in payload['branches'] if branch['id'] not in closed_branches and branch['id'] not in {b['id'] for b in state.get('coverage', {}).get('branches', [])}] if action == 'record_coverage' else [])  # New checks only.
    for prefix, identity in admissions:
        number = re.fullmatch(prefix + r'(\d+)', identity)  # Non-numeric legacy IDs remain compatible.
        if number and closures and int(number.group(1)) <= max(c.get('highwater', {}).get(prefix, 0) for c in closures):
            raise ValueError('New question or branch must exceed permanent highwater')  # Cleaned numbers are never recycled.
    if action == 'record_coverage' and any(branch['id'] in closed_branches and branch != closed_branches[branch['id']] for branch in payload['branches']):
        raise ValueError('Closed coverage needs a new branch ID')  # New facts receive new anchors.

    payload = copy.deepcopy(payload)  # Add provenance without mutating caller objects.
    if action in ('append_questions', 'start_feedback'):  # Every current-stage question admission reserves earlier identities.
        used = {q['id'] for stage in state.get('prior_stages', []) for q in stage['questions']}  # Same task history.
        incoming = payload if action == 'append_questions' else payload.get('questions', [])  # Omitted feedback questions reuse the current graph.
        current = {q['id'] for q in state['questions']} if action == 'start_feedback' else set()  # Normal current-stage feedback retains its answer history.
        if any(q['id'] in used and q['id'] not in current for q in incoming):  # Only newly admitted feedback questions can steal a historical identity.
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
    if action in ('review', 'review_feedback') and payload.get('actual_reply'):
        payload['qa_ref'] = str(path) + '#tca-record-' + str(len(events) + 1)  # 只添加原话位置，不修改确认或权限。
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
    if action in ('review', 'review_feedback') and payload.get('qa_ref'):
        event['record_anchor'] = 'tca-record-' + str(len(events) + 1)  # 与保存的实际评审原话同版绑定。
    if action == 'record_context':  # Report-stage text remains visible in the sole task record.
        event['display'] = payload['display']  # Exactly the text to send after successful read-back.
    elif action == 'start_feedback':  # Same task, new review chapter with actual proposal and questions.
        event['display'] = '评审回问\n原话：' + payload['actual_reply'] + '\n拟变更：' + json.dumps(updated['feedback_pending']['changes'], ensure_ascii=False) + '\n' + updated['chat']  # Record before displaying.
    elif action == 'record_note':  # Actual non-rule answers must be readable without inspecting JSON.
        event['display'] = '原话：' + payload['actual_reply'] + '\n来源：' + payload['source_ref']  # Preserve real words and provenance.
    elif action == 'record_coverage':  # Keep source review readable beside its authoritative event.
        event['display'] = '覆盖复核：' + payload['conclusion'] + '\n' + '\n'.join(f"{b['id']}：{b['topic']}；{b['status']}；来源：{b['source']}；依据：{b['basis']}；下一步：{b['next_step']}" for b in payload['branches'])  # Unknowns remain visible.
    new_events = events + [event]  # Preserve historical events unchanged.
    if action == 'record_coverage':  # Temporary display is derived from the permanent observation.
        temporary_rows = copy.deepcopy([branch for branch in payload['branches'] if branch['id'] not in closed_branches])  # No separate answer authority.
    temporary = None  # Allocation itself can fail before any write.
    try:  # Failed writes leave the old source available.
        descriptor, temporary = tempfile.mkstemp(dir=path.parent, suffix='.tmp')  # Same-volume atomic publication.
        with os.fdopen(descriptor, 'w', encoding='utf-8', newline='\n') as stream:  # Close before replace on Windows.
            stream.write(_render(new_events) + _temporary_text(temporary_rows))  # Permanent events and bounded working rows.
        if _expected_artifact is not None and _expected_artifact[0].read_bytes() != _expected_artifact[1]:
            raise ValueError('Saved candidate changed before closure evidence save; read it again')  # 候选稿变化后须重新核对永久依据。
        if path.read_bytes() != original_bytes:  # Detect concurrent event or temporary-row edits.
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


_TEMP_START = '<!-- tca-temporary:start -->'  # Single explicit disposable boundary.
_TEMP_END = '<!-- tca-temporary:end -->'  # Permanent events never enter this region.


def _temporary_text(rows):  # Canonical disposable coverage projection.
    return '' if not rows else _TEMP_START + '\n' + json.dumps(rows, ensure_ascii=False, sort_keys=True) + '\n' + _TEMP_END + '\n'  # Empty region disappears.


def _document(path, *, snapshot=None):  # Inspect actual file boundaries before any mutation.
    snapshot = path.read_bytes() if snapshot is None else snapshot  # 已有快照时使用调用方绑定的字节。
    text = snapshot.decode('utf-8').replace('\r\n', '\n').replace('\r', '\n')  # 兼容旧记录的多种换行符。
    if _TEMP_START not in text and _TEMP_END not in text:  # Legacy files remain valid.
        return text, []  # Never migrate history just to add a temporary table.
    if text.count(_TEMP_START) != 1 or text.count(_TEMP_END) != 1:  # Ambiguous region is unsafe.
        raise ValueError('Ambiguous temporary coverage boundary')  # Preserve evidence for reconciliation.
    permanent, suffix = text.split(_TEMP_START)  # Region must be the final block.
    try:  # Malformed content is never guessed or silently dropped.
        rows = json.loads(suffix.split(_TEMP_END)[0].strip())  # Only temporary coverage rows.
    except (ValueError, TypeError) as error:
        raise ValueError('Invalid temporary coverage region') from error  # Fail before writing.
    if not isinstance(rows, list) or any(not isinstance(row, dict) or not row.get('id') for row in rows) or _TEMP_START + suffix != _temporary_text(rows):
        raise ValueError('Invalid temporary coverage region')  # Reject content outside the exact boundary.
    return permanent, rows  # Permanent replay remains unchanged.


def _closure_restoration(batch, source_catalog, cache, base_path):  # 同一快照共享当前校验和历史比较的还原结果。
    from restoration import preflight  # 与具体评审共用当前来源和完整还原门。
    key = id(batch)  # 缓存仅存活于这次关闭调用，不跨版本或跨请求。
    if key not in cache:
        cache[key] = preflight(batch, source_catalog=source_catalog, base_path=base_path, require_current_sources=True)  # 读取实际来源，包括相对候选稿定位的文件。
    return cache[key]


def _closure_meaning(batch, identity, source_catalog, cache, base_path):  # 仅瞬时还原本次原审批的真实依赖，不接收 unchanged 自报。
    from preparation_scope import active_scopes, operation_scopes, scope_context  # 共用既有父源及公共适用关系。
    from review_projection import active_records, project_record  # 绑定真实可见表达，不只核源字段。
    from review_expression import source_binding  # typed 来源涵盖实际使用注册。
    from step_reuse import GROUPS  # 仅声明的步骤关系具有依赖语义。
    if scope_context(batch, source_catalog, require_parent=True)[1]:
        raise ValueError('Closure reuse needs the exact complete source catalog')  # 未知隐藏成员不能证明不变。
    restored = _closure_restoration(batch, source_catalog, cache, base_path)
    if identity in restored['blocked_case_ids']:
        raise ValueError('Closure reuse has unresolved dependencies: ' + identity)  # 失败不能以旧 approved 掩盖。
    complete = next(case for case in restored['complete_batch']['cases'] if case['id'] == identity)  # 实际完整动作及递归整例依赖。
    data = {item['id']: item for item in restored['complete_batch']['data']}  # 还原所用的准确数据。
    owners, refs = [], set()  # 收集实际依赖，不按自然语言标题猜测。
    def binding_owner(collection, owner):  # 瞬时展开对象用原始 owner 核显示绑定，避免 resolved_case 使真实评估失联。
        oid = owner.get('id', owner.get('case_id'))  # 仅稳定身份，不从显示标题匹配。
        for context in [batch] + ([source_catalog] if source_catalog is not None else []):
            matches = [item for item in context.get(collection, []) if item.get('id', item.get('case_id')) == oid]
            if len(matches) > 1:
                raise ValueError('Closure reuse has ambiguous owner identity')  # 不从重复身份选任意对象。
            if matches:
                return context, matches[0]  # 当前候选优先，外部完整来源只补实际缺失 owner。
        raise ValueError('Closure reuse has unknown display owner')  # 无法绑定可见含义时不猜。
    def technical(owner):  # 外部资料须有可重新读取的历史内容绑定。
        value = owner.get('technical_handoff', {})  # 未声明的自然语言说明仍按原字段比较。
        if isinstance(value, dict):
            value = value.get('shared_section', value)  # 与 restoration 相同的明确引用结构。
            if value.get('source_ref') and not value.get('sha256'):
                raise ValueError('Closure reuse cannot prove unbound external technical source')  # 单纯路径不证明旧内容仍有效。
    def visit(case):  # 已经由 preflight 拒绝环、缺失及失效引用。
        technical(case)  # preflight 同时读取并核对声明摘要。
        owners.append(('cases', case))  # 完整对象仍参与比较，包括未知业务扩展。
        for group in GROUPS:
            for step in case.get(group, []):
                technical(step)  # 步骤级资料也不能以存在代替版本证明。
                refs.update(step.get('data_refs', []))  # 字面 input 中的同名键不参与框架解析。
                refs.update(step.get('dependency', {}).get('data_refs', []))  # 整例输入/产出绑定的数据同样纳入。
                if step.get('resolved_case'):
                    visit(step['resolved_case'])  # 下游数据与完整终点同样约束原审批。
    visit(complete)
    if refs - data.keys():
        raise ValueError('Closure reuse has missing dependency data')  # 边输入/产出也必须有真实数据对象。
    owners.extend(('data', data[ref]) for ref in sorted(refs))  # 缺数据由还原门拒绝；不比较无关数据。
    owners.extend(('selection', item) for item in batch.get('selection', []) if item['case_id'] == identity)  # 本例实际交付含义。
    scopes, display = [], []  # 递归目标的适用义务和可见含义同样纳入证明。
    for collection, owner in owners:
        context, raw = binding_owner(collection, owner)  # 完整还原与原始评估绑定各负其责。
        display.append(dict(collection=collection, owner=project_record(context, collection, raw), records=active_records(context, collection, raw), sources=source_binding(context, [raw])))  # 实际使用的来源注册随各 owner 核对。
        if collection == 'cases':
            parent = source_catalog if context is batch else None  # 外部完整 catalog 不借当前子集倒推成员。
            operations, pending = operation_scopes(context, parent)
            legacy = active_scopes(context, parent)
            cid = raw['id']  # 根用例与每个传递依赖独立检查。
            relevant = [scope for scope in context.get('preparation_scopes', []) if cid in scope.get('applicable_case_ids', []) + scope.get('exception_case_ids', [])]  # 排除关系也是义务。
            if cid in pending or any(scope.get('contract_version') != 2 and cid in scope.get('applicable_case_ids', []) and legacy.get(cid) != scope for scope in relevant):
                raise ValueError('Closure reuse needs current operation applicability')  # 失效 legacy 不能静默退回内联并算未变。
            scopes.append(dict(case_id=cid, scopes=relevant, active_operations=operations.get(cid, []), legacy=legacy.get(cid)))  # 传递依赖的频次变化也不能漏过。
    return dict(complete=complete, owners=owners, scopes=scopes, display=display)  # 完整动作/数据及原始 owner 的活动可见表达分别比较。


def _closure_review_reuse(events, candidate, selected, source_catalog, base_path):  # 原审批只从同一永久 QA 的真实评审动作中寻找。
    snapshots, meanings, proofs = {}, {}, []  # 仅本调用缓存，绝不改 final_review。
    for identity in sorted(selected):
        case = next(item for item in candidate['cases'] if item['id'] == identity)
        review = case.get('final_review', {})
        if case.get('review_status') != 'approved' or review.get('approved') is not True or identity not in review.get('case_ids', []) or not review.get('actual_reply'):
            raise ValueError('Concrete current-version review required for every closing case')  # 原具体稿门不变。
        current = _closure_restoration(candidate, source_catalog, meanings, base_path)  # 逐个核对收尾用例的当前来源。
        blocker = next((item for item in current['blockers'] if item['case_id'] == identity), None)
        if blocker:
            raise ValueError('Closure has unresolved current dependencies for ' + identity + ': ' + blocker['reason'])  # 仅按当前用例的阻断项决定是否收尾。
        if review.get('content_version') == candidate['content_version']:
            continue  # 跨版本复用才需追加同一问答记录的比对。
        found = False
        for index, event in enumerate(events):
            if event['action'] not in ('review', 'review_feedback') or event['payload'].get('content_version') != review.get('content_version') or identity not in event['payload'].get('case_ids', []):
                continue  # 种子中的任意 approved/hash 不是原评审证据。
            if index not in snapshots:
                snapshots[index] = _replay(events[:index + 1])['batch']  # 复用同一 transition 重建当时真实保存结果。
            original = snapshots[index]
            old_case = next((item for item in original['cases'] if item['id'] == identity), None)
            if old_case != case or original['content_version'] != review['content_version']:
                continue  # 完整用例及 final_review 原文必须相同。
            original_source = event['payload'].get('source_catalog')  # 当时实际经过评审门的来源，不用调用者补历史。
            if _closure_meaning(original, identity, original_source, meanings, base_path) != _closure_meaning(candidate, identity, source_catalog, meanings, base_path):
                continue  # 数据、来源、公共适用、依赖或显示变化均不能复用。
            proofs.append(dict(case_id=identity, review_event=index + 1, content_version=original['content_version']))  # 仅记录证明位置，不创造审批。
            found = True
            break
        if not found:
            raise ValueError('Concrete current-version review or proven unchanged same-record approval required: ' + identity)
    return proofs  # 原 final_review 保持逐字不变。


def close_record_scope(path, candidate_path, case_ids, branch_ids, *, scope_bindings=None, source_catalog=None):  # 可选补准确范围，不重做澄清汇总。
    path = Path(path).resolve()  # Preserve original task path.
    candidate_path = Path(candidate_path).resolve()  # Actual artifact, not a saved boolean.
    before = path.read_bytes()  # 校验绑定永久区和临时区的原始字节。
    permanent, rows = _document(path, snapshot=before)
    events = _load(path, permanent=permanent)  # Validate permanent source before trusting decisions.
    state = _replay(events)  # Existing business rules remain sole authority.
    candidate_bytes = candidate_path.read_bytes()  # Read actual saved artifact before permanent closure.
    candidate = json.loads(candidate_bytes.decode('utf-8-sig'))  # Bind complete saved content.
    if candidate != state['batch']:
        raise ValueError('Saved candidate differs from current record')  # No cleanup after failed or stale saves.
    selected = set(case_ids)  # Explicit independently approved scope.
    cases = {case['id']: case for case in candidate['cases']}  # Stable business identity.
    if not selected or not selected <= cases.keys() or not branch_ids or len(set(branch_ids)) != len(branch_ids):
        raise ValueError('Explicit known closure scope required')  # Never guess the entire batch.
    reused_reviews = _closure_review_reuse(events, candidate, selected, source_catalog, candidate_path.parent)  # 只补真实未变证明，不升级旧审批版本。
    coverage = state.get('coverage', {})  # Reuse the permanent source review rather than a second ledger.
    if coverage.get('revision') != state['revision']:
        raise ValueError('Current coverage reread required')  # Changed premises invalidate old coverage.
    branches = {branch['id']: branch for branch in coverage.get('branches', [])}  # Permanent observations.
    if not set(branch_ids) <= branches.keys():
        raise ValueError('Unknown closure branches')  # No arbitrary temporary deletion.
    closing = [branches[identity] for identity in branch_ids]  # Preserve full basis and impact.
    from authoring import _digest  # 摘要现场计算自永久 branch，而非可编辑临时投影。
    bindings = {}  # 显式范围绑定仅随永久收尾依据保存。
    for binding in scope_bindings or []:
        if not isinstance(binding, dict) or set(binding) != {'branch_id', 'branch_digest', 'case_ids', 'provenance'}:
            raise ValueError('Explicit branch identity, digest, cases and provenance required')  # 未声明字段不获得新权威。
        bid, ids = binding['branch_id'], binding['case_ids']
        if bid not in branch_ids or bid in bindings or not isinstance(ids, list) or not ids or any(not isinstance(cid, str) for cid in ids) or len(ids) != len(set(ids)) or not set(ids) <= selected or not isinstance(binding['provenance'], str) or not binding['provenance'].strip():
            raise ValueError('Known distinct scope bindings entirely within closure required')  # 未知、重复及共享范围越界均拒绝。
        if binding['branch_digest'] != _digest(branches[bid]) or (branches[bid].get('case_ids') and set(ids) != set(branches[bid]['case_ids'])):
            raise ValueError('Stale or conflicting permanent branch scope binding')  # 已有范围不能无声覆盖。
        previous = [item for event in events if event['action'] == 'record_context' for item in event['payload'].get('scope_closure', {}).get('scope_bindings', []) if item['branch_id'] == bid]  # 准备中断也已形成永久绑定。
        if any(item['branch_digest'] != binding['branch_digest'] or set(item['case_ids']) != set(ids) for item in previous):
            raise ValueError('Conflicting saved closure scope binding')  # 原无 case_ids 的 B 也不能在清理后改属其他用例。
        bindings[bid] = copy.deepcopy(binding)  # 不改原 coverage、summary 或业务对象。
    for branch in closing:
        bound_cases = bindings.get(branch['id'], {}).get('case_ids', branch.get('case_ids'))  # 默认缺 scope 仍保守拒绝。
        if not bound_cases or not set(bound_cases) <= selected or branch['status'] not in ('resolved', 'deferred', 'excluded', 'not_applicable'):
            raise ValueError('Only disposed branches entirely within approved scope may close')  # Pending/shared branches remain.
        if branch['status'] == 'deferred' and not branch.get('impact'):
            raise ValueError('Deferred product impact must be permanently recorded')  # Unknown expected behavior stays visible.
    if any(row != branches.get(row['id']) for row in rows):  # Temporary content cannot replace authoritative observations.
        raise ValueError('Temporary coverage differs from permanent observation')  # Resolve drift before deletion.
    all_branch_ids = {branch['id'] for event in events if event['action'] == 'record_coverage' for branch in event['payload']['branches']}  # Earlier-stage highwater survives.
    all_question_ids = {q['id'] for stage in state.get('prior_stages', []) + [state] for q in stage['questions']}  # Permanent identity inventory.
    highwater = {prefix: max([int(match.group(1)) for identity in identities if (match := re.fullmatch(prefix + r'(\d+)', identity))] or [0]) for prefix, identities in [('Q', all_question_ids), ('B', all_branch_ids)]}  # Continue above cleaned numeric IDs.
    closure = dict(candidate_path=str(candidate_path), content_version=candidate['content_version'], candidate_sha256=hashlib.sha256(candidate_bytes).hexdigest(), case_ids=sorted(selected), branches=closing, reviews=[cases[identity]['final_review'] for identity in sorted(selected)], closed_question_ids=sorted(q['id'] for q in state['questions'] if q.get('case_id') in selected), used_question_ids=sorted({q['id'] for stage in state.get('prior_stages', []) + [state] for q in stage['questions']}), used_branch_ids=sorted(all_branch_ids), highwater=highwater)  # Exact artifact, original replies, dispositions and highwater identities.
    if bindings:
        closure['scope_bindings'] = [bindings[bid] for bid in sorted(bindings)]  # 原 branch 保持原字节，未来复核不误判成修改旧 B。
    if reused_reviews:
        closure['review_reuse'] = reused_reviews  # 永久原评审及证明位置同时可追溯。
    recorded = any(event['action'] == 'record_context' and event['payload'].get('scope_closure') == closure for event in events)  # Resume a previously saved preparation.
    if not recorded:  # Persist permanent evidence before touching any disposable row.
        payload = dict(display='已保存具体评审与收尾依据：' + ', '.join(sorted(selected)), basis=[str(candidate_path)], scope_closure=closure)
        advance_record(path, 'record_context', payload, _expected_record=before, _expected_artifact=(candidate_path, candidate_bytes))  # 沿用现有原子保存并核对快照。
        before = path.read_bytes()  # 永久保存后回读待清理快照。
        permanent, saved_rows = _document(path, snapshot=before)
        saved = _load(path, permanent=permanent)
        expected = dict(action='record_context', payload=payload, display=payload['display'])  # 回读时只允许增加本次收尾事件。
        if saved != events + [expected] or saved_rows != rows:
            raise ValueError('Q&A changed before cleanup; read it again')  # 回读发现变动后须重新校验。
        events = saved
    remaining = [row for row in rows if row['id'] not in set(branch_ids)]  # Only exact scoped IDs are disposable.
    if rows == remaining:  # Already completed or legacy record with no temporary rows.
        if candidate_path.read_bytes() != candidate_bytes or path.read_bytes() != before:
            raise ValueError('Record or artifact changed during cleanup')  # 重复调用也要核对实际完成状态。
        return _replay(events)
    temporary = None  # Failure leaves durable prepared evidence and original rows.
    try:
        descriptor, temporary = tempfile.mkstemp(dir=path.parent, suffix='.tmp')  # Same-volume atomic replacement.
        with os.fdopen(descriptor, 'w', encoding='utf-8', newline='\n') as stream:
            stream.write(_render(events) + _temporary_text(remaining))  # Permanent events are byte-identical.
        if candidate_path.read_bytes() != candidate_bytes or path.read_bytes() != before:
            raise ValueError('Record or artifact changed during cleanup')  # No stale overwrite.
        os.replace(temporary, path)  # Only bounded temporary projection is removed.
    finally:
        if temporary is not None and os.path.exists(temporary):
            os.unlink(temporary)  # Remove this private staging file only.
    permanent, actual_rows = _document(path)  # 一次读取同时核对已保存的两个区域。
    if _load(path, permanent=permanent) != events or actual_rows != remaining:
        raise ValueError('Cleanup read-back mismatch')  # Never report attempted cleanup as completed.
    return _replay(events)  # 保留可重放的永久记录及其他范围。
