# CR-20261115-007 — Same-version complete handoff

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | added |
| Scope | references-and-assets / scripts-and-validation / downstream-and-handoff |
| Source | Authorized issue #119, REQ-022, AC-031 |
| Baseline | bc8049c; integrated 351ee17 |
| Author | Codex |

## Summary

Existing checkpoint and resume entries reconstruct complete meaning and revalidate current P0 evidence instead of trusting saved success.

## Context And Problem

Saved recovery material previously checked source bytes but did not reconstruct active references or require current qualified P0 evidence. Review also found unrelated qualified P0 scope could mask an active unqualified source, and old checkpoint metadata could lag new decisions.

## Sections Changed

scripts/qa_record.py; scripts/test_handoff_revalidation.py; scripts/test_recovery.py; references/qa-record-contract.md; change records.

## Decision And Alternatives

Reuse expanded and check_extension through existing checkpoint/resume. No new approval flow, maintained expanded draft or execution checklist. Require actual evidence file for extension candidates; historical extension checkpoints report a gap instead of silently passing.

## Detailed Change

Bind current catalog/baseline/reports/request evidence path and hash. Verify each active definition belongs to passed scope and matches current source version, step and data. Historical unused definitions remain traceable. Return transient complete_batch only with no conflicts. Bind checkpoint event position and content version; subsequent decision events invalidate its next-step metadata, ordinary notes do not.

## Impact Analysis

P0 recovery remains compatible. P1/P2 callers provide current evidence explicitly. Recovery preserves original approval and pending states; complete restoration does not grant execution permission or downstream compatibility.

## Validation Evidence

Initial missing-parameter failure followed by passing handoff test. Two review regressions failed before repair and passed after. Pre-integration full suite: 177 passed. Post-repair targeted suite: 10 passed. Final integrated suite: 181 passed, external test-output/rr07/tests.txt. Actual XMind import/edit not verified: Sky snapshot blocked and alternative CUA app selection returned approval timeout. Tests do not substitute for actual client acceptance or business results.

## Safety And Privacy

Synthetic inputs only; no business execution, formal catalog mutation, global installation or publication. Existing seven structural validator findings remain out of scope.

## Risks And Follow-up

Client AC remains blocked. Actual multi-turn synthetic rehearsal completed through same-file questions, local modification, explicit shared P0 change, old-evidence rejection, explicitly authorized synthetic requalification, final review and checkpoint/resume. External handoff-result.json reports no conflicts, same content version and both cases not_run. Permission/display fixture gaps remain unresolved. This change is candidate implementation, not whole-ticket acceptance; the client requirement and real downstream compatibility remain unverified.
