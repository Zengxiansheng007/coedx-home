# CR-20261119-146 Product directory and module maps

| Field | Value |
| --- | --- |
| Status | applied |
| Target Skill | ui-test |
| Change Type | changed |
| Scope | references-and-assets, scripts-and-validation, downstream-and-handoff |
| Source | [#146](https://github.com/Zengxiansheng007/coedx-home/issues/146) |
| Baseline | 939ecd2c48d5fae9c3b4af74c09afdcda95fa613 |
| Author | Codex |

## Summary

Open active verified branch archives once and produce a total Markdown directory and complete operation maps. Module and Human View links match the active build.

## Context And Problem

The existing product renderer expects one scope and expands that scope as a single outline. The current directory needs module links and stable single-case entries.

## Sections Changed

The implementation, public-entry regression and `references/case-preparation.md`
record the same behavior.

## Decision And Alternatives

Keep the existing callbacks. Add an active-release adapter at the same product output boundary. Use explicit independent-page ownership and the verified ordered resolved steps.

## Impact Analysis

The updated output is scoped to the versioned candidate or verified active
selection. Existing approvals and release records keep their source identities.

## Validation Evidence

13 product map and legacy aggregate tests passed. The two verified announcement archives reconstructed 14 and 15 operations and three readable encoded links from copy-only input. A second regression checks the release verifier.

## Safety And Privacy

The checks used isolated local copies or hypothetical values. The evidence
and sensitive project inputs stay outside the source commit.

## Risks And Follow-up

Multi-module qualification and incremental updates continue in #147 and #148. Client link checks are assigned to #153.
