# CR-20261119-147 Independent page ownership and linked dependencies

| Field | Value |
| --- | --- |
| Status | applied |
| Target Skill | ui-test |
| Change Type | changed |
| Scope | references-and-assets, scripts-and-validation, downstream-and-handoff |
| Source | [#147](https://github.com/Zengxiansheng007/coedx-home/issues/147) |
| Baseline | 9155388d79c7b8c94694b813f2125116aa140f20 |
| Author | Codex |

## Summary

Use the full stable navigation path to classify menus, redirects and independent pages. Published branches keep their original route and agree with the total map. Verified dependency labels reference an active case and a binding declared in the archived source.

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

The multi-module entry covered an announcement-style redirect, independent assets, same-name pages and missing route evidence. Existing single-module checks also passed.

## Safety And Privacy

Inputs used in tests are local isolated files. Runtime data retains its
configuration references. No business site was contacted.

## Risks And Follow-up

The integrated workflow and user-performed client checks are tracked by #153.
