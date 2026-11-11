"""Audit observable file preservation, not natural-language understanding."""
from pathlib import Path
import hashlib
import re

root = Path(__file__).resolve().parents[2]
run = root / 'tests/test-point-discovery/roles-run'
old = (run / 'v1-before-feedback.md').read_bytes()
assert hashlib.sha256(old).hexdigest() == '658bb64e723f2160474cc2386fc56168961ac5cec64187a35b1dae06434e59c5'
before = old.decode('utf-8')
after = (run / 'accurate.md').read_text(encoding='utf-8')
candidate = (run / '08-review-d3.md').read_text(encoding='utf-8')

def branch(text, name):
    return text.split('### ' + name + '\n', 1)[1].split('\n### ', 1)[0].split('\n## ', 1)[0].strip()

assert branch(before, '普通客户') == branch(after, '普通客户')
assert branch(after, '有效VIP') == branch(candidate, '有效VIP')
assert 'v2' in after and 'A-R2' in after and 'A-R3' in after
assert '100元' in branch(after, '普通客户') and '90元' not in branch(after, '普通客户')
assert 'U1' in after and 'U2' in after
files = [root / 'skills/test-point-discovery/SKILL.md',
         root / 'skills/test-point-discovery/references/roles-entitlements.md']
for file in files:
    text = file.read_text(encoding='utf-8', errors='strict')
    for target in re.findall(r'\]\(([^)]+)\)', text):
        if not target.startswith(('http://', 'https://')):
            assert (file.parent / target).exists(), (file, target)
print('PASS: historical v1 identity, ordinary branch preserved, complete VIP candidate adopted, decisions retained, UTF-8 and local references')
print('LIMIT: artifact audit only; semantic review and real client/business results are separate')
