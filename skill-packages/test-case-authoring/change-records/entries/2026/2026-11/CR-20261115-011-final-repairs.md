# CR-20261115-011 — Flat history and referenced handoff

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | fixed |
| Scope | scripts-and-validation / references-and-assets / downstream-and-handoff |
| Source | final-review/standards-pre.md two P2 findings |
| Baseline | bc8049c |
| Author | Codex |

## Summary
Preserve complete revision content once and restore referenced step instructions in module projections.

## Context And Problem
History copied its entire prior history recursively; compressed references hid inherited technical instructions.

## Sections Changed
shared_step_feedback.py, module_handoff.py, test_shared_step_feedback.py and corresponding reference contracts.

## Decision And Alternatives
Append snapshots excluding only the history container, retaining existing entries untouched. Resolve through the existing checked resolver rather than duplicate reference rules.

## Detailed Change
Three source reviews retain three complete historical source revisions. Source provenance and structured handoff render under the referencing case group and ordinal, in both human and XMind projections.

## Impact Analysis
Existing historical trees remain untouched; no destructive migration. New growth is linear. No shared source or compact candidate mutation during rendering.

## Validation Evidence
External test-output/final-repairs: red-history.txt, green-history.txt, red-handoff.txt, green-handoff.txt, regression.txt. Each regression failed before its corresponding fix; five targeted tests passed. Initial test-runner path and encoding errors were corrected before genuine assertion RED evidence. Full regression result recorded externally.

## Safety And Privacy
Synthetic inputs only. Diff contains no credentials or private business data. No installs, global writes, business execution or publishing.

## Risks And Follow-up
Independent review and merge pending; no actual XMind client qualification. Existing nested historical entries preserved rather than rewritten.

Follow-up: initial full regression exposed four feedback-probe errors. scoped_review now uses its existing expression baseline for immutable module instructions; internal marker probes are not candidate sources. See regression-final.txt. Initial structural validation also found this batch CR-009 record defects; these were subsequently corrected as documentation-only work. No CR-011 findings.
