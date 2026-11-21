# Change Records

## Latest Changes

| Date | Change ID | Summary | Status |
|---|---|---|---|
| 2026-09-28 | CR-20260928-001 | Separate candidate validation from trusted gate acceptance and add a mandatory-gate contract. | validated |
| 2026-08-09 | CR-20260809-001 | Add traceable change-record requirements, validation, and self-records to `create-skill`. | validated |

## Category Index

| Category | Path | Purpose |
|---|---|---|
| Core Skill Markdown | categories/core-skill-md.md | Changes to `SKILL.md` workflow, operating rules, validation, and delivery contract. |
| References And Assets | categories/references-and-assets.md | Changes to references, templates, and traceability contract details. |
| Scripts And Validation | categories/scripts-and-validation.md | Changes to validators and deterministic tests. |
| Safety And Governance | categories/safety-and-governance.md | Changes to approval gates, sensitive-data boundaries, and governance rules. |
| Downstream And Handoff | categories/downstream-and-handoff.md | Contracts passed to a controlled Codex host for independent enforcement. |

## Open Risks

- No open P0/P1 risks for CR-20260809-001 after local copy validation.
- Global skill deployment was approved and completed; deployed global validation passed.
- CR-20260928-001 passed focused tests, structure validation, and 14-file global hash readback. A controlled Codex host is not supplied by this package, so mandatory runtime enforcement cannot yet be marked accepted.
