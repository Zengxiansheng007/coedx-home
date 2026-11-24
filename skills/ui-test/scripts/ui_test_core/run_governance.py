"""Canonical event-folded RunResult and immutable downstream projections."""

from __future__ import annotations

import copy
from datetime import UTC, datetime
from typing import Any

from .case_contracts import canonical_hash
from .pycharm_acceptance import validate_pycharm_acceptance_chain


def retained_action_data(actions):
    """保守保留每个已消费动作的事实；未知实体不补造，也不执行清理。"""
    return [dict(action_key=a['action_key'],entity_id=a['entity_id'],write_state=a['write_state'],
                 evidence_refs=copy.deepcopy(a['evidence_refs']),cleanup_status='not_planned_this_release')
            for a in actions if a['submit_count']==1]


def action_result_issues(result):
    """逐动作跨字段约束；schema负责形状，本函数不授予业务许可。"""
    actions=result['action_results'];issues=[]
    def issue(): issues.append(dict(code='ACTION_RESULT_INCONSISTENT',path='/action_results',message='Action facts conflict with canonical result'))
    if (len({a['action_id'] for a in actions})!=len(actions) or len({a['action_key'] for a in actions})!=len(actions)
        or len({a['source_step_id'] for a in actions})!=len(actions)
        or result['submit_count']!=sum(a['submit_count'] for a in actions)): issue()
    if any(type(s) is not dict for s in result['step_results']): issue();return issues
    steps={s.get('step_id'):s for s in result['step_results']}
    for action in actions:
        step=steps.get(action['source_step_id'])
        if (action['source_step_id']!=action['action_id'] or step is None
            or step is not None and (step.get('module_id')!=action['module_id'] or step.get('actor_ref')!=action['actor_ref'])
            or not set(action['evidence_refs']).issubset(result['evidence_refs'])
            or action['write_state']=='not_attempted' and (action['submit_count']!=0 or action['entity_id'] is not None)
            or action['write_state']!='not_attempted' and action['submit_count']!=1
            or action['write_state']=='write_succeeded_verified' and (not action['entity_id'] or not action['evidence_refs'])
            or result['overall_status']=='passed' and (action['write_state']!='write_succeeded_verified' or step.get('status')!='passed')): issue()
    expected=('not_attempted' if not actions or all(a['write_state']=='not_attempted' for a in actions)
        else 'write_succeeded_verified' if all(a['write_state']=='write_succeeded_verified' for a in actions)
        else 'write_outcome_unknown')
    if result['write_state']!=expected: issue()
    retained=retained_action_data(actions)
    if (result['retained_test_data']!=retained
        or result['cleanup_status']!=('not_planned_this_release' if retained else 'not_applicable')): issue()
    return issues


def aggregate_events(*, run: dict[str, Any], events: list[dict[str, Any]], release_status: str,
                     action_results: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    if 'action_results' in run: raise ValueError('E_ACTION_RESULT_RUN_OVERRIDE')
    ordered = sorted(events, key=lambda item: (item.get("sequence", 0), item.get("event_id", "")))
    steps: dict[str, dict[str, Any]] = {}
    evidence_refs: set[str] = set()
    findings: list[str] = []
    retained_data = []
    write_state = "not_attempted"
    submit_count = 0
    for event in ordered:
        step_id = event.get("step_id")
        if step_id:
            steps[step_id] = {
                "step_id": step_id, "section": event.get("section", "feature"), "status": event.get("status", "unknown"),
                "required": event.get("required", True), "tool": event.get("tool"), "evidence_refs": sorted(set(event.get("evidence_refs", []))),
                "failure_layer": event.get("failure_layer"),
                **({k:event[k] for k in ('module_id','actor_ref') if k in event} if action_results is not None else {}),
            }
            evidence_refs.update(event.get("evidence_refs", []))
        if event.get("event_type") == "write-outcome":
            write_state = event.get("write_state", write_state)
            submit_count = max(submit_count, int(event.get("submit_count", 0)))
            if event.get("retained_test_data"):
                retained_data.append(copy.deepcopy(event["retained_test_data"]))
    if action_results is not None:
        if any(e.get('event_type')=='write-outcome' for e in events): raise ValueError('E_ACTION_RESULT_MIXED_WRITES')
        action_results=copy.deepcopy(action_results)
        # 先用原schema核逐动作形状，防止任意载荷或Python布尔值进入求和。
        from jsonschema import Draft202012Validator
        from .case_contracts import load_schema
        schema=load_schema('run-result.schema.json')['properties']['action_results']
        if list(Draft202012Validator(schema).iter_errors(action_results)): raise ValueError('E_ACTION_RESULT_INVALID')
        retained_data=retained_action_data(action_results)
        submit_count=sum(a['submit_count'] for a in action_results)
        write_state=('not_attempted' if not action_results or all(a['write_state']=='not_attempted' for a in action_results)
            else 'write_succeeded_verified' if all(a['write_state']=='write_succeeded_verified' for a in action_results)
            else 'write_outcome_unknown')
    required = [item for item in steps.values() if item["required"]]
    setup_failed = any(item["section"] == "setup" and item["status"] != "passed" for item in required)
    if release_status != "in_sync":
        overall = "blocked"; findings.append("release-not-in-sync")
    elif action_results is None and submit_count > 1:
        overall = "blocked"; findings.append("double-submit")
    elif action_results is not None and any(a['write_state']!='write_succeeded_verified' for a in action_results):
        overall = 'failed'; findings.append('action-outcome-unverified')
    elif write_state == "write_succeeded_verification_failed":
        overall = "failed"; findings.append("write-succeeded-verification-failed")
    elif setup_failed:
        overall = "failed"; findings.append("setup-navigation-failure")
    elif any(item["status"] in {"failed", "blocked", "policy-failed", "security-failed"} for item in required):
        overall = "failed"; findings.append("required-step-failed")
    elif any(not item["evidence_refs"] for item in required):
        overall = "failed"; findings.append("required-evidence-missing")
    elif required and all(item["status"] == "passed" for item in required):
        overall = "passed"
    else:
        overall = "failed"; findings.append("incomplete-required-results")
    result = {
        "schema_version": "ui-test.run-result.v2", **run, "overall_status": overall,
        "release_status": release_status, "step_results": list(steps.values()),
        "evidence_refs": sorted(evidence_refs), "conflicts": [], "findings": findings,
        "write_state": write_state, "submit_count": submit_count, "retained_test_data": retained_data,
        "cleanup_status": "not_planned_this_release" if retained_data else "not_applicable",
        "business_cleanup_attempted": False,
    }
    if action_results is not None:
        result['action_results']=action_results
        if action_result_issues(result): raise ValueError('E_ACTION_RESULT_INCONSISTENT')
    result["run_result_hash"] = canonical_hash(result)
    return result


def project_run_result(
    run_result: dict[str, Any],
    projection: str,
    *,
    acceptance_result: dict[str, Any] | None = None,
    acceptance_chain: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source_hash = canonical_hash(run_result)
    common = {"schema_version": f"ui-test.{projection}.v1", "projection": projection, "run_id": run_result["run_id"], "case_id": run_result["case_id"], "branch_id": run_result["branch_id"], "overall_status": run_result["overall_status"], "source_run_result_hash": source_hash, "read_only_projection": True}
    if projection == "evidence-index":
        return {**common, "evidence_refs": copy.deepcopy(run_result["evidence_refs"]), "step_evidence": {item["step_id"]: item["evidence_refs"] for item in run_result["step_results"]}}
    if projection == "report-model":
        return {**common, "sections": {"setup": [item for item in run_result["step_results"] if item["section"] == "setup"], "feature": [item for item in run_result["step_results"] if item["section"] == "feature"], "assertions": [item for item in run_result["step_results"] if item["section"] == "assertions"]}, "retained_test_data": copy.deepcopy(run_result["retained_test_data"]), "cleanup_status": run_result["cleanup_status"], **({'action_results':copy.deepcopy(run_result['action_results'])} if 'action_results' in run_result else {})}
    if projection == "experience-candidate":
        chain = dict(acceptance_chain or {})
        required_chain = {
            "run_result", "finalization_commit", "finalization_receipt", "pytest_session_result",
            "acceptance_result", "approval_record", "execution_context", "terminal", "process_evidence",
        }
        external_acceptance_missing = run_result.get("schema_version") == "ui-test.run-result.v5" and (
            (acceptance_result or {}).get("overall_status", (acceptance_result or {}).get("verdict")) != "passed"
            or (acceptance_result or {}).get("observed_process_exit_code") != 0
            or set(chain) != required_chain
            or chain.get("run_result") != run_result
            or chain.get("acceptance_result") != (acceptance_result or {})
            or bool(validate_pycharm_acceptance_chain(**chain))
        )
        # V5业务passed没有资格单独生成正向经验；必须绑定进程退出后的外部验收。
        status = "negative" if run_result["overall_status"] != "passed" or external_acceptance_missing else "observed"
        return {**common, "experience_status": status, "permission_effect": "none", "promotion_effect": "none", "evidence_refs": copy.deepcopy(run_result["evidence_refs"]), "forbidden_reuse": [{"reason": "failed-run"}] if status == "negative" else []}
    raise ValueError("E_PROJECTION_UNKNOWN")


def create_run_reconciliation(*, run_result: dict[str, Any], reconciled_write_state: str, evidence: list[dict[str, Any]], reason_code: str, created_at: str | None = None) -> dict[str, Any]:
    if run_result.get("write_state") not in {"write_outcome_unknown", "submitted_unknown"}:
        raise ValueError("E_RECONCILIATION_SOURCE_NOT_UNKNOWN")  # Reconcile only genuinely unknown historical write outcomes.
    if reconciled_write_state not in {"write_failed", "write_succeeded_verified", "write_succeeded_verification_failed"}:
        raise ValueError("E_RECONCILIATION_STATE_INVALID")  # Never replace uncertainty with another ambiguous state.
    if not evidence or any(not item.get("ref") or not item.get("sha256", "").startswith("sha256:") for item in evidence):
        raise ValueError("E_RECONCILIATION_EVIDENCE_INVALID")  # Require hash-bound evidence for every historical conclusion.
    record = {
        "schema_version": "ui-test.run-reconciliation.v1",
        "run_id": run_result["run_id"],
        "case_id": run_result["case_id"],
        "canonical_run_result_hash": run_result["run_result_hash"],
        "original_write_state": run_result["write_state"],
        "reconciled_write_state": reconciled_write_state,
        "reason_code": reason_code,
        "evidence": copy.deepcopy(evidence),
        "canonical_run_result_unchanged": True,
        "reconciliation_effect": "diagnostic-only",
        "rerun_authorization_effect": "none",
        "created_at": created_at or datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }
    record["reconciliation_hash"] = canonical_hash(record)  # Make later diagnostic drift detectable without rewriting history.
    return record
