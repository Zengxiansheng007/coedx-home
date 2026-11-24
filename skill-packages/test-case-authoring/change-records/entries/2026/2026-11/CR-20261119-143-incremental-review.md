# CR-20261119-143 Incremental review and Markdown return

| Field | Value |
| --- | --- |
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | added |
| Scope | references-and-assets, scripts-and-validation, downstream-and-handoff |
| Source | [S1-01 / #143](https://github.com/Zengxiansheng007/coedx-home/issues/143) |
| Baseline | 374d6a56b01903727540f44d457f8043347e9b87 |
| Author | Codex |

## Summary

The scoped-review entry supports versioned incremental Markdown. The saved ID
and existing edit origins locate authored actions, data and expected results.

## Context And Problem

The older layout grouped individual steps and identified edited cases by
their displayed subtree. The confirmed incremental layout needs a visible
stable ID and operations directly beneath the individual case.

## Sections Changed

| File | Change |
| --- | --- |
| `scripts/incremental_review.py` | Project the approved review structure from the existing scope tree. |
| `scripts/aggregation.py`, `scripts/scoped_review.py` | Select and persist the layout at the scoped Markdown entry. |
| `scripts/feedback.py`, `scripts/module_handoff.py` | Bind the returned view to its exact case identity and materials directory. |
| `scripts/test_incremental_review.py` | Check saved unchanged return and one edited expectation. |
| `references/scoped-review-contract.md` | Document the request and return context. |

## Decision And Alternatives

Project the existing scope tree into the versioned layout and keep its edit
origins. Reusing those origins preserves the existing confirmation and
shared-scope rules for Markdown edits.

## Impact Analysis

Newly requested incremental copies bind their layout to the saved candidate.
The existing candidate record contains the original business source and scope.
Legacy Markdown keeps its existing parsing path.

## Validation Evidence

| Check | Result |
| --- | --- |
| New test before implementation | Required layout argument absent. |
| Scoped-review, companion-link and note lifecycle regressions | 19 passed with the temporary directory in the isolated evidence location. |
| Grouped feedback and common operations | 18 passed after grouping compatible shared definitions. |
| Four-case source round trip | Checked nine operations, nine expectations, a shared four-case applicability list, the local materials link, zero unchanged changes and one bound expectation edit. |

## Safety And Privacy

The validated document, source identifiers and receipts stay in the local
acceptance directory. Repository fixtures are fictional. The skill validator
reports three existing synthetic credential fixtures in unchanged tests.

## Risks And Follow-up

Mixed review and isolation merge are tracked in #144. Native return and recovery
are tracked in #145. User-performed XMind acceptance is tracked in #153.
