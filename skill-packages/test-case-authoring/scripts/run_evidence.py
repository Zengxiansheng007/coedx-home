"""Check received fields and summarize evidence from the current execution."""
from collections import Counter


def check_received_field(case_id, run_id, record, collection, name, expected):
    if collection not in ("headers", "form"):
        raise ValueError("collection must be headers or form")
    if not all(isinstance(value, str) and value.strip() for value in (case_id, run_id, name)):
        raise ValueError("case_id, run_id and name must be nonempty strings")
    if not isinstance(expected, str):
        raise ValueError("expected must be the source's exact string")
    correlation = f"{case_id}-{run_id}"
    if not isinstance(record, dict):
        gap = "缺可读的接收记录入口或本次请求记录"
    elif record.get("correlation") != correlation:
        gap = f"缺能关联 {correlation} 的实际请求记录"
    elif not isinstance(record.get("source_ref"), str) or not record["source_ref"].strip():
        gap = "缺本次实际接收记录的证据位置"
    elif not isinstance(record.get(collection), dict):
        gap = f"缺本次请求可读的完整 {collection} 集合"
    else:
        gap = None
    if gap:
        return {"status": "待取证", "gap": gap, "correlation": correlation,
                "collection": collection, "field": name, "expected": expected}
    fields = record[collection]
    if collection == "headers":
        matches = [value for key, value in fields.items() if key.lower() == name.lower()]
    else:
        matches = [fields[name]] if name in fields else []
    return {"status": "通过" if matches == [expected] else "失败", "source_ref": record["source_ref"],
            "correlation": correlation,
            "collection": collection, "field": name, "expected": expected, "observed_values": matches}


def _steps(case, parent_path=""):
    for group in ("common_preconditions", "special_preconditions", "steps",
                  "special_postconditions", "common_postconditions"):
        for step in case.get(group, []):
            escaped_id = step["id"].replace("~", "~0").replace("/", "~1")
            path = f"{parent_path}/{group}/{escaped_id}"
            yield path, step, not parent_path
            if "resolved_case" in step:
                yield from _steps(step["resolved_case"], path)


def summarize_case(case, run_id, observations, *, scoped_observations=None):
    """Roll up recorded judgements for one fully expanded case and one run."""
    if not case.get("steps") or not case.get("id") or not isinstance(run_id, str) or not run_id.strip():
        raise ValueError("expected a complete case and current run identifier")
    correlation = f"{case['id']}-{run_id}"
    assertions = []
    steps = list(_steps(case))
    root_ids = Counter(step["id"] for _, step, root in steps if root)
    scoped = scoped_observations or {}
    for path, step, root in steps:
        step_rows = scoped.get(path, {})
        if path not in scoped and root and root_ids[step["id"]] == 1:
            step_rows = observations.get(step["id"], {})
        checks = [item["text"] for key in ("expected", "verification") for item in step.get(key, [])]
        for check in dict.fromkeys(checks or [step["operation"]]):
            row = step_rows.get(check, {})
            if row.get("correlation") != correlation:
                row = {"status": "待取证", "gap": f"缺 {correlation} 的本步观测"}
            elif row.get("status") == "待取证" and row.get("gap"):
                pass
            elif (row.get("status") not in ("通过", "失败") or
                  not isinstance(row.get("source_ref"), str) or not row["source_ref"].strip() or
                  not ("observed" in row or "observed_values" in row)):
                row = {"status": "待取证", "gap": "缺本步实际观测、证据位置或判定"}
            assertions.append({**row, "step_id": step["id"], "step_path": path, "check": check})
    statuses = {row["status"] for row in assertions}
    status = "失败" if "失败" in statuses else "待取证" if "待取证" in statuses else "通过"
    return {"case_id": case["id"], "run_id": run_id, "status": status, "assertions": assertions}
