# CR-20261119-148 Refresh affected maps and retain the previous directory

| Field | Value |
| --- | --- |
| Status | applied |
| Target Skill | ui-test |
| Change Type | changed |
| Scope | references-and-assets, scripts-and-validation, downstream-and-handoff |
| Source | [#148](https://github.com/Zengxiansheng007/coedx-home/issues/148) |
| Baseline | 51f75c4 |
| Author | Codex |

## Summary

Fingerprint each module using its active source selection, route and related display evidence. Reuse verified unchanged files and switch the total directory after new module files and target release identities pass readback.

## Context And Problem

Updates must identify the active source version and leave historical output
available. Retry uses the same public entry and verifies actual bytes.

## Sections Changed

The public-entry regression covers the output, current build and retained
historical artifact.

## Decision And Alternatives

Reuse the existing active version and resolved input contracts.

## Impact Analysis

The scoped change preserves unrelated modules or branches.

## Validation Evidence

Isolated refresh regressions verify unaffected file modification time, interruption before the directory switch, known active-build drift and retry, module move, and retirement.

## Safety And Privacy

Tests use isolated local fixtures.

## Risks And Follow-up

The complete integrated run still requires #153 and its client evidence.
