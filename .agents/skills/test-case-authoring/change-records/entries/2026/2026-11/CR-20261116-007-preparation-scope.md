# CR-20261116-007 - Reviewed preparation applicability

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | fixed |
| Scope | core-skill-md, references-and-assets, scripts-and-validation |
| Source | TAS-07 issue 128; AC-011/012/013/021 |
| Baseline | 69149e48 |
| Author | Codex |
| Related Records | CR-20261116-005 |

## Summary
Replace automatic equivalence extraction with explicitly reviewed full-group scope.

## Context And Problem
Identical or singleton preparation was always extracted without broad applicability assessment.

## Sections Changed
| File | Section | Change Summary |
|---|---|---|
| SKILL.md | Aggregation entry | Require reviewed scope on all rendering entries |
| references/aggregation-contract.md | Scope | Review, exceptions, revisions and lifecycle |
| scripts/preparation_scope.py | Public review adapter | Explicit source binding and invalidation |
| scripts/aggregation.py | Projection | Only reviewed extraction; visible scope metadata |
| scripts/scoped_review.py | Candidate and baseline | Carry scope without widening selection |
| scripts/test_preparation_scope.py | Public tests | Generated artifacts, revisions, feedback and lifecycle |
| scripts/test_aggregation.py | Synthetic fixture | Explicit simulated approval replaces old extraction assumption |

## Decision And Alternatives
Reuse existing candidate/feedback flow. No ratio classifier, artificial groups or new state authority.

## Detailed Change
Full existing module/business group members and exceptions are enumerated. Per-case source hashes bind preparation, conditions and data. New/moved/deleted/changed members remain inline. Unreviewed partial-only preparation remains in steps.

## Impact Analysis
Public batch, scoped rendering and JSON resume share the check. Scalar feedback remains proposals for every owner. Existing obligations and data remain complete; rendering executes no preparation.

## Validation Evidence
| Check | Command or Method | Result | Evidence |
|---|---|---|---|
| TDD | Public generated scope | Original seven operations collapsed to one; now seven inline without approval | External tas-07 red-unreviewed.txt |
| Regression | unittest discover | 200 passed before final extra partial/deletion test | External tas-07 suite-initial.txt |
| Targeted | unittest preparation/aggregation/hierarchy/scoped | See final targeted log | External tas-07 targeted-final.txt |
| Static validator | validate_create_skill --require-change-records | See recorded findings; no runtime promotion | External tas-07 validator.txt |
| Privacy | Changed files inspected | Synthetic source only; no private material | External tas-07 completion.md |

## Safety And Privacy
No real source, credentials, global install, remote publication or business execution.

## Risks And Follow-up
Candidate only. A supplied reply string does not establish actual approval; source assessment remains the agent/user workflow duty. Actual user dialogue, real-client XMind and business acceptance are unverified. Partial display conservatively keeps preparation inline.

Refs: [Aggregation contract](../../../../references/aggregation-contract.md).
