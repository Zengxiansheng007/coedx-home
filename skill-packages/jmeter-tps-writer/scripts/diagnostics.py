"""Explain observed failures using only bounded assertion evidence."""
import re
import xml.etree.ElementTree as ET


def explain(status, samples, expected, confirmed_code_zero=()):
    expected = set(expected)
    seen = set()
    lines = []
    questions = set()
    for row in samples:
        key = (row.get("account_no"), row.get("label"))
        seen.add(key)
        if row.get("success") == "true":
            continue
        account, target = key
        code = row.get("responseCode", "")
        if not code.isdigit():
            code = "传输异常，服务端结果未知"
        lines.append(f"账号 {account} · {target} · HTTP {code} · 响应类型 {row.get('body_kind')} · "
                     f"success={row.get('success_value')} · 登录提示={row.get('login_hint')}")
        target_id = re.search(r"(T[0-9]+)\]?$", target or "")
        target = target_id[1] if target_id else target
        lines.append(f"请求观测：方法 {row.get('wire_method')}，URL 是否含查询令牌 {row.get('wire_ctoken')}，"
                     f"请求是否携带会话头 {row.get('wire_cookie')}；响应字段 {row.get('known_fields')}。")
        if row.get("message_kind") == "ctoken-required":
            questions.add(f"{target} 明确要求查询令牌。请在本地用 --ctokens 提供对应账号的值，配合 --ctoken-target {target} 另轮复验。")
        elif (code == "200" and row.get("code_kind") == "numeric-zero"
              and row.get("success_value") == "absent" and target not in confirmed_code_zero):
            questions.add(f"{target} 顶层 code 为数值 0，缺少默认要求的布尔 success=true。"
                          f"该接口是否约定数值 0 表示成功？确认后仅对此目标使用 --confirmed-code-zero {target} 另轮复验。")
        else:
            questions.add(f"{target} 请核对预期响应、该账号权限和服务端对应记录，再决定修复项。")
    if status != "已执行":
        lines.append(f"已记录 {len(samples)} 条样本。")
        for account, target in sorted(expected):
            if (str(account), target) not in seen:
                state = "已知跳过" if status.startswith("未执行") else "状态未知"
                lines.append(f"账号 {account} · {target} · {state}")
    if lines:
        lines.append("排查依据：本轮 plan.jmx、分轮 JTL 与本地引擎日志；请求含义请对照原始 cURL。")
    return lines + sorted(questions)


def diagnostic_plan(source, destination, target):
    tree = ET.parse(source)
    matched = []
    for parent in tree.iter("hashTree"):
        children = list(parent)
        for index, sampler in enumerate(children):
            if sampler.tag != "HTTPSamplerProxy":
                continue
            name = sampler.get("testname", "")
            if name == target or name.endswith(" [" + target + "]"):
                logged = any((n.text or "").lower() == "cookie" for n in
                             children[index+1].findall(".//stringProp[@name='Header.name']"))
                matched.append((name, logged))
            else:
                sampler.set("enabled", "false")
    if len(matched) != 1:
        raise ValueError("定向复验需要一个存在且唯一的目标编号")
    destination.write_bytes(ET.tostring(tree.getroot(), encoding="utf-8").replace(b"\r", b"&#13;"))
    return matched[0]
