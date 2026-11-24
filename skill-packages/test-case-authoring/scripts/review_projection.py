"""Source-assessed display only; candidate business records remain authoritative."""
import copy
from authoring import _digest, _credential_guard
from review_expression import source_binding  # 当前 owner 实际使用的来源注册。


def _at(record, path):
    if not isinstance(path, list):  # JSON 路径必须显式逐段给出，不能按字符串猜位置。
        raise ValueError('Known dictionary keys and nonnegative list indexes required')
    for key in path:
        if isinstance(record, dict) and type(key) is str and key in record:  # 字典键不接受索引强转。
            record = record[key]
        elif isinstance(record, list) and type(key) is int and 0 <= key < len(record):  # bool、负数和越界保持拒绝。
            record = record[key]
        else:
            raise ValueError('Known dictionary keys and nonnegative list indexes required')
    return record


def _owner_digest(collection, owner):  # 已知评审控制变化不会伪造业务/source 漂移。
    if collection == 'cases':
        owner = {key: value for key, value in owner.items() if key not in ('review_status', 'final_review', 'review_history', 'merge_status', 'execution_status')}  # 语义/数据版本、实际条件和规则决定继续参与漂移检查。
    return _digest(owner)


def assess_review_projection(batch, *, source_version, basis, assessments, source_catalog=None):  # 可选准确父源沿既有 contract 校验。
    """Bind explicit semantic decisions to exact owner records, not field-name rules."""
    _credential_guard(assessments)
    if source_catalog is not None:
        from preparation_scope import scope_context  # 范围副本不得信任漂移的父来源。
        if scope_context(batch, source_catalog, require_parent=True)[1]:
            raise ValueError('Current complete source catalog required')
    if source_version != batch['content_version'] or not basis.strip():
        raise ValueError('Current source version and assessment basis required')
    result = copy.deepcopy(batch)
    records = []
    for item in assessments:
        if item.get('collection') not in ('cases', 'data', 'selection') or item.get('disposition') not in ('technical', 'duplicate', 'readable') or not item.get('rationale') or not item.get('path'):
            raise ValueError('Explicit leaf role, owner and rationale required')
        owner = next(r for r in batch[item['collection']] if r.get('id', r.get('case_id')) == item['id'])
        value = _at(owner, item['path'])
        if isinstance(value, (dict, list)) or value is None:  # 路径可穿过列表，但只评估真实标量叶。
            raise ValueError('Assess individual known leaves; preserve unknown or compound business conditions')
        if item['disposition'] == 'duplicate':
            if not item.get('equivalent_to') or not _at(owner, item['equivalent_to']):
                raise ValueError('Duplicate needs a retained equivalent field in the same owner')
        if item['disposition'] == 'readable' and not item.get('text'):
            raise ValueError('Readable meaning required')
        records.append(dict(copy.deepcopy(item), owner_digest=_owner_digest(item['collection'], owner), source_digest=source_binding(batch, [owner]), value=value))  # 已知审计状态不改变实际业务 owner。
    result['review_projection'] = dict(source_version=source_version, source_digest=_digest(batch.get('sources', [])), basis=basis, records=records)  # 来源注册变化同样使旧评估失效。
    _require_visible_equivalents(result)  # Validate the complete decision set, not each source leaf in isolation.
    result['content_version'] = _digest({k: v for k, v in result.items() if k != 'content_version'})
    return result  # Assessment is not user approval, review completion or execution authority.


def active_records(batch, collection, owner):
    return [r for r in batch.get('review_projection', {}).get('records', []) if r['collection'] == collection and r['id'] == owner.get('id', owner.get('case_id')) and r['owner_digest'] == _owner_digest(collection, owner) and r.get('source_digest') == source_binding(batch, [owner])]  # 真实业务或实际使用来源变化恢复原文。


def project_record(batch, collection, owner, *, binding_owner=None):
    decisions = {tuple(item['path']): item for item in active_records(batch, collection, binding_owner or owner)}  # 使用原始位置，删除叶不会移动后续绑定。
    omitted = object()  # 仅投影内的哨兵，不写入候选。
    def project(value, path):
        item = decisions.get(path)  # 按原 JSON 路径定位，而非重排后的索引。
        if item:
            return item['text'] if item['disposition'] == 'readable' else omitted
        if isinstance(value, dict):
            return {key: child for key, original in value.items() if (child := project(original, (*path, key))) is not omitted}
        if isinstance(value, list):
            return [child for index, original in enumerate(value) if (child := project(original, (*path, index))) is not omitted]
        return copy.deepcopy(value)  # 未评估的业务事实完整保留。
    return project(owner, ())


def technical_notes(batch, case, *, value_formatter=None, labels=None):  # Optional Agent-only display; grouping retains original authority.
    from scoped_review import GROUPS
    refs = {r for group in GROUPS for step in case.get(group, []) for r in step.get('data_refs', [])}
    owners = [('cases', case)] + [('selection', s) for s in batch.get('selection', []) if s['case_id'] == case['id']] + [('data', d) for d in batch['data'] if d['id'] in refs]
    notes = {}
    for ordinal, (collection, owner) in enumerate(owners):  # Stable order is inherited from the candidate.
        owner_id = owner.get('id', owner.get('case_id'))  # The collection scopes each identifier.
        ambiguous = not owner_id or sum(o.get('id', o.get('case_id')) == owner_id for o in batch[collection]) != 1  # Duplicate/missing identities remain unresolved.
        for occurrence, item in enumerate(active_records(batch, collection, owner)):
            if item['disposition'] == 'technical':
                value = item['value'].strip() if isinstance(item['value'], str) else item['value']  # Compare source text before any lossy display conversion.
                key = (tuple(item['path']), type(value).__name__, value)  # Full path and scalar type prevent accidental equivalence.
                displayed = value_formatter(item['path'], value) if value_formatter else str(value)  # Actual inputs and unknown enums remain unchanged.
                text = displayed.replace('\\', '\\\\').replace('\r', '\\r').replace('\n', '\\n').replace('\t', '\\t')  # Reversible escapes preserve interior whitespace in one Markdown line.
                identity = collection + ':' + str(owner_id)  # Bind to candidate identity, never the display title.
                name = owner.get('object_ref') if collection == 'data' else owner.get('title') or owner.get('name') or case['title']  # Data objects keep their own readable name.
                label = {'validity': '有效性', 'reuse_policy': '复用条件', 'invalidation_action': '失效后的处理', 'priority_basis': '优先级依据', 'maintenance_action': '维护动作', 'action': '变更动作', 'reason': '变更原因'}.get(item['path'][0], item['path'][0])  # Labels supplement the lossless path.
                label = (labels or {}).get(item['path'][0], label)  # Original JSON Pointer stays visible beside the label.
                scope = str(name or '未命名对象') + '（' + identity + '） / ' + label + '（/' + '/'.join(str(k).replace('~', '~0').replace('/', '~1') for k in item['path']) + '）'  # 列表索引按原始 JSON Pointer 保留。
                if ambiguous:
                    scope += '（身份歧义；对象位置 ' + str(ordinal + 1) + '，记录 ' + str(occurrence + 1) + '）'  # Retain each unresolved occurrence visibly.
                scope_key = (identity, ordinal, occurrence) if ambiguous else identity  # Never infer identity from a shared name.
                notes.setdefault(key, (text, {}))[1].setdefault(scope_key, scope)  # One occurrence of the same object per rule.
    return ['通用技术说明：' + text + '；适用：' + '、'.join(scopes.values()) for text, scopes in notes.values()]


def _require_visible_equivalents(batch):
    from scoped_review import _render  # Reuse the real business projection and its baseline-bound probe behavior.
    from uuid import uuid4  # A fresh marker cannot collide with source business wording.
    for item in batch['review_projection']['records']:
        if item['disposition'] != 'duplicate':
            continue
        probe = copy.deepcopy(batch)  # No marker or probe writes escape into the candidate.
        owner = next(r for r in probe[item['collection']] if r.get('id', r.get('case_id')) == item['id'])
        path = item['equivalent_to']  # Direct visible endpoint required; invisible intermediate chains are rejected.
        value = _at(owner, path)
        if isinstance(value, (dict, list)):  # _at 已核对真实字典键和列表索引。
            raise ValueError('Duplicate needs a visible scalar business equivalent')
        marker = 'retention' + uuid4().hex
        _at(owner, path[:-1])[path[-1]] = marker  # Trace this exact target, not another coincidentally equal value.
        baseline = copy.deepcopy(batch)  # Readable target text is itself the retained business expression.
        for target in baseline['review_projection']['records']:
            if (target['collection'], target['id'], target['path'], target['disposition']) == (item['collection'], item['id'], path, 'readable'):
                target['text'] = marker
        rendered = _render(probe, _expression_baseline=baseline)  # Generated titles still read original source fields.
        if marker not in rendered['human_view'] or marker not in rendered['xmind_markdown']:
            raise ValueError('Duplicate needs a final visible business equivalent; point directly to the retained endpoint')
