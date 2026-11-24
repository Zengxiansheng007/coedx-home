# CR-20261116-006 - Semantic projection

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | fixed |
| Scope | references-and-assets / scripts-and-validation |
| Source | TAS-06 issue 127, parent 121 AC-009/010/021/022 |
| Baseline | bc4226cec89bbf90c32bed917111f7034b83f6eb; integrated 69149e4 |
| Author | Codex |
| Related Records | CR-20261116-003, CR-20261116-008 |

## Summary
Whole-claim comparison retains independent observations; one scalar data value uses a direct node.

## Context And Problem
Flattened text deduplication removed identical result text even when observation timing differed. Singleton data added an unnecessary child level.

## Sections Changed
| File | Section | Change Summary |
|---|---|---|
| scripts/review_expression.py | independent_checks | Compare complete projected claims; retain baseline visibility for feedback |
| scripts/scoped_review.py | shared renderer | Whole assertions and direct singleton data |
| scripts/test_semantic_projection.py | public tests | Synthetic announcement, approval, literal data, MD/native feedback |
| references/review-expression.md | rules and examples | Agent-owned source normalization, unknown retention, simple/complex data |
| references/source-semantics.md | authoring review | Consistent generation/change/recovery review |

## Decision And Alternatives
Reuse the single public renderer and existing source claims. No similarity classifier, field deletion list, new approval or business state machine. Existing source-semantics example remains valid; no standalone templates exist in this package.

## Detailed Change
Compare whole projected claims within each step only. Hidden internal assertions retain identity and provenance. A one-line data projection moves onto its parent; complex and unknown fields remain explicit. Literal action-like text is not executed or reinterpreted.

## Impact Analysis
Public generation, scoped review, feedback and recovery share this renderer. Legacy feedback mode retains historical layout. Neither native archive tests nor Python tests prove client acceptance or actual dialogue behavior.

## Validation Evidence
| Check | Command or Method | Result | Evidence |
|---|---|---|---|
| Red/green | unittest test_semantic_projection | pass, two captured red cases | external evidence/tas-06/red*.txt |
| Regression | unittest discover -p test_*.py | 191 passed before latest integration | external evidence/tas-06/green.txt |
| Integration affected tests | eight public suites | 35 passed | external evidence/tas-06/integration-tests.txt |
| Sensitive data | synthetic fixtures and diff inspection | no private source content added | scoped changes only |
| Skill validator | validate_create_skill --require-change-records | rejected on inherited fixture secret-patterns, CLI path parse, and mirror missing handoff reference | external evidence/tas-06/validator.txt |

## Safety And Privacy
Candidate-only. No business execution, global installation, remote publication or real private material used.

## Risks And Follow-up
Actual user dialogue and XMind client acceptance remain unverified. Whole semantic equivalence remains an Agent source-review decision; tests do not establish arbitrary-language equivalence. Root owns inherited mirror drift outside these files.

Refs: TAS-06 #127; TEST-AUTHORING-STAGE-20261116.
