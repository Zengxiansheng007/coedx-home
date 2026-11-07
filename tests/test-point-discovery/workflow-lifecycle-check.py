"""Check observable Markdown preservation and reference validity for #72."""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[2]
sample = root / "tests/test-point-discovery/workflow-lifecycle"
before = (sample / "history-v1.md").read_text(encoding="utf-8")
after = (sample / "current.md").read_text(encoding="utf-8")

def branch(text, heading):
    return text.split("### " + heading + "\n", 1)[1].split("\n#", 1)[0]

# Existing unrelated reviewed business branches survive a payment-eligibility update.
for heading in ("申请提交与审批接收", "成功回写与再次付款"):
    assert branch(before, heading) == branch(after, heading), heading
assert "准确版本v1" in before and "准确版本v2" in after
assert "审批通过且财务复核同意后才获得付款资格" in after
assert "付款金额不得超过该申请批准金额" in after
assert "申请被驳回时不能付款" in after
assert "## M1 采购申请" in after and "## M2 审批接收" in after
assert "## M3" not in after
for unknown in ("Q1", "Q2", "Q3"):
    assert unknown in after
coupon = (sample / "lifecycle-current.md").read_text(encoding="utf-8")
assert "支付确认成功时变为已使用" in coupon
assert "已使用券再次使用被拒绝" in coupon
assert "T1" in coupon and "T2" in coupon
assert "准确版本v1" in coupon and "XMind客户端未验证" in coupon
files = list((root / "skills/test-point-discovery").rglob("*.md"))
files += list(sample.glob("*.md"))
for file in files:
    text = file.read_text(encoding="utf-8")
    assert "\ufffd" not in text, str(file)
    if "skills" in file.parts:
        for target in re.findall(r"\]\(([^)]+)\)", text):
            if not re.match(r"[a-z]+://", target):
                assert (file.parent / target.split("#")[0]).exists(), (file, target)
print("PASS: UTF-8, local references, unrelated branch preservation, payment update timing snapshots, scoped modules, lifecycle unknowns")
