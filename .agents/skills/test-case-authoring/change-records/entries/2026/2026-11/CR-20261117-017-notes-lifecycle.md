# CR-20261117-017 - Agent notes lifecycle and display

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | fixed |
| Scope | scripts-and-validation / references-and-assets / downstream-and-handoff |
| Source | user-authorized AC1–AC4; TAS-10/11/12 |
| Baseline | 9b9271f08d0bf09db6e8899d5d5d8f0643d31542 |
| Author | Codex |
| Related Records | CR-20261116-016; CR-20261116-015; CR-20261116-011 |

## Summary
Retire obsolete notes only for restored selected owners; bind every retained/generated section to its candidate location and version, and display known technical controls in Chinese.

## Context And Problem
The writer iterated only cases with notes, leaving stale sections after notes disappeared. Shared notes lacked an exact candidate location. Business projection helpers also formatted technical controls, constraining display changes.

## Sections Changed
| File | Section | Change Summary |
|---|---|---|
| scripts/module_handoff.py | writer and local display | Ready-only section lifecycle, candidate binding, overwrite protection, local labels/enums |
| scripts/review_projection.py | technical_notes | Optional Agent value/label formatter; original grouping unchanged |
| scripts/authoring.py, scoped_review.py, extension.py, dependencies.py | CLI save | Reuse writer-owned complete candidate save |
| scripts/test_notes_lifecycle.py, test_technical_notes.py | public seam tests | Synthetic lifecycle, blocked/manual preservation, source binding, enums and unchanged values |
| references/module-handoff-contract.md | current delivery | Markdown/user-import scope and source ownership |

## Decision And Alternatives
Reuse preflight, stable section markers, candidate.json and the existing public writer. No new candidate schema, materialized data file, source snapshot, index or second authority. Reject destructive same-directory partial updates before writes; a new sibling batch location preserves old source bindings.

## Detailed Change
Ready selected note-free owners retire only their generated section. Manual text and unselected/blocked sections survive. An empty generated shell is removed. Each note section carries a file URI plus JSON Pointer, content version and case semantic/data versions. The writer persists the complete original candidate before publishing notes and preserves existing equal JSON bytes. Technical display maps exact known control fields, retains keys/values and leaves actual inputs and unknown values unchanged. Pure render remains planned.

## Impact Analysis
Canonical TCA and identical mirror only. Shared _business_lines, feedback semantics, data identities/references and candidate versions are unchanged. CR016 remains intact. User imports current Markdown; historical native/client evidence stays historical.

## Validation Evidence
| Check | Command or Method | Result | Evidence |
|---|---|---|---|
| Public TDD | unittest test_notes_lifecycle test_technical_notes test_module_handoff | 17 passed; five reproduced red/green slices | external evidence/notes-lifecycle-fix/implementer/green-5.json and red/green records |
| Full repository | tools/checks.py --output-dir external-result-directory | All eight stages passed: workflow 67, verification 8, authoring 252, distribution 1; total 328 tests | external test-output/notes-lifecycle/checks/summary.json |
| Traceability and sensitive patterns | validate_create_skill.py --require-change-records | Rejected only for three inherited synthetic negative fixtures; P0=3/P1=0/P2=0; no new finding | external evidence/notes-lifecycle-fix/implementer/validator.json |
| Mirror and patch format | tools/checks.py copies; git diff --check | Identical package/mirror; clean whitespace | full-check copies.json; local command evidence |
| Preserved correction | red-5 test insertion and check launcher | Initial test insertion missed CRLF boundary; corrected actual red recorded. Node process global absent; no checks launched until corrected | red-5.json; red-5-corrected.json; launcher-correction.json |

Local results are candidate evidence. Private four-case acceptance and independent review are Root-owned; no new native client operation.

## Safety And Privacy
Synthetic fixtures only; no real paths or private business materials committed. No dependencies installed, global changes, remote writes or business execution.

## Risks And Follow-up
Applied candidate pending independent review and Root four-case acceptance. No new native XMind/client acceptance. Known inherited synthetic credential negative fixtures remain separate from actual secrets.

Refs: #131; #132; #133; local four-repair plan.

## Independent review repair R2 — 2026-11-17

Baseline: 81fca5bb551be908c07e7e2bb1ba091cba526c2d. Findings: standards P2 missing right-side intent comments and P3 duplicated case-marker construction; spec axis reported no product finding.

The writer now derives begin/end/pattern through one small case-marker helper shared by retirement, replacement and retained-source protection. SHA-256 input, marker bytes and regex behavior remain unchanged. New lifecycle and localization logic/tests explain their ownership and byte-preservation boundaries. No business projection, feedback, schema or source-data behavior changes.

This is review-stage refactoring of already passing behavior: six public lifecycle tests passed before edits; original R1 red/green evidence remains unchanged. Existing public writer seams cover retirement, last-note removal, mixed source bindings, blocked/manual retention, localization/zero-edit feedback, and refused destructive overwrite. No implementation-coupled helper test was added. Validation results follow below.

Application of writing-for-agents: the marker protocol has one code owner; this detail holds the repair rationale, while index/category pointers reference it. Status remains applied candidate pending independent review; historical validator negative-fixture findings are retained.

### R2 validation outcome

- Public lifecycle: 6/6 before and after refactor; external review-repair/baseline-public.json and lifecycle-regression.json.
- Required eight stages: all passed; workflow 67, verification 8, authoring 252, distribution 1 (328 tests total); external test-output/notes-lifecycle-review/checks-complete/summary.json.
- create-skill --require-change-records: rejected with exactly the inherited three synthetic secret-pattern fixtures, P0=3/P1=0/P2=0; affected fixture sources unchanged. No new finding; status remains applied, not globally validated. External review-repair/create-skill-validator.json and inherited-negative-fixtures.json.
- Canonical/mirror identical and git diff --check passed. Final record-only changes receive mirror and validator rechecks.
- First check attempt interrupted by a short node wait; partial records preserved. A subsequent observer timeout occurred after checks-complete had already finished successfully; persisted stage records, rather than in-memory observer state, establish completion. No failed evidence was overwritten.
- P2 annotations and P3 shared marker protocol are repaired; independent closure review remains with Root. No product or external acceptance claim.
