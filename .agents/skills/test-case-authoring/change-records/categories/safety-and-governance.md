# safety-and-governance Change Ledger

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
- Validation: 97 synthetic tests pass; independent multi-turn behavior pending.
- Detail record: [CR-20261111-201](../entries/2026/2026-11/CR-20261111-201-source-semantics.md).
