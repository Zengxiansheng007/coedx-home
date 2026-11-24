# CR-20261116-014 - Final visible duplicate retention

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | fixed |
| Scope | scripts-and-validation / references-and-assets |
| Source | final Spec recheck P2; REQ-008/009, AC-009/010 |
| Baseline | 2a18a475aada9a1ec422703d120a049afded0f28 |
| Author | Codex |
| Related Records | CR-20261116-013 |

## Summary
Reject duplicate assessments whose declared equivalent loses every visible business expression.

## Context And Problem
Same-owner existence checks allowed deadline self-reference, mutually deleting duplicates, and references moved to technical notes. Original JSON retention alone does not preserve review meaning.

## Sections Changed
| File | Section | Change Summary |
|---|---|---|
| scripts/review_projection.py | whole assessment validation | Trace exact target through both existing business renderings |
| scripts/test_projection_retention.py | public API tests | Self/cycle/technical rejection, visible and readable endpoints, graded titles, source drift and unchanged identity |
| references/source-assessed-display.md | endpoint guidance | Direct visible endpoint and TAS-12 review evidence |

## Decision And Alternatives
Reuse baseline-bound rendering probes already used by feedback. No field blacklist, natural-language equivalence algorithm, approval state or second packet. Invisible intermediate duplicate chains are conservatively rejected; callers can directly target their retained endpoint. Source title/priority remain eligible when actually generated visibly.

## Detailed Change
Validate after assembling all decisions. A unique temporary marker traces the exact equivalent scalar through human and XMind business views; readable text is traced at its existing rendering source. Copies isolate probes; original cases, data, source binding and pending status are untouched. Existing owner drift invalidates assessment.

## Impact Analysis
Local package and identical mirror only. Existing feedback/restoration architecture unchanged. Public projection and drift/feedback tests cover affected behavior; actual sources/client and approval remain separate.

## Validation Evidence
| Check | Command or Method | Result | Evidence |
|---|---|---|---|
| Red-green | unittest test_projection_retention | three missing-rejection failures before change, pass after | evidence/projection-retention-fix/red.txt and green.txt outside repo |
| Targeted regression | retention plus existing projection feedback/drift | seven tests passed | retention-regression.txt |
| Frozen package checks | tools/checks.py | all eight checks passed | checks/summary.json |
| Skill traceability | validate_create_skill.py --require-change-records | rejected: exactly three inherited synthetic credential fixtures; P1=0, P2=0; fixtures unchanged | skill-validation.txt |

## Safety And Privacy
Synthetic fixture only; no private business files read or copied. Validator and existing credential negative tests unchanged. No install, business action, global update, remote publish or Root state change.

## Risks And Follow-up
Candidate only. Source equivalence still requires human/Agent semantic review. Actual TAS-12 source-assessed draft, real user feedback and XMind acceptance require separate evidence. This code proves target visibility, not equivalence truth.

Refs: #121; REQ-008; REQ-009; AC-009; AC-010.
