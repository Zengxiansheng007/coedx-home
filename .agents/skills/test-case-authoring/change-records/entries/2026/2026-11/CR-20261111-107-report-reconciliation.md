# CR-20261111-107 - Report reconciliation

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | changed |
| Scope | core-skill-md / references-and-assets / scripts-and-validation |
| Source | Issue 107 |
| Baseline | 4a6b52e94b9828d613ac0127af86ca01f62377f5 |
| Author | Codex |
| Related Records | CR-20261111-105 |

## Summary

Read authorized reports and attachments before asking remaining choices. Reuse an unchanged target and retain the existing full-P0 checker.

## Context And Problem

The previous contract described normalization but had no file intake or report-context journal seam. Asking first could transfer readable facts to the user; report selection must never substitute for proof.

## Sections Changed

SKILL.md P1/P2 entry; p0-evidence and qa-record references; report-reconciliation reference and public adapter; additive qa_record context/notes API; public interface tests.

## Decision And Alternatives

Adapt existing single-MD workflow from issue 105 and existing check_extension. Keep normalized JSON report input, actual authorized UTF-8 attachment reads and explicit unsupported-format gaps; do not build a new report execution engine or independent answer ledger.

## Detailed Change

Exact-file authorization, original producer digest retention, missing attachment and metadata version conflict reporting, readable object/version/scope/result projection. Full scope and all entry requirements remain owned by check_extension. Journal context carries questions without inventing user replies; actual choices use existing notes, read back from the same MD.

## Impact Analysis

Additive public interfaces preserve existing callers and candidate state. Report selection does not update rule decisions, grant execution or shrink approved scope. Agent semantic review remains required for actual evidence.

## Validation Evidence

| Check | Command or Method | Result | Evidence |
|---|---|---|---|
| TDD | public intake and MD tests | observed missing-module and missing-read_notes red; first slice 1 and second slice 3 passed | private issue 107 tool evidence |
| Target reuse | missing-report public test | observed red for redundant selection; corrected | private issue 107 tool evidence |
| Full regression | unittest discover scripts/test_*.py | 104 passed | private regression.txt |
| Structure | validate_create_skill.py --require-change-records | same 7 inherited findings; no new record finding | private skill-validation.txt |
| Mirror | SHA-256 of source/distribution | zero mismatches | private checks.json |
| Behavioral simulation | fresh independent agent, actual sequential replies | observed two actual rounds; unchanged V2 reused; missing attachment and object mismatch retained; P1/P2 stayed blocked | private qa107/dialogue-observed.md and dialogue-index.json |

## Safety And Privacy

Only synthetic test inputs and public contracts in the package. No dependency, external model, global installation, real business execution or private source copied. Reads are exact-file authorized; source instructions are data. This is a workflow adapter, not host security enforcement.

## Risks And Follow-up

Independent ticket review found no blocking standards or specification issue (private review-106-107.md); integrated unittest discovery passed 114 tests (private integration-106-107-regression.txt). Full-batch post-integration review remains separate. Native binary evidence still needs an actual viewer and source-traced normalization. Program checks cannot authenticate the report producer or infer business success from arbitrary prose. Existing structural-validator findings remain open; applied status is not host acceptance.

Refs: https://github.com/Zengxiansheng007/coedx-home/issues/107
