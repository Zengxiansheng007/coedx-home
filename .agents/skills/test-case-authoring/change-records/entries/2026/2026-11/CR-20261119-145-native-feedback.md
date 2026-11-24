# CR-20261119-145 Native XMind feedback and recovery

| Field | Value |
| --- | --- |
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | changed |
| Scope | references-and-assets, scripts-and-validation, downstream-and-handoff |
| Source | [S1-03 / #145](https://github.com/Zengxiansheng007/coedx-home/issues/145) |
| Baseline | 2853c8ebf79b2f8668f845721c242903955a28f2 |
| Author | Codex |

## Summary

Identify current and superseded native returns by the saved review version.
Start and recover valid native feedback through the existing Q&A record.

## Context And Problem

The older native reader expected links in the review header. The new guide
has a dedicated materials section. It also needs stable rendering order
across the first draft and Q&A serialization.

## Sections Changed

| File | Change |
| --- | --- |
| `scripts/xmind_feedback.py` | Bind materials, identify stale inputs and record valid feedback. |
| `scripts/scoped_review.py`, `scripts/aggregation.py` | Reproduce display after replay and inspect versioned topics. |
| `scripts/feedback.py`, `scripts/feedback_record.py` | Record original provenance and apply existing review rules. |
| `scripts/test_incremental_native_return.py` | Check same-version, stale, conflicting and saved native returns. |
| `references/xmind-feedback-contract.md` | Document return inputs and record entry. |

## Decision And Alternatives

Reconstruct approved material links at their exact topic location. Store the
normalized return and original digest in the sole Q&A event.

## Impact Analysis

Legacy files retain the existing reader. Clear current edits proceed to the
existing summary and review gates. Duplicate native returns reuse the event.

## Validation Evidence

| Check | Result |
| --- | --- |
| Native format, Markdown and recovery regression | 17 selected tests passed using isolated fixtures. |
| Actual client import and return | Tracked in joint acceptance #153. |

## Safety And Privacy

The adapter reads bounded offline documents. Original evidence stays with its
local source. The fixtures contain no real business or account data.

## Risks And Follow-up

The user performs Windows XMind import, link checks and a client-edited return
under #153.
