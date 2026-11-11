# CR-20261111-203 - Chinese presentation and stable identity

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | fixed |
| Scope | core-skill-md, references-and-assets, scripts-and-validation |
| Source | Approved PRE-03 presentation task |
| Baseline | 12f07270bf1ae55150d35b64dbc8f66184f298f6 |
| Author | Codex |
| Related Records | CR-20261111-202 |

## Summary
Separate business titles from stable internal identity in both public views and
bind feedback to the exact returned subtree after actual business clarification.

## Context And Problem
The aggregated tree exposed case IDs and used their heading prefixes for feedback
matching. Removing the prefix alone would lose rename and same-name identity.

## Sections Changed
| File | Section | Change Summary |
|---|---|---|
| SKILL.md, references/presentation-identity.md | Display and feedback | Chinese clarification and agent-only binding contract |
| scripts/presentation.py, authoring.py, scoped_review.py | Public views | Business title/reference display; stable source unchanged |
| scripts/aggregation.py, feedback.py, xmind_feedback.py | Return boundary | Exact subtree binding, current version, reply evidence and conservative ambiguity |
| scripts/test_*.py, identity_test_support.py | Public regression | Rename, same-name distinction, feedback and inherited display contracts |

## Decision And Alternatives
Reuse existing candidate IDs, immutable baseline, scalar mapping and review gates.
Unique full unchanged subtrees can match exactly. Edited subtrees require internal
bindings supported by actual business clarification. Never infer identity from
title or position. Native topic IDs lack a registered baseline and are not trusted.

## Detailed Change
Public headings and applicability omit English case codes; P0/P1/P2 remain.
Internal flat mapping and dependency IDs remain stable. Agent-maintained bindings
carry displayed version, complete returned subtree digest and actual reply; evidence
is retained and checked for tampering. Existing summary, review and merge boundaries
remain. Unseen cases remain in the full catalog.

## Impact Analysis
Ordinary/scoped views, Markdown scalar feedback and supported single-sheet native
returns share this contract. Human-view file emission belongs to PRE-04 and is
unchanged. No UI-Test assets, global installation or business execution changed.

## Validation Evidence
| Check | Method | Result | Evidence |
|---|---|---|---|
| TDD | Public identity tests before implementation | Failed as expected, then passed for initial slices | Private PRE-03 logs |
| Feedback regression | Existing 8 public feedback tests | Passed after trusted review metadata normalization | Private execution log |
| Combined regression and mirror | Full skill discovery, byte comparison | Final result recorded in handoff | Private PRE-03 evidence |
| Real dialogue and XMind client | Independent host exercise | Pending at implementation handoff | Host-owned evidence |
| Skill validator | require-change-records | Inherited findings retained; final output in handoff | Private PRE-03 evidence |

## Safety And Privacy
Synthetic inputs only. Source requirements and transcripts remain private outside
the repository. No installation, network export, publishing or real execution.

## Risks And Follow-up
Candidate only. Completely indistinguishable returns require business clarification
and chat-based correction; arbitrary native annotations and structural edits remain
unsupported. Client import and actual multi-turn simulation must be completed by
the host before claiming full PRE-03 acceptance. Inherited validator findings remain.

Refs: [Presentation identity](../../../../references/presentation-identity.md).
