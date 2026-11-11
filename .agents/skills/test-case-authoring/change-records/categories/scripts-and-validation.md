# scripts-and-validation Change Ledger

## Purpose

Trace rule Q&A changes in scripts-and-validation.

## Outline

| Date | Change ID | Section | Change Type | Summary | Status |
|---|---|---|---|---|---|
| 2026-11-11 | CR-20261111-105 | Rule clarification | changed | Persist complete dialogue | applied |
| 2026-11-11 | CR-20261111-201 | Source semantics | fixed | Goal-bounded authoring and retained constraints | applied |

| 2026-11-11 | CR-20261111-202 | Aggregation and review repair | fixed | Preserve preparation and answer state | applied |

## Detailed Records

### CR-20261111-105 - Rule Q&A

- Section changed: rule clarification.
- Before: pure state and English labels.
- After: single Markdown event source and Chinese full questions.
- Why: issue 105 answer traceability.
- Impact: existing computation seams preserved.
- Validation: public regression; observed formal/provisional/deferred simulations and independent local integration review completed. Inherited validator findings remain open; no host acceptance.
- Detail record: [CR-20261111-105](../entries/2026/2026-11/CR-20261111-105-rule-qa.md).


### CR-20261111-201 - Source semantics

- Section changed: source interpretation and technical handoff.
- Before: generic source comparison; separate technical handoff dropped by conversion.
- After: explicit authoring checks and candidate-only technical constraints.
- Why: wrong data ownership cannot be repaired by rendering.
- Impact: existing candidate and presentation contracts; no business execution.
- Validation: 97 candidate tests passed; actual multi-turn correction and exact-version public review completed for three simulated cases. Historical missed questions and orchestration failures retained; no host acceptance.
- Detail record: [CR-20261111-201](../entries/2026/2026-11/CR-20261111-201-source-semantics.md).

### CR-20261111-202 - Aggregation
- Section changed: rendering and feedback projection.
- Before: repeated per-case trees.
- After: semantic paths and shared preparation with source ownership.
- Why: keep bulk reviews readable without changing execution meaning.
- Impact: batch, scoped and feedback public interfaces.
- Validation: 99 public regressions passed; actual XMind r1 import and complete 127-topic comparison passed. Independent code review and inherited validator findings remain.
- Detail record: [CR-20261111-202](../entries/2026/2026-11/CR-20261111-202-aggregation.md).

PRE-02 review repair: answered/non-stale questions are historical, explicit empty-preparation notes stay in their group. Public regression and affected client sample are recorded in CR-20261111-202.
