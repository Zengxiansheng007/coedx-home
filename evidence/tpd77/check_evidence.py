"""Check evidence identities and matrix completeness only; not business semantics."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import argparse

from bind_sources import ADMIN, R1_COMMIT, task_root

root = Path(__file__).resolve().parents[2]
dev = task_root(root)
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--write-result', type=Path, help='Optional NEW result path; default is read-only.')
args = parser.parse_args()
binding = json.loads((root / 'evidence/tpd77/source-bindings-r2.json').read_text(encoding='utf-8'))
errors = []
r1_raw = subprocess.check_output(['git', '-C', str(root), 'show',
                                  R1_COMMIT + ':evidence/tpd77/source-bindings.json'])
r1 = json.loads(r1_raw)
immutable = [r for r in r1['evidence'] if (r['area'], r['path']) != ADMIN]
admin = [r for r in r1['evidence'] if (r['area'], r['path']) == ADMIN]
if ((root / 'evidence/tpd77/source-bindings.json').read_bytes() != r1_raw
        or binding.get('revision') != 'R2'
        or binding['evidence'] != immutable or len(immutable) != 287
        or binding.get('administrative_capture', {}).get('record') != admin[0]
        or binding.get('r1_capture', {}).get('sha256') != hashlib.sha256(r1_raw).hexdigest()
        or binding['requirements'] != r1['requirements']):
    errors.append('R2 must preserve all frozen R1 immutable identities and historical administrative capture')
for record in binding['evidence']:
    base = root if record['area'] == 'repo' else dev
    p = base / record['path']
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != record['sha256']:
        errors.append('Evidence bytes changed or missing: ' + record['path'])
expected = ['af4179ac42809c4006a52a781477d758543d44bc02291ff253b4b1333f910fb3',
            'ca149fe3f56727c833a0f617e620c4b933bb7cb197d5e66f20eadacebb8ff5a8',
            'f9b9277ca6fff7c9a4e449a8cf4b3aef50a7887b32af983f072c50c11dd5ede2']
if [r['sha256'] for r in binding['requirements'][:3]] != expected:
    errors.append('Approved requirements baseline changed')
matrix = (root / 'evidence/tpd77/ac-matrix.md').read_text(encoding='utf-8')
ids = re.findall(r'^\|TPD-AC-(\d{3})\|', matrix, re.M)
if ids != [f'{i:03}' for i in range(1,25)]:
    errors.append('AC coverage rows missing/duplicate/out of order')
stories = (root / 'evidence/tpd77/story-matrix.md').read_text(encoding='utf-8')
if re.findall(r'^\|(\d+)\|', stories, re.M) != [str(i) for i in range(1,53)]:
    errors.append('Story rows missing/duplicate/out of order')
draft = (root / 'evidence/tpd77/serial-run/review-d2.md').read_text(encoding='utf-8')
accurate = (root / 'evidence/tpd77/serial-run/current.md').read_text(encoding='utf-8')
def checks(text):
    return text.split('## 购买\n',1)[1].split('### 【待产品确认】',1)[1].split('## 资料与Agent交接说明',1)[0]
if checks(draft) != checks(accurate):
    errors.append('Reviewed product questions/checks changed during handoff')
if hashlib.sha256((root / 'evidence/tpd77/serial-run/current.md').read_bytes()).hexdigest() != 'dffc3f652b70dff3c8229a11bbb1fa4b0d01b1f6f4750fce0f333cea686b3e7d':
    errors.append('Receiver input changed')
subprocess.run(['git', '-C', str(root), 'diff', '--check'], check=True)
result = {'status': 'pass' if not errors else 'fail', 'evidence_files':len(binding['evidence']),
          'revision': 'R2', 'historical_administrative_captures_excluded': 1,
          'ac_rows':len(ids), 'story_rows':52, 'errors':errors,
          'scope':'identity, coverage index and approved-content preservation only; semantic conclusions require actual outputs and review'}
if args.write_result:
    with args.write_result.open('xb') as output:
        output.write((json.dumps(result, ensure_ascii=False, indent=2)+'\n').encode('utf-8'))
print(json.dumps(result, ensure_ascii=False))
raise SystemExit(bool(errors))
