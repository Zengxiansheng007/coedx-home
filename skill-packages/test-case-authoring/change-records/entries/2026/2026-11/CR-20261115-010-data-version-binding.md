# CR-20261115-010 — Shared data version bindings

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | fixed |
| Scope | scripts-and-validation / references-and-assets |
| Source | semantic-06 P1, issue 118, REQ-020 / AC-029 |
| Baseline | b96cd83 |
| Author | Codex |

## Summary
Shared source data changes now create immutable versioned data bindings.

## Context And Problem
Source version and step changed without its data; reference consumers rejected changed rules.

## Sections Changed
shared_step_feedback.py, test_shared_step_feedback.py and references/step-reuse.md.

## Decision And Alternatives
Copy-on-write data retains old consumers and historical snapshots. Global overwrite rejected.

## Detailed Change
Bind displayed P0 and continuing consumers to revised data. Preserve unchanged current generated bindings. Independent consumers retain old data. Source checks compare full business signatures so subsequent reviews accept versioned identities.

## Impact Analysis
Candidate-only update; old data and definitions retained. Existing deferred-review atomicity unchanged.

## Validation Evidence
Governed Python public feedback red: one failure and two errors. Green targeted: three tests including six data-binding subcases, multiple data and new generation rules, continued formatting and local feedback. Full regression evidence: external test-output/rr06-fix/tests.txt.

## Safety And Privacy
Synthetic fixtures only; no credentials, installs, publishing or real business changes.

## Risks And Follow-up
Independent review required. No actual XMind client qualification. Structural validator inherited findings remain separate.
Full regression: 169 tests passed. Runner trailing exit syntax failed after unittest completed; evidence retains genuine unittest OK. Final slot-identity guard targeted rerun: 3 tests passed. Diff check passed.
