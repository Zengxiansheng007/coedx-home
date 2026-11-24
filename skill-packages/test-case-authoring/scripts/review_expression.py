"""Conservative human projection; semantic authoring remains an Agent decision."""

PROVENANCE_FIELDS = frozenset(('source', 'source_ref', 'lines', 'basis', 'provenance'))  # 仅用于已声明类型的来源定位。


LITERAL_FIELDS = frozenset(('value', 'input', 'inputs', 'output', 'outputs'))  # 实际业务值不继承框架字段语义。
STEP_GROUPS = frozenset(('steps', 'common_preconditions', 'special_preconditions', 'special_postconditions', 'common_postconditions'))  # 框架步骤仅在用例声明位置。


def field_role(role, key):  # 展示、反馈枚举与来源更新共享最薄类型边界。
    if role == 'literal':  # 已进入真实输入/产出后，所有后代键均为业务字面值。
        return 'literal'  # 不把其 source/id/step_reference 当作框架语义。
    if role == 'context':  # context 直属条目仍遵守已有来源 claim 契约。
        return 'claim'  # 实际输入字段属于该 claim 的子树。
    if key in LITERAL_FIELDS:  # 其他声明节点的实际输入/产出由共享字段契约确定。
        return 'literal'  # literal 从准确边界贯穿后代。
    if role == 'case' and key in STEP_GROUPS:  # 仅准确用例根声明步骤集合。
        return 'step'  # 列表索引不会改变节点类型。
    if role == 'case' and key == 'context':  # 必要业务条件根有明确 claim 契约。
        return 'context'  # 其真实条件分别拥有来源。
    if role == 'step' and key in ('expected', 'verification'):  # 已声明条件与结果。
        return 'claim'  # 未知扩展字典不自动继承 claim。
    return None  # 没有声明的语义不靠键名猜测。


def path_role(path, role='case'):  # 用已有业务路径重放同一类型边界。
    for key in path:  # 路径由公开入口逐段核对。
        if isinstance(key, str):  # 列表元素保持集合声明的类型。
            role = field_role(role, key)  # literal 一旦进入便保持至叶。
    return role  # 仅用于派生判断，不成为第二份持久权威。


def source_binding(batch, owners):  # 每个实际 typed 来源都须匹配；有未分辨项时保守绑定全部注册。
    from authoring import _digest  # 复用既有摘要，不新增来源权威。
    used, unresolved = set(), False  # 某个来源已匹配不能掩盖另一个未分辨来源。
    def visit(value, role):  # 只走框架 owner、步骤和 claim，不进入实际业务输入。
        nonlocal unresolved  # 结构化引用未声明解析规则时保守处理。
        if isinstance(value, list):  # 集合元素继承声明的角色。
            for child in value:  # 来源仍逐项检查。
                visit(child, role)  # 不通过字典键递归猜测来源。
        elif isinstance(value, dict):  # 只有这些声明节点拥有框架溯源。
            if role in ('case', 'step', 'claim'):  # owner 根涵盖 data/selection 等原契约。
                for key in ('source', 'source_ref'):  # 真实输入中的同名键没有此职责。
                    if key in value:  # 缺少字段与无法解析的显式引用分开。
                        reference = value[key]  # 原始引用不改写。
                        if isinstance(reference, str) and reference.strip():  # 已声明字符串身份。
                            used.add(reference)  # fragment 定位在注册匹配时处理。
                        else:  # file/section/lines 等结构体暂不猜字段含义。
                            unresolved = True  # 精确解析不可用时仍保持来源保护。
            for key, child in value.items():  # 路径角色由展示与反馈共用定义。
                child_role = field_role(role, key)  # literal 值从此不参与框架溯源。
                if child_role in ('context', 'step', 'claim'):  # 未知扩展也不当成已声明 claim。
                    visit(child, child_role)  # 只访问准确来源 owner。
    for owner in owners:  # 每个消费者保持既有粒度。
        visit(owner, 'case')  # 根溯源和准确声明的 context/步骤均纳入。
    registered = batch.get('sources', [])  # 原注册仍是唯一来源列表。
    matched = []  # 保留原注册顺序与完整记录摘要。
    for reference in used:  # 每个引用独立要求至少一个映射。
        exact = [item for item in registered if any(item.get(key) == reference for key in ('id', 'kind', 'ref', 'path', 'source_ref'))]  # 完整身份优先。
        base, separator, fragment = reference.partition('#')  # 明确片段只定位同一注册材料内部。
        targets = exact or ([item for item in registered if any(item.get(key) == base for key in ('ref', 'path', 'source_ref'))] if separator and base and fragment else [])  # 不用kind猜片段归属。
        if not targets:  # mixed mapped/unmapped 也保持保守绑定。
            unresolved = True  # 另一已匹配来源不能抹去本引用。
        matched.extend(item for item in targets if item not in matched)  # 同一个注册只绑定一次。
    selected = registered if unresolved or not used else [item for item in registered if item in matched]  # 明确未使用注册仍不波及局部评估。
    return _digest(selected)  # 漂移自动使旧评估失效，实际文字与引用保持原样。


def business_value(value, role=None):  # 类型位置决定职责，未知业务字典不套键名黑名单。
    if isinstance(value, list):
        return [business_value(child, role) for child in value]  # 原列表顺序有业务意义。
    if not isinstance(value, dict):
        return value
    excluded = PROVENANCE_FIELDS if role in ('claim', 'step', 'data') else frozenset()  # 实际输入 value 不继承来源类型。
    if role in ('step', 'data'):
        excluded = excluded | {'id'}  # 仅本地步骤/数据身份不参与业务同义比较。
    result = {}
    for key, child in value.items():
        if key in excluded:
            continue
        result[key] = business_value(child, field_role(role, key))  # 实际输入/产出不继承来源类型，其他位置沿声明角色。
    return result


def title(case):
    return str(case.get('priority', '待核对')) + ' ' + case.get('title', '待核对')  # Presentation never changes identity.


def unique_checks(expected, checks):
    return list(dict.fromkeys(check for check in checks if check not in expected))  # Legacy scalar callers.


def independent_checks(expected, checks, project, baseline=None):
    """Suppress whole identical claims, never matching fragments of different contexts."""
    original_expected, original_checks = baseline or (expected, checks)  # Feedback probes retain source visibility.
    seen = [project(claim) for claim in original_expected]  # Compare the complete supplied business context.
    output = []  # Order and all leaves of independent claims survive.
    for index, claim in enumerate(original_checks):
        meaning = project(claim)  # No similarity heuristic or inferred synonym equivalence.
        if meaning not in seen:
            output.extend(project(checks[index]))  # A scalar probe changes content, not which claims are visible.
            seen.append(meaning)  # Exact repeated whole claims need only one visible expression.
    return output
