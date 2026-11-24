# CR-20261117-104 - Scope lifecycle

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | fixed |
| Scope | core-skill-md / references-and-assets / scripts-and-validation / downstream-and-handoff |
| Source | #134 and #138 |
| Baseline | ebed8ae1a5589165f07f0c66a1f7e87293e37261 |
| Author | Codex |
| Related Records | CR-20261117-102, CR-20261117-103 |

## Summary
Reviewed module authoring scope preserves business groups; full-parent provenance and local per-item invalidation survive selection, saving and restoration.

## Context And Problem
Subset membership was mistaken for a complete group; one changed member invalidated all owners; operation IDs collided across real business groups.

## Sections Changed
| File | Section | Change Summary |
|---|---|---|
| scripts/preparation_scope.py | review and membership | explicit module scope, business-path identity, local bindings and actual parent checks |
| scripts/aggregation.py | projection | source context and current exception names |
| scripts/scoped_review.py | render | preserve scope-pending actions and valid definitions |
| scripts/restoration.py | preflight | actual full source and localized blockers |
| scripts/module_handoff.py | writer | retain partial-scope review content while ready cases alone update notes |
| scripts/test_scope_lifecycle.py | public seams | meaningful lifecycle and artifact regression |
| SKILL.md, references | contract | bounded scope and partial copy obligations |

## Decision And Alternatives
Reuse preparation_scopes and initial_copy_baseline. No copied full parent or new business ledger. Explicit module scope is a source-reviewed option, never a grouping inference. Existing business/default legacy semantics remain compatible.

## Detailed Change
Each direction/item/member is checked independently; unresolved obligations remain inspectable and incomplete. Source copies require exact actual parent version/digest; old sources and approvals are preserved.

## Impact Analysis
Rendering, save and restoration consumers share parent checks. Existing exclusions stay in one record. No execution layer, global skill, material catalog or external service is changed.

## Validation Evidence
Public red/green tests and full repository checks are recorded in the ticket evidence. Existing create-skill negative-fixture findings are disclosed separately; this record remains applied pending independent acceptance.

## Safety And Privacy
Synthetic fixtures only. Sensitive-data scan uses the existing validator; no credentials or private material copied.

## Risks And Follow-up
Actual user draft review, XMind client and business execution remain outside these public-interface tests. Missing parent intentionally blocks affected inherited obligations. Local Python is not an independently enforced runtime security gate.

Refs: #134, #138
