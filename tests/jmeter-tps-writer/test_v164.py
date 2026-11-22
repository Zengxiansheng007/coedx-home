import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".agents/skills/jmeter-tps-writer/scripts"))
from plan import generate
from requests_input import parse_requests


class AccountPlan(unittest.TestCase):
    def test_native_csv_and_guest_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "plan.jmx"
            targets = parse_requests("curl http://localhost/a -b sid=one\ncurl http://localhost/b")
            generate(targets, path)
            tree = ET.parse(path)
            self.assertIsNotNone(tree.find(".//CSVDataSet"))
            self.assertIsNotNone(tree.find(".//IfController"))
            self.assertIn("${cookie}", path.read_text(encoding="utf8"))

    def test_preserves_measured_sampler_and_header_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw = Path(tmp) / "raw.jmx"
            final = Path(tmp) / "plan.jmx"
            targets = parse_requests("curl http://localhost/a?ctoken=fictionalQuery -b sid=fictional -H 'X-Probe: input' -d original")
            generate(targets, raw)
            tree = ET.parse(raw)
            group = tree.find(".//ThreadGroup/../hashTree")
            sampler = group.find("HTTPSamplerProxy")
            configs = list(group)[list(group).index(sampler)+1]
            group[:] = [sampler, configs]
            sampler.find(".//stringProp[@name='Argument.value']").text = "measured body"
            ET.SubElement(sampler, "stringProp", name="sentinel").text = "native"
            for h in configs.findall("HeaderManager/collectionProp/elementProp"):
                if h.find("stringProp[@name='Header.name']").text == "X-Probe":
                    h.find("stringProp[@name='Header.value']").text = "measured header"
            tree.write(raw, encoding="utf-8")
            generate(targets, final, raw_plan=raw)
            text = final.read_text(encoding="utf8")
            for sentinel in ("native", "measured header", "measured body"):
                self.assertIn(sentinel, text)
            for secret in ("sid=fictional", "fictionalQuery"):
                self.assertNotIn(secret, text)

    def test_duplicate_and_missing_pair(self):
        from writer import coverage, check_round
        expected = [("1", "T01"), ("2", "T01")]
        rows = [{"account_no":"1","label":"T01","success":"true","login_hint":"false"}]*2
        self.assertFalse(check_round("已执行", rows, expected))
        self.assertIn("重复", list(coverage(rows, expected))[0])
        self.assertIn("缺失", list(coverage(rows, expected))[1])
