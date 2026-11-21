# CR-20260809-001 - Traceable Change Records

| Field | Value |
|---|---|
| Status | validated |
| Target Skill | create-skill |
| Change Type | governance / validation |
| Scope | core-skill-md / references-and-assets / scripts-and-validation / safety-and-governance |
| Source | user request and final PRD |
| Baseline | `validate_create_skill.py` accepted-with-constraints; `test_create_skill.py` passed before workspace-copy edits |
| Author | Codex |
| Related Records | none |

## Summary

Add PRD-backed traceable change-record behavior to `create-skill`, including concise workflow rules, detailed reference guidance, validator support, regression tests, and a self-record for this update.

## Context And Problem

The final PRD requires `create-skill` to produce governable change records whenever it modifies an existing skill. A single changelog file was rejected as too hard to govern over time. The target design uses an index, category ledgers, and dated detail records.

## Sections Changed

| File | Section | Change Summary |
|---|---|---|
| `SKILL.md` | Operating Rules | Added mandatory traceable change-record rule for existing-skill updates. |
| `SKILL.md` | Workflow | Added traceable change-record mode before drafting/updating. |
| `SKILL.md` | Validation | Added `--require-change-records` validation command for file-changing updates. |
| `SKILL.md` | Deliver | Added Change ID and record-path reporting expectations. |
| `references/change-record-traceability.md` | all | Added detailed contract, category rules, templates, statuses, and final response contract. |
| `scripts/validate_create_skill.py` | validation logic | Added record structure validation, `--require-change-records`, and path resolution for `.` validation. |
| `scripts/test_create_skill.py` | deterministic tests | Added valid and missing-record cases. |
| `change-records/` | all | Added self-record system for this `create-skill` update. |

## Decision And Alternatives

Chosen: keep `SKILL.md` concise and place detailed traceability rules in `references/change-record-traceability.md`; implement deterministic validation in the existing validator with an optional required mode.

Alternatives considered:

- Put all rules in `SKILL.md`: rejected because it would bloat the core playbook.
- Require change records for every skill validation by default: rejected because brand-new guidance-only skills and legacy packages would fail unexpectedly.
- Use only a single `CHANGELOG.md`: rejected by final PRD and research evidence because long-term governance would be weak.

## Detailed Change

The workspace copy introduces a record mode for existing-skill updates. Agents must capture a baseline, allocate `CR-YYYYMMDD-NNN`, update `change-records/index.md`, update impacted category ledgers, create a dated detail record, run validation, and mention record paths in the final response.

The validator now checks `change-records/` when present and can require it explicitly with `--require-change-records`. The tests cover both a valid record system and a missing-record failure under required mode.

## Impact Analysis

- User-facing behavior: future `create-skill` updates should report Change ID and record paths when files changed.
- Skill workflow: existing-skill updates gain a traceability phase before drafting/updating.
- References/scripts/assets: one new reference and enhanced scripts.
- Downstream skills: `development-system` and handoff workflows get stronger evidence for completion review.
- Validation/reporting: required record validation can catch missing or malformed traceability artifacts.

## Validation Evidence

| Check | Command or Method | Result | Evidence |
|---|---|---|---|
| Baseline validator | `python -B validate_create_skill.py create-skill` on original global skill | passed | terminal output: accepted-with-constraints, P0/P1/P2 = 0 |
| Baseline tests | `python -B test_create_skill.py` on original global skill | passed | terminal output: create-skill tests passed |
| Workspace validator | `python -B scripts/validate_create_skill.py . --require-change-records` on same-name workspace copy | passed | terminal output: accepted-with-constraints, P0/P1/P2 = 0 |
| Workspace tests | `python -B scripts/test_create_skill.py` on same-name workspace copy | passed | terminal output: create-skill tests passed |
| Sensitive scan | validator sensitive-pattern scan | passed | included in workspace validator result |
| Global deployment | Copy validated workspace files to `~\.codex\skills\create-skill` after approval | passed | terminal output: deployed create-skill traceable change-record changes |
| Deployed validator | `python -B validate_create_skill.py create-skill --require-change-records` on global skill | passed | terminal output: accepted-with-constraints, P0/P1/P2 = 0 |
| Deployed tests | `python -B test_create_skill.py` on global skill | passed | terminal output: create-skill tests passed |
| Deployed sensitive scan | recursive local pattern scan | passed | terminal output: no obvious secret patterns found |

## Safety And Privacy

No credentials or private operational values are intentionally included. Local file paths are retained only as same-machine development evidence. Global skill deployment was approval-gated and completed after the workspace-copy validation passed.

## Risks And Follow-up

- The workspace copy must pass required record validation and deterministic tests before deployment.
- Copying the validated changes back to `~\.codex\skills\create-skill` required explicit user approval and was completed.
- After real usage, record any `development-system` routing, approval, feedback-review, or completion-judgment defects as required by the current dialogue node record.

Refs:

- Final PRD: `~\Documents\Codex\2026-08-09\new-chat-2\outputs\create-skill-traceable-change-records-final-prd.html`
- Research report: `~\Documents\Codex\2026-08-09\new-chat-2\outputs\create-skill-change-records-research-report.html`
