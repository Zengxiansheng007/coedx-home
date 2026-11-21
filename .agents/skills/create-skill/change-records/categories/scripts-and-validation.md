# Scripts And Validation Change Ledger

## Purpose

Record changes that affect validators, tests, deterministic scripts, command contracts, and validation evidence.

## Outline

| Date | Change ID | Section | Change Type | Summary | Status |
|---|---|---|---|---|---|
| 2026-09-28 | CR-20260928-001 | validate_create_skill.py / test_create_skill.py | validation | Validate gate declarations and return nonzero for P1 findings. | validated |
| 2026-08-09 | CR-20260809-001 | validate_create_skill.py / test_create_skill.py | validation | Add optional required change-record validation and regression tests. | validated |

## Detailed Records

### CR-20260928-001 - candidate-gate-validator

- Section changed: validator and deterministic tests.
- Before: No gate-contract check; `accepted-with-constraints` status and P1 exit code zero could be mistaken for acceptance.
- After: Contract-shape checks, candidate-only status, explicit unverified acceptance field, and P1 nonzero exit.
- Why: Static evidence must fail closed for host promotion without claiming runtime enforcement.
- Impact: Callers must distinguish local candidate validation from trusted host acceptance.
- Validation: Global `python -B scripts/test_create_skill.py` passed; validator P0/P1/P2=0 and 14-file hash readback matched.
- Detail record: ../entries/2026/2026-09/CR-20260928-001-trusted-gate-contract.md

### CR-20260809-001 - change-record-validator

- Section changed: validator and deterministic tests.
- Before: Validator checked frontmatter, links, resource folders, sensitive patterns, and dangerous commands, but not change-record artifacts.
- After: Validator checks record structure when present and supports `--require-change-records` for existing-skill updates.
- Why: PRD requires records to be objectively checkable rather than only described.
- Impact: Future file-changing updates can fail validation when traceability artifacts are missing or malformed.
- Validation: Workspace copy passed `validate_create_skill.py --require-change-records` and `test_create_skill.py`.
- Detail record: ../entries/2026/2026-08/CR-20260809-001-traceable-change-records.md

