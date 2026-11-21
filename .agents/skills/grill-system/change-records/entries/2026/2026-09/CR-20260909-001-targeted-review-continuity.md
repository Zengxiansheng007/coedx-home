# CR-20260909-001 - Targeted Review Continuity

| Field | Value |
|---|---|
| Status | validated |
| Target Skill | grill-system |
| Change Type | fixed / governance / validation |
| Scope | core-skill-md / references-and-assets / scripts-and-validation / safety-and-governance / downstream-and-handoff |
| Source | User approval on 2026-09-09: only substantive changes, conflicts or new major risks reopen related questions |
| Baseline | 38-file SHA-256 baseline and five passing existing checks retained in the local task evidence |
| Author | Codex |
| Related Records | CR-20260906-005 |

## Summary

Prevent format-only conversion and pending technical qualification from resetting
closed requirements. Retain scoped write authorization and independent readiness gates.

## Context And Problem

A completed direction review was incorrectly projected as requirements-review during
Markdown conversion. Existing local reopen behavior did not tell callers clearly
enough when not to invoke it.

## Sections Changed

| File | Section | Change Summary |
|---|---|---|
| SKILL.md | Operating Rules / Workflow / Validation | Required continuity contract and regression command |
| references/review-continuity.md | All | Triggers, non-triggers, impact record and separate statuses |
| references/routing-policy.md | Entry | Avoid automatic upstream re-interview |
| references/grill-session-contract.md | Active V2 | Preserve authority and implementation boundary |
| references/phase-boundary-contract.md | Runtime boundary | Explicit caller classification; no interface change |
| references/downstream-skill-map.md | Do Not Route | Downstream design is not upstream reset |
| assets/fixtures/review-continuity.json | 12 cases | Materiality and routing expectations |
| scripts/test_review_continuity.py | Three tests | Policy coverage and existing runtime invariants |

## Decision And Alternatives

Strengthen reviewer instructions and verify existing runtime behavior rather than
inventing an automatic semantic classifier or changing the public reopen interface.
Whole-review scope requires evidenced cross-cutting impact and explicit agreement.

## Detailed Change

Only substantive-requirement-change, evidenced-conflict or new-major-risk qualifies.
Keep prior closure, unrelated decisions and receipts; classify unknown impact before
continuing dependent work. A consumed writing batch is never revived by formatting.

## Impact Analysis

No production runtime, schema, external Agent or other installed Skill changes.
Development-system and write-prd callers must consume this continuity contract;
their installed packages are outside this approval. Historical reports stay unchanged.

## Validation Evidence

| Check | Command or Method | Result | Evidence |
|---|---|---|---|
| Baseline | Three existing suites + template + structure/change records | passed | task evidence/baseline.json |
| Candidate | Same checks + test_review_continuity.py | passed after fixture correction | task evidence/candidate-repaired.json; initial failed candidate.json retained |
| Installed | Exact 15-file change readback + six checks | passed | task evidence/install-receipt.json and installed.json |
| Privacy | Changed-text scan, no credential or private URL input | passed within documented scan limits | task evidence/security-scan.json |

The initial focused test used a shallow copy and accidentally shared two question
history lists. Only the synthetic fixture was corrected to deepcopy; runtime code
was unchanged. Final ledger status is recorded after actual installed validation.

## Safety And Privacy

Only user-approved global grill-system paths may receive validated changes after
backup and source-drift checks. No publish, model loading, D-drive writes or deletes.

## Risks And Follow-up

This is a workflow rule, not an OS barrier or semantic truth detector. Fixture checks
cannot prove every future agent will classify evidence correctly. Existing runtime
reason strings remain caller-supplied. Apply schema/runtime evolution only under a
separate requirement if a machine-enforced impact classifier is later requested.

Refs: references/review-continuity.md; local task scope.json and skill-baseline.json.
