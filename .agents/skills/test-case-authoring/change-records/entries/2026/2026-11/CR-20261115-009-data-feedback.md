# CR-20261115-009 — Materialize data feedback consumers

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | fixed |
| Scope | scripts-and-validation |
| Source | #117 independent review semantic-04-05; REQ-021 / AC-030 |
| Baseline | 66df0b444fd8a121e42c76803ea3018ebe23cafb |
| Author | Codex |
| Related Records | CR-20261115-005 |

## Summary
Resolve affected whole-step consumers before applying agreed current-data feedback.

## Context And Problem
Agreed data/value edits left frozen reference bindings unchanged and then failed validation with a binding-change exception.

## Sections Changed

| File | Section | Change Summary |
|---|---|---|
| scripts/local_step_feedback.py | Materialization | Resolve affected current consumers before data changes |
| scripts/feedback.py | Apply confirmed feedback | Refresh affected target digests afterward |
| scripts/test_local_step_feedback.py | Public feedback regressions | Cover shared data and isolated dynamic bindings |

## Decision And Alternatives
Materialize current consumers rather than mutate frozen source definitions. Explicit shared identities affect their consumers; separate dynamic bindings retain exact case scope.

## Detailed Change
After existing confirmation and review gates, copy full affected steps into their current cases, apply the reviewed data change and refresh their target digests. Source P0, frozen definitions and historical input snapshots remain unchanged.

## Impact Analysis
Only affected current consumers change. Pure layout feedback and protected references retain their existing behavior. This record correction changes documentation only; it does not alter product behavior.

## Validation Evidence

Evidence directory: external `D:/reference/tca-review-reuse-20261114/test-output/rr05-fix`.

| Check | Command or Method | Result | Evidence |
|---|---|---|---|
| RED | Public prepare_feedback/confirm synthetic seam | Five tests, one binding-change error before implementation | results.md; transcribed tool output, not raw capture |
| Targeted GREEN | Existing targeted unittest run | 22 tests passed | results.md; transcribed tool output |
| Implementer regression | unittest discover | 166 tests passed in 21.049s | results.md; transcribed tool output |
| Merger regression | Captured unittest output | 168 tests passed in 22.148s | merge-tests.txt |
| Merger reproduction | Public feedback reproduction | Affected HIGH and LOW; APPLIED | merge-repro.txt |

For this documentation-only correction, product tests are not rerun. The create-skill structural validator is rerun separately; remaining pre-batch findings are not evidence of product failure or acceptance.

## Safety And Privacy
Synthetic fixtures only; no credentials, source P0 rewrites, business execution, installation or publication. Historical evidence explicitly records that initial worktree creation preceded skill reading; subsequent testing and commit used the governed runner. This correction preserves that history.

## Risks And Follow-up
Candidate remains subject to independent review. No real client or business acceptance is claimed. Prior record formatting defects belong to this batch and are corrected here; they must not be described as inherited baseline findings.
