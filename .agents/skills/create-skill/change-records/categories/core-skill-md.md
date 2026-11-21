# Core SKILL.md Change Ledger

## Purpose

Record changes that affect `SKILL.md` trigger behavior, operating rules, workflow, validation, escalation, and delivery expectations.

## Outline

| Date | Change ID | Section | Change Type | Summary | Status |
|---|---|---|---|---|---|
| 2026-09-28 | CR-20260928-001 | Operating Rules / Workflow / Decision Rules / Validation / Deliver | governance | Treat Agent output as candidate and require trusted gate mapping and host promotion. | validated |
| 2026-08-09 | CR-20260809-001 | Operating Rules / Workflow / Validation / Deliver | governance | Add mandatory traceable change-record mode for existing-skill updates. | validated |

## Detailed Records

### CR-20260928-001 - trusted-gate-workflow

- Section changed: Operating Rules, Workflow, Decision Rules, Validation, Deliver.
- Before: The Agent ran validation and delivered a Skill without an independent acceptance boundary.
- After: Candidate-only output, structured gate mapping, and host-owned acceptance are explicit.
- Why: Mandatory conditions require a verifier and execution entry the Agent cannot skip.
- Impact: Generated Skills need runtime capability evidence before acceptance.
- Validation: Global focused tests and structure checks passed; 14-file hash readback matched.
- Detail record: ../entries/2026/2026-09/CR-20260928-001-trusted-gate-contract.md

### CR-20260809-001 - traceable-change-record-mode

- Section changed: Operating Rules, Workflow, Validation, Deliver.
- Before: Existing-skill updates did not require structured change records.
- After: File-changing updates must use `change-records/` index, category ledgers, and detail records.
- Why: Final PRD requires long-term traceability and governance beyond a single changelog file.
- Impact: Future skill updates have a stronger completion contract.
- Validation: Workspace copy passed validator and tests before global deployment approval.
- Detail record: ../entries/2026/2026-08/CR-20260809-001-traceable-change-records.md

