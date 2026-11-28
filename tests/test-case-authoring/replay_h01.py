"""Replay controlled H01 receipts on the original 194-case candidate, without device I/O."""
import argparse
import json
import sys
from hashlib import sha256
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".agents/skills/test-case-authoring/scripts"))
from run_evidence import check_received_field, summarize_case


def replay(batch, case_id, variant, expected_status):
    case = next(case for case in batch["cases"] if case["id"] == case_id)
    request_id = case["steps"][0]["data_refs"][0]
    request = next(item["value"]["arg0"] for item in batch["data"] if item["id"] == request_id)
    run_id = "controlled-" + variant
    correlation = case_id + "-" + run_id
    is_header = case_id == "HM-UP-141"
    collection = "headers" if is_header else "form"
    field = "X-Test-Case" if is_header else "traceCase"
    expected_value = request["header" if is_header else "params"][field]
    assert expected_value == "H01" and request["fileKey"] == "imgsfile"
    assert ("case=" + case_id + "-${RUN_ID}") in request["url"]
    steps = case["steps"]
    assert len(steps) == 6 and field in steps[-1]["expected"][0]["text"]
    assert ("HTTP 请求头" if is_header else "独立表单字段") in steps[-1]["operation"]

    source_file = b"controlled sample"
    record = {"source_ref": "controlled/receiver/" + correlation, "correlation": correlation,
              "headers": {"x-test-case": "H01"}, "form": {"traceCase": "H01"},
              "files": {"imgsfile": [source_file]}}
    if variant == "null":
        record[collection] = {field: None}
    elif variant == "missing":
        record[collection] = {}
    elif variant == "wrong-value":
        record[collection] = {field: "h01"}
    elif variant == "no-collection":
        record.pop(collection)
    elif variant == "wrong-run":
        record["correlation"] = case_id + "-previous"
    elif variant == "unreadable":
        record = None
    elif variant == "wrong-file":
        record["files"]["imgsfile"] = [b"different controlled sample"]

    # Controlled page and fixture observations. Receiver rows require a correlated record.
    page_ref = "controlled/page/" + correlation
    fixture_ref = "controlled/fixture/" + correlation
    observations = {}

    def observe(step, source_ref, raw, passed):
        row = {"correlation": correlation, "source_ref": source_ref, "observed": raw,
               "status": "通过" if passed else "失败"}
        observations[step["id"]] = {claim["text"]: row for key in ("expected", "verification")
                                    for claim in step[key]}

    observable = record is not None and record["correlation"] == correlation
    if observable:
        observe(case["common_preconditions"][0], record["source_ref"], "endpoint ready", True)
    observe(steps[0], page_ref, "输入匹配，已打开选择器", True)
    observe(steps[1], fixture_ref, "确认选择本次测试 TXT", True)
    observe(steps[2], page_ref, {"success": True}, True)
    if observable:
        files = record["files"]["imgsfile"]
        observe(steps[3], record["source_ref"], [len(item) for item in files],
                len(files) == 1 and bool(files[0]) and files[0] == source_file)
        hashes = [sha256(value).hexdigest() for value in [source_file, files[0]]]
        observe(steps[4], record["source_ref"], hashes, hashes[0] == hashes[1])
    result = check_received_field(case_id, run_id, record, collection, field, expected_value)
    observations[steps[5]["id"]] = {steps[5]["expected"][0]["text"]: result}
    report = summarize_case(case, run_id, observations)
    assert report["status"] == expected_status, report
    assert any(row.get("source_ref") == page_ref for row in report["assertions"])
    return {"case": case_id, "scenario": variant, "field_result": result, "case_status": report["status"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path)
    batch = json.loads(parser.parse_args().candidate.read_text(encoding="utf-8-sig"))
    assert len(batch["cases"]) == 194 and batch["content_version"].startswith("1976c683b7b6")
    for case_id in ("HM-UP-140", "HM-UP-141"):
        for variant, status in (("exact", "通过"), ("null", "失败"), ("missing", "失败"),
                                ("wrong-value", "失败"), ("wrong-file", "失败"),
                                ("wrong-run", "待取证"), ("no-collection", "待取证"), ("unreadable", "待取证")):
            print(json.dumps(replay(batch, case_id, variant, status), ensure_ascii=False))


if __name__ == "__main__":
    main()
