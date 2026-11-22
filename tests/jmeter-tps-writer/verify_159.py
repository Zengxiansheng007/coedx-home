"""The synthetic endpoint's documented contract defines numeric code 0 as success."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
from test_pilot import WRITER


class Service(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"code":0}')


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as folder, ThreadingHTTPServer(("127.0.0.1", 0), Service) as service:
        threading.Thread(target=service.serve_forever, daemon=True).start()
        root = Path(folder)
        (root/"input").write_text(f"curl http://127.0.0.1:{service.server_port}/status")
        (root/"accounts").write_text("cookie\nsid=fictitious")
        for name, options in [("before", []), ("after", ["--confirmed-code-zero", "T01"])]:
            out = root/name
            run = subprocess.run([sys.executable, WRITER, "--requests", root/"input", "--accounts",
                                  root/"accounts", "--out", out, *options])
            report = (out/"summary.md").read_text(encoding="utf8")
            assert run.returncode == (1 if name == "before" else 0)
            assert (out/"result"/"raw.jtl").is_file()
            if name == "before":
                assert "数值 0" in report and "是否" in report, report
            if len(sys.argv) > 1:
                dest = Path(sys.argv[1])/name
                dest.mkdir(parents=True, exist_ok=True)
                evidence = sorted((out/"result").glob("*.jtl"))
                expected = {"raw.jtl"} if name == "before" else {"raw.jtl", "full.jtl"}
                assert {file.name for file in evidence} == expected
                for file in [out/"summary.md", *evidence]:
                    (dest/file.name).write_bytes(file.read_bytes())
                assert not list(dest.glob("*.log"))
        service.shutdown()
