"""Thin feedback transition adapter for the existing sole Markdown record."""
import copy  # Isolate disposable projections.
import clarification as flow  # Preserve partial-answer and dependency behavior.
from feedback import prepare_feedback, apply_feedback, review_feedback  # Existing candidate-only workflow.
from review_expression import field_role, PROVENANCE_FIELDS  # 与业务投影共用准确类型边界。


def _technical_history_target(batch, target):  # 仅识别已声明来源/交接位置，不按问题文字授权。
    if len(target) < 3 or target[0] != 'cases' or type(target[1]) is not int or not 0 <= target[1] < len(batch['cases']):  # data 及未知 owner 不属于此技术历史。
        return False  # 不绕过共享数据消费者检查。
    value, role, technical = batch['cases'][target[1]], 'case', False  # 从准确用例根重放共享字段类型。
    for part in target[2:]:  # 技术根的后代只定位资料，不成为业务输入。
        if not technical and isinstance(part, str):  # 业务输入边界先于同名来源键。
            technical = (role in ('case', 'step', 'claim') and part in PROVENANCE_FIELDS) or (role == 'case' and part == 'technical_handoff')  # 仅已声明来源或用例交接。
            role = field_role(role, part)  # literal 会贯穿所有后代，未知结构无来源职责。
        try:  # 原路径必须能在当前候选准确恢复。
            if isinstance(value, list) and (type(part) is not int or not 0 <= part < len(value)):  # 不接受布尔或负索引别名。
                return False  # 未知位置回到正常范围检查。
            value = value[part]  # 逐段确认实际存在的来源。
        except (KeyError, IndexError, TypeError):  # 失效历史不可冒充当前技术定位。
            return False  # 不猜目标。
    return technical  # 完整路径都没有离开声明边界。


def _check_question_targets(batch, question, *, retained_history=False):  # 历史只读复用与本轮可写问题分开。
    for target in question['target_paths']:  # 每个目标独立检查，混合业务目标不能借技术目标过门。
        owned = len(target) >= 3 and target[0] == 'cases' and type(target[1]) is int and 0 <= target[1] < len(batch['cases']) and batch['cases'][target[1]]['id'] == question['case_id']  # 原业务目标归属门。
        if not owned and not (retained_history and _technical_history_target(batch, target)):  # 只放行原样完成技术历史的读取。
            raise ValueError('Feedback answer target must belong to its affected case')  # 真实业务、未知及未显示目标仍拒绝。


def transition(state, action, payload):  # Called only through the record's explicit action allowlist.
    if action == 'review':  # 普通具体稿评审同样使用当前完整父源。
        arguments = copy.deepcopy(payload)
        source_catalog = arguments.pop('source_catalog', None)
        return flow.review(state, arguments, source_catalog=source_catalog)  # 原确认与当前版本门不变。
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
        previous = {question['id']: question for question in state['questions']}  # 唯一 QA 回放提供准确历史，而非调用者自报标签。
        applied = {question['id']: question for question in state['batch']['questions'] if question.get('id')}  # 仅具名已应用问题可准确匹配；原无编号建议不获历史例外。
        for question in questions:  # Reset active aspect answers, preserving their history.
            retained = question == previous.get(question['id']) and question == applied.get(question['id']) and flow._answered(question) and question['id'] not in reopened  # 新增、变更、重开及依赖失效都不是只读历史。
            _check_question_targets(batch, question, retained_history=retained)  # 完成技术来源保留；实际可写业务目标仍属于本例。
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
        arguments = copy.deepcopy(payload)
        source_catalog = arguments.pop('source_catalog', None)  # Caller provides the original complete source at recovery.
        result = apply_feedback(pending, arguments, source_catalog=source_catalog)  # Existing scope and exact summary checks.
        session = copy.deepcopy(result['review_session'])  # Full updated cases await review.
        session.pop('feedback_pending', None)  # This proposal has been applied.
        session['feedback_result'] = result  # Keep existing review_feedback boundary available.
        return session  # Approval remains pending for affected cases.
    if action == 'review_feedback':  # Review the entire selected revised case at its new version.
        arguments = copy.deepcopy(payload)
        source_catalog = arguments.pop('source_catalog', None)  # Recheck exact parent at the review boundary.
        result = review_feedback(state['feedback_result'], arguments, source_catalog=source_catalog)  # Existing review gate rejects stale versions.
        session = copy.deepcopy(result['review_session'])  # Retain precise approval scope.
        session['feedback_result'] = result  # Disposable rendering projection.
        return session  # Merge and execution remain separately authorized.
    if action in ('apply_summary', 'review') and state.get('feedback_pending'):  # Prevent ordinary actions from skipping pending proposal.
        raise ValueError('Pending feedback uses apply_feedback then review_feedback')  # One existing approval path.
    if state.get('feedback_pending') and action in ('respond', 'append_questions'):  # 允许复用历史不等于允许反馈期间跨例重写。
        active = payload if action == 'append_questions' else [next(q for q in state['questions'] if q['id'] == reply['question_id']) for reply in payload]  # 实际答复及新发现都是本轮问题。
        for question in active:  # 不让后续公开入口绕过相同目标归属。
            _check_question_targets(state['batch'], question)  # 修正技术历史须回正常澄清核定准确范围。
    method = getattr(flow, action)  # Caller has already allowlisted normal actions.
    return method(state) if action == 'summarize' else method(state, payload)  # Preserve normal workflow behavior.
