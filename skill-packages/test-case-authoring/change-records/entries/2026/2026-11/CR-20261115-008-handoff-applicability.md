# CR-20261115-008 - Handoff applicability

| Field | Value |
|---|---|
| Status | validated |
| Target Skill | test-case-authoring |
| Change Type | fixed |
| Scope | scripts-and-validation / references-and-assets / downstream-and-handoff |
| Source | independent review of #113; #112 REQ-015-016 AC-023-024 |
| Baseline | 3b8aeeb |

## Summary

Bind technical instructions to group, ordinal and business operation without requiring provenance fields.

## Context And Problem

Case-wide deduplication collapsed identical sourceless step policies; distinct policies also lacked applicability.

## Sections Changed

module_handoff.py, test_module_handoff.py and module-handoff-contract.md.

## Decision And Alternatives

Retain each step scope in every instruction. Deduplicate within a scope; preserve original candidate.

## Impact Analysis

Both human and tree views use the same projection. Business validity stays in body. No step reuse implementation changed.

## Validation Evidence

Public render_batch to prepare_feedback regression failed before repair; 151 full script tests passed after repair (test-output/rr01-fix/tests.txt). Equal and distinct policies without source/lines retain both steps and unchanged feedback, candidate and business validity. Synthetic tests only.

## Safety And Privacy

Only synthetic input; no credentials, global installation, publishing or real execution. Operation text uses existing business projection; internal step IDs are never selected.

## Risks And Follow-up

Independent review pending; actual XMind client acceptance remains RR07.
