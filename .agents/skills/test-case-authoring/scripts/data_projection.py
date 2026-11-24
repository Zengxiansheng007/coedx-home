"""Display named scalar data without changing the authoritative record."""
import json  # 仅控制字符与反斜线使用可逆字符串转义。
import re  # 固定保留表示的边界，不按任意冒号拆业务值。

_SPACED = re.compile(r'^“(.*)”（前导空格：([0-9]+)；尾随空格：([0-9]+)）$', re.S)  # 完整表示才有解码语义。


def _display_string(value):  # 原始普通空格保留在闭合引号内，中文计数便于人读。
    if not isinstance(value, str) or (value == value.strip(' ') and not any(char in value for char in '\r\n\t') and not _SPACED.fullmatch(value)):
        return value
    leading, trailing = len(value) - len(value.lstrip(' ')), len(value) - len(value.rstrip(' '))
    return '“' + json.dumps(value, ensure_ascii=False)[1:-1] + '”（前导空格：' + str(leading) + '；尾随空格：' + str(trailing) + '）'  # 原值撞保留表示时再包一层。


def _decode_string(text):  # 提示从不直接写入真实数据。
    match = _SPACED.fullmatch(text)
    if not match:
        if text.startswith('“') and '（前导空格：' in text:
            raise ValueError('Invalid visible whitespace representation; clarify exact value')
        return text  # 旧稿和普通字符串沿原精确值解释。
    try:
        value = json.loads('"' + match[1] + '"')  # 转义只在明确保留表示内解码。
    except (ValueError, TypeError) as error:
        raise ValueError('Invalid visible whitespace representation') from error
    if (len(value) - len(value.lstrip(' ')), len(value) - len(value.rstrip(' '))) != (int(match[2]), int(match[3])):
        raise ValueError('Whitespace counts differ from the actual quoted value')
    return value  # 精确恢复原始空格，不把引号或计数当作业务输入。


def data_lines(record, project, *, legacy=False, metadata_legacy=False):  # 新可选标志仅重现已知旧 metadata 布局。
    from scoped_review import TECHNICAL_FIELDS  # Reuse existing provenance classification.
    visible = {key: value for key, value in record.items() if key not in TECHNICAL_FIELDS and (metadata_legacy or key != 'source_ref')}  # 仅 data 根的声明来源定位外置。
    if not metadata_legacy and 'value' in visible:
        visible['value'] = _display_string(visible['value'])  # 仅临时显示副本，原 record 不变。
    if (not legacy and {'object_ref', 'value'} <= set(visible) and set(visible) - {'object_ref', 'value'} <= (set() if metadata_legacy else {'validity', 'reuse_policy', 'invalidation_action'}) and
            isinstance(visible['object_ref'], str) and visible['object_ref'].strip() and
            isinstance(visible['value'], (str, int, float, bool))):  # Extra conditions always keep their own structure.
        return [visible['object_ref'] + '：' + str(visible['value']), *project({key: value for key, value in visible.items() if key not in ('object_ref', 'value')})]  # 对象值同行，生命周期与例外仍独立可读。
    return project(record if metadata_legacy else visible)  # 新格式保留真实 value 子树；旧格式沿原键过滤。


def decode_line(old, new, bindings):
    """Resolve exact renderer probes; never split arbitrary configuration colons."""
    import html
    def value(line, binding):
        prefix, suffix = binding[3:]
        if not line.startswith(prefix) or (suffix and not line.endswith(suffix)):
            raise ValueError('Markdown structure or labels changed')
        return html.unescape(line[len(prefix):len(line)-len(suffix) if suffix else None].replace('<br>', '\n'))
    def key(binding):
        return binding[0], binding[1], tuple(binding[2])
    original = {key(b): value(old, b) for b in bindings}  # Every original scalar comes from its probe boundary.
    if old == new:
        return original
    if len(bindings) == 1:
        return {key(bindings[0]): value(new, bindings[0])}
    pair = {tuple(b[2]): b for b in bindings}
    if (len(bindings) != 2 or set(pair) != {('object_ref',), ('value',)} or
            len({(b[0], b[1]) for b in bindings}) != 1 or bindings[0][0] != 'data'):
        raise ValueError('Unmapped Markdown edit')  # Unrelated joined fields require explicit interpretation.
    candidates = []
    for binding in bindings:  # An untouched counterpart anchors even values containing full-width colons.
        try:
            candidate = dict(original)  # Retain the counterpart unless its own bound edit is identified.
            candidate[key(binding)] = value(new, binding)
            if candidate not in candidates:
                candidates.append(candidate)
        except ValueError:
            pass
    left, right = pair[('object_ref',)], pair[('value',)]
    prefix, suffix = left[3], right[4]  # Outer structure comes only from the two existing field probes.
    if new.startswith(prefix) and (not suffix or new.endswith(suffix)):
        payload = new[len(prefix):len(new)-len(suffix) if suffix else None]
        baseline = old[len(prefix):len(old)-len(suffix) if suffix else None]
        quoted = payload.partition('：')[2]  # 计数内冒号属于明确字符串，不是对象分隔符。
        baseline_quoted = baseline.partition('：')[2]
        if payload.count('：') == baseline.count('：') == 1 or (_SPACED.fullmatch(quoted) and _SPACED.fullmatch(baseline_quoted)):
            name, scalar = payload.split('：', 1)  # 仍只接受原探针证明的对象/值外层分隔。
            candidate = {key(left): html.unescape(name.replace('<br>', '\n')), key(right): html.unescape(scalar.replace('<br>', '\n'))}
            if candidate not in candidates:
                candidates.append(candidate)
    if len(candidates) != 1:
        raise ValueError('Ambiguous object/value edit; clarify original fields')
    return candidates[0]


def typed_value(text, original, *, display_encoded=False):  # 字符串标识只在当前 data.value 显示类型中有协议含义。
    """Decode a bound scalar without changing its authoritative type."""
    import math
    import re
    if type(original) is str:
        return _decode_string(text) if display_encoded else text  # 历史稿/真实嵌套字段/用例正文不误解码同形文字。
    if type(original) is bool and text in ('True', 'False'):
        return text == 'True'  # Boolean syntax is exactly the rendered language.
    if type(original) is int and re.fullmatch(r'-?(?:0|[1-9][0-9]*)', text):
        return int(text)  # Reject decimal/fractional edits to integer fields.
    if type(original) is float and re.fullmatch(r'-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?', text):
        value = float(text)
        if math.isfinite(value):
            return value  # Preserve float identity even when the displayed value is integral.
    raise ValueError('Invalid typed scalar edit; clarify the original value')
