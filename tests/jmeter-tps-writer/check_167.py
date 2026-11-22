"""Independently check Writer's three first-pass rounds for the specified T01 query."""
import argparse
import csv
from collections import Counter
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

TITLE = "线上办按主题查询接口"
ALIAS = "根据个法获取当前的一件事"
LABEL = f"{TITLE} [T01]"


def require(ok, description):
    if not ok:
        raise ValueError(description)


def check(out, pilot_account="2"):
    plan = out / "plan.jmx"
    digest = hashlib.sha256(plan.read_bytes()).hexdigest()
    require(digest in (out / "summary.md").read_text(encoding="utf8"), "final JMX digest")
    tree = ET.parse(plan)
    samplers = tree.findall(".//HTTPSamplerProxy")
    require(len(samplers) == 1 and samplers[0].get("testname") == LABEL, "Chinese sampler label")
    require(len(tree.findall(".//CSVDataSet")) == 1, "native CSV component")
    for parent in tree.iter("hashTree"):
        if samplers[0] in list(parent):
            config = list(parent)[list(parent).index(samplers[0]) + 1]
            break
    checks = config.findall("ResponseAssertion")
    require(len(checks) == 3 and all(c.get("enabled") != "false" for c in checks), "three enabled native assertions")
    signatures = [(c.findtext("stringProp[@name='Assertion.test_field']"),
                   c.findtext("stringProp[@name='Scope.variable']"),
                   c.findtext("collectionProp/stringProp")) for c in checks]
    require(signatures == [("Assertion.response_code", None, "2[0-9][0-9]"),
                           ("Assertion.response_data", "success_value", "true"),
                           ("Assertion.response_data", "login_hint", "false")], "assertion rules")
    targets = (out / "targets.md").read_text(encoding="utf8")
    require(any(all(x in line for x in ("T01", TITLE, ALIAS)) for line in targets.splitlines()), "original aliases")
    result = out / "result"
    require(len(list(result.glob("*.jtl"))) == 3, "three independent JTL files")
    for phase, accounts in (("raw", ["2"]), ("pilot", [pilot_account]), ("full", ["1", "2"])):
        with (result / f"{phase}.jtl").open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        require(Counter(r["account_no"] for r in rows) == Counter(accounts), f"{phase} account coverage")
        for row in rows:
            require(row["trial_phase"] == phase and row["label"] == ("T01" if phase == "raw" else LABEL), f"{phase} identity")
            require(200 <= int(row["responseCode"]) < 300 and int(row["elapsed"]) >= 0, f"{phase} HTTP")
            require(row["success"] == row["success_value"] == "true" and row["body_kind"] == "json-object"
                    and row["login_hint"] == "false", f"{phase} business assertions")
            if phase == "raw":
                require(row["capture_diff"] == "matched", "native capture fidelity")
    report = out / "report"
    require((report / "index.html").is_file(), "native report entry")
    stats = json.loads((report / "statistics.json").read_text(encoding="utf8"))
    require(set(stats) == {"Total", LABEL}, "dashboard labels")
    for group in stats.values():
        require(group["sampleCount"] == len(rows) and group["errorCount"] == 0, "dashboard vs final JTL")
    return digest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("out", type=Path)
    print(check(parser.parse_args().out))

