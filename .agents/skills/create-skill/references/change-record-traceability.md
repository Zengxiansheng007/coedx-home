# Change Record Traceability Contract

Use this contract whenever `create-skill` changes an existing skill. A file-changing update is not complete until the change is traceable, validated, and referenced in the final response.

## When This Contract Applies

Apply when the task creates, edits, moves, deletes, or renames files in an existing skill package, including:

- `SKILL.md`;
- `references/`;
- `scripts/`;
- `assets/`;
- `agents/openai.yaml`;
- validation, report, or delivery rules.

Do not require change records for guidance-only work where no files are changed. If the user asks for a minimal change, still create records, but mark the detail record as `minimal-change` and list intentionally skipped impact checks.

## Record Artifact System

Use this structure inside the target skill:

```text
change-records/
  index.md
  categories/
    core-skill-md.md
    references-and-assets.md
    scripts-and-validation.md
    agent-metadata.md
    safety-and-governance.md
    downstream-and-handoff.md
  entries/
    YYYY/
      YYYY-MM/
        CR-YYYYMMDD-NNN-short-title.md
```

## Required Record Updates

Every file-changing update must:

1. Capture the source baseline before edits.
2. Allocate a unique Change ID in the form `CR-YYYYMMDD-NNN`.
3. Update `change-records/index.md`.
4. Update every impacted category ledger under `change-records/categories/`.
5. Add one detail record under `change-records/entries/YYYY/YYYY-MM/`.
6. Record validation evidence, skipped validation with reasons, sensitive-data scan result, and remaining risks.
7. Reference the Change ID and record paths in the final response.

## Category Ledgers

Use these default categories:

| Category file | Use when changes affect |
|---|---|
| `core-skill-md.md` | `SKILL.md` trigger wording, operating rules, workflow, decision rules, validation, or escalation. |
| `references-and-assets.md` | `references/` or `assets/` content, templates, rubrics, or schemas. |
| `scripts-and-validation.md` | validators, tests, deterministic scripts, command contracts, or validation evidence. |
| `agent-metadata.md` | `agents/openai.yaml` or UI-facing metadata. |
| `safety-and-governance.md` | approval gates, privacy boundaries, forbidden actions, governance, or sensitive-data handling. |
| `downstream-and-handoff.md` | handoff contracts, downstream skill routing, A2A packets, or feedback review boundaries. |

Each category ledger must include:

```markdown
# <Category Name> Change Ledger

## Purpose

## Outline

| Date | Change ID | Section | Change Type | Summary | Status |
|---|---|---|---|---|---|

## Detailed Records

### CR-YYYYMMDD-NNN - short-title

- Section changed:
- Before:
- After:
- Why:
- Impact:
- Validation:
- Detail record:
```

## Detail Record Template

```markdown
# CR-YYYYMMDD-NNN - Short Title

| Field | Value |
|---|---|
| Status | proposed / applied / validated / blocked / superseded / reverted |
| Target Skill | skill-name |
| Change Type | added / changed / fixed / removed / security / validation / governance |
| Scope | core-skill-md / references-and-assets / scripts-and-validation / agent-metadata / safety-and-governance / downstream-and-handoff |
| Source | user request / defect / validation failure / review finding |
| Baseline | git commit or file timestamp/checksum summary |
| Author | Codex / user / mixed |
| Related Records | CR-... |

## Summary

## Context And Problem

## Sections Changed

| File | Section | Change Summary |
|---|---|---|

## Decision And Alternatives

## Detailed Change

## Impact Analysis

## Validation Evidence

| Check | Command or Method | Result | Evidence |
|---|---|---|---|

## Safety And Privacy

## Risks And Follow-up

Refs:
```

## Status Rules

| Status | Meaning |
|---|---|
| `proposed` | Record exists before edits are complete. |
| `applied` | Files changed, but validation is incomplete or failed. |
| `validated` | Required validation and record updates are complete. |
| `blocked` | The change or record cannot be completed safely. |
| `superseded` | A later record replaces this decision. |
| `reverted` | A later record rolls back this change. |

Do not mark a record as `validated` when validation failed, was skipped without a reason, or sensitive-data scan found a real issue.

## Final Response Contract

For file-changing updates, the final response must include:

- Change ID;
- `change-records/index.md` path;
- impacted category ledger path(s);
- detail record path;
- validation commands and results;
- skipped validation and remaining risks.

If records cannot be written, return `blocked` or `review-required`; do not present the skill update as complete.
