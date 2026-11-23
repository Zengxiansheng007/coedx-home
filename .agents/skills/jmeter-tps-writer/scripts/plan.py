"""Fill the editable native JMeter template."""
import copy
from pathlib import Path
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit


def prop(node, name):
    return node.find(f"./*[@name='{name}']")


def element(tag, gui, title):
    return ET.Element(tag, guiclass=gui, testclass=tag, testname=title, enabled="true")


def assertion(title, field, pattern, variable=None):
    check = element("ResponseAssertion", "AssertionGui", title)
    patterns = ET.SubElement(check, "collectionProp", name="Asserion.test_strings")
    ET.SubElement(patterns, "stringProp", name="pattern").text = pattern
    ET.SubElement(check, "stringProp", name="Assertion.test_field").text = field
    ET.SubElement(check, "intProp", name="Assertion.test_type").text = "1" if not variable else "8"
    ET.SubElement(check, "stringProp", name="Assertion.custom_message").text = title
    if variable:
        ET.SubElement(check, "stringProp", name="Assertion.scope").text = "variable"
        ET.SubElement(check, "stringProp", name="Scope.variable").text = variable
    return check


def generate(targets, path, confirmed_code_zero=(), *, ctoken_targets=(), raw_plan=None,
             account_file="accounts.tsv", gui_pilot=False):
    tree = ET.parse(Path(__file__).with_name("base.jmx"))
    group = tree.find(".//ThreadGroup/../hashTree")
    sampler, children = list(group)[-2:]
    group.remove(sampler)
    group.remove(children)
    tree.find(".//ThreadGroup").set("testname", "接口试跑")
    del group[:2]
    authenticated = any(t.captured_session for t in targets)
    if authenticated:
        variables = tree.find(".//collectionProp[@name='Arguments.arguments']")
        source = ET.SubElement(variables, "elementProp", name="account_source", elementType="Argument")
        ET.SubElement(source, "stringProp", name="Argument.name").text = "account_source"
        ET.SubElement(source, "stringProp", name="Argument.value").text = str(account_file)
        csv = element("CSVDataSet", "TestBeanGUI", "CSV 数据文件设置")
        for key, value in (("filename", "${__P(accounts.file,${account_source})}"),
                           ("fileEncoding", "UTF-8"), ("variableNames", "cookie"),
                           ("delimiter", r"\t"), ("shareMode", "shareMode.all")):
            ET.SubElement(csv, "stringProp", name=key).text = value
        for key, value in (("ignoreFirstLine", "true"), ("quotedData", "false"),
                           ("recycle", "false"), ("stopThread", "true")):
            ET.SubElement(csv, "boolProp", name=key).text = value
        group.extend([csv, ET.Element("hashTree")])
    defaults = element("ConfigTestElement", "HttpDefaultsGui", "HTTP 请求默认值")
    origins = [urlsplit(t.url) for t in targets]
    common = {}
    for name, values in (("domain", {p.hostname for p in origins}), ("protocol", {p.scheme for p in origins}),
                         ("port", {str(p.port or "") for p in origins})):
        if len(values) == 1:
            common[name] = values.pop()
            ET.SubElement(defaults, "stringProp", name="HTTPSampler." + name).text = common[name]
    arguments = ET.SubElement(defaults, "elementProp", name="HTTPsampler.Arguments", elementType="Arguments")
    ET.SubElement(arguments, "collectionProp", name="Arguments.arguments")
    group.insert(0, defaults)
    group.insert(1, ET.Element("hashTree"))
    imported = ET.parse(raw_plan).find(".//ThreadGroup/../hashTree") if raw_plan else None
    for index, target in enumerate(targets, 1):
        request, config = copy.deepcopy(sampler), copy.deepcopy(children)
        native_headers = None
        if imported is not None:
            request, native_children = list(imported)[2 * index - 2:2 * index]
            native_headers = native_children.find("HeaderManager")
            if native_headers is not None:
                # XStream aliases the GUI header manager to the sampler's embedded properties.
                embedded = prop(request, "HTTPSampler.header_manager")
                if embedded is not None:
                    native_headers[:] = list(embedded)
                    request.remove(embedded)
                config[0] = native_headers
                headers = native_headers.find("collectionProp")
                for item in list(headers):
                    key = prop(item, "Header.name")
                    if key is not None and (key.text or "").lower() == "cookie":
                        headers.remove(item)
        parts = urlsplit(target.url)
        label = f"T{index:02d}"
        request.set("testname", f"{target.titles[0]} [{label}]")
        comment = prop(request, "TestPlan.comments")
        if comment is None:
            comment = ET.SubElement(request, "stringProp", name="TestPlan.comments")
        comment.text = "、".join(target.titles)
        values = {"domain": parts.hostname, "port": str(parts.port or ""), "protocol": parts.scheme,
                  "path": (parts.path or "/") + ("?" + parts.query if parts.query else ""),
                  "method": target.method, "contentEncoding": target.encoding,
                  "postBodyRaw": str(target.body is not None).lower(), "follow_redirects": "false"}
        for name, value in values.items():
            if imported is not None and name not in {"domain", "protocol", "port", "path"}:
                continue
            field = prop(request, "HTTPSampler." + name)
            if field is None:
                field = ET.SubElement(request, "stringProp", name="HTTPSampler." + name)
            field.tag = "stringProp"
            field.text = "" if name in common else value
        args = request.find(".//collectionProp")
        if imported is None:
            if target.body is None:
                args.clear()
                args.set("name", "Arguments.arguments")
            else:
                prop(args[0], "Argument.value").text = target.body
        headers = config.find(".//HeaderManager/collectionProp")
        config.find("HeaderManager").set("testname", "HTTP 信息头管理器")
        business_headers = target.headers if imported is None else []
        for key, value in business_headers + ([("Cookie", "${cookie}")] if target.captured_session else []):
            h = ET.SubElement(headers, "elementProp", name="", elementType="Header")
            ET.SubElement(h, "stringProp", name="Header.name").text = key
            ET.SubElement(h, "stringProp", name="Header.value").text = value
        for value in [*values.values(), target.body or "", *(v for pair in target.headers for v in pair)]:
            if "${" in value:
                raise ValueError("输入含 JMeter 表达式，需要补充字面值")
        if target.captured_session:
            binding = element("JSR223PreProcessor", "TestBeanGUI", "核对实际账号行")
            ET.SubElement(binding, "stringProp", name="scriptLanguage").text = "groovy"
            ET.SubElement(binding, "stringProp", name="script").text = Path(__file__).with_name("bind.groovy").read_text(encoding="utf8")
            config.extend([binding, ET.Element("hashTree")])
        if target.follow:
            processor = ET.SubElement(config, "JSR223PostProcessor", guiclass="TestBeanGUI",
                                      testclass="JSR223PostProcessor", testname="仅跟随同源重定向", enabled="true")
            for key, value in [("scriptLanguage", "groovy"), ("cacheKey", "true"),
                               ("script", Path(__file__).with_name("redirect.groovy").read_text(encoding="utf-8"))]:
                ET.SubElement(processor, "stringProp", name=key).text = value
            ET.SubElement(config, "hashTree")
            script = prop(config.find(".//JSR223Assertion"), "script")
            script.text = "\n".join(line for line in script.text.splitlines()
                                    if not line.startswith("vars.put('redirect_codes',"))
        original = config.find("JSR223Assertion")
        config.remove(original)
        del config[2]  # the corresponding empty hashTree
        evidence = element("JSR223PostProcessor", "TestBeanGUI", "记录脱敏响应证据")
        evidence.extend(list(original))
        script = prop(evidence, "script")
        script.text = script.text.split("def failures = []")[0]
        if not target.captured_session:
            script.text += "\nvars.put('account_no','guest')\nvars.put('trial_phase',props.getProperty('trial.phase','full'))"
        config.extend([evidence, ET.Element("hashTree")])
        zero = label in confirmed_code_zero
        checks = [assertion("HTTP 状态为 2xx", "Assertion.response_code", "2[0-9][0-9]"),
                  assertion("业务成功（数值 code 为 0）" if zero else "业务成功（顶层 success 为布尔值 true）",
                            "Assertion.response_data", "numeric-zero" if zero else "true",
                            "code_kind" if zero else "success_value"),
                  assertion("响应无登录失效提示", "Assertion.response_data", "false", "login_hint")]
        for check in checks:
            config.extend([check, ET.Element("hashTree")])
        if label in ctoken_targets:
            prop(request, "HTTPSampler.path").text += ("&" if parts.query else "?") + "=".join(("ctoken", "${account_ctoken}"))
        destination = group
        if index > 1 and authenticated:
            action = element("TestAction", "TestActionGui", "等待上一目标完成")
            ET.SubElement(action, "intProp", name="ActionProcessor.action").text = "1"
            ET.SubElement(action, "intProp", name="ActionProcessor.target").text = "0"
            ET.SubElement(action, "stringProp", name="ActionProcessor.duration").text = "0"
            checkpoint = ET.Element("hashTree")
            group.extend([action, checkpoint])
            barrier = ET.SubElement(checkpoint, "SyncTimer", guiclass="TestBeanGUI",
                                    testclass="SyncTimer", testname="等待全部账号完成上一目标", enabled="true")
            ET.SubElement(barrier, "intProp", name="groupSize").text = "0"
            ET.SubElement(barrier, "longProp", name="timeoutInMs").text = "0"
            ET.SubElement(checkpoint, "hashTree")
        if authenticated and not target.captured_session:
            gate = element("IfController", "IfControllerPanel", "最终轮访客一次")
            ET.SubElement(gate, "stringProp", name="IfController.condition").text = "${__groovy(ctx.getThreadNum() == 0 && props.getProperty('trial.phase') != 'pilot')}"
            ET.SubElement(gate, "boolProp", name="IfController.useExpression").text = "true"
            destination = ET.Element("hashTree")
            group.extend([gate, destination])
        destination.extend([request, config])
    for gui, title in (("ViewResultsFullVisualizer", "查看结果树"), ("SummaryReport", "汇总报告"),
                       ("StatVisualizer", "聚合报告")):
        listener = element("ResultCollector", gui, title)
        listener.set("enabled", "false")
        group.extend([listener, ET.Element("hashTree")])
    if gui_pilot:
        listener = element("ResultCollector", "SimpleDataWriter", "保存 GUI 单账号试跑结果")
        ET.SubElement(listener, "stringProp", name="filename").text = "${__P(writer.gui.jtl,)}"
        group.extend([listener, ET.Element("hashTree")])
    ET.indent(tree)
    xml = ET.tostring(tree.getroot(), encoding="utf-8", xml_declaration=True)
    # XML readers normalize literal carriage returns, including inside HTTP bodies.
    path.write_bytes(xml.replace(b"\r", b"&#13;"))

