# CR-20261116-004 - Scoped recovery and closure

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | changed |
| Scope | core-skill-md / references-and-assets / scripts-and-validation / safety-and-governance |
| Source | TAS-04 issue 125; parent 121; AC-007/026/027/028 |
| Baseline | 69149e4 integration |
| Author | Codex |
| Related Records | CR-20261116-002, CR-20261116-003 |

## Summary

Recover old paths and valid decisions; close only independently reviewed and saved scope. Candidate status; actual dialogue remains separately evaluated.

## Context And Problem

TCA had permanent replay and source checkpoints but no bounded temporary cleanup. TPD already had scoped cleanup, highwater and local reopening; preserve those rules and make upgrade recovery explicit.

## Sections Changed

| File | Section | Change Summary |
|---|---|---|
| SKILL.md | Recovery and closure | Preserve actual history and scoped completion |
| references/qa-record-contract.md | Recovery and closure | Preserve actual history and scoped completion |
| references/scope-closure.md | Recovery and closure | Preserve actual history and scoped completion |
| scripts/qa_record.py | Recovery and closure | Preserve actual history and scoped completion |
| scripts/test_scope_closure.py | Recovery and closure | Preserve actual history and scoped completion |

## Decision And Alternatives

Reuse existing qa_record permanent events and TPD procedural closure. No parallel answer store, new business state machine or shared-skill duplication. Original natural-language records continue in place; no bulk migration.

## Detailed Change

Permanent version, actual review reply, dispositions, product impact and identity highwater precede bounded temporary cleanup. Summary-only, partial whole-batch approval and failed saves cannot clear unfinished scope. Interruptions inspect actual files; later changed checks use new IDs and retain unchanged decisions. Cross-skill sources remain references.

## Impact Analysis

TCA touched-file mirrors match canonical. Inherited whole-mirror drift is Root-owned. TPD stays steps-only; script/public tests cannot prove actual parent interaction. No renderer, dependency helper, original business files or globally installed files changed.

## Validation Evidence

| Check | Command or Method | Result | Evidence |
|---|---|---|---|
| Public persistence seam | unittest test_scope_closure plus affected recovery/record/coverage/feedback/partial-answer suites | 25 passed; 5 new real-file closure tests | external evidence/tas-04/public-tests.json |
| Red/green | Missing public cleanup seam; then cleaned-ID reuse rejected | Both red findings retained in report | external evidence/tas-04/report.md |
| Skill validator | validate_create_skill.py --require-change-records | Rejected: same 3 inherited synthetic-secret matches and 1 CLI-resource regex finding; no new findings | external evidence/tas-04 |
| Actual parent interaction | Independent actor requested by Root | Pending; not claimed | Root-owned interaction evidence |
| Client and business | Not in this ticket execution scope | Unverified | No claim |

## Safety And Privacy

Changed source and synthetic fixtures contain no real inputs, credentials or private business URLs. No remote/global/business execution. Sanitized synthetic OS-failure injection verifies interrupted writes, never real business failure.

## Risks And Follow-up

Semantic coverage, confirmation scope, real identity and source interpretation remain Agent responsibilities. API validates file and structural consistency, not a host security boundary. Root must separately assess both parents through real routed interaction before full AC closure.

Refs: TEST-AUTHORING-STAGE-20261116; TAS-04.
