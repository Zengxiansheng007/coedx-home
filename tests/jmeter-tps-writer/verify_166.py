"""Run a delivered JMX twice and rebuild its native dashboard without network traffic."""
import csv
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading

from test_pilot import WRITER
sys.path.insert(0, str(WRITER.parent))
from engine import launcher_args
from plan import generate
from requests_input import parse_requests


def verify(use_desktop=False):
    hits = []
    class Query(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            hits.append(self.headers.get("Cookie"))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"success":true}')

    with tempfile.TemporaryDirectory() as temp, ThreadingHTTPServer(("127.0.0.1", 0), Query) as server:
        threading.Thread(target=server.serve_forever, daemon=True).start()
        root = Path(temp)
        source = root / "source.jmx"
        generate(parse_requests(f"curl http://127.0.0.1:{server.server_port}/query -b sid=captured"), source)
        for i in range(2):
            out = (root if i == 0 else root / "new" / "deeper") / str(i)
            accounts = root / f"accounts-{i}.tsv"
            cookie = f"sid=synthetic-round-{i}"
            accounts.write_text("cookie\n" + cookie + "\n", encoding="utf8")
            destination = [] if use_desktop and i == 0 else ["--out", out]
            run = subprocess.run([sys.executable, "-X", "utf8", WRITER, "--plan", source,
                                  "--accounts", accounts, *destination], capture_output=True, encoding="utf8")
            assert run.returncode == 0, run.stderr
            out = Path(run.stdout.strip().splitlines()[-1])
            print(f"Validated artifacts: {out}", flush=True)
            assert (out/"plan.jmx").read_bytes() == source.read_bytes()
            assert hits[-2:] == [cookie, cookie]
            assert len(list((out/"result").glob("*.jtl"))) == 2
            final = next((out/"result").glob("full*.jtl"))
            with final.open(encoding="utf8", newline="") as f:
                rows = list(csv.DictReader(f))
            assert len(rows) == 1 and rows[0]["success"] == "true"
            rebuild = out / "rebuilt"
            subprocess.run([sys.executable, WRITER, "--rebuild-report", final, "--out", rebuild], check=True)
            for report in [out/"report", rebuild]:
                assert (report/"index.html").is_file()
                stats = json.loads((report/"statistics.json").read_text(encoding="utf8"))
                assert stats["Total"]["sampleCount"] == stats[rows[0]["label"]]["sampleCount"] == 1
                assert stats["Total"]["errorCount"] == 0
            assert len(hits) == 3 * i + 2
            for path in out.rglob("*"):
                if path.is_file():
                    assert cookie.encode() not in path.read_bytes()
            source = out / "plan.jmx"
            # Open the same plan without Writer's CLI account overrides.
            gui_result = root / f"default-{i}.jtl"
            subprocess.run(launcher_args("jmeter.bat") + ["-n", "-t", str(source), "-l", str(gui_result),
                           "-j", str(root / "default.log"), "-Jsample_variables=account_no"], cwd=root, check=True)
            with gui_result.open(encoding="utf8", newline="") as handle:
                sample, = csv.DictReader(handle)
            assert sample["account_no"] == "1" and sample["success"] == "true"
            assert hits[-1] == cookie
        server.shutdown()


if __name__ == "__main__":
    verify(use_desktop="--desktop" in sys.argv)

