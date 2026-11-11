"""Check public development artifacts; does not judge natural-language semantics."""
import hashlib
import json
from pathlib import Path
import re

r = Path(__file__).parent / 'xmind-run'
current = (r / 'accurate.md').read_text(encoding='utf-8')
old = (r / 'historical-v3.md').read_text(encoding='utf-8')
receipt = json.loads((r / 'candidate-receipt.json').read_text(encoding='utf-8'))
assert hashlib.sha256((r / 'historical-v3.md').read_bytes()).hexdigest() == receipt['accurate_before_sha256']
assert receipt['accurate_before_sha256'] == receipt['accurate_after_candidate_sha256']
assert hashlib.sha256((r / 'xmind-candidate.md').read_bytes()).hexdigest() == receipt['candidate_sha256']
assert '当前准确版本v4' in current
assert current.split('### 告警数折线图')[1].split('## 资料与Agent交接说明')[0] == old.split('### 告警数折线图')[1].split('## 资料与Agent交接说明')[0]
assert '  - 起止日相同时保留该日范围；首日晚于末日不允许查询。' in current
assert '所选站点及日期范围无数据时显示“暂无数据”。' in current
assert 'P1：告警图刷新周期尚未明确' in current and 'U1：是否纳入导出检查尚未决定' in current
assert '清空档案名输入后恢复全部档案。' in current and '输入不匹配任何档案的名称时，列表显示为空。' in current
assert len([l for l in current.splitlines() if l.startswith('# ')]) == 1
for file in [r / 'accurate.md', r / 'xmind-candidate.md', Path('skills/test-point-discovery/SKILL.md'), Path('skills/test-point-discovery/references/xmind-feedback.md')]:
    text = file.read_text(encoding='utf-8')
    assert '\ufffd' not in text and '<<<<<<<' not in text
    for target in re.findall(r'\]\(([^)]+)\)', text):
        if '://' not in target:
            resolved = (file.parent / target).resolve()
            if target.startswith('../../../../../evidence/'):
                # Frozen D5 links were displayed from its original worktree.
                # After integration, retain the displayed bytes and locate the
                # separately governed development evidence at its owning root.
                owner = next(p for p in Path(__file__).resolve().parents if (p / 'context/issues/75.md').exists())
                resolved = owner / 'evidence' / target.split('/evidence/', 1)[1]
            assert resolved.exists(), (file, target)
print('PASS: v3 held before review; same MD v4; full alarm/archive retained; native text/hierarchy; local references and UTF8')
