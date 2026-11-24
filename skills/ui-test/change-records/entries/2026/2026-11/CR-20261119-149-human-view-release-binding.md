# CR-20261119-149 Bind authored Human View during release

| Field | Value |
| --- | --- |
| Status | applied |
| Target Skill | ui-test |
| Change Type | changed |
| Scope | references-and-assets, scripts-and-validation, downstream-and-handoff |
| Source | [#149](https://github.com/Zengxiansheng007/coedx-home/issues/149) |
| Baseline | 9155388d79c7b8c94694b813f2125116aa140f20 |
| Author | Codex |

## Summary

The selected formal compile produces a sanitized request with a fixed renderer version. Planning and activation bind the produced bytes to the same branch, build and active view. Existing archives use their historical format.

## Context And Problem

This ticket adds the confirmed authoring and publication behavior at the
existing entry. The active version and build identity must remain traceable.

## Sections Changed

The implementation and public-entry regression are recorded in this commit
and its companion reference.

## Decision And Alternatives

Retain the existing archive identities. Use current governed inputs for
the additional output and verify it during the existing workflow.

## Impact Analysis

The versioned entry enables the new behavior for the selected release or
product scope. Historical artifacts stay available under their build IDs.

## Validation Evidence

Publication and wrong-branch rejection passed through the v2 compiler, prepare, verification and activation APIs. The synthetic branch retains the exact handoff, archive and detail bytes.

## Safety And Privacy

Inputs used in tests are local isolated files. Runtime data retains its
configuration references. No business site was contacted.

## Risks And Follow-up

The integrated workflow and user-performed client checks are tracked by #153.
