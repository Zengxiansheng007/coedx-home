"""Check public demonstration artifacts; business semantics require the review rubric."""
from pathlib import Path
import re

root = Path(__file__).resolve().parent
run = root / 'feedback-run'
before = (run / 'history-v2.md').read_text(encoding='utf-8')
after = (run / 'accurate.md').read_text(encoding='utf-8')

def branch(text, title, next_title):
    return text.split(title, 1)[1].split(next_title, 1)[0]

assert before == (root / 'progress-run/accurate.md').read_text(encoding='utf-8'), 'historical input changed'
assert branch(before, '## M2趋势与指标卡', '## 资料与Agent交接说明') == branch(after, '## M2趋势与指标卡', '## 资料与Agent交接说明'), 'omitted module lost or modified'
assert '当前准确版本v4' in after
m1 = branch(after, '## M1渠道分布', '## M2趋势与指标卡')
assert '- Q6：' not in m1 and '- Q8：' in m1
assert '接收的渠道与M1点击渠道一致' in m1
assert '此次跳转携带用户所选平台' in m1 and '接收的平台与M1所选平台一致' in m1
assert '实际应用仍待Q5' in m1 and '时区/边界待Q2' in m1
history = before.split('### 版本与实际决定', 1)[1].split('### 来源与覆盖去向', 1)[0]
assert history in after, 'old review decisions rewritten'
for filename in ('chat-d1.md', 'md-d2.md'):
    doc = (run / filename).read_text(encoding='utf-8')
    assert '### 渠道分布柱图：跳转' in doc and '### 访问明细：接收与日期显示' in doc
    assert doc.count('\n# ') == 0 and doc.startswith('# ')

skill = root.parents[1] / 'skills/test-point-discovery'
for path in [skill / 'SKILL.md', *skill.joinpath('references').glob('*.md')]:
    for target in re.findall(r'\]\(([^)#]+)(?:#[^)]*)?\)', path.read_text(encoding='utf-8')):
        if '://' not in target:
            assert (path.parent / target).is_file(), (path, target)
print('PASS: historical input/decisions, unaffected module, reviewed output, unresolved rules, complete branches and local references')
