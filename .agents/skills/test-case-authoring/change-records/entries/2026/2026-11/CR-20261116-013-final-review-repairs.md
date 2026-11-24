# CR-20261116-013 - Final review repairs

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | fixed |
| Scope | core-skill-md / references-and-assets / scripts-and-validation / downstream-and-handoff |
| Source | final Spec review and observed native-client header failure |
| Baseline | 6d50281c1ad71455b71ba729ee19e355c2396ff4 |
| Author | Codex |
| Related Records | CR-20261116-006, CR-20261116-007, CR-20261116-009, CR-20261116-011 |

## Summary
Fix reviewed ancestor preparation scopes, nested valid P0 references, explicit source-assessed display partition and bound native header links.

## Context And Problem
The final review found leaf-only preparation, premature completeness checks and repeated governance in business prose. A separate actual client observation showed a self-authored Markdown header link returning as title plus href.

## Sections Changed
| File | Section | Change Summary |
|---|---|---|
| scripts/preparation_scope.py, aggregation.py | reviewed scope | Existing ancestor membership and original child paths |
| scripts/restoration.py, dependencies.py | whole-case reconstruction | Merge source definitions without business conflict masking; expand before completeness |
| scripts/review_projection.py, scoped_review.py, module_handoff.py | source assessment | Exact owner-bound leaf classification and preserved original values |
| scripts/xmind_feedback.py | native parsing | Exact current generated single header link only |
| scripts/test_final_repairs.py | public behavior | Synthetic positive, stale, conflict, feedback and annotation checks |
| SKILL.md, references | entry guidance | Apply assessment on actual sources and distinguish review/client/business acceptance |

## Decision And Alternatives
Reuse existing candidates, rendering and module notes. No semantic word blacklist, renderer guessing, rewritten business values, additional approval state, new project index or globally installed runtime changes. Unknown leaves remain visible. Source assessment is agent judgement, not an independently enforced approval gate.

## Detailed Change
Ancestor scope requires complete existing descendant membership and actual review. Full path/data/conditions/frequency bindings invalidate moved/new cases. Cross-module restoration retains current-source checking and complete operations. Display assessment binds exact owner bytes and source version, restores prose on drift, preserves original records and limits feedback probes to original display visibility. Native links require matching root/version/header and exact target; unsupported forms stay pending.

## Impact Analysis
All changes remain in the candidate package and its mirror. Original source, qualification gates, review_status and business execution stay unchanged. Full regression exposed legacy selection records lacking action, indistinguishable case identity after unassessed removal, and presentation-only definition changes; those were repaired before freezing. Selection partition is now explicit, never automatic.

## Validation Evidence
| Check | Command or Method | Result | Evidence |
|---|---|---|---|
| Red-green | public unittest seams | six targeted behaviors passed | local final-review-repairs red/green logs |
| Whole regression | tools/checks.py | all eight checks passed | local final-review-repairs/checks |
| Skill traceability | validate_create_skill.py --require-change-records | rejected only on three inherited synthetic credential negative-test strings; no P1/P2 findings | local skill-validation.txt |
| Client/business | independent Root evidence | not claimed by implementation | real baseline preserved outside repository |

## Safety And Privacy
Only synthetic tests committed. No private four-case source, archive, credentials or local business material copied. Historical synthetic credential detector findings remain unchanged and require separate manual explanation.

## Risks And Follow-up
Candidate only. Root must perform independent review and actual-client verification, regenerate a new reviewed source-assessed trial version without overwriting v1. Multiple native header links remain unsupported rather than guessed. Semantic correctness of an assessment must be reviewed against source.

Refs: #121; REQ-008 through REQ-017; AC-010 through AC-023.
