from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]/".agents/skills/jmeter-tps-writer/scripts"))
from writer import coverage, check_round

expected = [("1","T01"),("2","T01")]
rows = [dict(account_no="1",label="T01",success="true",login_hint="false")]*2
report = "\n".join(coverage(rows,expected))
assert "重复" in report and "缺失" in report
assert not check_round("已执行",rows,expected)
