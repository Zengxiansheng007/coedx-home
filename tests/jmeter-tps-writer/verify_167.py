"""Replay the spec fixture through Writer on loopback and inspect the four wire requests."""
from contextlib import ExitStack, nullcontext
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse
import subprocess
import sys
import tempfile
import threading

from check_167 import check

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = Path(__file__).with_name("formatted-cmd.txt")
WRITER = ROOT / ".agents/skills/jmeter-tps-writer/scripts/writer.py"


def verify(fixture, output, writer=WRITER, gui_pilot=False):
    events = []

    class Receiver(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            events.append((self.headers.get("Cookie"), self.path, self.headers.get("guc-accountType"),
                           self.rfile.read(int(self.headers["Content-Length"]))))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"success":true}')

    if output:
        output.mkdir(parents=True, exist_ok=False)
    temp = nullcontext(output) if output else tempfile.TemporaryDirectory()
    with temp as tmp, ThreadingHTTPServer(("127.0.0.1", 0), Receiver) as server, ExitStack() as cleanup:
        threading.Thread(target=server.serve_forever, daemon=True).start()
        cleanup.callback(server.shutdown)
        root = Path(tmp)
        local = f"http://127.0.0.1:{server.server_port}"
        source = fixture.read_text(encoding="utf8").replace("https://portal.example.invalid", local)
        source = source.replace(r"https\://portal.example\.invalid", local)
        assert "portal.example" not in source
        request = root / "request.txt"
        request.write_text(source, encoding="utf8")
        second = "ssoOnlineUserInfo=EXAMPLE_ONLY_INFO_2; C_sc_gsid=EXAMPLE_ONLY_SESSION_2; C_sc_platform=pc; C_sc_accountType=person"
        first = second.replace("_2", "_1")
        accounts = root / "accounts.tsv"
        accounts.write_text(f"cookie\n{first}\n{second}\n", encoding="utf8")
        out = root / "out"
        mode = ["--accounts-stdin", "--gui-pilot"] if gui_pilot else ["--accounts", accounts, "--pilot-account", "2"]
        subprocess.run([sys.executable, "-X", "utf8", writer, "--requests", request, "--out", out, *mode],
                       input=accounts.read_bytes() if gui_pilot else None, check=True)
        assert [e[0] for e in events[:2]] == [second, first if gui_pilot else second]
        assert sorted(e[0] for e in events[2:]) == sorted([first, second])
        assert all(e[1:] == ("/govportal/portal/affairs/getServiceWithCategory", "person",
                   b'{"personType":"1","searchChannel":"PC","siteId":"510000","tabOption":"THEME"}') for e in events)
        print(check(out, "1" if gui_pilot else "2"))



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=FIXTURE)
    parser.add_argument("--output", type=Path, help="retain synthetic artifacts in a new directory")
    parser.add_argument("--writer", type=Path, default=WRITER)
    parser.add_argument("--gui-pilot", action="store_true")
    args = parser.parse_args()
    verify(args.fixture, args.output, args.writer, args.gui_pilot)



