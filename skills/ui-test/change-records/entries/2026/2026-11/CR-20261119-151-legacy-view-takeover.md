# CR-20261119-151 Selected legacy Human View takeover

| Field | Value |
| --- | --- |
| Status | applied |
| Target Skill | ui-test |
| Change Type | changed |
| Scope | scripts-and-validation |
| Source | [#151](https://github.com/Zengxiansheng007/coedx-home/issues/151) |
| Baseline | 51f75c4 |
| Author | Codex |

## Summary

A changed case can adopt the TCA renderer on its own release. Subsequent
plans respect the renderer recorded by the active release.

## Context And Problem

Unchanged legacy cases must continue to resolve their original detail
and history. The case under review keeps its old detail through preparation.

## Sections Changed

`case_sync.py` checks the recorded active renderer. The takeover test covers
the compiler, archive, active pointer and product map links.

## Decision And Alternatives

Bind continued ownership to the active manifest for each branch.

## Impact Analysis

The compatible stable entry points to the activated version. Unrelated
branches and previous immutable archives retain their bytes.

## Validation Evidence

Nine selected checks passed, including selected migration, old and current
navigation, and rejected legacy planning after adoption.

## Safety And Privacy

Tests create and read isolated synthetic archives.

## Risks And Follow-up

Actual Windows XMind navigation is tracked under #153.
