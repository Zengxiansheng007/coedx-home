"""Execute all response variants in one loopback JMeter round."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import tempfile
import threading

from test_v162 import parse_requests
from plan import generate
from engine import run_round

cases = [
    (200, {"success": True}, True), (200, {"success": False}, False),
    (200, {"success": "true"}, False), (200, [True], False),
    (200, {"code": 0}, False), (200, '<html>请重新登录</html>', False),
    (403, {"success": True}, False), (200, {"success": True, "msg": "登入失效"}, False),
]
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        status, data, _ = cases[int(self.path[1:])]
        self.send_response(status, "private-transport-message")
        self.end_headers()
        self.wfile.write((data if isinstance(data, str) else json.dumps(data)).encode())

with tempfile.TemporaryDirectory() as tmp, ThreadingHTTPServer(('127.0.0.1', 0), Handler) as server:
    threading.Thread(target=server.serve_forever, daemon=True).start()
    out = Path(tmp)
    plan = out / 'plan.jmx'
    targets = [parse_requests(f"样例{i}\ncurl http://127.0.0.1:{server.server_port}/{i}")[0] for i in range(len(cases))]
    generate(targets, plan)
    status, rows = run_round(plan, None, out, 'full', 1, 1, 'jmeter.bat')
    assert status == '已执行' and len(rows) == len(cases), (status,len(rows))
    assert [r['success'] == 'true' for r in rows] == [c[2] for c in cases], rows
    assert rows[-1]['login_hint'] == 'true'
    assert 'private-transport-message' not in (out/'result/full.jtl').read_text(encoding='utf8')
    print('Eight JSON, HTTP and login variants verified with real JMeter.')
    server.shutdown()
