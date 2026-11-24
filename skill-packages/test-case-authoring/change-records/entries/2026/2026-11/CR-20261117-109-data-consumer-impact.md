# CR-20261117-109 - Complete data consumer impact

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | fixed |
| Scope | references-and-assets / scripts-and-validation / downstream-and-handoff |
| Source | Final independent Spec P2 and Standards P3; #134 / #140 |
| Baseline | 1f122a65efca30f9c417acea4cddf1f03173d0d6 |
| Author | Codex |
| Related Records | CR-20261117-106 |

## Summary
Compute complete actual data consumption independently of common-operation exclusions and recheck it on application.

## Context And Problem
A hidden common-operation exception independently used shared data but was absent from the proposal. The same cause affected partial copies without common scopes. Old prepared proposals could retain incomplete impact.

## Sections Changed
Feedback data-owner resolution and local impact-record helper; opt-in complete-parent context; public chat/Markdown/native and application regressions; feedback contract; identical distribution copy.

## Decision And Alternatives
Reuse baseline catalog hash/version, existing reference resolver and application review boundary. Reject incomplete review instead of adding unapproved cases or embedding a complete parent. One small local record helper eliminates duplicate owner-record construction.

## Detailed Change
Every current group and reference binding contributes data consumers. Operation exceptions remain operation-specific. Missing/stale parents block dependent data edits only. Apply rechecks historical proposals against actual ownership; expanded review can proceed and leaves exclusions intact.

## Impact Analysis
AC-034 and associated AC-029/031: precise data identity/impact, hidden-source preservation, legacy no-edit behavior and local edits. No generation/client/business acceptance claim.

## Validation Evidence
External tco-review-fix evidence retains original reproduction, red tests and targeted green logs. Required repository checks and create-skill validation are recorded in result.md; record remains applied candidate pending independent review. No historical evidence replaced.

## Safety And Privacy
Only labeled synthetic fixtures; no credentials, original business inputs, remote calls, global installation or execution writes. Sensitive-data validation distinguishes inherited synthetic fixtures from newly introduced findings.

## Risks And Follow-up
Independent final recheck and real generation/client/user review remain separate. Local guard is not host enforcement.

Refs: #134, #140; final Spec P2; final Standards P3.

Related regression repair: providing the actual parent exposed candidate-owned reference definitions absent from that older parent. Rendering retains existing candidate resolution when the parent lacks the exact definition; valid dynamically rebound local data remains editable. Affected synthetic feedback tests now explicitly include every data consumer or supply exact parent for unique data; hidden shared P0 consumers remain blocked.
