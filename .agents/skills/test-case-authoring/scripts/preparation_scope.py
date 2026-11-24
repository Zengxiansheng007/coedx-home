"""Explicit source-assessed preparation scope; never executes data preparation."""
import copy
import hashlib
import json
from review_expression import source_binding  # 只绑定公共项实际使用的来源注册。


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode('utf-8')).hexdigest()  # Stable source binding, independent of output version.


def _binding(batch, case):
    from aggregation import business_path
    refs = {ref for step in case.get('common_preconditions', []) for ref in step.get('data_refs', [])}  # Include lifecycle and invalidation rules.
    return _digest([case['title'], case['module_path'], business_path(case), case.get('context'), case.get('dependencies'),
                    case.get('common_preconditions'), case.get('common_preconditions_note'),
                    [d for d in batch['data'] if d['id'] in refs]])  # Changes require renewed assessment.


def _source_binding(batch, case, scope=None):  # 按方向和有序步骤截取本公共项使用范围。
    group = 'common_postconditions' if scope and scope.get('direction') == 'post' else 'common_preconditions'
    selected = scope.get('step_ids_by_case', {}).get(case['id']) if scope else None
    steps = [step for step in case.get(group, []) if selected is None or step['id'] in selected]
    refs = {ref for step in steps for ref in step.get('data_refs', [])}
    owner = dict(context=case.get('context', {}), common_preconditions=steps)  # 不把正文其他来源变成公共项义务。
    return source_binding(batch, [owner, *[data for data in batch['data'] if data['id'] in refs]])


def _authoring_scope(batch, source_catalog):  # 完整新作者范围与父 P0 来源集合明确分开。
    baseline = batch.get('initial_copy_baseline') or {}
    if not baseline.get('not_displayed_case_ids'):
        if source_catalog is not None and scope_context(batch, source_catalog, require_parent=True)[1]:
            raise ValueError('Current complete source catalog required')
        return None
    if source_catalog is None or scope_context(batch, source_catalog, require_parent=True)[1]:
        raise ValueError('Review applicability against the exact complete source catalog')
    from authoring import _digest as digest  # 复用既有范围基线摘要，不另设权威。
    keys = ('cases', 'data', 'selection', *(['step_definitions'] if 'step_definitions' in baseline else []))
    ids = [case['id'] for case in batch['cases']]
    frozen = [case['id'] for case in baseline.get('cases', [])]
    parent = [case['id'] for case in source_catalog['cases']]
    selection = batch.get('selection', [])
    valid = (batch.get('extension_entry', {}).get('can_extend') is True and batch.get('extension_design') is not None
        and not baseline.get('catalog_cases') and ids and len(ids) == len(set(ids)) and set(ids) == set(frozen)
        and len(selection) == len(ids) and {item['case_id'] for item in selection} == set(ids)
        and all(item.get('action') == 'add' for item in selection) and not set(ids) & set(parent)
        and len(baseline['not_displayed_case_ids']) == len(parent) and set(baseline['not_displayed_case_ids']) == set(parent)
        and digest({key: baseline[key] for key in keys}) == baseline.get('copy_version'))  # 未展示集合不能混入遗漏的新作者成员。
    if not valid:
        raise ValueError('Only the complete newly authored scope may be assessed separately from its exact parent')
    return dict(case_ids=ids, parent_case_ids=parent, catalog_digest=baseline['catalog_digest'])  # 父 P0 仅作来源核对，不列为例外。


def review_preparation_scope(batch, *, applicable_case_ids, exception_case_ids, coverage, basis, actual_reply, version, frequency, business_group_path=None, operation_id=None, step_ids_by_case=None, direction="pre", scope_kind="business", source_catalog=None):
    """Record supplied source assessment and actual review; callers cannot infer approval."""
    authoring_scope = _authoring_scope(batch, source_catalog)  # 普通 partial 仍拒；完整新作者范围保留准确父源门。
    if scope_kind == 'case':  # 单例特殊归属仍写入原 preparation_scopes，不搬源步骤。
        return _review_case_preparation(batch, operation_id=operation_id, step_ids_by_case=step_ids_by_case, direction=direction,
            applicable_case_ids=applicable_case_ids, exception_case_ids=exception_case_ids, coverage=coverage,
            basis=basis, actual_reply=actual_reply, version=version, frequency=frequency, authoring_scope=authoring_scope, source_catalog=source_catalog)
    if operation_id is not None or step_ids_by_case is not None:  # Explicit per-item review uses the same candidate ledger.
        return review_operation_scope(batch, operation_id=operation_id, step_ids_by_case=step_ids_by_case,
            direction=direction, applicable_case_ids=applicable_case_ids, exception_case_ids=exception_case_ids,
            coverage=coverage, basis=basis, actual_reply=actual_reply, version=version, frequency=frequency,
            business_group_path=business_group_path, scope_kind=scope_kind, source_catalog=source_catalog)
    if direction != 'pre':
        raise ValueError('Legacy preparation scopes are pre only')
    from aggregation import business_path
    from review_expression import business_value  # 来源定位与实际准备义务分别比较。
    if coverage != 'vast_majority_few_exceptions' or not all(isinstance(v, str) and v.strip() for v in (basis, actual_reply, version, frequency)):
        raise ValueError('Preparation scope requires source-assessed broad applicability and actual review')
    ids = applicable_case_ids + exception_case_ids  # Explicit enumeration, never inferred from matching text.
    indexed = {c['id']: c for c in batch['cases']}
    if not applicable_case_ids or len(ids) != len(set(ids)) or set(ids) - indexed.keys():
        raise ValueError('Preparation scope requires known distinct cases')
    first = indexed[applicable_case_ids[0]]
    if scope_kind not in ('business', 'module'):
        raise ValueError('Unknown reviewed scope kind')  # Explicit module review is distinct from inferred grouping.
    path = ([] if scope_kind == 'module' else business_path(first)) if business_group_path is None else business_group_path
    if not isinstance(path, list) or (not path and business_path(first) and scope_kind != 'module') or business_path(first)[:len(path)] != path:
        raise ValueError('Scope must be an existing business ancestor')
    if scope_kind == 'module' and path:
        raise ValueError('A reviewed module scope cannot name a subgroup')  # Keep owner and assessment scope consistent.
    owner = (first['module_path'], path)
    members = [c for c in batch['cases'] if c['module_path'] == owner[0] and business_path(c)[:len(path)] == path]
    if set(ids) != {c['id'] for c in members} or (len(members) < 2 and scope_kind != 'module'):
        raise ValueError('Assess the complete existing business group, never regroup for reuse')
    meanings = []
    for cid in applicable_case_ids:
        case = indexed[cid]
        if not case.get('common_preconditions'):
            raise ValueError('Unknown or explicit absent preparation cannot become a shared obligation')
        steps = [{k: v for k, v in s.items() if k != 'id'} for s in case['common_preconditions']]
        refs = {r for s in steps for r in s.get('data_refs', [])}
        meanings.append([business_value(case.get('context'), 'context'), business_value(case.get('dependencies')),
            business_value(steps, 'step'), business_value(case.get('common_preconditions_note'), 'claim'),
            [business_value(d, 'data') for d in batch['data'] if d['id'] in refs]])  # 保留真实条件、字面对象字段与生命周期。
    if any(m != meanings[0] for m in meanings):
        raise ValueError('Shared preparation must retain identical conditions, data lifecycle and operations')
    result = copy.deepcopy(batch)
    record = dict(id=_digest(owner), module_path=owner[0], business_path=owner[1], scope_kind=scope_kind, version=version,
                  applicable_case_ids=list(applicable_case_ids), exception_case_ids=list(exception_case_ids),
                  exception_names=[indexed[c]['title'] for c in exception_case_ids], coverage=coverage, basis=basis,
                  actual_reply=actual_reply, frequency=frequency,
                  source_bindings={cid: _source_binding(batch, indexed[cid]) for cid in ids}, bindings={cid: _binding(batch, indexed[cid]) for cid in ids})  # 来源按成员绑定，不相干注册不波及本项。
    if authoring_scope is not None:
        record['authoring_scope'] = authoring_scope  # 记录完整本轮作者集合与仅来源校验的父集合。
    result['preparation_scopes'] = [s for s in result.get('preparation_scopes', []) if s['id'] != record['id']] + [record]
    result['content_version'] = _digest({k: v for k, v in result.items() if k != 'content_version'})  # Bind the saved scope review without a self-hash cycle.
    return result  # Candidate only: no merge, execution, or global writes.


def scope_context(batch, source_catalog=None, *, require_parent=False):  # Data ownership needs full context even without common scopes.
    """Validate a selected copy against its exact complete parent, never its visible count."""
    baseline = batch.get('initial_copy_baseline') or {}  # Existing source provenance remains the only parent locator.
    if not baseline or (not require_parent and not batch.get('preparation_scopes')):
        return batch, False
    expected = {c['id'] for c in baseline.get('cases', [])} | set(baseline.get('not_displayed_case_ids', []))
    if source_catalog is None:
        return batch, {c['id'] for c in batch['cases']} != expected  # Full copies can recheck locally; subsets require their parent.
    from authoring import _digest as catalog_digest
    if source_catalog.get('content_version') != baseline.get('catalog_version') or catalog_digest(source_catalog) != baseline.get('catalog_digest'):
        return batch, True  # A changed source needs a new copy/review; historical approval never certifies it.
    cases = {c['id']: c for c in source_catalog['cases']}
    cases.update({c['id']: c for c in batch['cases']})  # Current selected edits are checked against reviewed bindings.
    data = {d['id']: d for d in source_catalog['data']}
    data.update({d['id']: d for d in batch['data']})
    return dict(batch, cases=list(cases.values()), data=list(data.values())), False


def active_scopes(batch, source_catalog=None):
    from aggregation import business_path
    if source_catalog is not None:
        batch, unavailable = scope_context(batch, source_catalog)  # Use actual parent when provided; frozen legacy copies retain their original interpretation.
        if unavailable:
            return {}
    result = {}
    for scope in batch.get('preparation_scopes', []):
        if scope.get('contract_version') == 2:
            continue  # Per-item definitions are resolved separately.
        if scope.get('coverage') != 'vast_majority_few_exceptions' or not scope.get('actual_reply') or not _current_sources(batch, scope):  # 来源注册变化不能复用旧评估。
            continue
        members = [c for c in batch['cases'] if c['module_path'] == scope['module_path'] and business_path(c)[:len(scope['business_path'])] == scope['business_path'] and c['id'] not in scope.get('authoring_scope', {}).get('parent_case_ids', [])]  # 父 P0 不变成当前新作者范围的例外。
        ids = {c['id'] for c in members}
        expected = set(scope['applicable_case_ids'] + scope['exception_case_ids'])
        if ids != expected or any(_binding(batch, c) != scope['bindings'].get(c['id']) for c in members):
            continue  # New, moved, deleted or edited members stay inline until reviewed again.
        for cid in scope['applicable_case_ids']:
            result[cid] = scope
    return result


def _current_sources(batch, scope, case=None):  # 范围副本保留父源定位，新记录按成员核来源。
    bindings = scope.get('source_bindings')
    indexed = {owner['id']: owner for owner in batch['cases']}
    ids = [case['id']] if case is not None else scope['applicable_case_ids'] + scope['exception_case_ids']
    if bindings is None or all(cid in indexed and bindings.get(cid) == _source_binding(batch, indexed[cid], scope) for cid in ids):
        return True  # 历史记录保持原 owner 绑定；新记录增加可分辨的注册保护。
    baseline = batch.get('initial_copy_baseline') or {}
    return (scope in baseline.get('preparation_scopes', []) and len(batch.get('sources', [])) == 1
            and batch['sources'][0].get('kind') == 'existing_catalog'
            and batch['sources'][0].get('sha256') == baseline.get('catalog_digest'))  # 仅精确父源副本可延续原评估。


def _operation_binding(batch, case, scope):
    group = 'common_preconditions' if scope['direction'] == 'pre' else 'common_postconditions'  # Direction reserves the compatible post seam.
    selected = scope['step_ids_by_case'].get(case['id'], [])
    steps = [s for s in case.get(group, []) if s['id'] in selected]
    refs = {ref for step in steps for ref in step.get('data_refs', [])}
    from aggregation import business_path
    return _digest([case['module_path'], business_path(case), case.get('context'), case.get('dependencies'),
                    case.get(group + '_note'), steps, [d for d in batch['data'] if d['id'] in refs]])  # Exact action and lifecycle binding, not an execution cache.


def _review_case_preparation(batch, *, operation_id, step_ids_by_case, direction, applicable_case_ids, exception_case_ids, coverage, basis, actual_reply, version, frequency, authoring_scope, source_catalog):  # 本例归属是显式业务评估，不从公共排除自动推导。
    if (direction not in ('pre', 'post') or coverage != 'case_specific' or len(applicable_case_ids) != 1 or exception_case_ids
            or not all(isinstance(value, str) and value.strip() for value in (operation_id, basis, actual_reply, version, frequency))):
        raise ValueError('Explicit single-case preparation attribution and actual review required')
    cid = applicable_case_ids[0]  # 仅该例原有步骤，不扩大到其他成员。
    indexed = {case['id']: case for case in batch['cases']}
    if cid not in indexed or not isinstance(step_ids_by_case, dict) or set(step_ids_by_case) != {cid}:
        raise ValueError('Known single owner and ordered source steps required')
    case = indexed[cid]
    group = 'common_preconditions' if direction == 'pre' else 'common_postconditions'
    chosen = step_ids_by_case[cid]
    actual = [step['id'] for step in case.get(group, []) if step['id'] in chosen]
    if not chosen or len(chosen) != len(set(chosen)) or chosen != actual:
        raise ValueError('Case-specific attribution must preserve existing source step order')
    from aggregation import business_path  # 单例归属保留原模块及真实业务路径。
    record = dict(id=_digest([cid, direction, operation_id, 'special']), contract_version=2, attribution='special', scope_kind='case',
        operation_id=operation_id, module_path=case['module_path'], business_path=business_path(case), direction=direction,
        applicable_case_ids=[cid], exception_case_ids=[], exception_names=[], step_ids_by_case=copy.deepcopy(step_ids_by_case),
        coverage=coverage, basis=basis, actual_reply=actual_reply, version=version, frequency=frequency)
    record['bindings'] = {cid: _operation_binding(batch, case, record)}  # 完整业务条件和关联数据变化仍失效。
    record['source_bindings'] = {cid: _source_binding(batch, case, record)}
    if authoring_scope is not None:
        record['authoring_scope'] = copy.deepcopy(authoring_scope)
    active, _ = operation_scopes(batch, source_catalog)  # 已适用公共项不能被特殊项静默覆盖。
    if any(existing['id'] != record['id'] and existing['direction'] == direction and set(existing['step_ids_by_case'][cid]) & set(chosen) for existing in active.get(cid, [])):
        raise ValueError('Preparation attribution conflicts with an existing reviewed operation')
    result = copy.deepcopy(batch)
    result['preparation_scopes'] = [scope for scope in result.get('preparation_scopes', []) if scope['id'] != record['id']] + [record]
    result['content_version'] = _digest({key: value for key, value in result.items() if key != 'content_version'})
    return result  # 不改 case.common_*，无执行授权。


def review_operation_scope(batch, *, operation_id, step_ids_by_case, direction, **review):
    if direction not in ('pre', 'post') or not isinstance(operation_id, str) or not operation_id.strip():
        raise ValueError('An identified pre or post operation is required')
    group = 'common_preconditions' if direction == 'pre' else 'common_postconditions'  # One directional source locator.
    applicable = review['applicable_case_ids']
    if not isinstance(step_ids_by_case, dict) or set(step_ids_by_case) != set(applicable):
        raise ValueError('Each applicable case needs ordered source step identities')
    narrowed = copy.deepcopy(batch)  # Reuse existing complete-business-scope assessment, never invent a grouping.
    for case in narrowed['cases']:
        if case['id'] not in applicable:
            continue
        chosen = step_ids_by_case[case['id']]
        actual = [s for s in case.get(group, []) if s['id'] in chosen]
        if not chosen or len(chosen) != len(set(chosen)) or [s['id'] for s in actual] != chosen:
            raise ValueError('Common operations must preserve known source order without duplicate steps')
        case['common_preconditions'] = actual
        case.pop('common_preconditions_note', None)  # Whole-list prose cannot silently constrain a single selected item.
    checked = review_preparation_scope(narrowed, **review)
    record = copy.deepcopy(checked['preparation_scopes'][-1])
    record.update(id=_digest([record['module_path'], record['business_path'], direction, operation_id]), operation_id=operation_id,
                  contract_version=2, direction=direction, step_ids_by_case=copy.deepcopy(step_ids_by_case))
    result = copy.deepcopy(batch)
    for existing in result.get('preparation_scopes', []):
        if existing.get('attribution') != 'special' and all(existing.get(key) == record.get(key) for key in ('module_path', 'business_path', 'direction', 'operation_id')):  # 公共和本例特殊归属身份分开。
            record['id'] = existing['id']  # Re-review an older v2 identity without leaving a competing historical record.
    for existing in result.get('preparation_scopes', []):
        if existing['id'] == record['id']:
            continue
        if existing.get('contract_version') == 2:
            for cid, ids in step_ids_by_case.items():
                if direction == existing['direction'] and set(ids) & set(existing.get('step_ids_by_case', {}).get(cid, [])):
                    raise ValueError('One source operation cannot belong to competing common definitions')
        elif direction == 'pre' and set(applicable) & set(existing['applicable_case_ids']):
            raise ValueError('Resolve overlapping legacy scope before reviewing per-item definitions')
    indexed = {c['id']: c for c in batch['cases']}
    record['bindings'] = {cid: _operation_binding(batch, indexed[cid], record) for cid in record['bindings']}
    result['preparation_scopes'] = [s for s in result.get('preparation_scopes', []) if s['id'] != record['id']] + [record]
    result['content_version'] = _digest({k: v for k, v in result.items() if k != 'content_version'})
    return result


def operation_scopes(batch, source_catalog=None):
    """Return source-bound per-item memberships and local pending reasons."""
    from aggregation import business_path
    batch, unavailable = scope_context(batch, source_catalog)  # Validate parent before per-item memberships.
    approved, pending = {}, {}
    for scope in batch.get('preparation_scopes', []):
        if scope.get('contract_version') != 2:
            continue  # Legacy whole-list records retain their original read interpretation.
        members = [c for c in batch['cases'] if c['module_path'] == scope['module_path'] and business_path(c)[:len(scope['business_path'])] == scope['business_path'] and c['id'] not in scope.get('authoring_scope', {}).get('parent_case_ids', []) and (scope.get('attribution') != 'special' or c['id'] in scope['applicable_case_ids'])]  # 单例归属只评估该例，不继承给同组其他例。
        expected = scope['applicable_case_ids'] + scope['exception_case_ids']
        malformed = (unavailable or not scope.get('actual_reply') or scope.get('coverage') != ('case_specific' if scope.get('attribution') == 'special' else 'vast_majority_few_exceptions'))  # 本例归属不伪装成广泛共用。
        contradictory = {cid for cid in expected if expected.count(cid) > 1}  # Repeated or crossed membership is local to that identity.
        indexed = {c['id']: c for c in batch['cases']}
        actual = {c['id'] for c in members}
        for cid in set(expected) | actual:  # Membership changes affect the changed member, never unrelated reviewed cases.
            invalid = malformed or cid in contradictory or cid not in expected or cid not in actual or (cid in indexed and not _current_sources(batch, scope, indexed[cid]))  # 注册漂移仅阻塞实际受影响成员。
            invalid = invalid or (cid in indexed and _operation_binding(batch, indexed[cid], scope) != scope['bindings'].get(cid))
            if invalid:
                pending[cid] = '公共操作适用范围待重新核对：' + scope['operation_id']
            elif cid in scope['applicable_case_ids']:
                approved.setdefault(cid, []).append(scope)
    for cid, records in list(approved.items()):
        conflicts = {record['id'] for record in records for other in records if other is not record
            and record['direction'] == other['direction']
            and set(record['step_ids_by_case'][cid]) & set(other['step_ids_by_case'][cid])}  # Only competing items are withheld.
        if conflicts:
            pending[cid] = '公共操作范围交叉冲突，待核对'
            approved[cid] = [record for record in records if record['id'] not in conflicts]
    return approved, pending
