"""Exercise repair of one target without hiding the failed run."""
import csv
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import subprocess
import sys
import tempfile
import threading

WRITER = Path(__file__).resolve().parents[2] / ".agents/skills/jmeter-tps-writer/scripts/writer.py"

class Service(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        if self.path.startswith('/token'):
            cookie = self.headers.get("Cookie","")
            token = cookie.partition("=")[2]
            ok = bool(token) and self.path == '/token?ctoken=' + token
            self.wfile.write(b'{"success":true}' if ok else b'{"message":"missing query ctoken"}')
            return
        self.wfile.write(b'{"code":0}' if self.path == '/contract' else b'{"success":true}')

with tempfile.TemporaryDirectory() as temp, ThreadingHTTPServer(("127.0.0.1", 0), Service) as server:
    threading.Thread(target=server.serve_forever, daemon=True).start()
    root = Path(temp)
    url = f"http://127.0.0.1:{server.server_port}"
    source = root / "input"
    source.write_text(f"One\ncurl {url}/ok\nTwo\ncurl {url}/contract", encoding="utf8")
    def run(name, *args):
        return subprocess.run([sys.executable, WRITER, "--out", root/name, *args]).returncode
    def rows(name, phase):
        with (root/name/"result"/(phase+".jtl")).open(encoding="utf8",newline="") as f:
            return list(csv.DictReader(f))
    assert run("failed", "--requests", source) == 1
    original = (root/"failed/result/raw.jtl").read_bytes()
    assert "数值 0" in (root/"failed/summary.md").read_text(encoding="utf8")
    # This controlled service explicitly confirms numeric zero for /contract.
    assert run("repaired", "--requests", source, "--confirmed-code-zero", "T02", "--diagnose-target", "T02") == 0
    diagnostic = rows("repaired","diagnostic")
    assert len(diagnostic) == 1 and diagnostic[0]["success"] == "true"
    assert not (root/"repaired/report").exists()
    assert run("final","--plan",root/"repaired/plan.jmx") == 0
    assert len(rows("final","full")) == 2
    assert original == (root/"failed/result/raw.jtl").read_bytes()
    source.write_text(f"Token\ncurl '{url}/token?ctoken=blue' -b 'sid=blue'", encoding="utf8")
    accounts = root/"accounts.tsv"
    accounts.write_text("cookie\nsid=blue\nsid=green", encoding="utf8")
    assert run("token-failed","--requests",source,"--accounts",accounts) == 1
    raw = rows("token-failed","raw")[0]
    pilot = rows("token-failed","pilot")[0]
    assert raw["success"] == raw["wire_ctoken"] == "true"
    assert pilot["wire_ctoken"] == "false" and pilot["message_kind"] == "ctoken-required"
    assert "查询令牌" in (root/"token-failed/summary.md").read_text(encoding="utf8")
    tokens = root/"tokens.tsv"
    tokens.write_text("ctoken\nblue\ngreen", encoding="utf8")
    assert run("token-fixed","--requests",source,"--accounts",accounts,"--ctokens",tokens,
               "--ctoken-target","T01","--diagnose-target","T01","--pilot-account","2") == 0
    assert rows("token-fixed", "diagnostic")[0]["account_no"] == "2"
    assert run("token-final","--plan",root/"token-fixed/plan.jmx","--accounts",accounts,
               "--ctokens",tokens) == 0
    assert len(rows("token-final","full")) == 2
    if len(sys.argv) > 1:
        evidence = Path(sys.argv[1])
        for name in ("failed","repaired","final","token-failed","token-fixed","token-final"):
            dest = evidence/name
            dest.mkdir(parents=True, exist_ok=False)
            for file in [root/name/"summary.md", *(root/name/"result").glob("*.jtl")]:
                (dest/file.name).write_bytes(file.read_bytes())
    server.shutdown()
