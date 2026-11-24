# CR-20261116-009 - Ordered complete cross-module references

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | fixed |
| Scope | core-skill-md, references-and-assets, scripts-and-validation |
| Source | TAS-09 #130, parent #121 AC-016/021 |
| Baseline | bc4226ce integration |
| Author | Codex |
| Related Records | CR-20261116-008 |

## Summary
Keep independently complete references in real operation order with endpoint selection.

## Context And Problem
Legacy dependencies forced P0 identity and special pre/post placement; unsuitable endpoints forced new P0 creation.

## Sections Changed
| File | Section | Change Summary |
|---|---|---|
| scripts/dependencies.py | review_dependencies | Ordered placement, alternative or complete inline operations, local replacement |
| scripts/cross_module_references.py | public resolver | Actual whole source and data digest, drift checks |
| scripts/test_cross_module_references.py | public tests | Ordered non-P0, payment mismatch, approval change/recovery, inline and stale sources |
| scripts/test_dependencies.py | endpoint expectation | Updated superseded route |
| SKILL.md | dependencies | Whole independent references and qualification boundary |
| references/dependency-contract.md | entry and recovery | Actual source and endpoint contract |

## Decision And Alternatives
Evolve existing review boundary; no second business state or persistent expansion. Preserve explicit legacy pre/post requests. Do not alter extension qualification.

## Detailed Change
References retain independent identities and full target content. Incompatible endpoints select a complete alternative or authored inline operations. Unknown endpoints require clarification. Source digest includes actual case and used data; shared source edits invalidate the reference even without version-label updates.

## Impact Analysis
Generation and changes use existing review_dependencies. Recovery resolver is public and will compose with TAS-11 completeness. Original source and independent cases remain unchanged. No execution-layer changes.

## Validation Evidence
| Check | Command or Method | Result | Evidence |
|---|---|---|---|
| TDD | Public unittest | Red before implementation, then green | External evidence/tas-09/red-01.txt, red-02.txt, regression.txt |
| Regression | unittest cross_module_references dependencies recovery extension | 31 passed | External regression.txt |
| Skill validation | validate_create_skill --require-change-records | Run before delivery; inherited package findings separately reported | External validator.txt |
| Sensitive data | Changed-file review | Synthetic fixtures only; no credentials or private source data | Diff review |
| Actual dialogue/client/business | Not run | Unverified, candidate only | No actual acceptance claim |

## Safety And Privacy
No global installation, external calls, business execution, publishing or source-catalog mutation. Fixture decisions explicitly simulated.

## Risks And Follow-up
Caller must reload current catalog; cached content cannot prove freshness. TAS-11 owns composed nested reference and cycle validation. Actual skill dialogue and client acceptance remain unverified.
