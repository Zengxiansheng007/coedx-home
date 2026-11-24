# CR-20261119-150 Branch-specific Human View data

| Field | Value |
| --- | --- |
| Status | applied |
| Target Skill | ui-test |
| Change Type | added |
| Scope | scripts-and-validation |
| Source | [#150](https://github.com/Zengxiansheng007/coedx-home/issues/150) |
| Baseline | 51f75c4 |
| Author | Codex |

## Summary

Two branches use the same data path and independently publish their
resolved parameters and assertions. A later data-only change publishes
one new build and keeps the other branch and older archive.

## Context And Problem

Branch labels are independent of the parameter identities and JSON
Pointers that determine the value.

## Sections Changed

`tests/test_human_view_branch_data.py` covers the compiler, TCA renderer,
release plan and archive verifier as one entry sequence.

## Decision And Alternatives

Exercise the existing binding with different case data. The implementation
already derives the display and assertion values from that same build.

## Impact Analysis

The regression binds the unchanged source hash and verifies the distinct
data hash, build ID, and resulting document bytes.

## Validation Evidence

Nine selected branch, formal publication and data contract checks passed.

## Safety And Privacy

The fixture uses local data and configuration references.

## Risks And Follow-up

Joint acceptance follows under #153.
