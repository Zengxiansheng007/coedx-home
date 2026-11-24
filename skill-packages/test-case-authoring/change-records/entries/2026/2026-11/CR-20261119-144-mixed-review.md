# CR-20261119-144 Mixed incremental review and isolated merge

| Field | Value |
| --- | --- |
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | changed |
| Scope | references-and-assets, scripts-and-validation, downstream-and-handoff |
| Source | [#144](https://github.com/Zengxiansheng007/coedx-home/issues/144) |
| Baseline | 939ecd2c48d5fae9c3b4af74c09afdcda95fa613 |
| Author | Codex |

## Summary

Show the five treatment types, place materials under the appropriate modules, and keep blank inputs and shared applicability readable. Keep increment labels in the review document and use the existing isolated merge entry for formal names.

## Context And Problem

The mixed sample needs multiple preparation scopes, shared post-operation conditions, action notes and a genuine source-only detail link.

## Sections Changed

The implementation, public-entry regression and `references/scoped-review-contract.md`
record the same behavior.

## Decision And Alternatives

Project existing selection decisions and file-backed links. Encode empty strings in the incremental layout while preserving the actual data object and value. Reuse the existing scoped confirmation and isolated merge contract.

## Impact Analysis

The updated output is scoped to the versioned candidate or verified active
selection. Existing approvals and release records keep their source identities.

## Validation Evidence

Mixed display, precision of shared feedback, unchanged return, reference-only detail, and selected isolated merge are tested using hypothetical fixtures.

## Safety And Privacy

The checks used isolated local copies or hypothetical values. The evidence
and sensitive project inputs stay outside the source commit.

## Risks And Follow-up

Client checks remain in #153.
