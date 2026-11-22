"""Controlled receiver verification of native CSV, mixed rounds, barrier and failures."""
import csv
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time

from test_pilot import WRITER
sys.path.insert(0, str(WRITER.parent))
from engine import run_round

class Receiver(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        cookie = self.headers.get("Cookie")
        path = self.path
        events.append((path, cookie, time.monotonic()))
        ok = True
        if path.startswith("/a") and cookie == cookies[0]:
            time.sleep(0.4)
            ok = not faults
        if faults and path == "/a" and cookie == cookies[2]:
            time.sleep(17)
        if path.startswith("/token"):
            ok = ("ctoken=" + cookie[-1]) in path
        self.send_response(200)
        self.end_headers()
        try:
            self.wfile.write(json.dumps({"success":ok, "msg": "" if ok else "ctoken required"}).encode())
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            pass  # Client-side timeout intentionally finishes before the server.

def rows(out, phase):
    with (out/"result"/(phase+".jtl")).open(encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))

def run(name, paths, n, success, *extra):
    out = root/name
    source = root/(name+".txt")
    source.write_text("\n".join(f"接口{i}\ncurl 'http://127.0.0.1:{server.server_port}{path}'" +
                                (" -b '"+cookies[1]+"'" if path != "/guest" else "")
                                for i,path in enumerate(paths)), encoding="utf8")
    accounts.write_text("cookie\n"+"\n".join(cookies[:n]),encoding="utf8")
    proc = subprocess.run([sys.executable, WRITER, "--requests", source, "--accounts", accounts,
                           "--pilot-account", "2", "--out", out, *extra])
    print(out, proc.returncode, flush=True)
    assert proc.returncode == (0 if success else 1), (out/"summary.md").read_text(encoding="utf8")
    return out

with ThreadingHTTPServer(("127.0.0.1",0), Receiver) as server:
    root = Path(tempfile.mkdtemp(prefix="writer164-"))
    print(root, flush=True)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    cookies = ["sid=fictional; ctoken="+str(i) for i in range(1,4)]
    accounts = root/"sessions.tsv"
    events = []
    faults = False
    mixed = run("mixed", ["/a?x=%2F&ctoken=2&x=1","/guest"],2,True)
    assert [len(rows(mixed,p)) for p in ("raw","pilot","full")] == [2,1,3]
    assert events[0][:2] == ("/a?x=%2F&ctoken=2&x=1",cookies[1])
    assert events[2][:2] == ("/a?x=%2F&x=1",cookies[1])
    assert sorted(c for path,c,t in events[-3:] if path != "/guest") == sorted(cookies[:2])
    assert all(c is None for path,c,t in events if path == "/guest")
    mixed_rows = rows(mixed, "full")
    assert sorted(r["account_no"] for r in mixed_rows[:2]) == ["1", "2"]
    assert mixed_rows[2]["account_no"] == "guest"
    # No accounts.file override: exercise GUI-default path reference with one thread.
    gui = root/"relative"
    gui.mkdir()
    status, data = run_round(mixed/"plan.jmx", None, gui, "manual", 1, 1, "jmeter.bat")
    assert status == "已执行" and [r["account_no"] for r in data] == ["1","guest"]
    assert events[-2][1] == cookies[0]
    faults = True
    barrier = run("barrier",["/a","/b"],3,False)
    assert [len(rows(barrier,p)) for p in ("raw","pilot","full")] == [2,2,6]
    full = rows(barrier,"full")
    assert sum(r["success"]=="false" for r in full)==2
    assert sum(r["timeout_state"]=="server-outcome-unknown" for r in full)==1
    end = max(int(r["timeStamp"])+int(r["elapsed"]) for r in full if r["label"].endswith("[T01]"))
    assert min(int(r["timeStamp"]) for r in full if r["label"].endswith("[T02]")) >= end
    failed = run("token",["/token?ctoken=2"],2,False)
    assert not (failed/"result/full.jtl").exists()
    tokens = root/"tokens.tsv"
    tokens.write_text("ctoken\n1\n2",encoding="utf8")
    repaired = run("token-repaired",["/token?ctoken=2"],2,True,"--ctokens",tokens,"--ctoken-target","T01")
    assert len(rows(repaired,"full")) == 2
    server.shutdown()
