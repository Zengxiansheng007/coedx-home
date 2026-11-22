"""Run pure guest through the Writer, edit the path in JMeter Swing and replay."""
import csv
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
from test_pilot import WRITER

class Receiver(BaseHTTPRequestHandler):
    def do_GET(self):
        self.server.received.append((self.path, self.headers.get('Cookie')))
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'{"success":true}')

with tempfile.TemporaryDirectory() as tmp, ThreadingHTTPServer(('127.0.0.1', 0), Receiver) as server:
    root = Path(tmp)
    server.received = []
    threading.Thread(target=server.serve_forever, daemon=True).start()
    source = root / 'input'
    source.write_text(f"查询指南\ncurl 'http://127.0.0.1:{server.server_port}/guide?page=1'", encoding='utf8')
    out = root / 'trial'
    subprocess.run([sys.executable, WRITER, '--requests', source, '--out', out], check=True)
    assert sorted(f.name for f in (out/'result').glob('*.jtl')) == ['full.jtl', 'raw.jtl']
    with (out/'result/full.jtl').open(encoding='utf-8-sig') as f:
        row, = csv.DictReader(f)
    assert (row['account_no'], row['success'], row['label']) == ('guest','true','查询指南 [T01]')
    home = Path(shutil.which('jmeter.bat')).parents[1]
    cp = os.pathsep.join(str(home / d / '*') for d in ('bin','lib','lib/ext'))
    edited = root/'edited.jmx'
    subprocess.run(['java','-Dfile.encoding=UTF-8','-cp',cp,'groovy.ui.GroovyMain',
                    Path(__file__).with_name('edit_163.groovy'),home,out/'plan.jmx',edited], cwd=root, check=True)
    subprocess.run([sys.executable, WRITER,'--plan',edited,'--out',root/'edited'], check=True)
    assert server.received == [('/guide?page=1',None),('/guide?page=1',None),('/guide?page=2',None)]
    print('Guest 1/0/1, saved Swing edit replayed successfully.')
    server.shutdown()
