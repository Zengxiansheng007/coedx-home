# CR-20261116-003 - Shared TCA stage adapter

| Field | Value |
| --- | --- |
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | changed |
| Scope | core-skill-md / references-and-assets / scripts-and-validation / safety-and-governance / downstream-and-handoff |
| Source | TAS-03 issue 124; parent 121; AC-001/002/003/004/006/024/025 |
| Baseline | bc4226cec89bbf90c32bed917111f7034b83f6eb |
| Author | Codex |
| Related Records | CR-20261111-105, CR-20261111-107, CR-20261111-109, CR-20261111-110 |

## Summary

Route shared questioning through test-grill-me while preserving all TCA professional qualification and authoring entries. Distinguish summary-only confirmation, continuation and concrete draft approval.

## Context And Problem

The parent duplicated shared interaction and instructed applying updates immediately after summary agreement. Existing record_note, record_context and apply/review boundaries already support the requested distinction; no new business workflow or runtime state is needed.

## Sections Changed

| File | Section | Change Summary |
| --- | --- | --- |
| SKILL.md | Stage entry | Shared routing, intent mapping or public behavior characterization |
| references/stage-adapter.md | Stage entry | Shared routing, intent mapping or public behavior characterization |
| references/clarification-contract.md | Stage entry | Shared routing, intent mapping or public behavior characterization |
| references/qa-record-contract.md | Stage entry | Shared routing, intent mapping or public behavior characterization |
| references/feedback-contract.md | Stage entry | Shared routing, intent mapping or public behavior characterization |
| references/product-reconciliation-contract.md | Stage entry | Shared routing, intent mapping or public behavior characterization |
| references/report-reconciliation.md | Stage entry | Shared routing, intent mapping or public behavior characterization |
| references/coverage-review.md | Stage entry | Shared routing, intent mapping or public behavior characterization |
| scripts/test_stage_adapter.py | Stage entry | Shared routing, intent mapping or public behavior characterization |

## Decision And Alternatives

Use a steps-only adapter onto the existing public seam. Reject a new executable stage controller or duplicate approval store. Confirmation intent stays contextual evidence in existing notes; actual candidate changes use existing apply_summary/apply_feedback. Preserve professional field contracts, report reading, full P0 qualification, explicit P1/P2 start, provisional/deferred meaning and scoped omission semantics.

## Detailed Change

Load test-grill-me through host name resolution and pass task/stage and return context. Replace parent batch dialogue sequence and conflicting linked application instructions. Confirm-only saves its exact summary/version/scope and waits; continuing later reuses still-valid confirmation. Explicit confirm-and-continue records both meanings then authoring returns directly to concrete review. No generated-existence confirmation is added. A reviewed case remains not_merged/not_run.

## Impact Analysis

Recording and complete handwritten input, reports and attachments, current full approved P0 evidence, human checks, priority, feedback and product conditions keep their current owners. Shared interaction alone never establishes qualification. Existing sole MD events remain untouched and replay is unchanged. Cleanup/recovery implementation belongs to TAS-04; cross-module resolver work belongs to TAS-09. Canonical and repository mirror carry this ticket's identical files only; inherited mirror drift is Root-owned.

## Validation Evidence

| Check | Command or Method | Result | Evidence |
| --- | --- | --- | --- |
| Existing API characterization | unittest test_stage_adapter plus qa_record/p0_evidence/report_reconciliation/handwritten/feedback_record/partial_answers/coverage_review | 34 passed | external evidence/tas-03/public-regression.txt |
| Red/green applicability | No production executable changes; new public tests characterize already-correct existing primitives | No artificial red test; procedural gap demonstrated in baseline instructions | baseline diff |
| Create-skill validation | validate_create_skill.py with --require-change-records | Rejected with 4 inherited findings: 3 synthetic credential-test matches and 1 CLI resource-regex match; no new record/section/trigger finding | external TAS-03 evidence |
| Actual dialogue | Shared core previously observed separately; changed TCA route not yet independently exercised | Pending; not inferred from tests | Root interaction evidence |
| Client/business | Not exercised by this ticket | Unverified | No claim |

## Safety And Privacy

Exact changed text and synthetic fixtures reviewed; no actual business inputs, credentials, private source paths or execution added. No remote/global/business actions. Candidate status only, never host acceptance.

## Risks And Follow-up

The thin adapter relies on agent intent interpretation; raw APIs intentionally do not parse natural language or enforce a second host boundary. Root must run actual routed dialogue and integrated acceptance. Scanner results may include inherited command regex and synthetic fixture false positives; preserve findings without changing tests to silence them.

Refs: TAS-03; parent TEST-AUTHORING-STAGE-20261116.
