"""Use the JMeter 5.6.3 Import from cURL component factory in a private directory."""
import copy
import hashlib
import json
import os
from pathlib import Path
from engine import resolve_java
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit

from plan import prop

SCRIPTS = Path(__file__).resolve().parent


def quoted(value):
    return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'


def command(target, guest):
    args = ["curl", "-X", target.method, target.raw_url]
    for key, value in target.headers:
        args.extend(["-H", key + ": " + value])
    if target.captured_session and not guest:
        args.extend(["-H", ": ".join(("Cookie", target.captured_session))])
    if target.body is not None:
        args.extend(["--data-raw", target.body])
    return " ".join(quoted(arg) if i and not arg.startswith("-") else arg for i, arg in enumerate(args))


def setprop(node, key, value):
    item = prop(node, key)
    if item is None:
        item = ET.SubElement(node, "stringProp", name=key)
    item.text = value


def capture_comparison(target):
    """Record names of differing fields only. Expected values stay in the private import."""
    def digest(value):
        return hashlib.sha256(value.encode("utf8")).hexdigest()
    expected = dict(method=digest(target.method), url=digest(target.raw_url),
                    body=digest(target.body or ""))
    headers = [(key.lower(), digest(value)) for key, value in target.headers]
    if target.captured_session:
        headers.append(("cookie", digest(target.captured_session)))
    # Embed only ASCII hex in Groovy. Header names are untrusted browser input.
    pairs = ", ".join("['" + digest(k) + "','" + v + "']" for k, v in headers)
    return f"""
def fingerprint = {{ v -> java.security.MessageDigest.getInstance('SHA-256').digest((v ?: '').getBytes('UTF-8')).encodeHex().toString() }}
def differences = []
if (fingerprint(prev.getHTTPMethod()) != '{expected["method"]}') differences << 'method'
if (fingerprint(prev.getURL()?.toString()) != '{expected["url"]}') differences << 'url'
if (fingerprint(prev.getQueryString()) != '{expected["body"]}' && sampler.getMethod() != 'GET') differences << 'body'
def headerPairs = (prev.getRequestHeaders() ?: '').readLines().findResults {{ h ->
    int colon = h.indexOf(':')
    colon <= 0 ? null : [fingerprint(h.substring(0,colon).toLowerCase(java.util.Locale.ROOT)), fingerprint(h.substring(colon+1).trim())]
}}
if (prev.getCookies()) headerPairs << [fingerprint('cookie'),fingerprint(prev.getCookies())]
if (!headerPairs.containsAll([{pairs}])) differences << 'headers'
vars.put('capture_diff', differences ? differences.join('|') : 'matched')
"""

def generate_raw(targets, path, jmeter, account_numbers=None, guest_targets=(), confirmed_code_zero=()):
    launcher = shutil.which(str(jmeter))
    java = resolve_java()
    if not launcher or not java:
        raise ValueError("缺少 Java 或 JMeter，原样试跑未执行")
    home = Path(launcher).resolve().parents[1]
    cp = os.pathsep.join(str(home / d / "*") for d in ("bin", "lib", "lib/ext"))
    tree = ET.parse(SCRIPTS / "base.jmx")
    group = tree.find(".//ThreadGroup/../hashTree")
    assertion = copy.deepcopy(group.find(".//JSR223Assertion"))
    group.clear()
    labels = [f"T{i:02d}" for i in range(1, len(targets)+1)]
    with tempfile.TemporaryDirectory(dir=path.parent) as tmp:
        imported = Path(tmp) / "import.jmx"
        config = Path(tmp) / "silent.xml"
        config.write_text('<Configuration status="OFF"><Loggers><Root level="off"/></Loggers></Configuration>')
        invocation = [java, "-Dfile.encoding=UTF-8", "-Djava.awt.headless=true",
                      "-Dlog4j.configurationFile=" + config.as_uri(), "-cp", cp,
                      "groovy.ui.GroovyMain", str(SCRIPTS / "import_curl.groovy"), str(home), str(imported)]
        commands = [command(t, label in guest_targets) for t, label in zip(targets, labels)]
        run = subprocess.run(invocation, input=json.dumps(commands).encode(), cwd=tmp,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if run.returncode or not imported.exists():
            raise ValueError("JMeter 5.6.3 原生导入失败，请核对安装与 Java 运行环境")
        components = list(ET.parse(imported).find("hashTree"))
    for idx, (label, target) in enumerate(zip(labels, targets)):
        sampler, children = components[2*idx:2*idx+2]
        parts = urlsplit(target.raw_url)
        # The importer can reinterpret URL parameters and JSON as form arguments.
        # Keep its sampler and managers, restore captured bytes before measuring.
        setprop(sampler, "HTTPSampler.path", (parts.path or "/") + ("?" + parts.query if parts.query else ""))
        setprop(sampler, "HTTPSampler.method", target.method)
        setprop(sampler, "HTTPSampler.contentEncoding", target.encoding)
        for key, value in (("postBodyRaw", str(target.body is not None).lower()),
                           ("follow_redirects","false"), ("auto_redirects","false"),
                           ("connect_timeout","10000"), ("response_timeout","15000")):
            setprop(sampler, "HTTPSampler."+key, value)
        args = sampler.find(".//collectionProp[@name='Arguments.arguments']")
        if args is None:
            args = ET.SubElement(ET.SubElement(sampler, "elementProp", name="HTTPsampler.Arguments", elementType="Arguments"), "collectionProp", name="Arguments.arguments")
        del args[:]
        if target.body is not None:
            item = ET.SubElement(args, "elementProp", name="", elementType="HTTPArgument")
            setprop(item, "HTTPArgument.always_encode", "false")
            setprop(item, "Argument.value", target.body)
            setprop(item, "Argument.metadata", "=")
        check = copy.deepcopy(assertion)
        script = prop(check, "script")
        number = str((account_numbers or {}).get(label, "guest"))
        script.text = f"vars.put('account_no','{number}')\nvars.put('trial_phase','raw')\n" + capture_comparison(target) + script.text
        if label in confirmed_code_zero:
            script.text = script.text.replace("!Boolean.TRUE.equals(success)", "!numericZero")
        if target.follow:
            processor = ET.SubElement(children,"JSR223PostProcessor",guiclass="TestBeanGUI",testclass="JSR223PostProcessor",testname="仅跟随同源跳转")
            setprop(processor,"scriptLanguage","groovy")
            setprop(processor,"script",(SCRIPTS / "redirect.groovy").read_text(encoding="utf8"))
            ET.SubElement(children,"hashTree")
            script.text = "\n".join(line for line in script.text.splitlines() if not line.startswith("vars.put('redirect_codes',"))
        children.extend([check, ET.Element("hashTree")])
        group.extend([sampler, children])
    path.write_bytes(ET.tostring(tree.getroot(),encoding="utf-8",xml_declaration=True).replace(b"\r",b"&#13;"))
