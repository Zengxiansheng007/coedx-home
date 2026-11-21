# CR-20260928-001 - Trusted Gate Contract

| Field | Value |
|---|---|
| Status | validated |
| Target Skill | create-skill |
| Change Type | governance / validation |
| Scope | core-skill-md / references-and-assets / scripts-and-validation / safety-and-governance / downstream-and-handoff |
| Source | User-confirmed Grill review and direct global-skill update authorization on 2026-09-28 |
| Baseline | Global `SKILL.md` SHA-256 `63322AFCBBBE5C626ED13F225CD04F2279DF784CAD15D5A43A2037DD4FAACEB8`; validator `D434B98F5263E63B6EC11CED50678066C56A5528D4F0EE96FE798CE7B98E8D97`; workspace copy before edits |
| Author | Codex |
| Related Records | CR-20260809-001 |

## Summary

Separate Agent-authored Skill candidates from trusted delivery and runtime acceptance. Add a structured mandatory-gate declaration and static validation that cannot claim actual enforcement.

## Context And Problem

The prior workflow told the Agent to run a validator and deliver. The validator returned `accepted-with-constraints` when no P0/P1 findings existed and exited successfully for P1-only `review-required` results. Neither output proved that a trusted host controlled installation or every path to a protected effect. The user confirmed nine design decisions in `<workspace>\grill-create-skill-gates-20260928.json`.

## Sections Changed

| File | Section | Change Summary |
|---|---|---|
| `SKILL.md` | Operating Rules / Workflow / Decision Rules / Validation / Deliver | Require candidate-only Agent output, gate mapping, host promotion, and runtime boundaries. |
| `references/mandatory-gate-contract.md` | Entire file | Define declaration shape, decision authority, coverage, receipt ownership, and first isolated test effect. |
| `references/skill-brief-template.md` | Brief fields | Capture protected effects, conditions, owners, alternate paths, and evidence. |
| `references/skill-quality-gates.md` | G4 / G4A | Add enforceability checks and host-owned acceptance. |
| `references/skill-artifact-contract.md` | Package / Adoption Status / Evidence | Reserve `accepted` for trusted host receipts and classify local success as candidate only. |
| `scripts/validate_create_skill.py` | Gate contract validation / Result / CLI | Check declaration structure, return nonzero for P1, and never emit accepted status. |
| `scripts/test_create_skill.py` | Regression cases | Check missing, valid, and fail-open contract cases plus P1 exit behavior. |

## Decision And Alternatives

Use a host-owned promotion and protected-action entry with independent permission control. Keep `gate-contract.json` as an untrusted declaration. An Agent-invoked script alone cannot make its own execution mandatory, and a user-disableable Hook does not prove all reachable paths are covered.

## Detailed Change

For host promotion, require a `gate-contract.json` declaration even when its mode claims no mandatory gates. The local validator checks its shape and reports `validated-candidate` only with no P0/P1 findings. A trusted host must independently review package bytes, effect inventory, alternate paths, approvals, and current-action evidence before installing or issuing an acceptance receipt. The first runtime acceptance effect is an isolated protected file write; it does not qualify other effects.

## Impact Analysis

Existing callers that treat `accepted-with-constraints` or a P1 exit code of zero as approval must use the new candidate and host-receipt distinction. Existing Skills are not retroactively changed. The create-skill package does not itself supply a controlled Codex host, installation privilege separation, or universal runtime coverage; those remain separate host work and cannot be represented as validated by this change.

## Validation Evidence

| Check | Command or Method | Result | Evidence |
|---|---|---|---|
| Candidate deterministic tests | `python scripts/test_create_skill.py` | Passed | `ok: create-skill tests passed` on workspace copy. |
| Candidate structure and records | `python -B scripts/validate_create_skill.py . --require-change-records` | Passed | P0/P1/P2 = 0 in workspace copy and global directory. |
| Sensitive-data scan | Validator's package-wide secret-pattern check | Passed | No sensitive-data finding in candidate or global validation. |
| Global tests | `python -B scripts/test_create_skill.py` | Passed | `ok: create-skill tests passed` in global directory. |
| Global readback | Final staged-versus-global SHA-256 comparison | Passed | 14 files, 0 mismatches in `<workspace>\create-skill-final-readback-20260928-v2.json`; runtime acceptance remains unverified. |

## Safety And Privacy

No credentials, account data, production target, or external call is introduced. The user explicitly authorized updating the global `create-skill` directory. The workspace copy preserves the source baseline until deployment is verified.

## Risks And Follow-up

- A real controlled Codex execution host and its isolated-file-write bypass tests remain to be built and accepted separately. Until then, candidate Skills cannot claim verified mandatory runtime enforcement or host-issued `accepted` status.
- Static validation cannot prove that the Agent listed every mandatory condition or alternate path. The trusted host must independently inspect those claims.
- P1 now exits nonzero; downstream callers that expected zero for review-required results need adjustment before using this validator as a gate.

Refs: `<workspace>\grill-create-skill-gates-20260928.json`, `<workspace>\grill-create-skill-gates-20260928.html`.
