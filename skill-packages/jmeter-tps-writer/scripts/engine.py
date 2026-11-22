import csv
import ctypes
import tempfile
import uuid
import os
from pathlib import Path
import shutil
import subprocess


VARIABLES = "capture_diff,wire_method,wire_ctoken,wire_cookie,account_no,trial_phase,body_kind,success_value,login_hint,known_fields,service_code,message_kind,code_kind,redirect_codes,timeout_state"


def desktop_root():
    # CSIDL_DESKTOPDIRECTORY follows Windows Known Folder redirection.
    folder = ctypes.create_unicode_buffer(32768)
    if os.name != "nt" or ctypes.windll.shell32.SHGetFolderPathW(None, 16, None, 0, folder):
        raise ValueError("无法定位 Windows 桌面，请指定 --out。")
    return Path(folder.value) / "jmeter"


def prepare_output(root):
    root = (root or desktop_root()).resolve()
    root.mkdir(parents=True, exist_ok=True)
    # Reserve the destination even when several writers start together.
    while True:
        try:
            (root / "result").mkdir()
            if any(p.name != "result" for p in root.iterdir()):
                (root / "result").rmdir()
            else:
                return root
        except FileExistsError:
            pass
        root = Path(tempfile.mkdtemp(prefix="run-", dir=root))


def resolve_java():
    home = os.environ.get("JAVA_HOME")
    if home:
        binary = Path(home) / "bin" / ("java.exe" if os.name == "nt" else "java")
        if binary.is_file():
            return str(binary)
    return shutil.which("java")


def launcher_args(jmeter):
    launcher = shutil.which(str(jmeter))
    if not launcher:
        return []
    jar = Path(launcher).resolve().parent / "ApacheJMeter.jar"
    java = resolve_java()
    return [java, "-Dfile.encoding=UTF-8", "-jar", str(jar)] if jar.is_file() and java else []


def rebuild_report(jtl, report, jmeter):
    launcher = launcher_args(jmeter)
    if not launcher or not jtl.is_file() or (report.exists() and any(report.iterdir())):
        raise ValueError("需要 JMeter、最终 JTL 和新的或空的报告目录。")
    report.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        result = subprocess.run(launcher + ["-g", str(jtl.resolve()), "-o", str(report.resolve()),
                                "-j", str(Path(tmp) / "dashboard.log")], cwd=tmp)
    return result.returncode == 0 and (report / "index.html").is_file()


def run_round(plan, accounts, out, phase, first, threads, jmeter, ctokens=None):
    launcher = launcher_args(jmeter)
    if not launcher:
        return "未执行：缺少 JMeter 或 Java", []
    results = out / "result"
    results.mkdir(exist_ok=True)
    result = results / (phase + ".jtl")
    if result.exists():
        result = results / (phase + "-" + uuid.uuid4().hex + ".jtl")
    report = out / "report"
    command = launcher + ["-n", "-t", str(plan.resolve()), "-l", str(result.resolve()),
               "-j", str(result.with_suffix(".private.log").resolve()),
               f"-Jaccount.first={first}", f"-Jthreads={threads}",
               "-Jtrial.phase=" + phase, "-Jsample_variables=" + VARIABLES, "-Jhttpclient4.retrycount=0",
               "-Jjmeterengine.nongui.port=0", "-Jjmeter.save.saveservice.output_format=csv",
               "-Jjmeter.save.saveservice.print_field_names=true", "-Jjmeter.save.saveservice.url=false",
               "-Jjmeter.save.saveservice.response_message=true",
               "-Jjmeter.save.saveservice.assertion_results_failure_message=true"]
    selected = None
    if accounts:
        source = accounts.resolve()
        command.append("-Jaccounts.source=" + str(source))
        if phase in ("pilot", "diagnostic") and b"<CSVDataSet " in plan.read_bytes():
            selected = tempfile.TemporaryDirectory()
            source = Path(selected.name) / "pilot.tsv"
            rows = accounts.read_text(encoding="utf-8-sig").splitlines()
            source.write_text("cookie\n" + rows[first] + "\n", encoding="utf8")
        command.append("-Jaccounts.file=" + str(source))
    if phase == "full":
        if report.exists() and any(report.iterdir()):
            return "未执行：报告目录已有内容", []
        command.extend(["-e", "-o", str(report.resolve())])
    for key in ("response_data", "response_data.on_error", "samplerData", "requestHeaders",
                "responseHeaders", "filename", "hostname", "subresults"):
        command.append("-Jjmeter.save.saveservice." + key + "=false")
    for key in ("time", "label", "response_code", "successful", "timestamp", "thread_name",
                "bytes", "sent_bytes", "thread_counts", "latency", "connect_time"):
        command.append("-Jjmeter.save.saveservice." + key + "=true")
    command.append("-Jjmeter.save.saveservice.timestamp_format=ms")
    command.append("-Jjmeter.save.saveservice.default_delimiter=,")
    command.append("-Jsampleresult.timestamp.start=true")
    if ctokens:
        command.append("-Jctokens.file=" + str(ctokens.resolve()))
    try:
        run = subprocess.run(command, cwd=out, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        completed = run.returncode == 0 and (phase != "full" or (report / "index.html").is_file())
    except KeyboardInterrupt:
        completed = False
    finally:
        if selected:
            selected.cleanup()
    rows = []
    if result.exists():
        with result.open(encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
    return ("已执行" if completed and rows else "运行中断"), rows
