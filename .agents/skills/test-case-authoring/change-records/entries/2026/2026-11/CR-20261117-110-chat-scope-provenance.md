# CR-20261117-110 - Chat scope provenance

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | fixed |
| Scope | references-and-assets / scripts-and-validation / downstream-and-handoff |
| Source | Actual public chat acceptance defect; #134 / #138 / #140 / #141 |
| Baseline | 3cbacc7e9dd399b425849ac99ebc57d28c20e83e |
| Author | Codex |
| Related Records | CR-20261117-109 |

## Summary
Render requested chat cases together while retaining complete current scope context and exact original parent provenance.

## Context And Problem
Single-case projections passed the current candidate as its own original catalog. This broke hash/version validation and duplicated module common operations, despite valid reviewed applicability.

## Sections Changed
Presentation, scoped renderer, aggregation and extension delivery; chat delivery reference; synthetic public regressions; identical distribution and records.

## Decision And Alternatives
Select display branches after assessing the complete current batch. Pass the optional original source_catalog separately; never fabricate provenance, weaken its digest check or reapprove membership.

## Detailed Change
One render aggregates requested cases. Per-item pre/post definitions and exceptions retain their existing authority. Source-only cases do not become visible bodies or questions. Genuine partial copies require the exact original parent; missing/stale parents stay pending. Candidate version and baseline remain unchanged.

## Impact Analysis
AC-030/031/032/034 and actual #141 chat delivery. Rendering is not fresh generation, client acceptance or business execution. Existing data/reference resolution, legacy feedback and all history remain.

## Validation Evidence
Red public regressions failed with false pending and absent exact-parent parameter. Three new synthetic scope regressions pass; required eight-stage checks and create-skill require-change-records reports are external task evidence. Initial broader run found the existing sandbox TEMP replacement denial; repeat uses task-owned TEMP. Independent review remains required.

## Safety And Privacy
No real acceptance input is copied into source/tests. Read-only real candidate reproduction is separate external evidence. No remote publishing, global install or business execution. Existing synthetic sensitive fixtures are reported separately from any new findings.

## Risks And Follow-up
Fresh real generation must use the frozen repaired source, followed by actual user review. Local checks cannot grant that acceptance.

Refs: #134, #138, #140, #141.
