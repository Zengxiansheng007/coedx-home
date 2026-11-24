# CR-20261119-152 Human View release recovery

| Field | Value |
| --- | --- |
| Status | applied |
| Target Skill | ui-test |
| Change Type | fixed |
| Scope | scripts-and-validation, references-and-assets, safety-and-governance |
| Source | [#152](https://github.com/Zengxiansheng007/coedx-home/issues/152) |
| Baseline | 4910bf8 |
| Author | Codex |

## Summary

Recover the active pointer and the previous detail from the branch's
saved activation state. Verify the expected bytes on reuse and retry.

## Context And Problem

The stable view and active pointer are different files. Abrupt termination
between writes needs exact before-images and a recoverable activation state.

## Sections Changed

The existing sync path, archive verifier and formal release regression
cover identity, raw byte binding, interruption, conflict and retry.

## Decision And Alternatives

Use the existing branch lock and a temporary activation record. Publish
the stable view after registering the pointer. Reject unresolved activation
during ordinary archive verification and restore the previous state on retry
when the new detail was never committed.

## Impact Analysis

Earlier archives remain immutable. Repeated requests require the same
product identity, build and exact archived and active Markdown bytes.

## Validation Evidence

The initial regression demonstrated stale visible bytes after interruption.
The targeted suite passed 18 checks covering that case, changed and missing handoffs,
wrong branch or build, and concurrent changes using isolated files.

## Safety And Privacy

The temporary record retains only the previous detail and pointer within
the selected branch. Verification uses no business system.

## Risks And Follow-up

Use the integrated isolated run and user-performed XMind checks in #153.
