"""Verify following same-origin redirects and stopping at an origin boundary."""
import csv
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
from test_pilot import WRITER


def verify():
    hits = []

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            hits.append((self.server.server_port, self.path))
            if self.path == "/final":
                assert self.headers.get("Cookie") == "sid=fictional"
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'{"success":true}')
                return
            self.send_response(302)
            location = "/final" if self.path == "/same" else f"http://127.0.0.1:{other.server_port}/final"
            self.send_header("Location", location)
            self.end_headers()

    with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as source, ThreadingHTTPServer(("127.0.0.1", 0), Handler) as other, tempfile.TemporaryDirectory() as folder:
        for server in (source, other):
            threading.Thread(target=server.serve_forever, daemon=True).start()
        root = Path(folder)
        account = root / "accounts"
        account.write_text("cookie\nsid=fictional")
        inputs = root / "requests"
        inputs.write_text("\n".join(f"curl -b sid=fictional -L http://127.0.0.1:{source.server_port}/{path}" for path in ("same", "cross")))
        out = root / "outputs"
        result = subprocess.run([sys.executable, WRITER, "--requests", inputs, "--accounts", account, "--out", out])
        assert result.returncode == 1
        with (out / "result" / "raw.jtl").open(encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
        assert [(r["responseCode"], r["redirect_codes"]) for r in rows] == [("200", "302"), ("REDIRECT_BLOCKED", "302")], rows
        assert hits == [(source.server_port, path) for path in ("/same", "/final", "/cross")], hits
        inputs.write_text(f"curl -b sid=fictional -L http://127.0.0.1:{source.server_port}/same")
        good = root / "good"
        subprocess.run([sys.executable, WRITER, "--requests", inputs, "--accounts", account, "--out", good], check=True)
        assert hits[3:] == [(source.server_port, path) for path in ("/same", "/final") * 3]
        for flag in ("follow_redirects", "auto_redirects"):
            plan = root / (flag + ".jmx")
            xml = (good / "plan.jmx").read_text(encoding="utf8")
            plan.write_text(xml.replace(f'HTTPSampler.{flag}">false', f'HTTPSampler.{flag}">true'), encoding="utf8")
            replay = root / flag
            result = subprocess.run([sys.executable, WRITER, "--plan", plan, "--accounts", account, "--out", replay])
            assert result.returncode == 2 and "cURL" in (replay / "summary.md").read_text(encoding="utf8")
        inputs.write_text(f"curl -L -X POST http://127.0.0.1:{source.server_port}/same")
        result = subprocess.run([sys.executable, WRITER, "--requests", inputs, "--accounts", account, "--out", root / "explicit"])
        assert result.returncode == 2 and len(hits) == 9
        print("same-origin followed once; cross-origin destination received zero requests")
        for server in (source, other):
            server.shutdown()


if __name__ == "__main__":
    verify()
