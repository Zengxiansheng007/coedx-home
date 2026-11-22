"""Windows JMeter trial entry point."""
import argparse
from collections import Counter
import hashlib
import json
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from tempfile import TemporaryDirectory

from native_import import generate_raw

from accounts import read_column
from diagnostics import explain, diagnostic_plan
from requests_input import parse_requests
from engine import launcher_args, prepare_output, rebuild_report, run_round
from plan import generate


def coverage(samples, expected):
    counts = Counter((r.get("account_no"), r.get("label")) for r in samples)
    for account, target in expected:
        n = counts[account, target]
        detail = "缺失" if n == 0 else "重复" if n > 1 else "完整"
        yield f"账号 {account} · {target} · 预期 1，实际 {n}（{detail}）"
    for account, target in counts.keys() - set(expected):
        yield f"账号 {account} · {target} · 预期 0，实际 {counts[account, target]}（意外组合）"


def check_round(status, samples, expected):
    actual = [(row.get("account_no"), row.get("label")) for row in samples]
    return (status == "已执行" and Counter(actual) == Counter(expected)
            and all(row.get("success") == "true" and row.get("login_hint") == "false" for row in samples))


def main():
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--requests", type=Path)
    source.add_argument("--plan", type=Path, help="复跑已交付的可信本地计划")
    parser.add_argument("--html", action="store_true")
    source.add_argument("--rebuild-report", type=Path, metavar="FINAL_JTL")
    parser.add_argument("--out", type=Path)
    account_input = parser.add_mutually_exclusive_group()
    account_input.add_argument("--accounts", type=Path)
    account_input.add_argument("--accounts-stdin", action="store_true", help="从 UTF-8 标准输入读取单列 TSV，保存为计划旁的 accounts.tsv")
    parser.add_argument("--gui-pilot", action="store_true", help="打开最终 JMX，点击启动并在结束后关闭 GUI，随后自动执行最终轮")
    parser.add_argument("--jmeter", default="jmeter.bat")
    parser.add_argument("--pilot-account", type=int, default=1)
    parser.add_argument("--confirmed-code-zero", action="append", default=[])
    parser.add_argument("--ctokens", type=Path)
    parser.add_argument("--ctoken-target", action="append", default=[])
    parser.add_argument("--diagnose-target", metavar="T01", help="只复验此目标并单独保存记录")
    parser.add_argument("--guest-target", action="append", default=[], help="已确认免登录的目标编号")
    parser.add_argument("--login-target", action="append", default=[], help="已确认需要登录的目标编号")
    args = parser.parse_args()
    if args.gui_pilot and (not args.requests or args.pilot_account != 1 or args.diagnose_target):
        parser.error("--gui-pilot 用于新建计划，按 GUI 默认读取账号 1。")
    if args.rebuild_report:
        try:
            report = args.out or (args.rebuild_report.resolve().parent.parent / "report-rebuilt")
            return 0 if rebuild_report(args.rebuild_report, report, args.jmeter) else 1
        except (OSError, ValueError) as exc:
            parser.error(str(exc))
    args.out = prepare_output(args.out)
    print(args.out)
    summary = args.out / "summary.md"
    lines = []
    try:
        plan = args.out / "plan.jmx"
        if args.plan:
            if args.confirmed_code_zero or args.ctoken_target or args.guest_target or args.login_target:
                raise ValueError("复跑沿用计划内已确认的断言和查询字段。")
            tree = ET.parse(args.plan)
            for sampler in tree.findall(".//HTTPSamplerProxy"):
                flags = ("HTTPSampler.follow_redirects", "HTTPSampler.auto_redirects")
                if any((node.text or "").strip().lower() != "false" for node in sampler
                       if node.get("name") in flags):
                    raise ValueError("原计划启用了 JMeter 自动跳转，请用原始 cURL 重新生成包含同源检查的计划。")
            labels = [n.attrib["testname"] for n in tree.findall(".//HTTPSamplerProxy")]
            guest_only = not any(n.text in ("${cookie}", "${account_cookie}") for n in tree.findall(".//stringProp[@name='Header.value']"))
            if not labels:
                raise ValueError("计划缺少目标请求。")
            needs_tokens = any("${account_ctoken}" in (n.text or "") for n in tree.findall(".//stringProp[@name='HTTPSampler.path']"))
            if needs_tokens != bool(args.ctokens):
                raise ValueError("查询值文件应与原计划所需字段一致。")
            shutil.copyfile(args.plan, plan)
            titles = args.plan.with_name("targets.md")
            if titles.is_file():
                shutil.copyfile(titles, args.out / "targets.md")
        else:
            targets = parse_requests(args.requests.read_text(encoding="utf-8-sig"))
            labels = [f"T{i:02d}" for i in range(1, len(targets) + 1)]
            if bool(args.ctoken_target) != bool(args.ctokens) or set(args.ctoken_target) - set(labels):
                raise ValueError("已确认需要 URL ctoken 的目标编号和本地值文件必须一起提供。")
            if set(args.confirmed_code_zero) - set(labels):
                raise ValueError("确认规则引用了不存在的目标编号")
            (args.out / "targets.md").write_text("\n".join(
                f"{label} · {'、'.join(t.titles)}" for label, t in zip(labels, targets)), encoding="utf8")
            plan = args.out / "plan.jmx"
            if (set(args.guest_target + args.login_target) - set(labels)
                    or set(args.guest_target) & set(args.login_target)):
                raise ValueError("请为每个编号确认唯一的登录要求。")
            for label, target in zip(labels, targets):
                if label in args.guest_target:
                    target.captured_session = ""
                if label in args.login_target and not target.captured_session:
                    raise ValueError(f"{label} 请补充抓包会话 Cookie。")
            guest_only = all(not target.captured_session for target in targets)
        if args.accounts_stdin and not guest_only:
            args.accounts = args.out / "accounts.tsv"
            data = sys.stdin.buffer.read().decode("utf-8-sig")
            with args.accounts.open("x", encoding="utf8") as stream:
                stream.write(data.replace("\r\n", "\n"))
        if not guest_only and not args.accounts:
            raise ValueError("需登录接口需要 --accounts。")
        cookies = read_column(args.accounts, "cookie") if args.accounts and not guest_only else []
        if len(cookies) != len(set(cookies)):
            raise ValueError("账号 Cookie 行重复，无法唯一核对身份。")
        count = len(cookies)
        if not guest_only and not 1 <= args.pilot_account <= count:
            raise ValueError("先导账号编号超出输入行数。")
        if args.ctokens and len(read_column(args.ctokens, "ctoken")) != count:
            raise ValueError("ctoken 行数必须与账号行数相同。")
        account_file = "accounts.tsv" if args.accounts_stdin or not cookies else str(args.accounts.resolve())
        if cookies and args.plan and ".private/accounts.path" in plan.read_text(encoding="utf8"):
            reference = plan.parent / ".private" / "accounts.path"
            reference.parent.mkdir()
            reference.write_text(str(args.accounts.resolve()), encoding="utf8")
        elif cookies and args.plan:
            source = tree.find(".//elementProp[@name='account_source']/stringProp[@name='Argument.value']")
            if source is not None and source.text != account_file:
                source.text = account_file
                xml = ET.tostring(tree.getroot(), encoding="utf-8", xml_declaration=True)
                plan.write_bytes(xml.replace(b"\r", b"&#13;"))
        if args.requests:
            account_numbers = {}
            for label, target in zip(labels, targets):
                if target.captured_session:
                    matches = [i for i, session in enumerate(cookies, 1) if session == target.captured_session]
                    if len(matches) != 1:
                        raise ValueError(f"{label} 抓包 Cookie 需要对应唯一账号行。")
                    account_numbers[label] = matches[0]
                else:
                    account_numbers[label] = "guest"
            if not launcher_args(args.jmeter):
                generate(targets, plan, confirmed_code_zero=args.confirmed_code_zero, ctoken_targets=args.ctoken_target,
                         account_file=account_file)
                raise ValueError("缺少 JMeter 或 Java；已保存未执行的草稿 plan.jmx")
            with TemporaryDirectory() as private:
                raw = Path(private).resolve() / "raw.jmx"
                generate_raw(targets, raw, args.jmeter, account_numbers,
                             confirmed_code_zero=args.confirmed_code_zero)
                trial = raw
                if args.diagnose_target:
                    isolated = raw.with_name("raw-selected.jmx")
                    diagnostic_plan(raw, isolated, args.diagnose_target)
                    trial = isolated
                status, samples = run_round(trial, args.accounts, args.out, "raw", 1, 1, args.jmeter)
                expected = [(str(account_numbers[label]), label) for label in labels if not args.diagnose_target or label == args.diagnose_target]
                lines.append(f"# 原样试跑\n\n{status}，预期 {len(expected)} 条，实际 {len(samples)} 条。")
                lines.extend(coverage(samples, expected))
                for sample in samples:
                    lines.append(f"{sample['label']} · 对照抓包={sample.get('capture_diff')}，原样实发方法={sample.get('wire_method')}，"
                                 f"URL 是否含查询令牌 {sample.get('wire_ctoken')}，请求是否携带会话头 {sample.get('wire_cookie')}。")
                if not check_round(status, samples, expected) or any(
                        row.get("capture_diff") != "matched" for row in samples):
                    lines.extend(explain(status, samples, expected, args.confirmed_code_zero))
                    lines.append("已知跳过：整理后单账号试跑和最终验证。")
                    summary.write_text("\n\n".join(lines), encoding="utf8")
                    return 1
                generate(targets, plan, confirmed_code_zero=args.confirmed_code_zero, ctoken_targets=args.ctoken_target,
                         raw_plan=raw, account_file=account_file, gui_pilot=args.gui_pilot and not guest_only)
            labels = [n.get("testname") for n in ET.parse(plan).findall(".//HTTPSamplerProxy")]
        if args.diagnose_target:
            with TemporaryDirectory() as private:
                isolated = Path(private) / "diagnostic.jmx"
                name, logged = diagnostic_plan(plan, isolated, args.diagnose_target)
                identity = str(args.pilot_account) if logged else "guest"
                status, samples = run_round(isolated, args.accounts, args.out, "diagnostic",
                                            args.pilot_account, 1, args.jmeter, args.ctokens)
            expected = [(identity, name)]
            lines.extend(["# 定向复验", status, *coverage(samples, expected),
                          *explain(status, samples, expected, args.confirmed_code_zero),
                          "交付前须使用完整 plan.jmx 进行最终验证。"])
            summary.write_text("\n\n".join(lines), encoding="utf8")
            return 0 if check_round(status, samples, expected) else 1
        guest_labels = set()
        tree = ET.parse(plan)
        for subtree in tree.iter("hashTree"):
            for node, configs in zip(subtree, list(subtree)[1:]):
                if node.tag == "HTTPSamplerProxy" and not any(
                        item.text in ("${cookie}", "${account_cookie}") for item in configs.findall(".//stringProp[@name='Header.value']")):
                    guest_labels.add(node.get("testname"))
    except (OSError, UnicodeError):
        summary.write_text("未执行：需要可读的 UTF-8 本地输入。", encoding="utf8")
        return 2
    except (ValueError, ET.ParseError) as exc:
        summary.write_text(f"未执行：{exc}", encoding="utf8")
        return 2
    for phase, title, first, threads in [("pilot", "单账号试跑", args.pilot_account, 1),
                                        ("full", "最终验证", 1, 1 if guest_only else count)]:
        if guest_only and phase == "pilot":
            continue
        before = hashlib.sha256(plan.read_bytes()).hexdigest()
        status, samples = run_round(plan, args.accounts, args.out, phase, first, threads, args.jmeter, args.ctokens,
                                    gui=args.gui_pilot and phase == "pilot")
        expected = [(str(a), label) for a in range(first, first + threads) for label in labels if label not in guest_labels]
        if phase == "full":
            expected.extend(("guest", label) for label in labels if label in guest_labels)
        passed = check_round(status, samples, expected)
        if hashlib.sha256(plan.read_bytes()).hexdigest() != before:
            passed = False
            lines.append("运行期间 JMX 已修改，请用保存后的计划重新验证。")
        if passed and phase == "full":
            try:
                total = json.loads((args.out / "report/statistics.json").read_text(encoding="utf8"))["Total"]
                passed = total["sampleCount"] == len(samples) and total["errorCount"] == 0
            except (OSError, ValueError, KeyError, TypeError):
                passed = False
            if not passed:
                lines.append("Dashboard 汇总与最终 JTL 无法核对。")
        lines.append(f"# {title}\n\n{status}，预期 {len(expected)} 条，实际 {len(samples)} 条。")
        lines.extend(coverage(samples, expected))
        for row in samples:
            lines.append(f"账号 {row.get('account_no')} · {row.get('label')} · HTTP {row.get('responseCode')} · "
                         f"{row.get('elapsed')} ms · {'通过' if row.get('success') == 'true' else '失败'} · "
                         f"success={row.get('success_value')}，登录提示={row.get('login_hint')}")
            if row.get("redirect_codes"):
                lines.append(f"跟随跳转（子请求） · {row['redirect_codes']}")
            if row.get("timeout_state"):
                lines.append("客户端超时，本次计一次，服务端结果未知。")
        lines.extend(explain(status, samples, expected, args.confirmed_code_zero))
        if not passed:
            if phase == "pilot":
                lines.append("全账号验证未执行。")
            break
    if passed:
        digest = hashlib.sha256(plan.read_bytes()).hexdigest()
        conclusion = "访客业务验证通过。" if guest_only else "全账号验证通过，本轮所有账号登录态可用。"
        lines.append(f"{conclusion}计划 SHA-256：{digest}")
        if not guest_only:
            (args.out / "accounts.template.tsv").write_text("cookie\n", encoding="utf8")
        extra = ' --ctokens "C:\\local\\ctokens.tsv"' if args.ctokens else ""
        command = ('python scripts/writer.py --plan "<上轮输出>\\plan.jmx" '
                   '--accounts "C:\\local\\accounts.tsv" --out "<新的输出目录>" '
                   f'--pilot-account {args.pilot_account}' + extra)
        if guest_only:
            command = 'python scripts/writer.py --plan "<上轮输出>\\plan.jmx" --out "<新的输出目录>"'
        def quoted(value):
            return "'" + str(value).replace("'", "''") + "'"
        native = (f"& {quoted(shutil.which(args.jmeter) or args.jmeter)} -n -t {quoted(plan)} "
                  f"-l {quoted(args.out / 'result' / 'rerun.jtl')} -e -o {quoted(args.out / 'report-rerun')} "
                  f"'-Jthreads={count or 1}'")
        if args.ctokens:
            native += " " + quoted("-Jctokens.file=" + str(args.ctokens.resolve()))
        (args.out / "rerun.md").write_text("JMeter 最终轮复跑（再次执行请换新的 JTL 和报告路径）\n\n```powershell\n"
            + native + "\n```\n\nWriter 分轮复验\n\n```powershell\n" + command + "\n```\n", encoding="utf8")
    summary.write_text("\n\n".join(lines) + "\n", encoding="utf8")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
