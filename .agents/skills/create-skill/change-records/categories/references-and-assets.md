# References And Assets Change Ledger

## Purpose

Record changes that affect `references/`, `assets/`, reusable templates, rubrics, schemas, or long-form guidance.

## Outline

| Date | Change ID | Section | Change Type | Summary | Status |
|---|---|---|---|---|---|
| 2026-09-28 | CR-20260928-001 | Mandatory gate / brief / quality / artifact references | governance | Add gate declaration and host acceptance guidance. | validated |
| 2026-08-09 | CR-20260809-001 | references/change-record-traceability.md | added | Add the detailed traceability contract and Markdown templates. | validated |

## Detailed Records

### CR-20260928-001 - gate-contract-references

- Section changed: `references/mandatory-gate-contract.md`, `skill-brief-template.md`, `skill-quality-gates.md`, and `skill-artifact-contract.md`.
- Before: Quality and adoption status were mostly prose and local report fields.
- After: References distinguish untrusted declarations, candidate validation, host receipts, per-action checks, and effect-scoped coverage.
- Why: Prevent an Agent-written package from certifying its own gate.
- Impact: Host promotion requires an explicit gate declaration and independent coverage review.
- Validation: Global focused tests and structure checks passed; 14-file hash readback matched.
- Detail record: ../entries/2026/2026-09/CR-20260928-001-trusted-gate-contract.md

### CR-20260809-001 - traceability-reference

- Section changed: `references/change-record-traceability.md`.
- Before: Traceability rules were only present in the generated PRD.
- After: The skill package contains directly linked operating guidance for record artifacts, categories, detail template, statuses, and final response contract.
- Why: `SKILL.md` should stay concise while long rules live in `references/`.
- Impact: Future agents can apply the PRD-backed record system without bloating `SKILL.md`.
- Validation: Reference link resolves from `SKILL.md`.
- Detail record: ../entries/2026/2026-08/CR-20260809-001-traceable-change-records.md

