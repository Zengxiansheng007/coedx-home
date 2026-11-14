# downstream-and-handoff Change Ledger

## Purpose

Track source semantics and technical handoff changes in this category.

## Outline

| Date | Change ID | Section | Change Type | Summary | Status |
|---|---|---|---|---|---|
| 2026-11-11 | CR-20261111-201 | Source semantics | fixed | Goal-bounded authoring and retained constraints | applied |

## Detailed Records

### CR-20261111-201 - Source semantics

- Section changed: source interpretation and technical handoff.
- Before: generic source comparison; separate technical handoff dropped by conversion.
- After: explicit authoring checks and candidate-only technical constraints.
- Why: wrong data ownership cannot be repaired by rendering.
- Impact: existing candidate and presentation contracts; no business execution.
- Validation: 97 candidate tests passed; actual multi-turn correction and exact-version public review completed for three simulated cases. Historical missed questions and orchestration failures retained; no host acceptance.
- Detail record: [CR-20261111-201](../entries/2026/2026-11/CR-20261111-201-source-semantics.md).

## CR-20261114-001 — Module handoff partition

- Section changed: review projection and feedback.
- Before: hidden provenance and repeated process metadata.
- After: direct-owner module instruction branches; business applicability remains visible.
- Why: #113 / REQ-015-016 / AC-023-024.
- Impact: scoped, ordinary and chat views; supported markdown/native feedback.
- Validation: public red/green; 149 synthetic regressions passed; real client unverified.
- Detail record: [CR-20261114-001](../entries/2026/2026-11/CR-20261114-001-module-handoff.md).
