#!/usr/bin/env python3
"""Deterministic tests for create-skill validator."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = ROOT / "scripts" / "validate_create_skill.py"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_validate(folder: Path, require_change_records: bool = False, require_gate_contract: bool = False) -> dict:
    command = [sys.executable, str(VALIDATOR), str(folder)]
    if require_change_records:
        command.append("--require-change-records")
    if require_gate_contract:
        command.append("--require-gate-contract")
    process = subprocess.run(command, capture_output=True, text=True)
    assert process.returncode in {0, 1}, process.stderr
    report = json.loads(process.stdout)
    expected_exit = 1 if report["summary"]["P0"] or report["summary"]["P1"] else 0
    assert process.returncode == expected_exit, (process.returncode, report)
    return report


def has_rule(report: dict, rule: str) -> bool:
    return any(item["rule"] == rule for item in report["findings"])


def main() -> int:
    self_report = run_validate(ROOT)
    assert self_report["summary"]["P0"] == 0, self_report
    assert self_report["status"] == "validated-candidate", self_report
    assert self_report["acceptance"] == {"authority": "trusted-host-only", "verified": False}

    with tempfile.TemporaryDirectory(prefix="create-skill-test-") as tempdir:
        temp = Path(tempdir)

        good = temp / "good-skill"
        write(
            good / "SKILL.md",
            """---
name: good-skill
description: Create concise example reports from supplied notes. Use when asked to turn notes into a structured report, validate report shape, or package a reusable reporting workflow.
---

# Good Skill

## Operating Rules

- Keep reports concise.

## Workflow

1. Read the notes.
2. Produce the report.

## Validation

Run the report shape check.

## Escalation

Ask before writing outside the output directory.
""",
        )
        good_report = run_validate(good)
        assert good_report["summary"]["P0"] == 0, good_report
        assert good_report["status"] == "validated-candidate"

        no_contract_report = run_validate(good, require_gate_contract=True)
        assert has_rule(no_contract_report, "gate-contract-missing")
        assert no_contract_report["status"] == "review-required"

        contract = {
            "schemaVersion": "1.0",
            "targetRuntime": "controlled-codex-host",
            "mode": "required",
            "gates": [{
                "id": "G-001",
                "condition": "Only an approved isolated test target may be written",
                "protectedEffect": "write isolated test file",
                "protectedAction": "write-file",
                "enforcementEntry": "host.writeProtectedFile",
                "decisionAuthority": "program",
                "decisionProvider": "host-file-policy",
                "bindTo": ["action", "arguments", "target", "state"],
                "freshness": "per-action",
                "failureMode": "deny",
                "alternatePaths": [{"path": "direct-shell-write", "disposition": "disabled", "verificationRef": "host-negative-test-001"}],
            }],
        }
        write(good / "gate-contract.json", json.dumps(contract))
        gate_report = run_validate(good, require_gate_contract=True)
        assert gate_report["status"] == "validated-candidate", gate_report
        assert gate_report["acceptance"]["verified"] is False

        contract["gates"][0]["failureMode"] = "continue"
        contract["gates"][0]["bindTo"].remove("state")
        write(good / "gate-contract.json", json.dumps(contract))
        unsafe_gate_report = run_validate(good, require_gate_contract=True)
        assert has_rule(unsafe_gate_report, "gate-contract-failure-mode")
        assert has_rule(unsafe_gate_report, "gate-contract-bindings")
        assert unsafe_gate_report["status"] == "review-required"
        contract["gates"][0]["failureMode"] = "deny"
        contract["gates"][0]["bindTo"].append("state")
        write(good / "gate-contract.json", json.dumps(contract))

        write(
            good / "change-records" / "index.md",
            """# Change Records

## Latest Changes

| Date | Change ID | Summary | Status |
|---|---|---|---|
| 2026-08-09 | CR-20260809-001 | Add record system. | validated |

## Category Index

| Category | Path |
|---|---|
| Core | categories/core-skill-md.md |

## Open Risks

- None.
""",
        )
        write(
            good / "change-records" / "categories" / "core-skill-md.md",
            """# Core SKILL.md Change Ledger

## Purpose

Track core skill changes.

## Outline

| Date | Change ID | Section | Change Type | Summary | Status |
|---|---|---|---|---|---|
| 2026-08-09 | CR-20260809-001 | Workflow | governance | Add records. | validated |

## Detailed Records

### CR-20260809-001 - add-record-system

- Section changed: Workflow
- Before: No record requirement.
- After: Record requirement.
- Why: Traceability.
- Impact: Safer updates.
- Validation: Passed.
- Detail record: ../entries/2026/2026-08/CR-20260809-001-add-record-system.md
""",
        )
        write(
            good / "change-records" / "entries" / "2026" / "2026-08" / "CR-20260809-001-add-record-system.md",
            """# CR-20260809-001 - Add Record System

| Field | Value |
|---|---|
| Status | validated |
| Target Skill | good-skill |
| Change Type | governance |
| Scope | core-skill-md |
| Source | test |
| Baseline | temporary fixture |
| Author | Codex |
| Related Records | none |

## Summary

Add records.

## Context And Problem

No records existed.

## Sections Changed

| File | Section | Change Summary |
|---|---|---|
| SKILL.md | Workflow | Add record step. |

## Decision And Alternatives

Use Markdown records.

## Detailed Change

Added fixture records.

## Impact Analysis

Improves traceability.

## Validation Evidence

| Check | Command or Method | Result | Evidence |
|---|---|---|---|
| validator | run_validate | passed | stdout |

## Safety And Privacy

No sensitive data.

## Risks And Follow-up

None.
""",
        )
        good_record_report = run_validate(good, require_change_records=True)
        assert good_record_report["summary"]["P0"] == 0, good_record_report

        bad = temp / "bad-skill"
        secret = "pass" + "word=abc123"
        destructive = "Remove" + "-Item C:\\temp -Recurse -Force"
        write(
            bad / "SKILL.md",
            f"""---
name: bad
description: Helps.
extra: nope
---

# Bad Skill

Run this with {secret} and then {destructive}.
""",
        )
        bad_report = run_validate(bad)
        assert has_rule(bad_report, "name-folder-mismatch")
        assert has_rule(bad_report, "frontmatter-extra-fields")
        assert has_rule(bad_report, "description-too-weak")
        assert has_rule(bad_report, "secret-pattern")
        assert has_rule(bad_report, "dangerous-command")
        assert bad_report["summary"]["P0"] >= 2

        missing_ref = temp / "missing-ref"
        write(
            missing_ref / "SKILL.md",
            """---
name: missing-ref
description: Review skill resources and validate links. Use when asked to check references, scripts, assets, or package shape in an existing skill.
---

# Missing Ref

Read [the guide](references/guide.md).

## Validation

Validate links.

## Escalation

Ask before external access.
""",
        )
        missing_report = run_validate(missing_ref)
        assert has_rule(missing_report, "link-missing")

        no_records_report = run_validate(missing_ref, require_change_records=True)
        assert has_rule(no_records_report, "change-records-missing")
    print("ok: create-skill tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
