from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import threading
from test_pilot import WRITER

received = []
class Receiver(BaseHTTPRequestHandler):
    def do_POST(self):
        received.append([self.path, self.headers["X-Test"], self.rfile.read(int(self.headers["Content-Length"])).decode()])
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'{"success":true}')

with tempfile.TemporaryDirectory() as tmp, ThreadingHTTPServer(("127.0.0.1", 0), Receiver) as server:
    threading.Thread(target=server.serve_forever, daemon=True).start()
    p = Path(tmp)
    url = f"http://127.0.0.1:{server.server_port}/api?a=2&a=1"
    payload = '{"值":"中文"}'
    bash = f"curl '{url}' -H 'X-Test: wire' -H 'Content-Type: application/json' --data-raw '{payload}'"
    cmd = f'curl.exe ^"{url}^" ^\n -H ^"X-Test: wire^" -H ^"Content-Type: application/json^" --data-raw ^"{{^\\"值^\\":^\\"中文^\\"}}^"'
    batch = f"# 标题甲\n{bash}\n# 标题乙\n{cmd}\n| 标题 | cURL |\n|---|---|\n| 表单 | curl '{url}' -H 'X-Test: form' -d 'a=%E4%B8%AD&a=2' |\n# 文本\ncurl '{url}' -H 'X-Test: text' -H 'Content-Type: text/plain' -d $'原文\\r\\n第二行'"
    (p/"accounts").write_text("cookie\nsid=fictional")
    def run(data, name):
        (p/"requests").write_text(data, encoding="utf8")
        return subprocess.run([sys.executable, WRITER, "--requests", p/"requests", "--accounts", p/"accounts", "--out", p/name]).returncode
    assert run(batch + "\n[疑问](https://example.invalid/)\n# 上传\ncurl -F @file https://example.invalid", "blocked") != 0
    report = (p/"blocked/summary.md").read_text(encoding="utf8")
    assert not received and all(x in report for x in ["标题甲","标题乙","疑问","上传"])
    assert run(batch, "ready") == 0
    expected = [["/api?a=2&a=1","wire",payload],["/api?a=2&a=1","form","a=%E4%B8%AD&a=2"],["/api?a=2&a=1","text","原文\r\n第二行"]]
    assert received == expected * 3, received
    server.shutdown()
    result = json.dumps(dict(preflight_requests=0, raw=received[:3], pilot=received[3:6], full=received[6:], titles=["标题甲","标题乙"]),ensure_ascii=False)
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(result + "\n", encoding="utf8")
    print(result)
