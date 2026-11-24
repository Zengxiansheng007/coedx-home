# CR-20261116-008 - Whole-step semantic consistency

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | fixed |
| Scope | references-and-assets / scripts-and-validation / safety-and-governance |
| Source | TAS-08 issue 129; REQ-012/017; AC-014/015/021 |
| Baseline | 093ee090594368f174c2723d68ad9737d1e5de63 |
| Author | Codex |
| Related Records | CR-20261115-003, CR-20261115-004, CR-20261115-005, CR-20261115-006 |

## Summary

Reuse existing whole-step selection, reconstruction, feedback and reviewed shared-definition update. Repair three demonstrated consistency gaps without replacing the established candidate workflow.

## Context And Problem

Recursive metadata removal erased nested business object identities. Shared operation whitespace was treated as a business change despite local feedback treating it as formatting. A data edit shared by displayed P0 and P1/P2 could mutate the source without an explicit shared proposal.

## Sections Changed

| File | Section | Change Summary |
|---|---|---|
| scripts/step_reuse.py | semantic signature | Strip only declared record metadata; retain nested objects; ignore outer operation whitespace |
| scripts/local_step_feedback.py | materialize_data | Refuse mixed P0 and P1/P2 data edits before application |
| scripts/test_step_reuse.py | public generation | Distinct step/data/assertion business identities retain full target steps |
| scripts/test_local_step_feedback.py | public feedback | Shared data cannot silently alter displayed P0 |
| scripts/test_shared_step_feedback.py | public proposal | Outer whitespace preserves business review scope |
| references/step-reuse.md | consistency corrections | Same rule across generation, feedback and reconstruction |

## Decision And Alternatives

Retain known public interfaces and the existing shared-change impact assessment. Limit normalization to operation outer whitespace; never normalize literal data values or assertion text. Block mixed-owner data edits rather than invent a local binding or infer P0 authority from ambiguous feedback.

## Detailed Change

Metadata is non-business only at the step, data record and assertion record levels. Nested id/source/basis leaves remain comparison inputs. Shared formatting uses the same signature as selection and recovery. Before materializing data owners, reject a binding consumed by both P0 and P1/P2 and route it through explicit shared-change review.

## Impact Analysis

Complete independent steps, generated-value bindings, original ordering and endpoints, local copies, historical snapshots, exact proposal review and P0-only feedback retain their existing contracts. Existing saved references that relied on discarded nested identities may now fail validation and need source reassessment; they are not silently migrated. Original input materials and global installed skills are untouched. Canonical package and repository mirror carry identical files.

## Validation Evidence

| Check | Command or Method | Result | Evidence |
|---|---|---|---|
| Public regression red | unittest focused new tests | All three gaps reproduced before fixes | external TAS-08 red logs |
| Whole-step and feedback green | python -X utf8 -B -m unittest test_step_reuse test_local_step_feedback test_shared_step_feedback | 23 passed | external TAS-08 green-reuse.txt |
| Broader regression | unittest discover -p test_*.py | 184 passed | external TAS-08 full-regression.txt |
| Skill structure | validate_create_skill.py --require-change-records | Rejected: 7 inherited findings (3 P0 / 3 P1 / 1 P2); no change-record findings | external TAS-08 validator.txt |
| Sensitive data | Reviewed exact changed files | Synthetic identifiers only; no real business material or credentials added | exact diff review |

## Safety And Privacy

Candidate-only local behavior. Simulated replies remain explicitly labeled. No live UI, model, business submission, global installation, remote publication or original data edits.

## Risks And Follow-up

Actual Skill dialogue and XMind client acceptance remain unverified for this ticket. Public-interface regression does not prove those layers. Existing inherited validator findings remain separately reported. Integration and independent acceptance stay with Root.

Refs: issue 129; parent 121; TEST-AUTHORING-STAGE-20261116.
