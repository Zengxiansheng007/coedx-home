# CR-20261115-004 — Dynamic whole-step data binding

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | added |
| Scope | references-and-assets / scripts-and-validation |
| Source | Authorized issue #116, REQ-019/022, AC-027 |
| Baseline | dc52db180f55d53fb9fbc76062471ef87f69f483 |
| Author | Codex |
| Related Records | CR-20261115-003 |

## Summary

Explicit generation_rule separates runtime value from business data semantics.
Whole steps bind ordered current data IDs and a full data digest. Reconstructed
values and endpoint remain checked against the complete authored target.

## Context And Problem

Static reference selection rejected same-rule runtime values. Reusing the P0
data IDs would instead leak source values into the current scenario.

## Sections Changed

scripts/step_reuse.py selects by complete rules and resolves current bindings.
scripts/scoped_review.py shows current dynamic data beside the P0 reference.
scripts/test_step_reuse.py exercises public authoring and rendering.
references/step-reuse.md documents the conservative dynamic contract.

## Decision And Alternatives

Only value differs under a nonempty generation_rule; object_ref, constraints,
validity and unknown business fields remain strict. There is no partial field
override. Existing duplicate-data rejection and source clarification remain.

## Detailed Change

Two complete synthetic candidates use different current values and data IDs.
Changed length rule, object relationship or validity stays fully inline.
Binding mutation fails before rendering. Legacy fixed bindings remain supported.

## Impact Analysis

resolve_step retains its interface and returns current data_refs; feedback
materialization must use that resolved whole step. No downstream execution occurs.

## Validation Evidence

160 unittest regressions passed. Corrected public fixture fails on the parent
step_reuse implementation at the expected reference assertion, and passes here.
The initial failed fixture was stale P0 qualification, not behavior-red evidence.
Logs: task test-output/rr04/tests.txt and baseline-red.txt.
Structural scanner result is separately recorded in task test-output/rr04;
seven inherited findings remain and independent review is pending.

## Safety And Privacy

Synthetic values only; no global installation, real samples or business runs.
No credentials added. Original inputs remain copied and historical evidence retained.

## Risks And Follow-up

Arbitrary natural-language rule contradictions require Agent clarification.
Object_ref instance differences conservatively stay independent. Actual XMind
client and downstream acceptance are not proven by these synthetic checks.
