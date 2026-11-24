# CR-20261117-102 - Module common preconditions

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | fixed |
| Scope | core-skill-md / references-and-assets / scripts-and-validation / downstream-and-handoff |
| Source | user-authorized #136 / TCO-02 |
| Baseline | 1b7a133ee03644e304e9819486c210143d362eb5 |
| Author | Codex |
| Related Records | CR-20261116-007; CR-20261117-017 |

## Summary
Common preparation is defined directly under the module. Cases retain actual special operations, while unknown common applicability remains visibly pending. Version 2 per-item scopes retain original ordered actions as their definition source.

## Context And Problem
Whole-list scope aggregation placed definitions inside business subgroups and generated repeated common references. One whole-list assessment could not express different exception sets for separate operations.

## Sections Changed
| File | Section | Change Summary |
|---|---|---|
| SKILL.md; references/aggregation-contract.md | Generation and recovery | Module placement, per-item review and legacy handling |
| scripts/preparation_scope.py | Existing review adapter | Compatible version 2 source locators, lifecycle bindings and local conflicts |
| scripts/aggregation.py; scripts/scoped_review.py | Public XMind and chat projection | Module definitions, special-only case headings, retained pending content |
| scripts/feedback.py; scripts/restoration.py | Existing consumers | Exact prior-layout retry and local binding checks |
| scripts/test_common_operations.py; scripts/test_aggregation.py; assets/fixtures/common-pre-1b7a133.json | Public seam checks | Synthetic review, per-item exclusions, save/read and actual old-emitter return |

## Decision And Alternatives
Extend preparation_scopes inside the candidate; do not duplicate operations into another registry. Definition locators reference existing source step IDs, so operation conditions, ordered data and expectations keep one authority. Keep business applicability independent of display placement. Unknown content stays pending instead of relabelling it special.

## Detailed Change
The optional operation_id and step_ids_by_case extend the existing review adapter. Direction reserves the postcondition seam; this ticket authors preconditions. Complete existing business membership, actual review evidence, qualitative coverage and source equivalence remain required. Overlapping step owners fail. A version 2 stale binding blocks affected restoration; separate ready cases survive. Old whole-list records retain read compatibility. The exact pre-increment emitter fixture verifies no-edit and changed shared returns.

## Impact Analysis
No source material migration, data identity change, expiry alteration, operation execution or permission grant. Existing special groups and actual operations remain intact. #137 extends postconditions; #138 covers full-catalog scope lifecycle and selected-copy context. Actual Skill dialogue, real four-case regeneration, client import and business acceptance remain later gates.

## Validation Evidence
| Check | Command or Method | Result | Evidence |
|---|---|---|---|
| TDD module placement | Public scoped generation | Red indentation 12 vs 10; green | external evidence/tco-02/red-1.log; green-1.log |
| TDD per-item semantics | Public scope, render, feedback and preflight | Red missing optional argument; green | red-2.log; green-2.log |
| TDD retained notes | Public generation | Red lost condition; green | red-notes.log; green-notes.log |
| Public regression | unittest discover | 255 passed before final note addition; final required checks follow | full-authoring.log |
| Frozen old emitter and save/read | Public feedback/writer/render | Passed; initial test destination contract error corrected without product change | green-save-legacy-2.log |

## Safety And Privacy
Only explicitly synthetic fixtures. Original private material, global installation and historical outputs untouched. No network, dependencies, model calls or business execution. Existing synthetic secret-negative fixtures are not live secrets.

## Risks And Follow-up
Applied candidate pending independent review and integration checks. Supplied actual_reply strings are evidence, not independently enforced authorization. Preserve inherited validator findings and distinguish local interface coverage from real dialogue/client acceptance.

Refs: #134; #136; existing aggregation contract.

### Final local validation

- Required tools/checks.py: all eight stages passed, including 256 authoring tests; workflow 67, verification 8 and distribution 1 (332 total). Evidence: external evidence/tco-02/checks-final.log and ticket worktree test-output/tco-02/checks-final/summary.json.
- create-skill --require-change-records: exactly the three inherited synthetic negative-fixture secret-pattern findings; P0=3/P1=0/P2=0. All affected sources unchanged. No new finding; status remains applied candidate.
- git diff --check clean; repository copies check proves canonical and mirror identity. No installation, remote publication, actual XMind client or business acceptance.

### Upstream integration: TCO-01 and TCO-05

Merged integration fbfd700 after initial candidate a839eea. Preserve separate data, common-operation and audit layout switches; the feedback adapter tries only their known historical combinations against the same immutable baseline. All data projection flags remain present in normal, recursive and feedback-probe rendering. Additive change ledgers retain every ticket record.

Combined public tests: 36 passed (external upstream-combined-3.log), including a new compound object/value edit inside a grouped shared preparation definition. The proposal preserves the single original data identity and exact field paths. Initial added-test errors concerned its simulated grouped-case binding and the public proposal field name; corrected harness only, with failures retained. Final required merged-tree checks are reported in the external integration result.
