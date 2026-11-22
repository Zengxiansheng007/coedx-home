"""Mirror the published two-title fixture to a loopback receiver with synthetic accounts."""
import csv
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import subprocess
import sys
import tempfile
import threading

from test_pilot import WRITER
from test_v162 import parse_requests

received = []
class Receiver(BaseHTTPRequestHandler):
    def do_POST(self):
        body = self.rfile.read(int(self.headers["Content-Length"]))
        received.append((self.path, self.headers.get("Cookie"), self.headers.get("guc-platform"), body))
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'{"success":true}')

with tempfile.TemporaryDirectory() as tmp, ThreadingHTTPServer(("127.0.0.1", 0), Receiver) as server:
    threading.Thread(target=server.serve_forever, daemon=True).start()
    root = Path(tmp)
    text = Path(__file__).with_name("formatted-cmd.txt").read_text(encoding="utf8")
    endpoint = f"http://127.0.0.1:{server.server_port}"
    text = text.replace("https://portal.example.invalid", endpoint)
    text = text.replace("getServiceWithCategory^", "getServiceWithCategory?a=2&ctoken=fake&a=1^")
    target, = parse_requests(text)
    cookie = target.captured_session
    equivalent = f"curl '{target.raw_url}' -b '{cookie}'"
    assert parse_requests(equivalent)[0].captured_session == cookie
    accounts = root / "accounts.tsv"
    accounts.write_text("cookie\nid=demo1\n" + cookie, encoding="utf8")
    requests = root / "requests.txt"
    requests.write_text(text, encoding="utf8")
    out = root / "run"
    subprocess.run([sys.executable, WRITER, "--requests", requests, "--accounts", accounts,
                    "--pilot-account", "2", "--out", out], check=True)
    assert len(received) == 4
    assert received[0] == ("/govportal/portal/affairs/getServiceWithCategory?a=2&ctoken=fake&a=1",
                           cookie, "pc", target.body.encode("utf8"))
    with (out / "result" / "raw.jtl").open(encoding="utf-8-sig") as stream:
        row, = csv.DictReader(stream)
    assert (row["account_no"], row["label"], row["success"]) == ("2", "T01", "true")
    assert all(title in (out / "targets.md").read_text(encoding="utf8") for title in target.titles)
    print("Verified two titles, one raw POST, captured cookie, query token and account 2; four total samples.")
    server.shutdown()
