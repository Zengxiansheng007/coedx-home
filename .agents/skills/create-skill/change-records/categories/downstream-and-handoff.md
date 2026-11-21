# Downstream And Handoff Change Ledger

## Purpose

Record changes to the contract passed from `create-skill` candidates to a controlled runtime or delivery host.

## Outline

| Date | Change ID | Section | Change Type | Summary | Status |
|---|---|---|---|---|---|
| 2026-09-28 | CR-20260928-001 | Candidate-to-host handoff | governance | Require independent gate coverage and host-owned acceptance receipt. | validated |

## Detailed Records

### CR-20260928-001 - controlled-host-handoff

- Section changed: `gate-contract.json` declaration and host acceptance requirements.
- Before: Candidate validation and report status could be treated as delivery authority.
- After: The host must independently verify package bytes, effects, alternate paths, action freshness, and permissions before a scoped receipt.
- Why: The handoff needs an enforceable boundary outside Agent-writable files.
- Impact: Other runtimes must qualify their own effects and cannot inherit the first isolated-file-write result.
- Validation: Focused tests passed on workspace copy; host acceptance tests remain downstream work.
- Detail record: ../entries/2026/2026-09/CR-20260928-001-trusted-gate-contract.md
