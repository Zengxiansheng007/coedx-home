"""Audit received file identity and preservation; not prose understanding."""
from pathlib import Path
import hashlib
import re

root = Path(__file__).resolve().parents[2]
run = root / 'evidence/tpd76'
current = (run / 'current.md').read_bytes()
old = (run / 'current-v3-historical.md').read_bytes()
assert hashlib.sha256(current).hexdigest() == '5d1fb706ebf471354b5cf15da8662628015b618bc56a878ee28c00dfe0f1cf9b'
assert hashlib.sha256(old).hexdigest() == '4bd9803db0b97fb304c80d9492ac47f799703edc6eb6b7fb6092f27660c85705'
now, before = current.decode('utf-8'), old.decode('utf-8')

def evaluated_content(text):
    # Human range status is metadata; all product questions/checks must survive.
    body = text.split('## 资料与Agent交接说明', 1)[0]
    return re.sub(r'### 【待确认】\n.*?(?=### 【待产品确认】)', '', body, flags=re.S)

assert evaluated_content(now) == evaluated_content(before)
draft = (run / 'review-draft.md').read_text(encoding='utf-8')
assert evaluated_content(now).split('\n', 1)[1] == evaluated_content(draft).split('\n', 1)[1]
assert now.split('### 来源与分支对应', 1)[1] == before.split('### 来源与分支对应', 1)[1]
assert now.count('### 【待确认】\n- 无新增待确认事项。') == 2
assert len(re.findall(r'^# ', now, re.M)) == 1
files = [root / 'skills/test-point-discovery/SKILL.md',
         root / 'skills/test-point-discovery/references/single-file-handoff.md',
         root / 'skills/test-point-discovery/references/review-and-progress.md',
         run / 'current.md', run / 'review-draft.md']
for file in files:
    text = file.read_text(encoding='utf-8', errors='strict')
    assert '\ufffd' not in text and '<<<<<<<' not in text
    for target in re.findall(r'\]\(([^)]+)\)', text):
        if '://' not in target:
            assert (file.parent / target).is_file(), (file, target)
print('PASS: received v3/v4 byte identities; D1 checks/questions preserved; decisions/mappings unchanged; closed human range status; UTF8/local references')
print('LIMIT: does not prove business semantics, historic message authenticity, P0 or client compatibility; independent receiver reports are separate')
