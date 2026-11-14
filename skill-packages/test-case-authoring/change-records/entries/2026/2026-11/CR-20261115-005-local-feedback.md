# CR-20261115-005 — Local referenced-step feedback

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | added |
| Scope | core-skill-md / references-and-assets / scripts-and-validation |
| Source | User-authorized issue #117, REQ-021 / AC-030 |
| Baseline | dc52db180f55d53fb9fbc76062471ef87f69f483 |
| Author | Codex |

## Summary

Chat, Markdown and supported native returns modify the current candidate only.
After actual summary agreement, a changed reference becomes one complete local
step. Other references and frozen P0 definitions retain their original content.

## Context And Problem

Reference-only records had no editable business leaves. Scalar edits could not
map the displayed action, and partial overrides would violate the reuse contract.

## Sections Changed

feedback.py resolves inherited scalar fields and applies local copies;
local_step_feedback.py materializes current bindings and renews endpoint proofs;
scoped_review.py preserves compact layout during feedback probes. Public tests,
SKILL.md and step-reuse.md describe the same candidate-only behavior.

## Decision And Alternatives

Reuse existing summary, clarification and final-review gates. Do not introduce
shared-source editing or a second review system. Outer action whitespace is a
conservative formatting-only no-op; unknown semantic equivalence needs the Agent.

## Detailed Change

Source identities cannot be edited. A complete resolved step replaces a reference
before local scalar writes; target order and endpoint are rebound afterward.
The source catalog, another referencing case and historical baseline stay intact.

## Impact Analysis

No execution, global install or formal catalog update. Explicit P0 updates remain
outside this ticket and require the existing shared-impact clarification boundary.

## Validation Evidence

Observed public red/green: chat initially rejected unknown displayed field;
Markdown initially rejected unmapped edit; whitespace initially created a change.
Four new public tests cover chat/MD/native, complete local content, two consumers,
source immutability, protected reference metadata and formatting scope.
Full regression output: external test-output/rr05/tests.txt.
162 tests passed. Structural validator retains the seven baseline findings
(three synthetic secret-pattern fixtures, description wording, conventional
validation/safety headings, command resource parsing). No new change-record
finding; scanner status is still rejected, not package acceptance.

## Safety And Privacy

Synthetic data only. No credentials, real business runs or client automation.

## Risks And Follow-up

Native archive parsing is not actual XMind client acceptance; client verification
belongs to #119. Arbitrary semantic equivalence is an Agent judgment.
